import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from cashmoov_api.chatbot.redis import (
    add_online_user,
    get_online_users,
    remove_online_user,
    assistant_existed,
    assistant_joigned,
    remove_assistant_joigned
)

USER_TYPE_CUSTOMER = "customer"
USER_TYPE_ASSISTANT = "assistant"
TYPE_RESPONSE = "response_none"


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Le consumer pour la gestion de tout ce qui est chat
    """

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope["user"]

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        if self.user.is_authenticated:
            username = f"{self.user.first_name} {self.user.last_name}"
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.joingned",
                    "message": f"L'assistant {username} a rejoint votre discussion.",
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

            # await database_sync_to_async(add_online_user)(username)
            await database_sync_to_async(assistant_joigned)(self.room_group_name)

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
            f"{self.user.first_name} {self.user.last_name}"
            if self.user.is_authenticated
            else USER_TYPE_CUSTOMER
        )
        # user_type = self.user.user_type if self.user.is_authenticated else USER_TYPE_CUSTOMER

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.joingned",
                "message": f"{username} A quitté la discussion.",
            },
        )

        if self.user.is_authenticated:
            # await database_sync_to_async(remove_online_user)(username)
            await database_sync_to_async(remove_assistant_joigned)(self.room_group_name)


    async def receive(self, text_data):
        response = None
        try:
            data = json.loads(text_data)

            username = (
                f"{self.user.first_name} {self.user.last_name}"
                if self.user.is_authenticated
                else USER_TYPE_CUSTOMER
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
                    "user_type":user_type
                },
            )

            if user_type == USER_TYPE_CUSTOMER:
                is_assisted = await database_sync_to_async(assistant_existed)(self.room_group_name)

                response = await self.search_response_ia(message) if not is_assisted else None
                
                if response and response.get('type') != TYPE_RESPONSE:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "ia.message",
                            "username": response["username"],
                            "message": response["message"],
                            "user_type": "ia"
                        },
                    )
                else:
                    users = await database_sync_to_async(get_online_users)()
                    if not is_assisted and len(users) > 0:
                        await self.send(
                            text_data=json.dumps(
                                {
                                    "type":"waiting",
                                    "message":f"""
                                        Nous avons bien reçu votre message ! 
                                        Un membre de notre équipe va prendre le relais pour vous aider au mieux. 
                                        
                                        Pas besoin de renvoyer d'autre message, nous traitons votre demande prioritairement.
                                        """,
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
                    elif not is_assisted:
                        await self.send(
                            text_data=json.dumps(
                                {
                                    "type": "waiting",
                                    "message": (
                                        "Nos conseillers sont actuellement indisponibles."
                                        "Nous vous invitons à renouveler votre demande ultérieurement."
                                        "Merci de votre compréhension."
                                    ),
                                }
                            )
                        )
            else:
                await self.create_chat(
                    group_name=self.room_group_name,
                    answers=message,
                    username=username,
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
                    "user_type": event["user_type"]
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
                    "user_type": event["user_type"]
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


    async def chat_joingned(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat.joingned",
                    "message": event['message'],
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
    def create_chat(self, group_name, message=None, username=None, answers=None):
        from cashmoov_api.chatbot.models import Chatbot, Group

        group, _ = Group.objects.get_or_create(name=group_name)
        Chatbot.objects.create(
            username=username,
            group=group,
            question=message,
            answers=answers,
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
                "message": chat.question or "question_none",
                "username": chat.username,
                "group_name": group.name,
                "answere": chat.answers or "response_none"
            }
            for chat in chats.order_by("-created_at")
        ]
    


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Le consumer pour la gestion des notifications
    """

    unanswered_counts = {}

    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            self.send(text_data=json.dumps({"error": "Authentication required"}))
            await self.close()
            return

        await self.channel_layer.group_add("notifications", self.channel_name)
        await self.accept()

        self.username = f"{user.first_name} {user.last_name}"

        await self.send(
            text_data=json.dumps(
                {
                    "type": "notification.init",
                    "count": 0,
                }
            )
        )
        
        await database_sync_to_async(add_online_user)(self.username)
        await self.alerte_online(message="Connection d'un nouveau assistant")


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifications", self.channel_name)
        await database_sync_to_async(remove_online_user)(self.username)
        await self.alerte_online(message="deconnection d'un assistant")



    async def alerte_online(self,message):
        users = await database_sync_to_async(get_online_users)()
        await self.channel_layer.group_send(
            "online",
            {
                "type": "online.users",
                "count": len(users),
                "members": users,
                "message": message
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
    """
    Le consumer pour la gestion des assistants en ligne
    """

    async def connect(self):
        await self.channel_layer.group_add("online", self.channel_name)
        await self.accept()

        # user = self.scope["user"]
        # if user.is_authenticated:
        #     self.username = f"{user.first_name} {user.last_name}"

            # await database_sync_to_async(add_online_user)(self.username)

        await self.broadcast_online_state(f"Assistant en ligne.")

    async def disconnect(self, close_code):
        await database_sync_to_async(remove_online_user)(self.username)

        await self.broadcast_online_state(f"{self.username} n'est plus en ligne")

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

    
