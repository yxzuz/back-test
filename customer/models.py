"""Provide model using in customer app."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import models
from django.contrib.auth.models import User
from business.models import Entry, LoginForm



class Customer(models.Model):
    """Represents a customer in the system.

    Customer has one-to-one relationship with the User model.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        """Return username of the customer."""
        return self.user.username


class CustomerSignupForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.CharField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ["username", "password1", "password2", "email"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            Customer.objects.create(user=user)
        return user


class CustomerQueue(models.Model):
    """Represents a queue entry for a customer in a specific business."""

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)

    def __str__(self):
        """Return a string representation of the CustomerQueue instance."""
        return f"{self.customer.user.username}, {self.entry.business},{self.entry.name}"
