from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from . import views

app_name = 'business'
urlpatterns = [
    path('add_customer/', views.add_customer, name='add_customer'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('', RedirectView.as_view(url='home/', permanent=False)),
    path('home/', views.show_entry, name='home'),
    path('addQueue/', views.add_queue, name='add_queue'),
    path('<int:pk>/editQueue/', views.edit_queue, name='edit_queue'),
    path('<int:pk>/runQueue/', views.run_queue, name='run_queue'),
]
