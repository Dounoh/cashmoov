# import pytest
# import json
# from channels.testing import WebsocketCommunicator

# @pytest.mark.asyncio
# async def test_chat_consumer_basic():
#     """Test basique du ChatConsumer"""
#     from cashmoov_api.chatbot.consumers import ChatConsumer

#     communicator = WebsocketCommunicator(
#         ChatConsumer.as_asgi(),
#         "/ws/chat/general/"
#     )

#     connected, subprotocol = await communicator.connect()
#     assert connected

#     await communicator.send_json_to({
#         "type": "chat.message",
#         "username": "cashmoov_user",
#         "groupe_name": "room1",
#         "message": "Comment recharger mon compte CashMoov ?",
#         "user_type":"customer"
#         }
# )

#     response = await communicator.receive_json_from()

#     assert response["message"] == "Comment recharger mon compte CashMoov ?"
#     assert response["username"] == "cashmoov_user"

#     await communicator.disconnect()


# @pytest.mark.asyncio
# async def test_online_user_consumer():
#     from cashmoov_api.chatbot.consumers import OnlineUser

#     communicator = WebsocketCommunicator(
#         OnlineUser.as_asgi(),
#         "/ws/online/"
#     )

#     connected, _ = await communicator.connect()
#     assert connected

#     # Envoyer une requête pour obtenir les utilisateurs en ligne
#     await communicator.send_json_to({
#         "type": "get_online_users"
#     })
