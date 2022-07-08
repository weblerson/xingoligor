from django.urls import path
from . import views

urlpatterns = [
    # Register urls
    path('register/', views.register, name='register'),
    path('activate/<str:token>', views.activate, name='activate'),

    # Login url
    path('login/', views.login, name='login'),

    # Recover urls
    path('recover/', views.recover_menu, name='recover_menu'),
    path('recover/<str:token>', views.recover_password, name='recover'),
    path('norecover/<str:token>', views.no_recover, name='norecover'),

    # Logout url
    path('logout/', views.logout, name='logout')
]