# from django.shortcuts import render, redirect, get_object_or_404
# from django.http import HttpResponse, HttpResponseRedirect
# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth import update_session_auth_hash
# from django.contrib.auth.forms import PasswordChangeForm
# from django.urls import reverse
# from django.contrib import messages
# from django.contrib.auth.models import User
# from django.contrib.auth.decorators import login_required
# from Employee.models import Employee
# from .forms import UserLogin, UserAddForm
# import random
# import logging
#
# logger = logging.getLogger(__name__)
#
#
# @login_required
# def changepassword(request):
#     if request.method == 'POST':
#         form = PasswordChangeForm(request.user, request.POST)
#         if form.is_valid():
#             user = form.save(commit=True)
#             update_session_auth_hash(request, user)  # Keeps the user logged in after password change
#             messages.success(
#                 request,
#                 'Your password has been changed successfully!',
#                 extra_tags='alert alert-success alert-dismissible show'
#             )
#             return redirect('Accounts:changepassword')
#         else:
#             messages.error(
#                 request,
#                 'There was an error changing your password. Please correct the errors below.',
#                 extra_tags='alert alert-danger alert-dismissible show'
#             )
#     else:
#         form = PasswordChangeForm(request.user)
#
#     return render(request, 'Accounts/change_password_form.html', {'form': form})
#
#
# def register_user_view(request):
#     if request.method == 'POST':
#         form = UserAddForm(data=request.POST)
#         if form.is_valid():
#             instance = form.save(commit=False)
#             instance.save()
#             username = form.cleaned_data.get("username")
#
#             messages.success(request, 'Account created for {0} !!!'.format(username),
#                              extra_tags='alert alert-success alert-dismissible show')
#             return redirect('Accounts:register')
#         else:
#             messages.error(request, 'Username or password is invalid',
#                            extra_tags='alert alert-warning alert-dismissible show')
#             return redirect('Accounts:register')
#
#     form = UserAddForm()
#     dataset = dict()
#     dataset['form'] = form
#     dataset['title'] = 'register users'
#     return render(request, 'Accounts/register.html', dataset)
#
#
# def login_view(request):
#     """
#     User login view with form validation, human verification, and redirection.
#     """
#     if request.method == 'POST':
#         form = UserLogin(data=request.POST)
#         captcha_answer = request.POST.get("captcha_answer")
#         correct_answer = request.session.get("captcha_answer")
#
#         logger.debug(f"CAPTCHA Answer from user: {captcha_answer}, Correct Answer: {correct_answer}")
#         logger.debug(f"Session Keys: {request.session.keys()}")  # Debugging session data
#
#         # Validate CAPTCHA first
#         if correct_answer is not None and captcha_answer and captcha_answer.isdigit():
#             if int(captcha_answer) == correct_answer:
#                 if form.is_valid():
#                     username = form.cleaned_data.get('username')
#                     password = form.cleaned_data.get('password')
#
#                     # Authenticate user credentials
#                     user = authenticate(request, username=username, password=password)
#                     if user is not None and user.is_active:
#                         login(request, user)
#                         return redirect('dashboard:dashboard')  # Redirect on success
#                     else:
#                         messages.error(
#                             request,
#                             'Invalid username or password.',
#                             extra_tags='alert alert-danger alert-dismissible show'
#                         )
#                 else:
#                     messages.error(
#                         request,
#                         'Please fill out the form correctly.',
#                         extra_tags='alert alert-warning alert-dismissible show'
#                     )
#             else:
#                 messages.error(
#                     request,
#                     'Incorrect CAPTCHA. Please try again.',
#                     extra_tags='alert alert-warning alert-dismissible show'
#                 )
#         else:
#             messages.error(
#                 request,
#                 'Invalid CAPTCHA input. Please provide a numeric answer.',
#                 extra_tags='alert alert-warning alert-dismissible show'
#             )
#
#         return redirect('Accounts:login')
#     else:
#         form = UserLogin()
#
#     # Generate a new CAPTCHA question
#     num1 = random.randint(1, 10)
#     num2 = random.randint(1, 10)
#     captcha_question = f"{num1} + {num2} = ?"
#     request.session["captcha_answer"] = num1 + num2
#     request.session.modified = True  # Ensure session updates
#
#     return render(request, 'Accounts/login.html', {
#         'form': form,
#         'captcha_question': captcha_question,
#     })
#
#
# def logout_view(request):
#     logout(request)
#     return redirect('Accounts:login')
#
#
# def users_list(request):
#     employees = Employee.objects.all()
#     return render(request, 'Accounts/users_table.html', {'employees': employees, 'title': 'Users List'})
#
#
# def users_unblock(request, id):
#     user = get_object_or_404(User, id=id)
#     emp = Employee.objects.filter(user=user).first()
#     emp.is_blocked = False
#     emp.save()
#     user.is_active = True
#     user.save()
#
#     return redirect('Accounts:users')
#
#
# def users_block(request, id):
#     user = get_object_or_404(User, id=id)
#     emp = Employee.objects.filter(user=user).first()
#     emp.is_blocked = True
#     emp.save()
#
#     user.is_active = False
#     user.save()
#
#     return redirect('Accounts:users')
#
#
# def unblock_user(request, id):
#     """
#     View to restore a previously deleted employee.
#     """
#     user = get_object_or_404(User, id=id)
#     emp = Employee.objects.filter(user=user).first()
#     if emp:
#         emp.is_deleted = False
#         emp.save()
#
#     user.is_active = True
#     user.save()
#
#     return redirect('Accounts:users_blocked_list')
#
#
# # def users_blocked_list(request):
# #     blocked_employees = Employee.objects.filter(deleted=True)
# #     print(blocked_employees)
# #     return render(request, 'Accounts/all_deleted_users.html', {
# #         'employees': blocked_employees,
# #         'title': 'Blocked Users List'
# #     })
#
# # def users_blocked_list(request):
# #     """Fetch and display blocked employees."""
# #     blocked_employees = Employee.objects.filter(is_deleted=True)
# #     return render(request, 'Accounts/all_deleted_users.html', {
# #         'employees': blocked_employees,
# #         'title': 'Blocked Users List'
# #     })
#
# #
# # def delete_employee(request, employee_id):
# #     """Mark an employee as deleted (soft delete)."""
# #     employee = get_object_or_404(Employee, id=employee_id)
# #     employee.is_deleted = True  # Soft delete
# #     employee.save()
# #
# #     messages.success(request, f"Employee {employee.get_full_name()} has been blocked successfully.")
# #     return redirect('Accounts:users_blocked_list')  # Ensure the redirect URL is correct# Redirect to the blocked users list
#
# def delete_employee(request, id):
#     employee = get_object_or_404(Employee, id=id)
#     employee.delete()  # Hard delete
#     messages.success(request, f"Employee {employee.get_full_name()} has been deleted.")
#     return redirect('dashboard:employees_list', {'employee': employee})  # Redirect to the employees list
#
#
#
# @login_required
# def user_profile_view(request):
#     employee = get_object_or_404(Employee, user=request.user)
#
#     context = {
#         'employee': employee,
#     }
#     return render(request, 'Accounts/user_profile_page.html', context)



from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from Employee.models import Employee
from .forms import UserLogin, UserAddForm
import random
import logging
from django.http import JsonResponse
logger = logging.getLogger(__name__)


@login_required
def changepassword(request):
    """
    View for changing the user's password.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            update_session_auth_hash(request, user)  # Keeps the user logged in after password change
            messages.success(
                request,
                'Your password has been changed successfully!',
                extra_tags='alert alert-success alert-dismissible show'
            )
            return redirect('Accounts:changepassword')
        else:
            messages.error(
                request,
                'There was an error changing your password. Please correct the errors below.',
                extra_tags='alert alert-danger alert-dismissible show'
            )
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'Accounts/change_password_form.html', {'form': form})


def register_user_view(request):
    """
    View for registering a new user.
    """
    if request.method == 'POST':
        form = UserAddForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.',
                              extra_tags='alert alert-warning alert-dismissible show')
                return redirect('Accounts:register')

            instance = form.save(commit=False)
            instance.save()
            messages.success(request, 'Account created for {0} !!!'.format(username),
                             extra_tags='alert alert-success alert-dismissible show')
            return redirect('Accounts:register')
        else:
            messages.error(request, 'Username or password is invalid',
                           extra_tags='alert alert-warning alert-dismissible show')
            return redirect('Accounts:register')

    form = UserAddForm()
    dataset = {
        'form': form,
        'title': 'Register Users'
    }
    return render(request, 'Accounts/register.html', dataset)


def login_view(request):
	'''
	work on me - needs messages and redirects
	
	'''
	login_user = request.user
	if request.method == 'POST':
		form = UserLogin(data = request.POST)
		if form.is_valid():
			username = request.POST.get('username')
			password = request.POST.get('password')

			user = authenticate(request, username = username, password = password)
			if user and user.is_active:
				login(request,user)
				if login_user.is_authenticated:
					return redirect('dashboard:dashboard')
			else:
			    messages.error(request,'Unable to verify your account. Please enter a valid credentials',extra_tags = 'alert alert-error alert-dismissible show' )
			    return redirect('accounts:login')

		else:
			return HttpResponse('data not valid')

	dataset=dict()
	form = UserLogin()

	dataset['form'] = form
	return render(request,'accounts/login.html',dataset)

@login_required
def logout_view(request):
    """
    View for logging out the user.
    """
    logout(request)
    return redirect('Accounts:login')


@login_required
def users_list(request):
    """
    View for displaying a list of all users.
    """
    employees = Employee.objects.filter(is_deleted=False)
    return render(request, 'Accounts/users_table.html', {
        'employees': employees,
        'title': 'Users List'
    })


@login_required
def users_block(request, id):
    """
    View for blocking a user.
    """
    user = get_object_or_404(User, id=id)
    emp = Employee.objects.filter(user=user).first()
    if emp:
        emp.is_blocked = True
        emp.save()

    user.is_active = False
    user.save()

    messages.success(request, f"User {user.username} has been blocked.")
    return redirect('Accounts:users')


# @login_required
# def users_unblock(request, id):
#     """
#     View for unblocking a user.
#     """
#     user = get_object_or_404(User, id=id)
#     emp = Employee.objects.filter(user=user).first()
#     if emp:
#         emp.is_blocked = False
#         emp.save()
#
#     user.is_active = True
#     user.save()
#
#     messages.success(request, f"User {user.username} has been unblocked.")
#     return redirect('Accounts:users')
def users_block(request, id):
    # Fetch the user by ID
    user = get_object_or_404(User, id=id)

    # Attempt to fetch the associated Employee record
    emp = Employee.objects.filter(user=user).first()
    if emp:
        emp.is_blocked = True
        emp.save()
    else:
        # Optional: log a warning or set a message if Employee record is missing
        messages.warning(request, f"No Employee record found for user {user.username}.")

    # Set the user as inactive
    user.is_active = False
    user.save()

    # Display a success message
    messages.success(request, f"User {user.username} has been blocked.")

    return redirect('Accounts:users')


# @login_required
# def users_blocked_list(request):
#     """
#     View for displaying a list of blocked users.
#     """
#     blocked_employees = Employee.objects.filter(is_blocked=True)
#     return render(request, 'Accounts/all_deleted_users.html', {
#         'employees': blocked_employees,
#         'title': 'Blocked Users List'
#     })

@login_required
def users_blocked_list(request):
    """
    View for displaying a list of blocked/deleted users.
    """
    blocked_employees = Employee.objects.filter(is_deleted=True)  # Fetch soft-deleted employees
    return render(request, 'Accounts/all_deleted_users.html', {
        'employees': blocked_employees,
        'title': 'Blocked Users List'
    })



# @login_required
# def delete_employee(request, id):
#     print(f"Deleting employee with ID: {id}")  # Debugging statement
#     if not id:
#         messages.error(request, "Invalid employee ID.")
#         return redirect('dashboard:dashboard')
#
#     employee = get_object_or_404(Employee, id=id)
#     employee.is_deleted = True  # Soft delete
#     employee.save()
#     messages.success(request, f"Employee {employee.get_full_name()} has been blocked successfully.")
#     return redirect('Accounts:users_blocked_list')

# @login_required
# def delete_employee(request, id):
#     """
#     Soft delete an employee instead of permanently deleting.
#     """
#     employee = get_object_or_404(Employee, id=id)
#     employee.is_deleted = True  # Soft delete
#     employee.save()
#
#     messages.success(request, f"Employee {employee.get_full_name()} has been deleted.")
#     return redirect('Accounts:users_blocked_list')  # Redirect to blocked users page
#

# def delete_employee(request, id):
#     """
#     View for deleting an employee by id.
#     """
#     if request.method == 'DELETE':
#         employee = get_object_or_404(Employee, id=id)
#         employee.delete()  # Hard delete or mark as deleted (soft delete)
#         return JsonResponse({'success': True})
#     else:
#         return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def unblock_user(request, id):
    """
    View for restoring a previously blocked user.
    """
    user = get_object_or_404(User, id=id)
    emp = Employee.objects.filter(user=user).first()
    if emp:
        emp.is_deleted = False
        emp.save()

    user.is_active = True
    user.save()

    messages.success(request, f"User {user.username} has been unblocked.")
    return redirect('Accounts:users')


@login_required
def user_profile_view(request):
    """
    View for displaying the logged-in user's profile.
    """
    employee = get_object_or_404(Employee, user=request.user)
    return render(request, 'Accounts/user_profile_page.html', {
        'employee': employee,
    })

# def deleted_users_list(request):
#     """
#     View for displaying the list of deleted users.
#     """
#     deleted_employees = Employee.objects.filter(is_deleted=True)
#     return render(request, 'Accounts/deleted_users_list.html', {
#         'employees': deleted_employees,
#         'title': 'Deleted Users List'
#     })
