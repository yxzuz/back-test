from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from typing import List, Union
from customer.schemas import CustomerQueueListSchema, CustomerQueueCreateSchema
from customer.models import Customer, CustomerQueue
from .models import Entry
from .schemas import EntrySchema


router = Router()


class UserSchema(Schema):
    username: str
    is_authenticated: bool


@router.get("all-customers-entries/", response=list[EntrySchema])
def get_all_entries(request):
    entries = Entry.objects.all()
    return entries