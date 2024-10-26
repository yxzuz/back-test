"""Views for customer app."""

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from .models import CustomerQueue, Customer, Entry, CustomerSignupForm, LoginForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cancel_queue(request, entry_id):
    """When the queue is canceled, the entry is also cancel."""
    try:
        my_queue = CustomerQueue.objects.get(entry__id=entry_id)
    except CustomerQueue.DoesNotExist:
        messages.warning(request, "This entry does not exist in customer queue.")
        return redirect("customer:home")

    if my_queue.entry.status != "waiting":
        messages.warning(request, "You cannot to cancel this entry.")
        return redirect("customer:home")

    if not request.user.is_authenticated or request.user != my_queue.customer.user:
        messages.warning(request, "You do not have the authority to delete this entry.")
        return redirect("customer:home")
    Entry.objects.get(id=entry_id).delete()
    return redirect("customer:home")


class HomeListView(ListView):
    """View for customer's home page."""

    template_name = "customer/home.html"
    context_object_name = "customer_queue_list"

    def get_queryset(self):
        """Return a queryset of CustomerQueue instances for the authenticated user.

        If it's an anonymous user, it will return nothing.
        """
        if not self.request.user.is_authenticated:
            return []
        return CustomerQueue.objects.filter(
            customer__user__username=self.request.user
        )

    def post(self, request, *args, **kwargs):
        """Allow an authenticated user to cancel and view their customer queue by inputting track code.

        Visitor can only view a single entry based on track code.
        In case another user tried to access the track code of others,
        they cannot view the entry nor cancel it either.
        """

        track_code = request.POST.get("track-code")
        try:
            my_entry = Entry.objects.get(tracking_code=str(track_code))
        except (Entry.DoesNotExist, KeyError):
            messages.warning(request, "The track code is incorrect.")
            return redirect("customer:home")

        if not self.request.user.is_authenticated:  # visitors
            logger.info("Visitor tried to see entry.")
            return render(
                request,
                self.template_name,
                {"customer_queue_list": [CustomerQueue.objects.get(entry=my_entry)]},
            )

        try:
            my_queue = CustomerQueue.objects.get(entry=my_entry)
            if my_queue.customer.user != self.request.user:
                messages.warning(request, "You can't access someone else entry!")
        except CustomerQueue.DoesNotExist:
            my_customer = Customer.objects.get(user=self.request.user)
            CustomerQueue.objects.create(customer=my_customer, entry=my_entry)
            messages.success(request, "This entry is added to your queue history.")
        return redirect("customer:home")
      

def profile(request):
    return HttpResponse("Profile")


def signup(request):
    """Register new customer user."""
    if request.method == "POST":
        form = CustomerSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("customer:home")
        else:
            messages.error(request, "Form is invalid.")
            return redirect("customer:signup")
    else:
        form = CustomerSignupForm()
        return render(request, "customer/signup.html", {"form": form})


def logout_view(request):
    """Logout the user and redirect to login page."""
    logout(request)
    return redirect('customer:home')


def login_view(request):
    """Login page for customer user."""
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=username, password=password)
            if user is not None:
                try:
                    Customer.objects.get(user=user)
                except Customer.DoesNotExist:
                    messages.error(
                        request, "Business account can not use with customer."
                    )
                    return redirect("customer:login")
                login(request, user)
                return redirect("customer:home")
            else:
                messages.error(request, "Invalid credentials")
        else:
            messages.error(request, "Form is not valid")

    else:
        form = LoginForm()

    return render(request, "customer/login.html", {"form": form})
