from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from fractions import Fraction
from datetime import timedelta
from Employee.models import Employee
from datetime import date


class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.user.username} - {self.status}"


# ====================================================================================
class LeaveManager(models.Manager):
    def all_pending_leaves(self):
        """Return all leaves with a status of 'pending'."""
        return self.filter(status='pending')


    def all_approved_leaves(self):
        """Return all approved leaves."""
        return self.filter(status='approved')

    def all_cancelled_leaves(self):
        """Return all cancelled leaves."""
        return self.filter(status='cancelled')

    def all_rejected_leaves(self):
        """Return all rejected leaves."""
        return self.filter(status='rejected')

# ===============================================================================================================================

class Leave(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('full day', 'Full Day'),
        ('half day', 'Half Day'),
    ]

    FULL_DAY_LEAVE_CHOICES = [
        ('sick leave', 'Sick Leave'),
        ('earned leave', 'Earned Leave'),
        ('casual leave', 'Casual Leave'),
        ('loss of pay', 'Loss of Pay'),
        ('work from home', 'Work From Home'),
        ('emergency leave', 'Emergency Leave'),
    ]

    HALF_DAY_SESSION_CHOICES = [
        ('morning session', 'Morning Session'),
        ('afternoon session', 'Afternoon Session'),
    ]

    DEFAULT_LEAVE_DAYS = 25

    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    startdate = models.DateField(verbose_name=_('Start Date'), null=True, blank=False)
    enddate = models.DateField(verbose_name=_('End Date'), null=True, blank=False)
    leavetype = models.CharField(choices=LEAVE_TYPE_CHOICES, max_length=25, default='None', blank=False)
    leave_category = models.CharField(
        max_length=20,
        choices=FULL_DAY_LEAVE_CHOICES + HALF_DAY_SESSION_CHOICES,
        blank=True,
        null=True,
        default='None'
    )
    start_time = models.TimeField(verbose_name=_('Start Time'), null=True, blank=True)
    end_time = models.TimeField(verbose_name=_('End Time'), null=True, blank=True)

    reason = models.CharField(verbose_name=_('Reason for Leave'), max_length=255,
                              help_text='Add additional information for leave', null=True, blank=True)
    defaultdays = models.PositiveIntegerField(verbose_name=_('Leave days per year counter'), default=DEFAULT_LEAVE_DAYS,
                                              null=True, blank=True)
    status = models.CharField(max_length=12, default='pending',
                              choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'),
                                       ('cancelled', 'Cancelled')])
    is_approved = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    half_day = models.BooleanField(default=False)

    objects = LeaveManager()

    class Meta:
        verbose_name = _('Leave')
        verbose_name_plural = _('Leaves')
        ordering = ['-created']

    def __str__(self):
        return f"{self.leavetype} - {self.user.username}"


    @property
    def leave_days(self):
        """Calculates the total number of leave days in fraction format (e.g., 1/2 for half-day)."""
        if self.startdate and self.enddate and self.startdate <= self.enddate:
            days = (
                               self.enddate - self.startdate).days + 1  # Calculate the total number of days between startdate and enddate

            # If it's a one-day leave
            if days == 1:
                if self.leavetype == 'half day':  # For half-day leave, return 1/2
                    return Fraction(1, 2)
                return Fraction(1)  # For full-day leave, return 1

            # For multiple-day leave, if it's a full-day leave, return full days
            if self.leavetype == 'full day':
                return Fraction(days)

            # For half-day leave across multiple days, consider each day as 1/2 day
            if self.leavetype == 'half day':
                return Fraction(days * 1, 2)  # Treat every day as half-day leave (1/2)

        return Fraction(0)  # Invalid date range, return 0 days

    # Other methods (approve_leave, cancel_leave, reject_leave, etc.) remain unchanged
    def approve_leave(self):
        """Approve the leave request and update leave balance/LOP."""
        if not self.is_approved and self.status == 'pending':
            leave_days = self.leave_days
            if leave_days <= self.user.employee.leavebalance.annual_leave:
                self.user.employee.leavebalance.annual_leave -= leave_days
                self.user.employee.leavebalance.used_annual_leave += leave_days
                self.lop_taken = 0
            else:
                extra_days = leave_days - self.user.employee.leavebalance.annual_leave
                self.lop_taken = extra_days
                self.user.employee.leavebalance.annual_leave = 0
                self.user.employee.leavebalance.lop_days += extra_days

            self.user.employee.leavebalance.save()
            self.is_approved = True
            self.status = 'approved'
            self.save()

    def cancel_leave(self):
        """Cancel the leave request."""
        if self.status != 'cancelled':
            self.is_approved = False
            self.status = 'cancelled'
            self.save()

    def reject_leave(self):
        """Reject the leave request."""
        if self.status != 'rejected':
            self.is_approved = False
            self.status = 'rejected'
            self.save()

    @property
    def is_rejected(self):
        """Check if the leave request is rejected."""
        return self.status == 'rejected'



# ===============================================================================
from django.contrib import admin

# class LeaveBalance(models.Model):
#     employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
#
#     # Total Leaves (Fixed as per requirements)
#     TOTAL_LEAVE = 25
#     SICK_LEAVE_LIMIT = 3
#     ANNUAL_LEAVE_LIMIT = 3
#     CASUAL_LEAVE_LIMIT = 3
#     EMERGENCY_LEAVE_LIMIT = 3
#     EARNED_LEAVE_LIMIT = 3
#     LOSS_OF_PAY_LIMIT = 5
#     WORK_FROM_HOME_LIMIT = 5
#
#     # Allocated Leave Types
#     sick_leave = models.IntegerField(default=SICK_LEAVE_LIMIT)
#     annual_leave = models.IntegerField(default=ANNUAL_LEAVE_LIMIT)
#     casual_leave = models.IntegerField(default=CASUAL_LEAVE_LIMIT)
#     emergency_leave = models.IntegerField(default=EMERGENCY_LEAVE_LIMIT)
#     earned_leave = models.IntegerField(default=EARNED_LEAVE_LIMIT)
#     loss_of_pay = models.IntegerField(default=LOSS_OF_PAY_LIMIT)
#     work_from_home = models.IntegerField(default=WORK_FROM_HOME_LIMIT)
#
#     # Used Leaves
#     used_sick_leave = models.IntegerField(default=0)
#     used_annual_leave = models.IntegerField(default=0)
#     used_casual_leave = models.IntegerField(default=0)
#     used_emergency_leave = models.IntegerField(default=0)
#     used_earned_leave = models.IntegerField(default=0)
#     used_loss_of_pay = models.IntegerField(default=0)
#     used_work_from_home = models.IntegerField(default=0)
#
#     @admin.display(description="Remaining LOP Days")  # ✅ Correct way to display in admin
#     def lop_days(self):
#         return self.loss_of_pay - self.used_loss_of_pay
#
#     @property
#     def remaining_total_leave(self):
#         """
#         Calculate remaining total leave.
#         """
#         total_used = (
#             self.used_sick_leave +
#             self.used_annual_leave +
#             self.used_casual_leave +
#             self.used_emergency_leave +
#             self.used_earned_leave +
#             self.used_loss_of_pay +
#             self.used_work_from_home
#         )
#         return self.TOTAL_LEAVE - total_used
#
#     @property
#     def remaining_sick_leave(self):
#         return max(0, self.sick_leave - self.used_sick_leave)
#
#     @property
#     def remaining_annual_leave(self):
#         return max(0, self.annual_leave - self.used_annual_leave)
#
#     @property
#     def remaining_casual_leave(self):
#         return max(0, self.casual_leave - self.used_casual_leave)
#
#     @property
#     def remaining_emergency_leave(self):
#         return max(0, self.emergency_leave - self.used_emergency_leave)
#
#     @property
#     def remaining_earned_leave(self):
#         return max(0, self.earned_leave - self.used_earned_leave)
#
#     @property
#     def remaining_loss_of_pay(self):
#         return max(0, self.loss_of_pay - self.used_loss_of_pay)
#
#     @property
#     def remaining_work_from_home(self):
#         return max(0, self.work_from_home - self.used_work_from_home)
#
#     def take_leave(self, leave_type, days):
#         """
#         Deducts leave from the respective category and updates the leave balance.
#         """
#         if leave_type == "sick_leave":
#             if self.remaining_sick_leave >= days:
#                 self.used_sick_leave += days
#             else:
#                 raise ValueError("Not enough sick leave balance.")
#
#         elif leave_type == "annual_leave":
#             if self.remaining_annual_leave >= days:
#                 self.used_annual_leave += days
#             else:
#                 raise ValueError("Not enough annual leave balance.")
#
#         elif leave_type == "casual_leave":
#             if self.remaining_casual_leave >= days:
#                 self.used_casual_leave += days
#             else:
#                 raise ValueError("Not enough casual leave balance.")
#
#         elif leave_type == "emergency_leave":
#             if self.remaining_emergency_leave >= days:
#                 self.used_emergency_leave += days
#             else:
#                 raise ValueError("Not enough emergency leave balance.")
#
#         elif leave_type == "earned_leave":
#             if self.remaining_earned_leave >= days:
#                 self.used_earned_leave += days
#             else:
#                 raise ValueError("Not enough earned leave balance.")
#
#         elif leave_type == "loss_of_pay":
#             if self.remaining_loss_of_pay >= days:
#                 self.used_loss_of_pay += days
#             else:
#                 raise ValueError("Not enough loss of pay balance.")
#
#         elif leave_type == "work_from_home":
#             if self.remaining_work_from_home >= days:
#                 self.used_work_from_home += days
#             else:
#                 raise ValueError("Not enough work-from-home balance.")
#
#         else:
#             raise ValueError("Invalid leave type.")
#
#         self.save()  # Save updated leave balance



from django.db import models
from django.contrib import admin

class LeaveBalance(models.Model):
    employee = models.OneToOneField("Employee.Employee", on_delete=models.CASCADE)

    # Leave Type Limits (Constants)
    LEAVE_LIMITS = {
        "sick_leave": 3,
        "annual_leave": 3,
        "casual_leave": 3,
        # "medical_leave": 5,
        "emergency_leave": 3,
        "earned_leave": 3,
        "loss_of_pay": 5,
        "work_from_home": 5,
    }

    # Allocated Leave Types (Dynamically set based on the limits)
    sick_leave = models.IntegerField(default=LEAVE_LIMITS["sick_leave"])
    annual_leave = models.IntegerField(default=LEAVE_LIMITS["annual_leave"])
    casual_leave = models.IntegerField(default=LEAVE_LIMITS["casual_leave"])
    emergency_leave = models.IntegerField(default=LEAVE_LIMITS["emergency_leave"])
    # medical_leave = models.IntegerField(default=LEAVE_LIMITS["medical_leave"])  # Corrected from emergency_leave
    earned_leave = models.IntegerField(default=LEAVE_LIMITS["earned_leave"])
    loss_of_pay = models.IntegerField(default=LEAVE_LIMITS["loss_of_pay"])
    work_from_home = models.IntegerField(default=LEAVE_LIMITS["work_from_home"])

    # Used Leaves
    used_sick_leave = models.IntegerField(default=0)
    used_annual_leave = models.IntegerField(default=0)
    used_casual_leave = models.IntegerField(default=0)
    used_emergency_leave = models.IntegerField(default=0)
    # used_medical_leave = models.IntegerField(default=0)
    used_earned_leave = models.IntegerField(default=0)
    used_loss_of_pay = models.IntegerField(default=0)
    used_work_from_home = models.IntegerField(default=0)

    @admin.display(description="Remaining LOP Days")
    def lop_days(self):
        return self.loss_of_pay - self.used_loss_of_pay

    @property
    def total_allocated_leave(self):
        """Dynamically calculate total allocated leave."""
        return sum(self.LEAVE_LIMITS.values())

    @property
    def total_used_leave(self):
        """Sum of all used leaves."""
        return (
            self.used_sick_leave + self.used_annual_leave + self.used_casual_leave +
            self.used_emergency_leave + self.used_earned_leave +
            self.used_loss_of_pay + self.used_work_from_home
        )

    @property
    def remaining_total_leave(self):
        """Dynamically calculate remaining total leave."""
        return max(0, self.total_allocated_leave - self.total_used_leave)

    @property
    def remaining_sick_leave(self):
        return max(0, self.sick_leave - self.used_sick_leave)

    @property
    def remaining_annual_leave(self):
        return max(0, self.annual_leave - self.used_annual_leave)

    @property
    def remaining_casual_leave(self):
        return max(0, self.casual_leave - self.used_casual_leave)

    @property
    def remaining_emergency_leave(self):
        return max(0, self.emergency_leave - self.used_emergency_leave)

    @property
    def remaining_earned_leave(self):
        return max(0, self.earned_leave - self.used_earned_leave)

    # @property
    # def remaining_medical_leave(self):
    #     return max(0, self.medical_leave - self.used_medical_leave)  # Fixed calculation

    @property
    def remaining_loss_of_pay(self):
        return max(0, self.loss_of_pay - self.used_loss_of_pay)

    @property
    def remaining_work_from_home(self):
        return max(0, self.work_from_home - self.used_work_from_home)

    # Generic method for remaining leave per type
    def get_remaining_leave(self, leave_type):
        if leave_type in self.LEAVE_LIMITS:
            allocated = getattr(self, leave_type, 0)
            used = getattr(self, f"used_{leave_type}", 0)
            return max(0, allocated - used)
        return 0

    # Generic method to apply leave
    def take_leave(self, leave_type, days):
        """Deducts leave from the respective category and updates the balance."""
        if leave_type not in self.LEAVE_LIMITS:
            raise ValueError("Invalid leave type.")

        remaining = self.get_remaining_leave(leave_type)

        if days > remaining:
            raise ValueError(f"Not enough {leave_type.replace('_', ' ')} balance. You have {remaining} days left.")

        # Update the used leave for the specified leave type
        used_field = f"used_{leave_type}"
        current_used = getattr(self, used_field, 0)
        setattr(self, used_field, current_used + days)

        self.save()  # Save updated leave balance

    def __str__(self):
        return f"{self.employee} - Remaining Leaves: {self.remaining_total_leave}"
