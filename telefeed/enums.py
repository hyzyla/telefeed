from enum import Enum, unique

@unique
class PostStatus(Enum):
    new = 'new'
    sent = 'sent'