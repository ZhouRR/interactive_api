from channels.generic.websocket import AsyncWebsocketConsumer
import json


class ActivityConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print('connect')
        # Join room group
        await self.channel_layer.group_add(
            'ohs',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            'ohs',
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['activity']
        if message == '000':
            message = 'pong'
        # Send message to group
        await self.channel_layer.group_send(
            'ohs',
            {
                'type': 'send_message',
                'message': message
            }
        )

    async def send_message(self, resp):
        await self.send(text_data=json.dumps({
            'message': resp
        }))
