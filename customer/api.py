from ninja import Router, Schema
from django.utils import timezone
from django.shortcuts import get_object_or_404
from typing import List, Union
from .schemas import CustomerQueueListSchema, CustomerQueueCreateSchema
from .models import Customer, CustomerQueue
from business.models import Entry
from business.api import serialize_queue_entry, serialize_single_entry
from business.schemas import EntryDetailSchema


router = Router()


class UserSchema(Schema):
    username: str
    is_authenticated: bool


@router.get("all-customers-entries/", response=list[EntryDetailSchema])
def get_all_entries(request):
    """Show every entries."""
    print(request.user)
    today = timezone.now().date()
    entry_list = Entry.objects.filter(
    time_in__date=today).order_by("time_in")
    ans = serialize_queue_entry(entry_list)
    return ans


@router.post("cancel-queue/{entry_id}", response=dict)   
def cancel_queue(request, entry_id: int):
    """When the queue is canceled, the entry is also cancel."""
    try:
        my_queue = CustomerQueue.objects.get(entry__id=entry_id)
        if my_queue.entry.status != "waiting":
            return {"msg": "You cannot to cancel this entry."}

        if not request.user.is_authenticated or request.user != my_queue.customer.user:
            return {"msg": "You do not have the authority to delete this entry."}
        
    except CustomerQueue.DoesNotExist:
        return {"msg": "This entry does not exist in customer queue."}


    my_entry = get_object_or_404(Entry, id=entry_id)
    my_entry.delete()
    # print(Entry.objects.filter(id=entry_id).exists())
    return {"msg": "deletion success"}


# TODO need to test with user enter other people queue (claimed), refacter
@router.post("add-trackcode/{tracking_code}", response=list[EntryDetailSchema] | dict)
def add_customer_queue(request, tracking_code: CustomerQueueCreateSchema):
    """Add a queue to the customer queue."""
    # Check if the tracking code is valid
    
    try:
        my_entry = Entry.objects.get(tracking_code=tracking_code.tracking_code)
    except Entry.DoesNotExist:
        return {"msg": "Invalid track code"}

    if request.user.is_anonymous:
        # Return the entries associated with the tracking code for unauthenticated users
        return [serialize_single_entry(my_entry)]

    try:
        my_customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        return {"msg": "You are not a customer"}
    # Proceed with creating or getting the customer queue for authenticated users
    try:
        my_queue = CustomerQueue.objects.get(
            entry=my_entry, customer__user=request.user)
    except CustomerQueue.DoesNotExist:
        CustomerQueue.objects.create(
            customer=my_customer, entry=my_entry)


    # customer_queues = CustomerQueue.objects.filter(customer__user=request.user)
    # print(customer_queues)
    # can retreive the entries from the link api/customer/all-my-entries/
    return {'msg': 'successfully add this queue'}


@router.get("all-my-entries/", response=list[EntryDetailSchema])
def get_customer_queue_list(request):
    """Return a list of entries for the authenticated user."""
    print(request.user)
    today = timezone.now().date()
    if not request.user.is_authenticated:
        return []
    my_queues = CustomerQueue.objects.filter(
        customer__user=request.user
    )

    entry_ids = [queue.entry.id for queue in my_queues]
    entry_list = Entry.objects.filter(
        id__in=entry_ids, time_in__date=today).order_by("time_in")
    ans = serialize_queue_entry(entry_list)
    return ans


@router.get("me/", response=UserSchema)
def me(request):
    return request.user  # will turn into schema
