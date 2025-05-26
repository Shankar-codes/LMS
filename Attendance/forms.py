from django import forms
from .models import Attendance
# from Employee.models import Employee


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'employeeid', 'date', 'time_in', 'time_out', 'total_hours']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time_in': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'time_out': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'total_hours': forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        time_in = cleaned_data.get("time_in")
        time_out = cleaned_data.get("time_out")

        # Validate that time_out is after time_in
        if time_in and time_out and time_out < time_in:
            raise forms.ValidationError("Time out must be after time in.")

        return cleaned_data