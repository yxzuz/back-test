from importlib.metadata import entry_points

import helpers
from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from ninja_extra import api_controller, http_get, http_post, http_put
from django.utils import timezone
from typing import List, Union
from .models import Entry, Business, Queue, QueueForm
from .schemas import (
    BusinessSchema,
    QueueSchema,
    EntryDetailSchema,
    QueueDetailSchema,
    EditIn,
    QueueCreateSchema
)

@api_controller("/business")
class BusinessController:

    @http_get("my-business/", response=BusinessSchema | None)
    def my_business(self, request):
        """Return information of the business."""
        print(request.user)
        if request.user.is_anonymous:
            print('anonymous')
            return None
        return Business.objects.get(user=request.user)

    @http_get("queue/", response=List[QueueDetailSchema], auth=helpers.api_auth_user_required)
    def get_business_queues(self, request):
        """Return list of all queues in the business."""
        # return Queue.objects.all()
        business = Business.objects.get(user=request.user)
        queue_list = Queue.objects.filter(business=business)
        return queue_list

    @http_get("all-customers-entries/", response=dict)
    def get_business_entries(self, request):
        """Return list of all entries in the business."""
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

    @http_post("queue/", response=dict, auth=helpers.api_auth_user_required)
    def create_business_queue(self, request, data: QueueCreateSchema):
        data_dict = data.dict()
        business = Business.objects.get(user=request.user)
        all_alphabet = Queue.objects.filter(business=business).values_list('alphabet', flat=True)
        if data_dict['alphabet'] in all_alphabet:
            return {'msg': 'This alphabet has been used.'}
        new_queue = Queue.objects.create(business=business, **data_dict)
        new_queue.save()
        return {'msg': f'Queue {new_queue.name} is successfully created.'}


@api_controller("/queue")
class QueueController:

    @http_get("get_entry/{queue_id}", response=List[EntryDetailSchema], auth=helpers.api_auth_user_required)
    def get_waiting_entry_in_queue(self, request, queue_id: int):
        """Return list of all entry in this queue, which status is waiting and create today ordering by time-in."""
        today = timezone.now().date()
        queue = get_object_or_404(Queue, business__user=request.user, pk=queue_id)
        entry = Entry.objects.filter(queue=queue, status='waiting', time_in__date=today).order_by("time_in")
        return entry

    @http_post("add_entry/{queue_id}", auth=helpers.api_auth_user_required)
    def add_entry(self, request, queue_id: int):
        """Adding new entry into the queue."""
        business = Business.objects.get(user=request.user)
        try:
            queue = Queue.objects.get(business=business, pk=queue_id)
        except Queue.DoesNotExist:
            return {'msg': 'This queue does not exist'}

        new_entry = Entry.objects.create(business=business, queue=queue, status='waiting')
        return {'msg': f'New entry successfully add to queue {queue.name}.', 'tracking_code': new_entry.tracking_code}

    @http_put("editQueue/{queue_id}", auth=helpers.api_auth_user_required)
    def edit_queue(self, request, queue_id: int, edit_attrs: EditIn):
        """
        Edit queue to the specified business.

        Args:
            request: The HTTP request object.
            queue_id: The primary key of the queue.

        Returns: message indicate whether the queue is successfully edit or not
        """
        print(request.user)
        business = Business.objects.get(user=request.user)
        try:
            queue = Queue.objects.get(pk=queue_id, business=business)
        except Queue.DoesNotExist:
            return {'msg': 'Cannot edit this queue.'}

        for attr, value in edit_attrs.dict().items():
            setattr(queue, attr, value)
        queue.save()
        return {'msg': f"Successfully updated the queue '{queue.name}' "
                       f"with the alphabet '{queue.alphabet}'."}


@api_controller("/entry")
class EntryController:

    @http_get("entry/{entry_id}", response=EntryDetailSchema | None)
    def get_entry(self, request, entry_id: int):
        """Get information of a specific entry."""
        try:
            entry = Entry.objects.get(pk=entry_id)
        except Entry.DoesNotExist:
            return None
        return entry

    @http_post("runQueue/{entry_id}", auth=helpers.api_auth_user_required)
    def complete_entry(self, request, entry_id: int):
        """Change the status of entry as 'completed'."""
        print(request.user)
        business = Business.objects.get(user=request.user)
        try:
            entry = Entry.objects.get(pk=entry_id, business=business)
        except Entry.DoesNotExist:
            return {'msg': 'Deletiion failed.'}

        entry.mark_as_completed()
        return {'msg': f'{entry.name} marked as completed.'}

    @http_post("cancelQueue/{entry_id}", auth=helpers.api_auth_user_required)
    def cancel_entry(self, request, entry_id: int):
        """Change the status of entry as 'cancel'."""
        print(request.user)
        business = Business.objects.get(user=request.user)
        try:
            entry = Entry.objects.get(pk=entry_id, business=business)
        except Entry.DoesNotExist:
            return {'msg': 'Deletiion failed.'}

        entry.mark_as_completed()
        return {'msg': f'{entry.name} marked as canceled.'}
