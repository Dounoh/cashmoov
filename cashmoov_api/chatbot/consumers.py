import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ValidationError


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps(
            {
                "type": "welcome",
                "message": "Bienvenue Monsieur, je suis l'assistant IA CashMoov"
            }
        ))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)



    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            username = data.get("username", "").strip()
            message = data.get("message", "").strip()

            if not username or not message:
                await self.send_error("Username et message requis")
                return

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "username": username,
                    "group_name": self.room_group_name,
                    "message": message
                }
            )

            response = await self.search_response_ia(message)
            if not response or (response and response.get("type") == "response_none"):
                await self.send(text_data=json.dumps({
                    "type": "waiting",
                    "message": "Le message est transmis à un assistant humain."
                }))

                await self.channel_layer.group_send(
                    "notifications",
                    {
                        "type": "new.message",
                        "username": username,
                        "group_name": self.room_group_name,
                        "message": message
                    }
                )
            else:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "ia.message",
                        "username": response["username"],
                        "message": response["message"]
                    }
                )

        except json.JSONDecodeError:
            await self.send_error("Format de message JSON invalide")



    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat.message",
            "username": event.get("username"),
            "group_name": event.get("group_name"),
            "message": event["message"]
        }))


    async def ia_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "ia.message",
            "username": event.get("username"),
            "message": event["message"]
        }))

    async def send_error(self, error_message):
        """Envoyer un message d'erreur"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': error_message
        }))

    async def search_response_ia(self, query_text):
        from cashmoov_api.chatbot.rags.retrieval import search_documents

        response = None 

        try:
            response = await search_documents(query_text)
        except Exception as e:
            await self.send_error(f"Erreur IA: {str(e)}")
            response = f"Erreur lors du traitement du message: {str(e)}"

        return response
    



class NotificationConsumer(AsyncWebsocketConsumer):
    unanswered_counts = {}

    async def connect(self):
        await self.channel_layer.group_add("notifications", self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            "type": "notification.init",
            "count": 0
        }))


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifications", self.channel_name)


    async def new_message(self, event):
        group_name = event["group_name"]

        self.unanswered_counts[group_name] = self.unanswered_counts.get(group_name, 0) + 1

        await self.send(text_data=json.dumps({
            "type": "notification",
            "group_name": group_name,
            "count": self.unanswered_counts[group_name],
            "username": event["username"],
            "message": event["message"]
        }))


    async def message_answered(self, event):
        group_name = event["group_name"]

        if group_name in self.unanswered_counts:
            self.unanswered_counts[group_name] = max(0, self.unanswered_counts[group_name] - 1)

        await self.send(text_data=json.dumps({
            "type": "notification.decrement",
            "groupe_name": group_name,
            "count": self.unanswered_counts.get(group_name, 0)
        }))
