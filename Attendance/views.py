from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Attendance
from django.utils import timezone
from datetime import timedelta
from Employee.models import Employee
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.contrib import messages
from django.db import IntegrityError
from datetime import date
from django.http import HttpResponseForbidden




@login_required
def clock_in(request):
    user = request.user
    employee = get_object_or_404(Employee, user=user)  # Fetch Employee instance

    # Get the exact current time using timezone.now()
    current_time = timezone.now()

    # Check if an attendance record for today already exists
    attendance, created = Attendance.objects.get_or_create(
        user=user,
        employee=employee,
        date=current_time.date(),
        defaults={'time_in': current_time}
    )

    if not created:  # If the record already exists, update time_in if it's empty
        if attendance.time_in is None:
            attendance.time_in = current_time
            attendance.save()
        else:
            return JsonResponse({'error': 'Already checked in'}, status=400)

    return JsonResponse({
        'message': 'Check-in successful',
        'time_in': attendance.time_in.strftime('%Y-%m-%d %H:%M:%S')
    })


@login_required
def clock_out(request):
    user = request.user
    employee = get_object_or_404(Employee, user=user)  # Fetch Employee instance

    # Get the exact current time using timezone.now()
    current_time = timezone.now()

    try:
        attendance = Attendance.objects.get(user=user, employee=employee, date=current_time.date())

        if attendance.time_out is None:
            attendance.time_out = current_time
            attendance.total_hours = attendance.time_out - attendance.time_in
            attendance.save()
        else:
            return JsonResponse({'error': 'Already Check out'}, status=400)

        return JsonResponse(
            {'message': 'Check-out successful', 'time_out': attendance.time_out.strftime('%Y-%m-%d %H:%M:%S')})

    except Attendance.DoesNotExist:
        return JsonResponse({'error': 'No check-in record found for today'}, status=400)


@login_required
def my_attendance(request, employee_id=None):
    user = request.user

    # Get the employee instance associated with the user
    try:
        employee = Employee.objects.get(user=user)
    except Employee.DoesNotExist:
        return HttpResponseForbidden("You are not allowed to view this page.")

    # If no employee_id is provided, use the logged-in user's employee ID
    if employee_id is None:
        employee_id = employee.id

    # Admin Section: View any employee's attendance
    if user.is_staff or user.is_superuser:
        attendance_records = Attendance.objects.filter(employee__id=employee_id).order_by('-date')
    else:
        # Employees can only view their own attendance
        if employee.id != employee_id:
            return HttpResponseForbidden("You are not allowed to view this page.")

        attendance_records = Attendance.objects.filter(employee=employee).order_by('-date')

    return render(request, 'attendance/my_attendance.html', {
        'attendance_records': attendance_records,
        'employee': employee,  # Pass employee object to access employee ID in template
    })


@login_required
def all_attendance_history(request):
    attendance_records = Attendance.objects.select_related('user', 'employee').order_by('-date', 'time_in')
    return render(request, 'attendance/all_attendance_history.html', {'attendance_records': attendance_records})





