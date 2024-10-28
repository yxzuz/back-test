from ninja import Router, Schema
from django.utils import timezone
from typing import List, Union
from .models import Entry, Business, Queue, QueueForm
from .schemas import EntryRetrieveSchema, BusinessSchema, QueueSchema, EntryDetailSchema, EditIn
from ninja_jwt.authentication import JWTAuth


router = Router()


class UserSchema(Schema):
    username: str
    is_authenticated: bool


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
        {"detail": "Not authenticated"}, 401
    today = timezone.now().date()
    try:
        business = Business.objects.get(user=request.user)
    except Business.DoesNotExist:
        return {"detail": "Business not found"}, 404
    queue_list = Queue.objects.filter(business=business)
    entry_list = Entry.objects.filter(
        business=business,
        time_in__date=today,
    ).order_by("time_in")

    serialized_queues = [QueueSchema.from_orm(queue) for queue in queue_list]
    serialized_entries = serialize_queue_entry(entry_list)

    # Serialize the business object
    serialized_business = BusinessSchema.from_orm(business)

    return {
        "queues": serialized_queues,
        "entries": serialized_entries,
        "business": serialized_business
    }


def serialize_queue_entry(entry_list):
    """Get serialized entry list with number of queue ahead."""
    serialized_entries = []
    if len(entry_list) == 0:
        return []
    if len(entry_list) == 1:
        return serialize_single_entry(entry_list)
    for entry in entry_list:
        entry_detail = serialize_single_entry(entry)
        serialized_entries.append(entry_detail)
    return serialized_entries

def serialize_single_entry(entry):
    queue_ahead = entry.get_queue_position()  # Get queue position
    entry_detail = EntryDetailSchema(
            id=entry.id,
            name=entry.name,
            queue=entry.queue,
            business=entry.business.name,
            tracking_code=entry.tracking_code,
            time_in=entry.time_in,
            time_out=entry.time_out,
            status=entry.status,
            queue_ahead=queue_ahead
        )
    
    return entry_detail


@router.get("{pk}/entry/", response=EntryDetailSchema | None)
def get_entry(request, pk: int):
    """Get a specific entry."""
    try:
        entry = Entry.objects.get(pk=pk)
    except Entry.DoesNotExist:
        return None
    return serialize_single_entry(entry)


@router.post("{pk}/runQueue")
def run_queue(request, pk: int):
    """
    Mark a specific entry as completed.

    Args:
        request: The HTTP request object.
        pk: The primary key of the entry.

    Returns:
        A message indicating the status of the operation.
    """
    print(request.user)
    business = Business.objects.get(user=request.user)
    try:
        entry = Entry.objects.get(pk=pk, business=business)
    except Entry.DoesNotExist:
        return {'msg': 'Deletion failed.'}

    entry.mark_as_completed()
    return {'msg': f'{entry.name} marked as completed.'}


@router.put("editQueue/{pk}")
def edit_queue(request, pk: int, edit_attrs: EditIn):
    """
    Edit queue to the specified business.

    Args:
        request: The HTTP request object.
        pk: The primary key of the queue.

    Returns:

    """
    print(request.user)
    if not request.user.is_authenticated:
        return {'msg': 'User not authenticated.'}
    business = Business.objects.get(user=request.user)
    try:
        queue = Queue.objects.get(pk=pk, business=business)
    except Queue.DoesNotExist:
        return {'msg': 'Cannot edit this queue.'}
    
    for attr, value in edit_attrs.dict().items():
        setattr(queue, attr, value)
    queue.save()
    return {'msg': f"Successfully updated the queue '{queue.name}' "
            f"with the alphabet '{queue.alphabet}'."}
