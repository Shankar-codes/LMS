from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create-user/', views.register_user_view, name='register'),
    path('user/change-password/', views.changepassword, name='changepassword'),
    path('users/all', views.users_list, name='users'),
    path('user/block/<int:id>/', views.users_block, name='userblock'),
    path('user/unblock/<int:id>/', views.unblock_user, name='userunblock'),
    path('users/blocked/all', views.users_blocked_list, name='userblockedlist'),
    path('profile/', views.user_profile_view, name='user_profile_view'),
    path('unblock/<int:id>/', views.unblock_user, name='unblock_user'),
    # path('delete-employee/<int:id>/', views.delete_employee, name='delete_employee'),
    path('blocked-users/', views.users_blocked_list, name='users_blocked_list'),
    # path('deleted_users/', views.deleted_users_list, name='deleted_users_list'),
]
