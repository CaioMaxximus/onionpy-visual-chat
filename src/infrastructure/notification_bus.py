import asyncio
from src.models import Notification

class NotificationBus():

    def __init__(self):
        self._notification_queue = None

    def start(self):
        self._notification_queue = asyncio.Queue()

    async def consume(self):
        if self._notification_queue is None:
            raise ValueError("You nedd to start the event queue first!")
        return await self._notification_queue.get()

    async def send(self, notification):
        if self._notification_queue is None:
            raise ValueError("You nedd to start the event queue first!")
        if notification is None:
            raise ValueError("None is an invalid value")
        if not isinstance(notification, Notification):
            raise ValueError(f"Object type must be an {Notification}; actual type {type(notification)}")
        
        await self._notification_queue.put(notification)
