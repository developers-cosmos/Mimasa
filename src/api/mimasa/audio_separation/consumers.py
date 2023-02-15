import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from celery.result import AsyncResult


class AudioSeparationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        task_id = self.scope["url_route"]["kwargs"]["task_id"]
        self.task_id = task_id
        self.task = AsyncResult(task_id)
        await self.accept()
        while not self.task.ready():
            await asyncio.sleep(1)
        result = self.task.result
        if self.task.state == "SUCCESS":
            await self.send_json(
                {
                    "type": "success",
                    "music_filename": result["music_filename"],
                    "speech_filename": result["speech_filename"],
                }
            )
        else:
            await self.send_json(
                {"type": "error", "exc_type": result["exc_type"], "exc_message": result["exc_message"]}
            )
        await self.close()
