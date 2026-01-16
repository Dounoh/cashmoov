# cashmoov_api/chatbot/consumers.py
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .rags.retrieval import search_documents
from .models import Document, ChatMessage, AssistantResponse

class ChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer WebSocket pour le chatbot avec RAG et assistants humains
    """
    
    async def connect(self):
        """Connexion d'un utilisateur au WebSocket"""
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"
        self.user_type = self.scope.get('query_string', b'').decode('utf-8')
        
        # Déterminer si c'est un utilisateur ou un assistant
        self.is_assistant = 'assistant' in self.user_type
        
        # Rejoindre le groupe
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        # Notifier la connexion
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'message': f"{'Assistant' if self.is_assistant else 'Utilisateur'} a rejoint le chat",
                'timestamp': timezone.now().isoformat()
            }
        )

    async def disconnect(self, close_code):
        """Déconnexion du WebSocket"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Réception d'un message du WebSocket"""
        try:
            data = json.loads(text_data)
            message = data.get('message', '')
            sender = data.get('sender', 'Anonymous')
            
            if not message:
                return
            
            # Différencier le traitement selon le type d'utilisateur
            if self.is_assistant:
                # Message d'un assistant : le sauvegarder comme réponse
                await self.save_assistant_response(message, sender)
            else:
                # Message d'un utilisateur : essayer RAG d'abord
                await self.handle_user_message(message, sender)
                
        except json.JSONDecodeError:
            await self.send_error("Format de message invalide")

    async def handle_user_message(self, message, sender):
        """
        Gérer un message utilisateur : essayer RAG puis transférer aux assistants si besoin
        """
        # Envoyer le message à tous pour montrer que l'utilisateur a parlé
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_message',
                'sender': sender,
                'message': message,
                'timestamp': timezone.now().isoformat()
            }
        )
        
        # Essayer d'obtenir une réponse du RAG
        try:
            rag_response = await self.get_rag_response(message)
            
            if rag_response and rag_response.strip():
                # Le RAG a une réponse : l'envoyer directement
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'bot_response',
                        'sender': 'CashMoov IA',
                        'message': rag_response,
                        'source': 'RAG',
                        'timestamp': timezone.now().isoformat()
                    }
                )
                
                # Sauvegarder la conversation
                await self.save_conversation(message, rag_response, 'RAG')
            else:
                # Le RAG n'a pas de réponse : demander aux assistants
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'need_assistance',
                        'message': message,
                        'sender': sender,
                        'timestamp': timezone.now().isoformat()
                    }
                )
                
        except Exception as e:
            # Erreur RAG : demander aux assistants
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'need_assistance',
                    'message': message,
                    'sender': sender,
                    'error': str(e),
                    'timestamp': timezone.now().isoformat()
                }
            )

    async def get_rag_response(self, query):
        """
        Obtenir une réponse du système RAG de manière asynchrone
        """
        try:
            # Exécuter la fonction synchrone dans un thread séparé
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, search_documents, query)
            
            # Vérifier si la réponse est valide
            if response and isinstance(response, str):
                # Nettoyer la réponse
                response = response.strip()
                
                # Vérifier si ce n'est pas un message d'erreur standard
                error_messages = [
                    "Je n'ai pas cette information pour le moment.",
                    "Je n'ai pas trouvé d'information pour répondre à votre demande."
                ]
                
                if response not in error_messages and len(response) > 10:
                    return response
                    
            return None
            
        except Exception as e:
            print(f"Erreur RAG: {e}")
            return None

    async def save_conversation(self, user_message, bot_response, source):
        """
        Sauvegarder une conversation en base de données
        """
        try:
            await database_sync_to_async(ChatMessage.objects.create)(
                room_name=self.room_name,
                user_message=user_message,
                bot_response=bot_response,
                response_source=source,
                timestamp=timezone.now()
            )
        except Exception as e:
            print(f"Erreur sauvegarde conversation: {e}")

    async def save_assistant_response(self, message, assistant_name):
        """
        Sauvegarder la réponse d'un assistant et la mettre à disposition du RAG
        """
        try:
            # Sauvegarder la réponse de l'assistant
            await database_sync_to_async(AssistantResponse.objects.create)(
                room_name=self.room_name,
                assistant_name=assistant_name,
                response=message,
                timestamp=timezone.now()
            )
            
            # Notifier que la réponse est disponible
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'assistant_response',
                    'sender': assistant_name,
                    'message': message,
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            # Ajouter la réponse aux documents du RAG pour futurs apprentissages
            await self.add_to_rag_documents(message, assistant_name)
            
        except Exception as e:
            print(f"Erreur sauvegarde réponse assistant: {e}")

    async def add_to_rag_documents(self, response, assistant_name):
        """
        Ajouter une réponse d'assistant aux documents RAG
        """
        try:
            await database_sync_to_async(Document.objects.create)(
                title=f"Réponse assistant - {assistant_name}",
                content=response,
                source_type='conversation',
                is_active=True
            )
        except Exception as e:
            print(f"Erreur ajout document RAG: {e}")

    async def send_error(self, error_message):
        """Envoyer un message d'erreur au client"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': error_message,
            'timestamp': timezone.now().isoformat()
        }))

    # Handlers pour les messages du groupe
    async def user_message(self, event):
        """Message utilisateur reçu du groupe"""
        await self.send(text_data=json.dumps({
            'type': 'user_message',
            'sender': event['sender'],
            'message': event['message'],
            'timestamp': event['timestamp']
        }))

    async def bot_response(self, event):
        """Réponse du bot RAG reçue du groupe"""
        await self.send(text_data=json.dumps({
            'type': 'bot_response',
            'sender': event['sender'],
            'message': event['message'],
            'source': event['source'],
            'timestamp': event['timestamp']
        }))

    async def need_assistance(self, event):
        """Demande d'assistance pour les assistants humains"""
        await self.send(text_data=json.dumps({
            'type': 'need_assistance',
            'message': event['message'],
            'sender': event['sender'],
            'error': event.get('error', None),
            'timestamp': event['timestamp']
        }))

    async def assistant_response(self, event):
        """Réponse d'un assistant reçue du groupe"""
        await self.send(text_data=json.dumps({
            'type': 'assistant_response',
            'sender': event['sender'],
            'message': event['message'],
            'timestamp': event['timestamp']
        }))

    async def user_joined(self, event):
        """Notification de connexion d'un utilisateur"""
        await self.send(text_data=json.dumps({
            'type': 'system_message',
            'message': event['message'],
            'timestamp': event['timestamp']
        }))