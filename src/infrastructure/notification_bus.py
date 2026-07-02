import asyncio
from src.models import Notification

class NotificationBus():

    """
        This class is a event bus, used to capture and collect data asynchronously through 
        different layers from the application
        
        Methods
        -------
        start: 
            start the asynchronous queue inside the proper event loop, it need to be called 
            first
        consume:
            collects the stored data from the queue
        send:
            stores a proper Notification type object
    """
    def __init__(self):
        self._notification_queue = None

    def start(self) -> None:
        self._notification_queue = asyncio.Queue()

    async def consume(self):
        if self._notification_queue is None:
            raise ValueError("You need to start the event queue first!")
        return await self._notification_queue.get()

    async def send(self, notification):
        if self._notification_queue is None:
            raise ValueError("You nedd to start the event queue first!")
        if notification is None:
            raise ValueError("None is an invalid value")
        if not isinstance(notification, Notification):
            raise ValueError(f"Object type must be an {Notification}; actual type {type(notification)}")
        
        await self._notification_queue.put(notification)
