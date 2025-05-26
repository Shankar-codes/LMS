from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.conf import settings
from .models import Leave, Employee, LeaveRequest, LeaveBalance
from .forms import LeaveCreationForm
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .serializers import LeaveSerializer, LeaveRequestSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.http import JsonResponse
from rest_framework.views import APIView
from .decorators import superuser_required
from rest_framework import generics, status
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


# from Leave.decorators import superuser_required


# Decorator for superuser check
def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser, login_url='login')(view_func)


def send_leave_email(recipients, subject, message):
    send_mail(
        subject,
        message,
        'from@example.com',  # Replace with your actual sender email
        recipients,  # List of email recipients
        fail_silently=False,
    )


def update_leave_status(leave, status, is_approved=False):
    leave.status = status
    leave.is_approved = is_approved
    leave.save()


@login_required
def leave_creation(request):  # 1
    # Check if the request method is POST
    if request.method == 'POST':
        # Bind the POST data to the form
        form = LeaveCreationForm(data=request.POST)

        # Check if the form is valid
        if form.is_valid():
            # Save the form data without committing to the database
            instance = form.save(commit=False)

            # Assign the logged-in user to the leave request
            instance.user = request.user

            # If the leave type is half day, adjust the logic accordingly
            if instance.leavetype == 'half day':
                # Ensure that both half-day start and end times are provided for half-day leave
                start_time = form.cleaned_data.get('start_time')
                end_time = form.cleaned_data.get('end_time')

                if not start_time or not end_time:
                    messages.error(request, "Please provide valid start and end times for half-day leave.")
                    return redirect('Leave:createleave')

                # Ensure start time is before end time for half-day leave
                if start_time >= end_time:
                    messages.error(request, "Start time must be earlier than end time for half-day leave.")
                    return redirect('Leave:createleave')

                # Save the times to the instance
                instance.start_time = start_time
                instance.end_time = end_time

            # Save the instance to the database
            instance.save()

            # Prepare the email details
            subject = 'Leave Request Confirmation'
            message = f'Hi {request.user.username}, Your leave request from {instance.startdate} to {instance.enddate} has been submitted.'
            recipients = [request.user.email]  # Send the email to the logged-in user

            # Send email to the user
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipients,
                fail_silently=False,
            )

            # Show a success message
            messages.success(request, 'Leave Request Sent, wait for Admin\'s response',
                             extra_tags='alert alert-success alert-dismissible show')
            return redirect('Leave:createleave')

        # If the form is not valid, show an error message
        messages.error(request, 'Failed to Request a Leave, please check entry dates',
                       extra_tags='alert alert-warning alert-dismissible show')
        return redirect('Leave:createleave')

    # If the request method is GET, display the leave creation form
    form = LeaveCreationForm()
    return render(request, 'dashboard/create_leave.html', {
        'form': form,
        'title': 'Apply for Leave'
    })




@superuser_required
def leaves_list(request):
    leaves = Leave.objects.all_pending_leaves()
    return render(request, 'dashboard/leaves_recent.html', {
        'leave_list': leaves,
        'title': 'Leaves List - Pending'
    })


# API views for Leave Requests

@api_view(['GET'])
@permission_classes([IsAdminUser])
def api_leaves_list(request):
    leaves = Leave.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filters = request.GET.get('status', None)
    if filters:
        leaves = leaves.filter(status=filters)
    serializer = LeaveSerializer(leaves, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_create_leave(request):
    serializer = LeaveSerializer(data=request.data)
    if serializer.is_valid():
        try:
            serializer.save(user=request.user)
            return Response({"message": "Leave request created successfully!", "data": serializer.data},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LeaveRequestCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LeaveSerializer(data=request.data)
        if serializer.is_valid():
            leave_request = serializer.save()
            messages.success(request, "Leave request submitted successfully.")
            return Response({
                "success": True,
                "message": "Your leave request has been submitted successfully."
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def api_approve_leave(request, id):
    leave = get_object_or_404(Leave, id=id)
    update_leave_status(leave, 'approved', is_approved=True)
    return Response({'message': 'Leave approved successfully'}, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def api_reject_leave(request, id):
    leave = get_object_or_404(Leave, id=id)
    update_leave_status(leave, 'rejected')
    return Response({'message': 'Leave rejected successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_leave_details(request, id):
    leave = get_object_or_404(Leave, id=id, user=request.user)
    serializer = LeaveSerializer(leave)
    return Response(serializer.data, status=status.HTTP_200_OK)


@login_required
def leaves_view(request, id):
    leave = get_object_or_404(Leave, id=id)
    employee = Employee.objects.filter(user=leave.user).first()  # Use .first() to avoid IndexError

    if not employee:
        return render(request, 'dashboard/leave_detail_view.html', {
            'leave': leave,
            'employee': None,
            'title': f'{leave.user.username}-{leave.status} leave',
            'error_message': 'No associated employee record found.'
        })

    return render(request, 'dashboard/leave_detail_view.html', {
        'leave': leave,
        'employee': employee,
        'title': f'{leave.user.username}-{leave.status} leave',
    })


@superuser_required
def approve_leave(request, id):
    leave = get_object_or_404(Leave, id=id)

    employee = Employee.objects.filter(user=leave.user).first()
    if not employee:
        messages.error(
            request,
            "No associated employee found for this leave request.",
            extra_tags="alert alert-danger alert-dismissible show"
        )
        return redirect('Leave:userleaveview', id=id)

    leave.status = 'approved'
    leave.is_approved = True
    leave.save()

    # Sending the approval email to the employee
    send_mail(
        'Leave Request Approved',  # Subject of the email
        f'Hello {employee.firstname},\n\n'
        f'Your {leave.leavetype} leave request from {leave.startdate} to {leave.enddate} has been approved.\n\n'
        f'Best regards,\nYour Company',  # Email body
        settings.DEFAULT_FROM_EMAIL,  # From email (use the default email set in settings.py)
        [employee.user.email],  # To email (the employee's email address)
        fail_silently=False,  # Set to True if you want to suppress errors
    )

    # Display success message
    messages.success(
        request,
        f"The {leave.leavetype} leave request for {employee.user.get_full_name()} "
        f"({leave.startdate} - {leave.enddate}) has been approved, and an email has been sent.",
        extra_tags="alert alert-success alert-dismissible show"
    )

    return redirect('Leave:leavesapprovedlist')


@superuser_required
def leaves_approved_list(request):
    approved_leaves = Leave.objects.all_approved_leaves()  # Fetch approved leaves
    return render(request, 'dashboard/leaves_approved.html', {
        'leave_list': approved_leaves,
        'title': 'Approved Leave List'
    })


@superuser_required
def cancel_leave(request, id):
    leave = get_object_or_404(Leave, id=id)

    # Check if the leave is already cancelled
    if leave.status == 'cancelled':
        messages.warning(
            request,
            f'The {leave.leavetype} leave request for {leave.user.get_full_name()} '
            f'({leave.startdate} - {leave.enddate}) is already canceled.',
            extra_tags='alert alert-warning alert-dismissible show'
        )
        return redirect('Leave:canceleaveslist')

    # Mark the leave as canceled
    leave.status = 'cancelled'  # Update status to 'cancelled'
    leave.is_approved = False  # Reset approval status
    leave.save()

    # Get the employee associated with the leave request
    employee = Employee.objects.filter(user=leave.user).first()
    if employee:
        # Send cancellation email to the employee
        send_mail(
            'Leave Request Canceled',  # Subject of the email
            f'Hello {employee.firstname},\n\n'
            f'Your {leave.leavetype} leave request from {leave.startdate} to {leave.enddate} has been canceled.\n\n'
            f'Best regards,\nYour Company',  # Email body
            settings.DEFAULT_FROM_EMAIL,  # From email (use the default email set in settings.py)
            [employee.user.email],  # To email (employee's email address)
            fail_silently=False,  # Set to True to suppress errors
        )

    # Display a success message with leave details
    messages.success(
        request,
        f'The {leave.leavetype} leave request for {leave.user.get_full_name()} '
        f'({leave.startdate} - {leave.enddate}) has been canceled, and an email has been sent.',
        extra_tags='alert alert-success alert-dismissible show'
    )

    return redirect('Leave:canceleaveslist')


@superuser_required
def cancel_leaves_list(request):
    # Fetch all leaves with the 'cancelled' status
    leaves = Leave.objects.filter(status='cancelled')  # Use the 'status' field to filter canceled leaves

    return render(request, 'dashboard/leaves_cancel.html', {
        'leave_list_cancel': leaves,
        'title': 'Cancel Leave List',
    })


@superuser_required
def reject_leave(request, id):
    leave = get_object_or_404(Leave, id=id)

    # Change the leave status to 'rejected' and set is_approved to False
    leave.status = 'rejected'
    leave.is_approved = False
    leave.save()

    # Get the employee associated with the leave request
    employee = Employee.objects.filter(user=leave.user).first()
    if employee:
        # Send rejection email to the employee
        send_mail(
            'Leave Request Rejected',  # Subject of the email
            f'Hello {employee.firstname},\n\n'
            f'Sorry! Your {leave.leavetype} request from {leave.startdate} to {leave.enddate} has been rejected.\n\n'
            f'Best regards,\nYour Company',  # Email body
            settings.DEFAULT_FROM_EMAIL,  # From email (use the default email set in settings.py)
            [employee.user.email],  # To email (employee's email address)
            fail_silently=False,  # Set to True to suppress errors (for debugging, keep it False)
        )

    # Display a success message mentioning the leave type
    messages.success(
        request,
        f'The {leave.leavetype} leave request for {leave.user.get_full_name()} '
        f'({leave.startdate} - {leave.enddate}) has been rejected, and an email has been sent.',
        extra_tags='alert alert-success alert-dismissible show'
    )

    return redirect('Leave:leavesrejected')


@superuser_required
def leave_rejected_list(request):
    leave = Leave.objects.all_rejected_leaves()

    return render(request, 'dashboard/rejected_leaves_list.html', {
        'leave_list_rejected': leave
    })



@login_required
def leave_balance_view(request):
    try:
        # Check if user has an employee record
        if hasattr(request.user, 'employee'):
            employee = request.user.employee
            leave_balance = LeaveBalance.objects.get(employee=employee)
        else:
            # Allow admin to view all employee leave balances
            if request.user.is_superuser or request.user.is_staff:
                return redirect('admin_leave_dashboard')  # Create an admin view or template

            raise Employee.DoesNotExist  # Force error for non-admin users
    except Employee.DoesNotExist:
        return render(request, 'dashboard/error.html', {'message': 'Employee record not found.'})
    except LeaveBalance.DoesNotExist:
        return render(request, 'dashboard/error.html', {'message': 'Leave balance record not found.'})

    context = {
        'remaining_total_leave': leave_balance.remaining_total_leave,
        'sick_leave': leave_balance.remaining_sick_leave,
        'used_sick_leave': leave_balance.used_sick_leave,
        'annual_leave': leave_balance.remaining_annual_leave,
        'used_annual_leave': leave_balance.used_annual_leave,
        'casual_leave': leave_balance.remaining_casual_leave,
        'used_casual_leave': leave_balance.used_casual_leave,
        'emergency_leave': leave_balance.remaining_emergency_leave,
        'used_emergency_leave': leave_balance.used_emergency_leave,
        'earned_leave': leave_balance.remaining_earned_leave,
        'used_earned_leave': leave_balance.used_earned_leave,
        'loss_of_pay': leave_balance.remaining_loss_of_pay,
        'used_loss_of_pay': leave_balance.used_loss_of_pay,
        'work_from_home': leave_balance.remaining_work_from_home,
        'used_work_from_home': leave_balance.used_work_from_home,
    }

    return render(request, 'dashboard/leave_balance.html', context)


@superuser_required
def uncancel_leave(request, id):
    leave = get_object_or_404(Leave, id=id)

    # Check if the leave is not canceled
    if leave.status != 'cancelled':
        messages.info(request, 'Leave is not canceled, so it cannot be uncanceled.',
                      extra_tags='alert alert-info alert-dismissible show')
        return redirect('Leave:canceleaveslist')

    # Unmark the leave as canceled by changing the status to 'pending'
    leave.status = 'pending'  # You can use another status like 'approved' if necessary
    leave.save()

    # Notify the employee if necessary
    employee = Employee.objects.filter(user=leave.user).first()
    if employee:
        send_mail(
            'Leave Request Uncanceled',
            f'Hello {employee.firstname},\n\nYour leave request cancellation has been reverted.\n\nBest regards,\nYour Company',
            settings.DEFAULT_FROM_EMAIL,
            [employee.user.email],
            fail_silently=False,
        )

    messages.success(request, 'Leave uncanceled successfully.',
                     extra_tags='alert alert-success alert-dismissible show')
    return redirect('Leave:canceleaveslist')


@superuser_required
def unapprove_leave(request, id):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method."}, status=400)

    leave = get_object_or_404(Leave, id=id)

    if leave.status != "approved":
        messages.warning(
            request,
            "Only approved leaves can be unapproved.",
            extra_tags="alert alert-warning alert-dismissible show"
        )
        return redirect("Leave:leavesapprovedlist")

    leave.status = "pending"
    leave.save()

    messages.success(
        request,
        "Leave has been unapproved and is now pending.",
        extra_tags="alert alert-success alert-dismissible show"
    )

    return redirect("Leave:leavesapprovedlist")



@superuser_required
def unreject_leave(request, id):
    leave = get_object_or_404(Leave, id=id)
    leave.status = 'pending'
    leave.is_approved = False
    leave.save()

    messages.success(request, 'Leave is now in pending list',
                     extra_tags='alert alert-success alert-dismissible show')

    return redirect('Leave:leavesrejected')


@login_required
def view_my_leave_table(request):
    user = request.user
    leaves = Leave.objects.filter(user=user)
    employee = Employee.objects.filter(user=user).first()

    return render(request, 'dashboard/staff_leaves_table.html', {
        'leave_list': leaves,
        'employee': employee,
        'title': 'Leaves List'
    })


# Leave CRUD Views
class LeaveListCreateView(generics.ListCreateAPIView):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return leaves for the logged-in user
        return Leave.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Assign the logged-in user to the leave request
        serializer.save(user=self.request.user)


class LeaveRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return leaves for the logged-in user
        return Leave.objects.filter(user=self.request.user)


# LeaveRequest CRUD Views
class LeaveRequestListCreateView(generics.ListCreateAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return leave requests for the logged-in user
        return LeaveRequest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Assign the logged-in user to the leave request
        serializer.save(user=self.request.user)


class LeaveRequestRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return leave requests for the logged-in user
        return LeaveRequest.objects.filter(user=self.request.user)


# Admin-only views for Leave and LeaveRequest
class AdminLeaveListView(generics.ListAPIView):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    permission_classes = [IsAdminUser]


class AdminLeaveRequestListView(generics.ListAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAdminUser]


class AdminApproveLeaveView(generics.UpdateAPIView):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 'approved'
        instance.is_approved = True
        instance.save()
        return Response({'message': 'Leave approved successfully'}, status=status.HTTP_200_OK)


class AdminRejectLeaveView(generics.UpdateAPIView):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 'rejected'
        instance.is_approved = False
        instance.save()
        return Response({'message': 'Leave rejected successfully'}, status=status.HTTP_200_OK)

    @csrf_exempt
    def api_create_leave(request):
        if request.method == 'POST':
            form = LeaveCreationForm(request.POST)
            if form.is_valid():
                leave = form.save(commit=False)
                leave.user = request.user
                leave.save()
                return JsonResponse({'id': leave.id}, status=201)
            else:
                return JsonResponse({'error': form.errors}, status=400)
        return JsonResponse({'error': 'Invalid request method'}, status=405)


# @csrf_exempt
# def unapprove_leave(request, id):
#     if request.method == 'POST':
#         try:
#             leave = Leave.objects.get(id=id)
#             leave.status = 'pending'  # Change status to pending
#             leave.is_approved = False
#             leave.save()
#             return JsonResponse({'success': True})
#         except Leave.DoesNotExist:
#             return JsonResponse({'success': False, 'error': 'Leave request not found.'}, status=404)
#     return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)


# from django.test import TestCase
# from .models import Employee


# class EmployeeTestCase(TestCase):
#     def test_employee_creation(self):
#         employee = Employee.objects.create(user="john_doe", department="IT")
#         self.assertEqual(employee.department, 'IT')
