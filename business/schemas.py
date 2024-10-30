from typing import List, Any, Optional
from datetime import datetime
from ninja import Schema, ModelSchema
from .models import Business, Queue, User, Entry
# from pydantic import EmailStr


class BusinessSchema(ModelSchema):
    class Meta:
        model = Business
        fields = ('user', 'name')


class QueueDetailSchema(Schema):
    id: int
    name: str
    
class QueueSchema(Schema):
    # GET
    name: str

class EntryRetrieveSchema(Schema):
    # ask for specific entry
    # GET -> data
    # WaitListEntryOut
    id: int


class EntryDetailSchema(Schema):
    id: int                    # Auto-generated ID
    name: str                   # Name of the entry
    queue:QueueSchema     # ForeignKey to Queue
    business: BusinessSchema  # ForeignKey to Business (optional)
    tracking_code: Optional[str]
    time_in: datetime             # Time in (auto-populated)
    time_out: Optional[datetime]  # Time out (optional)
    status: str = "waiting"


class EditIn(Schema):
    name: str
    alphabet: str


class QueueCreateSchema(Schema):
    name: str
    alphabet: str