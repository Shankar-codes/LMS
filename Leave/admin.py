from django.contrib import admin
from .models import LeaveBalance, Leave  # Ensure correct imports

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'sick_leave', 'annual_leave', 'casual_leave', 'lop_days']  # ✅ This now works

admin.site.register(Leave)  # Ensure Leave model is also registered properly
