from typing import List, Any, Optional
from datetime import datetime
from ninja import Schema, ModelSchema
from .models import Customer, CustomerQueue


class CancelQueueSchema(Schema):
    entry_id: int
    
class CustomerQueueListSchema(Schema):
    customer: str
    track_code: str
    
    
# class CustomerQueueListSchema(ModelSchema):
#     class Meta:
#         model = CustomerQueue
#         # fields = ['customer', 'entry']
#         fields = ['customer','entry']
        
    # class Config:
    #     orm_mode = True
    
class CustomerQueueCreateSchema(Schema):
    tracking_code: str 


# class VisitorDetailSchema(Schema):
#     # show customer queue with track code
#     tracking_code: str
    
