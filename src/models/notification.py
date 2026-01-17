from enum import Enum

class NotificationType(Enum):
    ERROR = "error"
    SUCCESS = "success"
    WARNING = "warning"
    INFO = "info"

class Notification():
    def __init__(self, message_type: NotificationType, content: str):
        if not isinstance(message_type, NotificationType):
            raise ValueError("message_type must be an instance of MessageType Enum")
        self.message_type = message_type
        self.content = content

    def __str__(self):
        return f"[{self.message_type.value.upper()}] {self.content}" 