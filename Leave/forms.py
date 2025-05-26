from django import forms
from .models import Leave


class LeaveCreationForm(forms.ModelForm):
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 40, 'placeholder': 'Enter reason for leave...'})
    )

    start_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time'})
    )

    end_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time'})
    )

    class Meta:
        model = Leave
        exclude = ['user', 'defaultdays', 'status', 'is_approved', 'updated', 'created']
        widgets = {
            'startdate': forms.DateInput(attrs={'type': 'date'}),
            'enddate': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        startdate = cleaned_data.get('startdate')
        enddate = cleaned_data.get('enddate')
        leavetype = cleaned_data.get('leavetype')
        leave_category = cleaned_data.get('leave_category')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        print(
            f"DEBUG: Start Date - {startdate}, End Date - {enddate}, Leave Type - {leavetype}, Leave Category - {leave_category}, Start Time - {start_time}, End Time - {end_time}")

        # Validate start and end dates
        if not startdate:
            raise forms.ValidationError("Start date is required.")
        if not enddate:
            raise forms.ValidationError("End date is required.")
        if startdate > enddate:
            raise forms.ValidationError("Start date cannot be after end date.")

        # Validate leave type
        if not leavetype:
            raise forms.ValidationError("Please select a leave type.")

        # Validate half-day leave
        if leavetype == 'half day':
            if startdate != enddate:
                raise forms.ValidationError("For half-day leave, start and end date must be the same.")
            if not leave_category or leave_category not in ['morning session', 'afternoon session']:
                raise forms.ValidationError("Please select a valid session (morning or afternoon) for half-day leave.")

            # Ensure start_time and end_time are provided and valid
            if not start_time:
                raise forms.ValidationError("Please provide a valid start time for half-day leave.")
            if not end_time:
                raise forms.ValidationError("Please provide a valid end time for half-day leave.")
            if start_time >= end_time:
                raise forms.ValidationError("Start time must be before end time.")

        # Validate full-day leave
        if leavetype == 'full day':
            if leave_category not in ['sick leave', 'earned leave', 'casual leave', 'loss of pay', 'work from home',
                                      'emergency leave']:
                raise forms.ValidationError("Please select a valid leave category for full-day leave.")
            if start_time or end_time:
                raise forms.ValidationError("Start and end times are not required for full-day leave.")

        return cleaned_data