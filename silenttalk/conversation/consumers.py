import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ConversationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name  = self.scope['url_route']['kwargs']['room_name']
        self.room_group = f"conv_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group,
            self.channel_name
        )
        await self.accept()

        # Notify others someone joined
        await self.channel_layer.group_send(
            self.room_group,
            {
                "type":    "system_message",
                "message": "A new person joined the conversation."
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group,
            self.channel_name
        )

    async def receive(self, text_data):
        data      = json.loads(text_data)
        message   = data.get("message", "")
        sender    = data.get("sender", "Anonymous")
        msg_type  = data.get("msg_type", "text")
        emotion   = data.get("emotion", "")

        # Broadcast to entire room
        await self.channel_layer.group_send(
            self.room_group,
            {
                "type":     "chat_message",
                "message":  message,
                "sender":   sender,
                "msg_type": msg_type,
                "emotion":  emotion
            }
        )

    # Handler for chat messages
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message":  event["message"],
            "sender":   event["sender"],
            "msg_type": event["msg_type"],
            "emotion":  event.get("emotion", "")
        }))

    # Handler for system messages
    async def system_message(self, event):
        await self.send(text_data=json.dumps({
            "message":  event["message"],
            "sender":   "System",
            "msg_type": "system",
            "emotion":  ""
        }))
