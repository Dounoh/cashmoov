# # # cashmoov_api/chatbot/consumers.py
# import json
# import asyncio
# from channels.generic.websocket import AsyncWebsocketConsumer

# class ChatConsumer(AsyncWebsocketConsumer):
#     """
#     Consumer WebSocket pour le chatbot avec RAG
#     """
    
#     async def connect(self):
#         """Connexion d'un utilisateur au WebSocket"""
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = f"chat_{self.room_name}"
        
#         # Rejoindre le groupe
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
        
#         # Accepter la connexion
#         await self.accept()
        
#         # Envoyer un message de bienvenue immédiat
#         await self.send(text_data=json.dumps({
#             'type': 'connection_established',
#             'message': f'✅ Connecté au chat room: {self.room_name}',
#             'room': self.room_name,
#             'status': 'connected'
#         }))
        
#         print(f"✅ WebSocket connecté à la room: {self.room_name}")

#     async def disconnect(self, close_code):
#         """Déconnexion du WebSocket"""
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
#         print(f"📴 WebSocket déconnecté, code: {close_code}")

#     async def receive(self, text_data):
#         """Réception d'un message du WebSocket"""
#         try:
#             data = json.loads(text_data)
#             message = data.get('message', '').strip()
            
#             if not message:
#                 return
            
#             print(f"📥 Message reçu: {message[:100]}...")
            
#             # Accusé de réception
#             await self.send(text_data=json.dumps({
#                 'type': 'message_received',
#                 'message': 'Message reçu, traitement en cours...',
#                 'status': 'processing'
#             }))
            
#             # Traiter le message
#             await self.handle_user_message(message)
            
#         except json.JSONDecodeError:
#             await self.send_error("Format de message JSON invalide")
#         except Exception as e:
#             print(f"❌ Erreur: {e}")
#             await self.send_error(f"Erreur: {str(e)}")

#     async def handle_user_message(self, message):
#         """
#         Gérer un message utilisateur
#         """
#         try:
#             # Envoyer le message de l'utilisateur à tous les clients
#             await self.send(text_data=json.dumps({
#                 'type': 'user_message',
#                 'message': message,
#                 'sender': 'Utilisateur'
#             }))
            
#             # Simuler un traitement
#             await asyncio.sleep(0.5)
            
#             # Obtenir une réponse du RAG (si disponible)
#             rag_response = await self.get_rag_response(message)
            
#             if rag_response:
#                 # Utiliser la réponse du RAG
#                 await self.send(text_data=json.dumps({
#                     'type': 'bot_response',
#                     'sender': 'CashMoov IA',
#                     'message': rag_response,
#                     'source': 'RAG',
#                     'is_rag': True
#                 }))
#             else:
#                 # Réponse par défaut si pas de RAG
#                 default_response = await self.get_default_response(message)
#                 await self.send(text_data=json.dumps({
#                     'type': 'bot_response',
#                     'sender': 'CashMoov IA',
#                     'message': default_response,
#                     'source': 'default',
#                     'is_rag': False
#                 }))
                
#         except Exception as e:
#             print(f"❌ Erreur traitement message: {e}")
#             await self.send(text_data=json.dumps({
#                 'type': 'error',
#                 'message': f"Désolé, une erreur s'est produite: {str(e)}"
#             }))

#     async def get_rag_response(self, query):
#         """
#         Obtenir une réponse du système RAG
#         """
#         try:
#             # Importer la fonction de recherche seulement quand nécessaire
#             from .rags.retrieval import search_documents
            
#             # Exécuter dans un thread séparé
#             loop = asyncio.get_event_loop()
#             response = await loop.run_in_executor(None, search_documents, query)
            
#             if response and isinstance(response, str) and response.strip():
#                 response = response.strip()
                
#                 # Vérifier si ce n'est pas un message d'erreur
#                 error_messages = [
#                     "Je n'ai pas cette information pour le moment.",
#                     "Je n'ai pas trouvé d'information pour répondre à votre demande."
#                 ]
                
#                 if response not in error_messages and len(response) > 10:
#                     return response
            
#             return None
            
#         except ImportError as e:
#             print(f"⚠️  Module RAG non disponible: {e}")
#             return None
#         except Exception as e:
#             print(f"❌ Erreur RAG: {e}")
#             return None

#     async def get_default_response(self, query):
#         """
#         Réponse par défaut si RAG n'est pas disponible
#         """
#         # Réponses intelligentes basées sur des mots-clés
#         query_lower = query.lower()
        
#         responses = {
#             'bonjour': "Bonjour ! Comment puis-je vous aider avec CashMoov aujourd'hui ?",
#             'salut': "Salut ! Je suis l'assistant CashMoov. Que souhaitez-vous savoir ?",
#             'aide': "Je suis là pour vous aider ! Posez-moi vos questions sur CashMoov.",
#             'compte': "Pour créer un compte CashMoov : 1. Téléchargez l'app, 2. Inscrivez-vous, 3. Validez votre identité.",
#             'créer': "Pour créer un compte : téléchargez l'application CashMoov sur l'App Store ou Google Play.",
#             'frais': "CashMoov propose différents types de frais : transferts (1-3%), retraits (gratuits pour les Premium), etc.",
#             'virement': "Pour faire un virement : 1. Allez dans 'Envoyer', 2. Choisissez le destinataire, 3. Saisissez le montant.",
#             'carte': "Pour commander une carte : 1. Allez dans 'Carte', 2. Choisissez 'Commander', 3. Suivez les instructions.",
#             'support': "Contactez le support : support@cashmoov.net ou via le chat dans l'application.",
#             'merci': "De rien ! N'hésitez pas si vous avez d'autres questions sur CashMoov.",
#         }
        
#         # Chercher des mots-clés dans la requête
#         for keyword, response in responses.items():
#             if keyword in query_lower:
#                 return response
        
#         # Réponse par défaut
#         return f"J'ai bien reçu votre question : '{query}'. Pour des informations précises sur CashMoov, consultez notre FAQ ou contactez le support."

#     async def send_error(self, error_message):
#         """Envoyer un message d'erreur"""
#         await self.send(text_data=json.dumps({
#             'type': 'error',
#             'message': error_message
#         }))

#     # Handlers pour les messages de groupe (si vous utilisez channel_layer)
#     async def chat_message(self, event):
#         """Recevoir un message du groupe"""
#         await self.send(text_data=json.dumps(event))



# # routing.py
# from django.urls import re_path
# from .consumers import ChatConsumer, NotificationConsumer

# websocket_urlpatterns = [
#     re_path(r"ws/chat/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()),
#     re_path(r"ws/notifications/$", NotificationConsumer.as_asgi()),
# ]


# await self.channel_layer.group_send(
#     "notifications",
#     {
#         "type": "notify",
#         "message": "Nouveau message dans le chat"
#     }
# )


# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.channel_layer.group_add("notifications", self.channel_name)
#         await self.accept()

#     async def notify(self, event):
#         await self.send(text_data=json.dumps({
#             "notification": event["message"]
#         }))


# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user_id = self.scope["user"].id
#         self.group_name = f"user_{self.user_id}"

#         await self.channel_layer.group_add(self.group_name, self.channel_name)
#         await self.accept()

#     async def notify(self, event):
#         await self.send(text_data=json.dumps({
#             "notification": event["message"]
#         }))


# # consumers.py
# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = f"chat_{self.room_name}"

#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         await self.accept()

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data["message"]

#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {"type": "chat_message", "message": message}
#         )

#     async def chat_message(self, event):
#         await self.send(text_data=json.dumps({"message": event["message"]}))




# # 📩 Message utilisateur → chat
# await self.channel_layer.group_send(
#     self.room_group_name,
#     {
#         "type": "chat.message",
#         "username": username,
#         "groupe_name": groupe_name,
#         "message": message
#     }
# )

# # 🔔 Envoi vers le système de notifications (NON RÉPONDU)
# await self.channel_layer.group_send(
#     "notifications",   # 👈 Groupe global de notifications
#     {
#         "type": "new.unanswered.message",
#         "room": self.room_name,
#         "username": username,
#         "message": message
#     }
# )




# from channels.generic.websocket import AsyncWebsocketConsumer
# import json

# class NotificationConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         await self.channel_layer.group_add("notifications", self.channel_name)
#         await self.accept()

#         # Initialisation du compteur
#         await self.send(text_data=json.dumps({
#             "type": "notification.init",
#             "unanswered_count": 0
#         }))

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard("notifications", self.channel_name)

#     # 🔔 Réception des messages non répondus
#     async def new_unanswered_message(self, event):
#         await self.send(text_data=json.dumps({
#             "type": "notification",
#             "room": event["room"],
#             "username": event["username"],
#             "message": event["message"]
#         }))









# await self.channel_layer.group_send(
#     "notifications",
#     {
#         "type": "new.unanswered.message",
#         "room": self.room_name,
#         "username": username,
#         "message": message
#     }
# )



# # 🤖 Réponse IA simulée
# await self.channel_layer.group_send(
#     self.room_group_name,
#     {
#         "type": "ia.message",
#         "username": "Cashmoov IA",
#         "message": "la reponse du rag"
#     }
# )

# # ✅ IMPORTANT : on dit au système que le message a été répondu
# await self.channel_layer.group_send(
#     "notifications",
#     {
#         "type": "message.answered",
#         "room": self.room_name
#     }
# )


# async def message_answered(self, event):
#     await self.send(text_data=json.dumps({
#         "type": "notification.decrement",
#         "room": event["room"]
#     }))












# # notifiaction par groupe


# await self.channel_layer.group_send(
#     "notifications",
#     {
#         "type": "message.answered",
#         "room": self.room_name   # 👈 on précise la room à décrémenter
#     }
# )



# from channels.generic.websocket import AsyncWebsocketConsumer
# import json

# class NotificationConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         await self.channel_layer.group_add("notifications", self.channel_name)
#         await self.accept()

#         # On initialise un dictionnaire de compteurs par room
#         self.unanswered_counts = {}

#         await self.send(text_data=json.dumps({
#             "type": "notification.init",
#             "counts": self.unanswered_counts
#         }))

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard("notifications", self.channel_name)

#     # 🔔 Nouveau message NON répondu → +1 pour la room concernée
#     async def new_unanswered_message(self, event):
#         room = event["room"]

#         # Incrémenter le compteur pour cette room
#         self.unanswered_counts[room] = self.unanswered_counts.get(room, 0) + 1

#         await self.send(text_data=json.dumps({
#             "type": "notification",
#             "room": room,
#             "count": self.unanswered_counts[room],
#             "username": event["username"],
#             "message": event["message"]
#         }))

#     # ✅ Message répondu → -1 pour la BONNE room
#     async def message_answered(self, event):
#         room = event["room"]

#         if room in self.unanswered_counts:
#             self.unanswered_counts[room] = max(
#                 0, self.unanswered_counts[room] - 1
#             )

#         await self.send(text_data=json.dumps({
#             "type": "notification.decrement",
#             "room": room,
#             "count": self.unanswered_counts.get(room, 0)
#         }))
