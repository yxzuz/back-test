"""Provide model using in business app."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from nanoid import generate
from django.forms import ModelForm


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))


class SignUpForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.CharField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    business_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email")
        if commit:
            user.save()
            business_name = self.cleaned_data.get("business_name")
            Business.objects.create(user=user, name=business_name)
        return user


class Business(models.Model):
    """Business model to keep track of business owners' information."""
  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        """Return name of Business."""
        return self.name


class BusinessSignupForm(forms.ModelForm):
    name = forms.CharField(max_length=255)

    class Meta:
        model = User
        fields = ["username", "password", "email"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            Business.objects.create(
                user=user, business_name=self.cleaned_data["business_name"]
            )
        return user


class Queue(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    alphabet = models.CharField(max_length=1, default="A")
    estimated_time = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class Entry(models.Model):
    name = models.CharField(max_length=50)
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE, null=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True)
    tracking_code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    time_in = models.DateTimeField(default=timezone.now)
    time_out = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default="waiting")

    def save(self, *args, **kwargs):
        if not self.tracking_code and self.status != "completed":
            while True:
                new_tracking_code = generate(
                    "1234567890abcdefghijklmnopqrstuvwxyz", size=10
                )
                if not Entry.objects.filter(
                    tracking_code=new_tracking_code, time_out__isnull=True
                ).exists():
                    self.tracking_code = new_tracking_code
                    break

        if not self.name:
            today = timezone.now().date()
            queue_entries_today = (
                Entry.objects.filter(queue=self.queue, time_in__date=today).count() + 1
            )
            self.name = f"{self.queue.alphabet}{queue_entries_today}"

        super().save(*args, **kwargs)

    def mark_as_completed(self):
        self.status = "completed"
        self.time_out = timezone.now()
        self.tracking_code = None
        self.save()

    def get_queue_position(self) -> int:
        """Calculate the number of people ahead in the queue.

        Return:
            int: The number of entries ahead of this one in the queue.
        """
        return Entry.objects.filter(
            queue=self.queue,
            business=self.business,
            time_in__lt=self.time_in,
            status="waiting",
        ).count()

    def is_waiting(self):
        return self.status == 'waiting'

    def __str__(self):
        """Return string representation of Entry's model."""
        return self.name


class QueueForm(ModelForm):
    class Meta:
        model = Queue
        fields = ["name", "alphabet"]

