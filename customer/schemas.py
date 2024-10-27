from typing import List, Any, Optional
from datetime import datetime
from ninja import Schema, ModelSchema
from .models import Customer, CustomerQueue
from business.models import Entry
from business.schemas import EntryDetailSchema


class CancelQueueSchema(Schema):
    entry_id: int
    
class CustomerQueueListSchema(Schema):
    customer: str
    track_code: str
    
    
    
class CustomerQueueCreateSchema(Schema):
    tracking_code: str 

    
