from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from Employee.models import Employee  # Adjust this import if necessary


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('unmarked', 'Unmarked'),
        ('present', 'Present'),
        ('leave', 'Leave'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records', null=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    employeeid = models.CharField(max_length=8, null=True, blank=True)
    date = models.DateField()
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)
    total_hours = models.DurationField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.username} - {self.date}"
