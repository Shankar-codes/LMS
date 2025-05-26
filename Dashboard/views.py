from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q
import datetime
from django.core.mail import send_mail
from django.contrib import messages
from django.urls import reverse
from Leave.models import Leave
from Employee.models import *
from Leave.forms import LeaveCreationForm
from Attendance.models import Attendance
from Attendance.forms import AttendanceForm
from Employee.models import Employee
from django.core.paginator import Paginator
from Employee.forms import EmployeeCreateForm
import logging
from Leave.models import LeaveBalance
from Employee.models import Employee, LeaveRecord
# from .decorators import superuser_required
from django.http import JsonResponse
from Employee.models import Role

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    # Fetch the employee data for the logged-in user
    employee = Employee.objects.filter(user=request.user).first()

    if employee:
        employee_id = employee.id
        logger.info(f"Employee ID for user {request.user.username} (ID: {request.user.id}): {employee_id}")
    else:
        employee_id = None
        logger.warning(f"No Employee record found for user {request.user.username} (ID: {request.user.id})")

    # Prepare context data for the dashboard view
    dataset = {
        'employees': Employee.objects.all()[:50],  # Limit the number of employees to 50
        'leaves': Leave.objects.filter(status='pending')[:50],  # Fetch only pending leaves, limit to 50
        'staff_leaves': Leave.objects.filter(user=request.user),
        'employee_id': employee_id,
        'title': 'Summary',
    }

    return render(request, 'dashboard/dashboard_index.html', dataset)



# def dashboard_employees(request):
#     if not (request.user.is_authenticated and request.user.is_superuser and request.user.is_staff):
#         return redirect('/')
#
#     # Fetch departments and employees
#     departments = Department.objects.all()
#     employees = Employee.objects.all()
#     # employeees = Employee.objects.filter(is_deleted=False)
#
#     # Filter employees based on search query
#     query = request.GET.get('search')
#     if query:
#         employees = employees.filter(
#             Q(firstname__icontains=query) |
#             Q(lastname__icontains=query)
#         )
#
#     # Pagination logic
#     paginator = Paginator(employees, 10)
#     page = request.GET.get('page')
#     employees_paginated = paginator.get_page(page)
#
#     # Fetch blocked employees
#     blocked_employees = Employee.objects.all_blocked_employees()
#
#     # Create context to pass to the template
#     dataset = {
#         'employees': employees_paginated,
#         'departments': departments,
#         'blocked_employees': blocked_employees
#     }
#
#     return render(request, 'dashboard/employee_app.html', dataset)

def dashboard_employees(request):
    if not (request.user.is_authenticated and request.user.is_superuser and request.user.is_staff):
        return redirect('/')

    # Fetch departments and employees (exclude deleted employees)
    departments = Department.objects.all()
    employees = Employee.objects.filter(is_deleted=False)  # Exclude deleted employees

    # Debugging: Print employee IDs
    for employee in employees:
        print(f"Employee ID: {employee.id}, Name: {employee.firstname} {employee.lastname}")

    # Filter employees based on search query
    query = request.GET.get('search')
    if query:
        employees = employees.filter(
            Q(firstname__icontains=query) |
            Q(lastname__icontains=query)
        )

    # Pagination logic
    paginator = Paginator(employees, 10)
    page = request.GET.get('page')
    employees_paginated = paginator.get_page(page)

    # Fetch blocked employees
    blocked_employees = Employee.objects.all_blocked_employees()

    # Create context to pass to the template
    dataset = {
        'employees': employees_paginated,
        'departments': departments,
        'blocked_employees': blocked_employees
    }

    return render(request, 'dashboard/employee_app.html', dataset)



def dashboard_employees_create(request):
    if not (request.user.is_authenticated and request.user.is_superuser and request.user.is_staff):
        return redirect('/')

    if request.method == 'POST':
        form = EmployeeCreateForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save(commit=False)

            # Check if user already exists
            user = request.POST.get('user')
            try:
                assigned_user = User.objects.get(id=user)
                instance.user = assigned_user
            except User.DoesNotExist:
                messages.error(request, 'User does not exist', extra_tags='alert alert-warning alert-dismissible show')
                return redirect('dashboard:employeecreate')

            # Check for duplicate employee using employeeid
            if Employee.objects.filter(employeeid=instance.employeeid).exists():
                messages.error(request, 'An employee with this ID already exists', extra_tags='alert alert-warning alert-dismissible show')
                return redirect('dashboard:employeecreate')

            # Check if the role exists
            role = request.POST.get('role')
            try:
                role_instance = Role.objects.get(id=role)
                instance.role = role_instance
            except Role.DoesNotExist:
                messages.error(request, 'Role does not exist', extra_tags='alert alert-warning alert-dismissible show')
                return redirect('dashboard:employeecreate')

            # Other instance data assignment (if needed, since form handles the data directly)
            instance.title = form.cleaned_data.get('title')
            instance.image = form.cleaned_data.get('image')
            instance.firstname = form.cleaned_data.get('firstname')
            instance.lastname = form.cleaned_data.get('lastname')
            instance.othername = form.cleaned_data.get('othername')
            instance.birthday = form.cleaned_data.get('birthday')
            instance.startdate = form.cleaned_data.get('startdate')
            instance.employeetype = form.cleaned_data.get('employeetype')
            instance.date_of_joining = form.cleaned_data.get('date_of_joining')
            instance.dateissued = form.cleaned_data.get('dateissued')
            instance.degree = form.cleaned_data.get('degree')

            # Save instance
            instance.save()

            return redirect('dashboard:employees')

        else:
            messages.error(request, 'There were errors in the form. Please correct them and try again.',
                           extra_tags='alert alert-danger alert-dismissible show')
            return redirect('dashboard:employeecreate')

    # Initialize form for GET request
    form = EmployeeCreateForm()
    dataset = {
        'form': form,
        'title': 'Register Employee'
    }
    return render(request, 'dashboard/employee_create.html', dataset)


def employee_edit_data(request, id):
    # Authorization check
    if not (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)):
        messages.error(request, "Unauthorized access")
        return redirect('/')

    # Fetch the employee object
    employee = get_object_or_404(Employee, id=id)

    if request.method == 'POST':
        form = EmployeeCreateForm(request.POST, request.FILES, instance=employee)

        if form.is_valid():
            instance = form.save(commit=False)

            # Assign user
            user_id = request.POST.get('user')
            try:
                assigned_user = User.objects.get(id=user_id)
                instance.user = assigned_user
            except User.DoesNotExist:
                messages.error(request, 'Invalid User selected')
                return render(request, 'dashboard/employee_create.html', {
                    'form': form,
                    'employee': employee,
                    'title': f'Edit - {employee}'
                })

            # Assign department
            department_id = request.POST.get('department')
            try:
                department = Department.objects.get(id=department_id)
                instance.department = department
            except Department.DoesNotExist:
                messages.error(request, 'Invalid Department selected')
                return render(request, 'dashboard/employee_create.html', {
                    'form': form,
                    'employee': employee,
                    'title': f'Edit - {employee}'
                })

            # Assign role
            role_id = request.POST.get('role')
            try:
                role_instance = Role.objects.get(id=role_id)
                instance.role = role_instance
            except Role.DoesNotExist:
                messages.error(request, 'Invalid Role selected')
                return render(request, 'dashboard/employee_create.html', {
                    'form': form,
                    'employee': employee,
                    'title': f'Edit - {employee}'
                })

            # Save instance only if no errors
            instance.save()
            messages.success(request, 'Account Updated Successfully')
            return redirect('dashboard:employeeinfo', id=employee.id)  # Include id here

        else:
            # Show form errors
            messages.error(request, 'Form validation failed')
            print(form.errors)
            return render(request, 'dashboard/employee_create.html', {
                'form': form,
                'employee': employee,
                'title': f'Edit - {employee}'
            })

    # Initialize form with instance data
    form = EmployeeCreateForm(instance=employee)

    return render(request, 'dashboard/employee_create.html', {
        'form': form,
        'employee': employee,
        'title': f'Edit - {employee}'
    })


def dashboard_employee_info(request, id):
    if not request.user.is_authenticated:
        return redirect('/')

    employee = get_object_or_404(Employee, id=id)
    dataset = {
        'employee': employee,
        'title': f"profile - "
    }
    return render(request, 'dashboard/employee_detail.html', dataset)


def dashboard_employees(request):
    # Fetch all employees from the Employee model
    employees = Employee.objects.all()

    # Optional: Add pagination


    paginator = Paginator(employees, 10)  # Show 10 employees per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pass the employees to the template (or use paginated employees if pagination is applied)
    return render(request, 'dashboard/employee_app.html', {'page_obj': page_obj})


def delete_employee(request, id):
    """
    Delete an employee.
    """
    employee = get_object_or_404(Employee, id=id)
    if request.method == 'POST':
        employee.delete()

        messages.success(
            request,
            f'Employee {employee.get_full_name() if hasattr(employee, "get_full_name") and callable(employee.get_full_name) else employee.get_full_name} has been deleted successfully.'
        )

        return redirect('dashboard:employees')

    return redirect('dashboard:employees')


@login_required
def leave_balance_view(request):
    try:
        leave_balance = LeaveBalance.objects.get(employee=request.user)
    except LeaveBalance.DoesNotExist:
        return render(request, 'error.html', {'message': 'Leave balance record not found.'})

    context = {
        'annual_leave': leave_balance.calculate_remaining_annual_leave(),
        'sick_leave': leave_balance.calculate_remaining_sick_leave(),
        'used_annual_leave': leave_balance.used_annual_leave,
        'used_sick_leave': leave_balance.used_sick_leave,
    }
    return render(request, 'dashboard/dashboard_index.html', context)


def restore_employee(request, id):
    """
    Restore a blocked employee.
    """
    employee = get_object_or_404(Employee, id=id)
    employee.is_deleted = False  # Unblock employee
    employee.save()

    messages.success(request, f'Employee {employee.get_full_name()} has been restored successfully.')

    return redirect('dashboard:blocked_users')




def leaves_approved_list(request):
    # Fetch approved leaves
    approved_leaves = Leave.objects.filter(status='approved')  # Ensure this returns a QuerySet
    approved_leave_count = approved_leaves.count()  # Get the count of approved leaves

    print(f"DEBUG: Approved Leave Count = {approved_leave_count}")  # Print for debugging

    return render(request, 'dashboard/leaves_approved.html', {
        'leave_list': approved_leaves,
        'approved_leave_count': approved_leave_count,  # Pass the count to the template
        'title': 'Approved Leave List'
    })
#
# def leaves_approved_list(request):
#     approved_leaves = Leave.objects.all_approved_leaves()  # Fetch approved leaves
#     return render(request, 'dashboard/leaves_approved.html', {
#         'leave_list': approved_leaves,
#         'title': 'Approved Leave List'
#     })
#
# def approvedleaves(request):
#     # Fetch approved leaves
#     approved_leaves = Leave.objects.filter(status='approved')  # Ensure this returns a QuerySet
#     approved_leave_count = approved_leaves.count()  # Get the count of approved leaves
#
#     print(f"DEBUG: Approved Leave Count = {approved_leave_count}")  # Print for debugging
#
#     return render(request, 'dashboard/approvedleaves.html', {
#         'leave_list': approved_leaves,
#         'approved_leave_count': approved_leave_count,  # Pass the count to the template
#         'title': 'Approved Leave List'
#     })


def get_roles(request):
    department_id = request.GET.get('department_id')
    roles = Role.objects.filter(department_id=department_id).values('id', 'name')
    return JsonResponse(list(roles), safe=False)
