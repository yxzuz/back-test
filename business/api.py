from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from typing import List, Union
from customer.schemas import CustomerQueueListSchema, CustomerQueueCreateSchema
from customer.models import Customer, CustomerQueue
from .models import Entry, Business
from .schemas import EntrySchema, BusinessSchema


router = Router()


# class UserSchema(Schema):
#     username: str
#     is_authenticated: bool

@router.get("my-business/", response=BusinessSchema)
def my_business(request):
    """Show business information."""
    return Business.objects.get(user=request.user)


@router.get("all-customers-entries/", response=list[EntrySchema])
def get_all_entries(request):
    if request.user.is_anonymous:
        return Entry.objects.all()
    entries = Entry.objects.filter(business__user=request.user)
    return entries
