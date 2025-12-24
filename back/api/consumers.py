import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ReviewConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.book_id = self.scope['url_route']['kwargs'].get('book_id')
        self.group_name = f'book_{self.book_id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Event handler for created review
    async def review_created(self, event):
        await self.send(text_data=json.dumps({
            'type': 'review.created',
            'review': event.get('review')
        }))

    # Event handler for deleted review
    async def review_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'review.deleted',
            'review_id': event.get('review_id'),
            'deleted_ids': event.get('deleted_ids')
        }))

