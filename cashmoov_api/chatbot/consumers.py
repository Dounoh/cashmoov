import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from cashmoov_api.chatbot.redis import (
    get_online_users,
    add_online_user,
    remove_online_user,
)

USER_TYPE_CUSTOMER = 'customer'
USER_TYPE_ASSISTANT = 'assistant'
TYPE_RESPONSE = 'response_none'


class ChatConsumer(AsyncWebsocketConsumer):
    """
    La view pour le chat la conversation
    """

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope["user"]

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        if self.user.is_authenticated:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "username": self.user.first_name,
                    "group_name": self.room_name,
                    "message": "un assistant a rejoint votre discussion",
                },
            )

            questions = await self.load_chat(self.room_group_name)

            await self.send(
                text_data=json.dumps(
                    {
                        "type": "history",
                        "data": questions,
                    }
                )
            )

        else:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "welcome",
                        "message": (
                            "Bonjour et bienvenue sur CashMoov ! "
                            "Si vous avez des questions ou besoin d'assistance, "
                            "notre service client est à votre disposition ☺️"
                        ),
                    }
                )
            )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        username = (
            self.user.first_name
            if self.user.is_authenticated
            else "client"
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "username": username,
                "group_name": self.room_name,
                "message": "A quitté votre discussion.",
            },
        )

    async def receive(self, text_data):
        response = None
        try:
            data = json.loads(text_data)

            username = (
                self.user.first_name
                if self.user.is_authenticated
                else "client"
            )

            message = data.get("message", "").strip()
            user_type = data.get("user_type", "").strip()

            if not username or not message or not user_type:
                await self.send_error("Username message et type requis")
                return

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "username": username,
                    "group_name": self.room_name,
                    "message": message,
                },
            )

            if user_type == USER_TYPE_CUSTOMER:
                response = await self.search_response_ia(message)

                if not response or (
                    response and response.get("type") == TYPE_RESPONSE
                ):
                    users = await database_sync_to_async(get_online_users)()

                    if len(users) > 0:
                        await self.send(
                            text_data=json.dumps(
                                {
                                    "type": "waiting",
                                    "message": "Le message est transmis à un assistant humain.",
                                }
                            )
                        )
                    else:
                        await self.send(
                            text_data=json.dumps(
                                {
                                    "type": "waiting",
                                    "message": (
                                        "Aucun assistant en ligne veillez revenir plus tard s'il vous plait."
                                    ),
                                }
                            )
                        )

                    await self.create_chat(
                        group_name=self.room_group_name,
                        username=username,
                        message=message,
                    )

                    await self.channel_layer.group_send(
                        "notifications",
                        {
                            "type": "new.message",
                            "username": username,
                            "group_name": self.room_name,
                            "message": message,
                        },
                    )
                else:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "ia.message",
                            "username": response["username"],
                            "message": response["message"],
                        },
                    )

                    await self.create_chat(
                        group_name=self.room_group_name,
                        message=response["message"],
                        username="ia",
                    )

            else:
                await self.create_chat(
                    group_name=self.room_group_name,
                    message=message,
                    username=self.user.first_name,
                )

                await self.channel_layer.group_send(
                    "notifications",
                    {
                        "type": "message.answered",
                        "username": username,
                        "group_name": self.room_name,
                        "message": f"{username} a répondu au client.",
                    },
                )

        except json.JSONDecodeError:
            await self.send_error("Format de message JSON invalide")

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat.message",
                    "username": event.get("username"),
                    "group_name": event.get("group_name"),
                    "message": event["message"],
                }
            )
        )

    async def ia_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "ia.message",
                    "username": event.get("username"),
                    "message": event["message"],
                }
            )
        )

    async def send_error(self, error_message):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "error",
                    "message": error_message,
                }
            )
        )

    async def search_response_ia(self, query_text):
        from cashmoov_api.chatbot.rags.retrieval import search_documents

        response = None

        try:
            response = await search_documents(query_text)
        except Exception as e:
            await self.send_error(f"Erreur IA: {str(e)}")
            response = None

        return response

    @database_sync_to_async
    def create_chat(self, group_name, message, username):
        from cashmoov_api.chatbot.models import Chatbot, Group

        group, _ = Group.objects.get_or_create(name=group_name)
        Chatbot.objects.create(
            username=username,
            group=group,
            question=message,
        )

    @database_sync_to_async
    def load_chat(self, group_name):
        from cashmoov_api.chatbot.models import Chatbot, Group

        try:
            group = Group.objects.prefetch_related("chatbots").get(name=group_name)
            chats = group.chatbots.all()
        except Group.DoesNotExist:
            return []

        return [
            {
                "message": chat.question,
                "username": chat.username,
                "group_name": group.name,
            }
            for chat in chats.order_by("-created_at")
        ]


class NotificationConsumer(AsyncWebsocketConsumer):
    unanswered_counts = {}

    async def connect(self):
        await self.channel_layer.group_add("notifications", self.channel_name)
        await self.accept()

        self.user = self.scope["user"]
        self.username = USER_TYPE_ASSISTANT

        await self.send(
            text_data=json.dumps(
                {
                    "type": "notification.init",
                    "count": 0,
                }
            )
        )

        await self.channel_layer.group_send(
            "online",
            {
                "type": "add.online",
                "username": self.username,
            },
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifications", self.channel_name)

        await self.channel_layer.group_send(
            "online",
            {
                "type": "remove.online",
                "username": self.username,
            },
        )

    async def new_message(self, event):
        group_name = event["group_name"]

        self.unanswered_counts[group_name] = (
            self.unanswered_counts.get(group_name, 0) + 1
        )

        await self.send(
            text_data=json.dumps(
                {
                    "type": "notification",
                    "group_name": group_name,
                    "count": self.unanswered_counts[group_name],
                    "username": event["username"],
                    "message": event["message"],
                }
            )
        )

    async def message_answered(self, event):
        group_name = event["group_name"]

        if group_name in self.unanswered_counts:
            self.unanswered_counts[group_name] = 0

        await self.send(
            text_data=json.dumps(
                {
                    "type": "notification.decrement",
                    "groupe_name": group_name,
                    "count": self.unanswered_counts.get(group_name, 0),
                }
            )
        )


class OnlineUser(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("online", self.channel_name)
        await self.accept()

        self.username = (
            self.scope["user"].first_name
            if self.scope["user"].is_authenticated
            else "client"
        )

        await database_sync_to_async(add_online_user)(self.username)

        await self.broadcast_online_state(
            f"{self.username} est maintenant en ligne"
        )

    async def disconnect(self, close_code):
        await database_sync_to_async(remove_online_user)(self.username)

        await self.broadcast_online_state(
            f"{self.username} n'est plus en ligne"
        )

        await self.channel_layer.group_discard("online", self.channel_name)

    async def broadcast_online_state(self, message):
        users = await database_sync_to_async(get_online_users)()

        await self.channel_layer.group_send(
            "online",
            {
                "type": "online.users",
                "count": len(users),
                "members": users,
                "message": message,
            },
        )

    async def online_users(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "online_users",
                    "count": event["count"],
                    "members": event["members"],
                    "message": event["message"],
                }
            )
        )
