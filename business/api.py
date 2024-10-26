from ninja import Router, Schema
from django.utils import timezone
from typing import List, Union
from customer.schemas import CustomerQueueListSchema, CustomerQueueCreateSchema
from customer.models import Customer, CustomerQueue
from .models import Entry, Business, Queue
from .schemas import EntrySchema, BusinessSchema, QueueSchema
from ninja_jwt.authentication import JWTAuth


router = Router()


class UserSchema(Schema):
    username: str
    is_authenticated: bool


#TODO add , auth=JWTAuth()
@router.get("my-business/", response=BusinessSchema| None)
def my_business(request):
    """Show business information."""
    print(request.user)
    if request.user.is_anonymous:
        print('anonymous')
        return None
    return Business.objects.get(user=request.user)



#TODO add , auth=JWTAuth()
@router.get("all-customers-entries/", response=dict)
def get_all_entries(request):
    """Show all my business entries."""
    print(request.user)
    if request.user.is_anonymous:
        print('anonymous')
        return {}
    today = timezone.now().date()
    try:
        business = Business.objects.get(user=request.user)
    except Business.DoesNotExist:
        return {}
    queue_list = Queue.objects.filter(business=business)
    entry_list = Entry.objects.filter(
        business=business,
        time_in__date=today,
    ).order_by("time_in")
    
    serialized_queues = [QueueSchema.from_orm(queue) for queue in queue_list]
    serialized_entries = [EntrySchema.from_orm(entry) for entry in entry_list]

    # Serialize the business object
    serialized_business = BusinessSchema.from_orm(business)

    return {
        "queues": serialized_queues,
        "entries": serialized_entries,
        "business": serialized_business
    }
