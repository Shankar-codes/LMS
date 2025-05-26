from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('welcome/', views.dashboard, name='dashboard'),
    path('employees/all/', views.dashboard_employees, name='employees'),
    path('employee/create/', views.dashboard_employees_create, name='employeecreate'),
    path('employee/profile/<int:id>/', views.dashboard_employee_info, name='employeeinfo'),
    path('employee/profile/edit/<int:id>/', views.employee_edit_data, name='edit'),
    path('employee/delete/<int:id>/', views.delete_employee, name='delete_employee'),
    # path('leaves/approved/', views.approvedleaves, name='approvedleaves'),
    path('get-roles/', views.get_roles, name='get_roles'),
]
