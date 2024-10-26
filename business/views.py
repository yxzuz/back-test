"""Views for business app."""
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import SignUpForm, LoginForm, Business, Entry, Queue, QueueForm


def add_customer(request):
    """Add a customer to a specific business and queue."""
    this_user = request.user

    try:
        business = Business.objects.get(user=this_user)
    except Business.DoesNotExist:
        return redirect('business:login')

    queues = Queue.objects.filter(business=business)
    if not queues.exists():
        return redirect('business:home')

    tracking_code = None

    if request.method == 'POST':
        queue_id = request.POST.get('queue')

        try:
            selected_queue = Queue.objects.get(id=queue_id, business=business)
        except Queue.DoesNotExist:
            return redirect('business:home')

        entry = Entry(
            queue=selected_queue,
            business=business,
            time_in=timezone.now()
        )
        entry.save()

        tracking_code = entry.tracking_code

    return render(request, 'business/add_customer.html', {
        'business': business,
        'queues': queues,
        'tracking_code': tracking_code
    })


def queue(request):
    return HttpResponse("Your Queue")


def signup(request):
    """Register new business user."""
    if request.method =='POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('business:home')
        else:
            messages.error(request, 'Form is invalid.')
            return redirect('business:signup')
    else:
        form = SignUpForm()
        return render(request, 'business/signup.html', {'form': form})


def login_view(request):
    """Login page for business user."""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                try:
                    Business.objects.get(user=user)
                except Business.DoesNotExist:
                    messages.error(request, 'Customer account can not use with business.')
                    return redirect('business:login')
                login(request, user)
                return redirect('business:home')
            else:
                messages.error(request, 'Invalid credentials')
        else:
            messages.error(request, 'Form is not valid')

    else:
        form = LoginForm()

    return render(request, 'business/login.html', {'form': form})


def show_entry(request):
    """Display the entries for a specific business, filtered by today's date.

    Args:
        request: The HTTP request object.
        pk: The primary key of the business.

    Returns:
        Rendered template with queue and entry lists for the business.
    """
    today = timezone.now().date()
    if not request.user.is_authenticated:
        return redirect('business:login')
    try:
        business = Business.objects.get(user=request.user)
    except Business.DoesNotExist:
        return redirect('business:login')
    queue_list = Queue.objects.filter(business=business)
    entry_list = Entry.objects.filter(
        business=business,
        time_in__date=today,
    ).order_by("time_in")
    return render(
        request,
        "business/show_entry.html",
        {"queue_list": queue_list, "entry_list": entry_list,
         "business": business},
    )


def add_queue(request):
    """
    Add new queue to the specified business.

    Args:
        request: The HTTP request object.
        pk: The primary key of the business.

    Returns:
        Rendered template or redirect to the entry page with the updated queue.
    """
    this_user = request.user
    business = get_object_or_404(Business, user=this_user)
    if request.method == "POST":
        form = QueueForm(request.POST)
        if form.is_valid():
            queue = form.save(commit=False)
            queue.business = business
            queue.save()
            messages.success(
                request,
                f"Successfully added the queue '{queue.name}' "
                f"with alphabet '{queue.alphabet}'.",
            )
            return redirect("business:home")
    return render(request, "business/show_entry.html", {"business": business})


def edit_queue(request, pk):
    """
    Edit queue to the specified business.

    Args:
        request: The HTTP request object.
        pk: The primary key of the queue.

    Returns:
        Rendered template or redirect to the entry page with the updated queue.
    """
    business = Business.objects.get(user=request.user)
    try:
        queue = Queue.objects.get(pk=pk, business=business)
    except Queue.DoesNotExist:
        messages.error(request, "Cannot edit this queue.")
        return redirect('business:home')
    if request.method == "POST":
        form = QueueForm(request.POST, instance=queue)
        if form.is_valid():
            queue_form = form.save(commit=False)
            queue_form.business = business
            queue_form.save()
            messages.success(
                request,
                f"Successfully updated the queue '{queue.name}' "
                f"with the alphabet '{queue.alphabet}'.",
            )
            return redirect("business:home")
    return render(request, "business/show_entry.html", {"business": business})


def run_queue(request, pk):
    """
    Mark a specific entry as completed.

    Args:
        request: The HTTP request object.
        pk: The primary key of the entry.

    Returns:
        Rendered template or redirect to the entry page with the updated queue.
    """
    business = Business.objects.get(user=request.user)
    try:
        entry = Entry.objects.get(pk=pk, business=business)
    except Entry.DoesNotExist:
        messages.error(request, "Cannot run this entry.")
        return redirect('business:home')
    if request.method == "POST":
        entry.mark_as_completed()
        messages.success(request, f"{entry.name} marked as completed.")
        return redirect("business:home")
    return render(request, "business/show_entry.html")


def logout_view(request):
    """Logout the user and redirect to login page."""
    logout(request)
    return redirect('business:login')
