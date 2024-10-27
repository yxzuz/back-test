import helpers
from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from django.utils import timezone
from typing import List, Union
from customer.schemas import CustomerQueueListSchema, CustomerQueueCreateSchema
from customer.models import Customer, CustomerQueue
from .models import Entry, Business, Queue
from .schemas import EntryRetrieveSchema, BusinessSchema, QueueSchema, EntryDetailSchema, QueueDetailSchema
from ninja_jwt.authentication import JWTAuth


router = Router()


class UserSchema(Schema):
    username: str
    is_authenticated: bool


@router.get("queue/", response=List[QueueDetailSchema], auth=helpers.api_auth_user_required)
def list_business_queue(request):
    # return Queue.objects.all()
    business = Business.objects.get(user=request.user)
    queue_list = Queue.objects.filter(business=business)
    return queue_list


@router.get("get_entry/{queue_id}", response=List[EntryDetailSchema], auth=helpers.api_auth_user_required)
def list_waiting_entry_in_queue(request, queue_id:int):
    today = timezone.now().date()
    queue = get_object_or_404(Queue, business__user=request.user, pk=queue_id)
    entry = Entry.objects.filter(queue=queue, status='waiting', time_in__date=today).order_by("time_in")
    return entry


# TODO add , auth=JWTAuth()
@router.get("my-business/", response=BusinessSchema | None)
def my_business(request):
    """Show business information."""
    print(request.user)
    if request.user.is_anonymous:
        print('anonymous')
        return None
    return Business.objects.get(user=request.user)


# TODO add , auth=JWTAuth()
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
    serialized_entries = [EntryDetailSchema.from_orm(
        entry) for entry in entry_list]

    # Serialize the business object
    serialized_business = BusinessSchema.from_orm(business)

    return {
        "queues": serialized_queues,
        "entries": serialized_entries,
        "business": serialized_business
    }


@router.get("{pk}/entry/", response=EntryDetailSchema | None)
def get_entry(request, pk: int):
    """Get a specific entry."""
    try:
        entry = Entry.objects.get(pk=pk)
    except Entry.DoesNotExist:
        return None
    return entry

@router.post("{pk}/runQueue")
def run_queue(request, pk: int):
    """Delete entry"""
    print(request.user)
    business = Business.objects.get(user=request.user)
    try:
        entry = Entry.objects.get(pk=pk, business=business)
    except Entry.DoesNotExist:
        return {'msg': 'Deletiion failed.'}

    entry.mark_as_completed()
    return {'msg': f'{entry.name} marked as completed.'}


@router.post("add_entry/{queue_id}", auth=helpers.api_auth_user_required)
def add_entry(request, queue_id: int):
    business = Business.objects.get(user=request.user)
    try:
        queue = Queue.objects.get(business=business, pk=queue_id)
    except Queue.DoesNotExist:
        return {'msg': 'This queue does not exist'}

    new_entry = Entry.objects.create(business=business, queue=queue, status='waiting')
    return {'msg': f'New entry successfully add to queue {queue.name}.', 'tracking_code': new_entry.tracking_code}
