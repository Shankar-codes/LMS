# from logging import PlaceHolder
# from django import forms
# from Employee.models import Employee
# from django.core.exceptions import ValidationError
#
#
# class EmployeeCreateForm(forms.ModelForm):
#     employeeid = forms.CharField(
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Please enter your ID',
#             'class': 'form-control',
#         }),
#         max_length=8,
#         help_text="Employee ID must be exactly 8 characters long."
#     )
#
#     image = forms.ImageField(
#         required=False,
#         widget=forms.FileInput(attrs={
#             'onchange': 'previewImage(this);',
#             'class': 'form-control-file',
#         }),
#         help_text="Upload an image for the employee (optional)."
#     )
#
#     Degree = forms.CharField(  # Changed this line to CharField
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Enter Your Degree ',
#         }),
#         max_length=100,  # Set a maximum length for the institution name
#         help_text="Enter your degree."
#     )
#
#     class Meta:
#         model = Employee
#         fields = ['employeeid', 'image', 'Degree','date_of_joining']
#
#
#     class Meta:
#         model = Employee
#         exclude = ['is_blocked', 'is_deleted', 'created', 'updated', 'date_of_joining']
#         widgets = {
#
#             'date_of_birth': forms.DateInput(attrs={
#                 'type': 'date',
#                 'class': 'form-control',
#             }),
#
#         }

    # def clean_employeeid(self):
    #     employeeid = self.cleaned_data.get('employeeid')
    #
    #     # Ensure the length is exactly 8 characters
    #     if len(employeeid) != 8:
    #         raise ValidationError("Employee ID must be exactly 8 characters.")
    #
    #     # Ensure the employeeid contains only numeric values
    #     if not employeeid.isdigit():
    #         raise ValidationError("Employee ID must contain only numbers.")
    #
    #     return employeeid
from django import forms
from Employee.models import Employee

class EmployeeCreateForm(forms.ModelForm):
    employeeid = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Please enter your ID',
            'class': 'form-control',
        }),
        max_length=8,
        help_text="Employee ID must be exactly 8 characters long."
    )

    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'onchange': 'previewImage(this);',
            'class': 'form-control-file',
        }),
        help_text="Upload an image for the employee (optional)."
    )

    degree = forms.CharField(  # Fixed field name
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Your Degree',
        }),
        max_length=100,
        help_text="Enter your degree."
    )

    class Meta:
        model = Employee
        exclude = ['is_blocked', 'is_deleted', 'created', 'updated']  # Removed 'date_of_joining'
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
        }

        def __init__(self, *args, **kwargs):
            super( self).__init__(*args, **kwargs)
            self.fields['role'].queryset = Role.objects.none()  # Initially empty

            if 'department' in self.data:
                try:
                    department_id = int(self.data.get('department'))
                    self.fields['role'].queryset = Role.objects.filter(department_id=department_id).order_by('name')
                except (ValueError, TypeError):
                    pass
            elif self.instance.pk:
                self.fields['role'].queryset = self.instance.department.roles.order_by('name')
