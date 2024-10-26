from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from typing import List, Union
from .schemas import CustomerQueueListSchema, CustomerQueueCreateSchema
from .models import Customer, CustomerQueue
from business.models import Entry
from business.schemas import EntrySchema


router = Router()


class UserSchema(Schema):
    username: str
    is_authenticated: bool


@router.get("all-customers-entries/", response=list[EntrySchema])
def get_all_entries(request):
    entries = Entry.objects.all()
    return entries



@router.post("cancel-queue/{entry_id}")  # TODO
def cancel_queue(request, entry_id: int):
    my_entry = get_object_or_404(Entry, id=entry_id)
    # my_entry.delete()
    # return {"success": "deletion success"}
    return my_entry


# TODO need to test with user enter other people queue (claimed), refacter
@router.post("home", response=list[CustomerQueueListSchema])
def add_customer_queue(request, tracking_code: CustomerQueueCreateSchema):
    track_code_value = tracking_code.tracking_code
    my_entry = Entry.objects.get(tracking_code=str(track_code_value))
    # Check if the tracking code is valid
    try:
        my_entry = Entry.objects.get(tracking_code=str(track_code_value))
    except Entry.DoesNotExist:
        #     if request.user.is_authenticated:
        #         return []  # Return an empty list if invalid track code for authenticated users
        return {"error": "Invalid track code"}

    customer_queues = CustomerQueue.objects.filter(
        entry__tracking_code=track_code_value)

    if request.user.is_anonymous:
        # Return the entries associated with the tracking code for unauthenticated users
        return [
            CustomerQueueListSchema(
                customer=queue.customer.user.username,
                track_code=queue.entry.tracking_code
            )
            for queue in customer_queues
        ]

    # Proceed with creating or getting the customer queue for authenticated users
    try:
        my_queue = CustomerQueue.objects.get(
            entry=my_entry, customer__user=request.user)
    except CustomerQueue.DoesNotExist:
        my_customer = Customer.objects.get(user=request.user)
        my_queue = CustomerQueue.objects.create(
            customer=my_customer, entry=my_entry)

    # Fetch the queues for the authenticated user
    customer_queues = CustomerQueue.objects.filter(customer__user=request.user)

    # Serialize the queryset
    return [
        CustomerQueueListSchema(
            customer=queue.customer.user.username,
            track_code=queue.entry.tracking_code
        )
        for queue in customer_queues
    ]


@router.get("home/", response=list[CustomerQueueListSchema])
def get_customer_queue_list(request):
    customer_queues = CustomerQueue.objects.filter(customer__user=request.user)
    return [
        CustomerQueueListSchema(
            customer=queue.customer.user.username,
            track_code=queue.entry.tracking_code
        )
        for queue in customer_queues
    ]


@router.get("me/", response=UserSchema)
def me(request):
    return request.user  # will turn into schema
