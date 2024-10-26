from typing import List, Any, Optional
from datetime import datetime
from ninja import Schema, ModelSchema
from .models import Business, Queue, User, Entry
# from pydantic import EmailStr



class BusinessSchema(ModelSchema):
    class Meta:
        model = Business
        fields = ('user', 'name')

    
class QueueSchema(ModelSchema):
    alphabet: str = "A"
    estimated_time: int = None
    
    class Meta:
        model = Queue
        fields = ('business', 'name', 'alphabet', 'estimated_time')
        

class EntrySchema(Schema):
    id: int                    # Auto-generated ID
    name: str                   # Name of the entry
    queue_id: Optional[int]     # ForeignKey to Queue (optional)
    business: BusinessSchema  # ForeignKey to Business (optional)
    tracking_code: Optional[str] 
    time_in: datetime            # Time in (auto-populated)
    time_out: Optional[datetime] # Time out (optional)
    status: str = "waiting"   
    