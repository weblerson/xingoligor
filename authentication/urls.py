from django.urls import path
from . import views

urlpatterns = [
    # Register urls
    path('register/', views.register, name='register'),
    path('activate/<str:token>', views.activate, name='activate'),

    # Login url
    path('login/', views.login, name='login'),

    # Logout url
    path('logout/', views.logout, name='logout')
]