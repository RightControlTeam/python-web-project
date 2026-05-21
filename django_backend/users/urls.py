from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('me/', views.get_me, name='get_me'),
    path('me/update/', views.update_me, name='update_me'),
    path('me/delete/', views.delete_me, name='delete_me'),
    path('change_balance/', views.change_balance, name='change_balance'),
]