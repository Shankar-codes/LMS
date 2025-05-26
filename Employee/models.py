# import datetime
# from django.db import models
# from django.utils.translation import gettext as _
# from django.contrib.auth.models import User
# from django.core.exceptions import ValidationError
# from Employee.utility import code_format
# # from .models import Department, Role
#
# class EmployeeManager(models.Manager):
#     def all_blocked_employees(self):
#         return self.filter(is_blocked=True)
#
#     def all_approved_leaves(self):
#         """Return all leaves with a status of 'approved'."""
#         return self.filter(status='approved')  # Ensure this returns a QuerySet
#
#
#
# class Role(models.Model):
#     department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="roles", null=True, blank=True)
#     name = models.CharField(max_length=125)
#     description = models.CharField(max_length=125, null=True, blank=True)
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         ordering = ['name']
#
#     def __str__(self):
#         return self.name
#
#
# class Department(models.Model):
#     name = models.CharField(max_length=125)
#     description = models.CharField(max_length=125, null=True, blank=True)
#
#     created = models.DateTimeField(verbose_name=_('Created'), auto_now_add=True)
#     updated = models.DateTimeField(verbose_name=_('Updated'), auto_now=True)
#
#     class Meta:
#         verbose_name = _('Department')
#         verbose_name_plural = _('Departments')
#         ordering = ['name', 'created']
#
#     def __str__(self):
#         return self.name
#
#
# class Employee(models.Model):
#     MALE = 'male'
#     FEMALE = 'female'
#     OTHER = 'other'
#     NOT_KNOWN = 'Not Known'
#
#     GENDER = (
#         (MALE, 'Male'),
#         (FEMALE, 'Female'),
#         (OTHER, 'Other'),
#         (NOT_KNOWN, 'Not Known'),
#     )
#
#     FULL_TIME = 'Full-Time'
#     PART_TIME = 'Part-Time'
#     CONTRACT = 'Contract'
#     INTERN = 'Intern'
#
#     EMPLOYEETYPE = (
#         (FULL_TIME, 'Full-Time'),
#         (PART_TIME, 'Part-Time'),
#         (CONTRACT, 'Contract'),
#         (INTERN, 'Intern'),
#     )
#
#     # PERSONAL DATA
#
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
#     image = models.FileField(
#         _('Profile Image'),
#         upload_to='profiles',
#         default='profiles/default.png',
#         blank=True,
#         null=True,
#         help_text='Upload image size less than 2.0MB'
#     )
#     firstname = models.CharField(_('Firstname'), max_length=125, null=False, blank=False)
#     lastname = models.CharField(_('Lastname'), max_length=125, null=False, blank=False)
#     email = models.EmailField(default="default@example.com")
#     date_of_birth = models.DateField(
#         null=True,
#         blank=True,
#         help_text="Enter date of birth in YYYY-MM-DD format"
#     )
#     gender = models.CharField(
#         _('Gender'),
#         max_length=15,
#         choices=GENDER,
#         default=NOT_KNOWN
#     )  # Added gender field
#     location = models.CharField(max_length=255, null=True, blank=True)
#     address = models.TextField(blank=True, max_length=500)
#     phone_number = models.CharField(max_length=15, blank=True)
#     Department = models.ForeignKey(
#         Department,
#         verbose_name=_('Department'),
#         on_delete=models.SET_NULL,
#         null=True
#     )
#     role = models.ForeignKey(
#         Role,
#         verbose_name=_('Role'),
#         on_delete=models.SET_NULL,
#         null=True,
#         default=None
#     )
#
#     employeetype = models.CharField(
#         _('Employee Type'),
#         max_length=15,
#         default=FULL_TIME,
#         choices=EMPLOYEETYPE,
#         blank=False,
#         null=True
#     )
#     employeeid = models.CharField(_('Employee ID Number'), max_length=8, null=True, blank=True)
#
#     def clean(self):
#         """Custom validation for employee ID format."""
#         super().clean()
#
#     dateissued = models.DateField(
#         _('Date Issued'),
#         help_text='Date staff ID was issued',
#         blank=False,
#         null=True
#     )
#     Degree = models.CharField(max_length=255, null=True, blank=True)
#
#
#     # App related
#     is_blocked = models.BooleanField(
#         _('Is Blocked'),
#         help_text='Toggle employee block/unblock',
#         default=False
#     )
#     is_deleted = models.BooleanField(
#         _('Is Deleted'),
#         help_text='Toggle employee delete/undelete',
#         default=False
#     )
#
#     created = models.DateTimeField(verbose_name=_('Created'), auto_now_add=True, null=True)
#     updated = models.DateTimeField(verbose_name=_('Updated'), auto_now=True, null=True)
#     objects = EmployeeManager()
#
#     def __str__(self):
#         return self.name
#
#     def calculate_deduction(self, total_leaves):
#         """Calculate salary deduction based on leaves."""
#         return total_leaves * self.leave_deduction_rate
#
#
#
#     class Meta:
#         verbose_name = _('Employee')
#         verbose_name_plural = _('Employees')
#         ordering = ['-created']
#
#     def __str__(self):
#         return self.get_full_name or 'Employee'
#
#     @property
#     def get_full_name(self):
#         parts = [self.firstname, self.lastname]
#         return " ".join(part for part in parts if part).strip()
#
#     @property
#     def get_age(self):
#         if self.date_of_birth:
#             today = datetime.date.today()
#             return (
#                 today.year - self.date_of_birth.year -
#                 ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
#             )
#         return None  # Return None if no `date_of_birth` is set
#
#     @property
#     def get_gender_display(self):
#         return dict(self.GENDER).get(self.gender, 'Not Known')
#
#     def clean(self):
#         # Check if the date of birth is in the future
#         if self.date_of_birth and self.date_of_birth >= datetime.date.today():
#             raise ValidationError("Date of birth cannot be in the future.")
#
#         # Increase file size limit to 5MB and handle missing image files
#         if self.image:
#             try:
#                 if self.image.size > 10 * 1024 * 1024:  # 10mb size limit
#                     raise ValidationError("Profile image must be less than 5MB.")
#             except FileNotFoundError:
#                 # Handle the case where the image file does not exist
#                 raise ValidationError("Image file is missing.")
#
#         super().clean()
#
#     def save(self, *args, **kwargs):
#         '''
#         Override the save method to format employee_id
#         '''
#         if self.employeeid:
#             self.employeeid = code_format(self.employeeid)
#         super().save(*args, **kwargs)
#
#
# class LeaveRecord(models.Model):
#     employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
#     date = models.DateField()
#     reason = models.TextField(blank=True, null=True)
#     is_approved = models.BooleanField(default=False)


import datetime
from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from Employee.utility import code_format


# Department Model (Defined before Role to avoid Reference Issues)
class Department(models.Model):
    name = models.CharField(max_length=125)
    description = models.CharField(max_length=125, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')
        ordering = ['name', 'created']

    def __str__(self):
        return self.name


# Role Model
class Role(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="roles", null=True, blank=True)
    name = models.CharField(max_length=125)
    description = models.CharField(max_length=125, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name



# Employee Manager
class EmployeeManager(models.Manager):
    def all_blocked_employees(self):
        return self.filter(is_blocked=True)

    def all_approved_leaves(self):
        """Return all leaves with a status of 'approved'."""
        return self.filter(status='approved')


# Employee Model
# class Employee(models.Model):
#     MALE = 'male'
#     FEMALE = 'female'
#     OTHER = 'other'
#     NOT_KNOWN = 'Not Known'
#
#     GENDER = (
#         (MALE, 'Male'),
#         (FEMALE, 'Female'),
#         (OTHER, 'Other'),
#         (NOT_KNOWN, 'Not Known'),
#     )
#
#     FULL_TIME = 'Full-Time'
#     PART_TIME = 'Part-Time'
#     CONTRACT = 'Contract'
#     INTERN = 'Intern'
#
#     EMPLOYEETYPE = (
#         (FULL_TIME, 'Full-Time'),
#         (PART_TIME, 'Part-Time'),
#         (CONTRACT, 'Contract'),
#         (INTERN, 'Intern'),
#     )
#
#     # PERSONAL DATA
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
#     image = models.FileField(
#         _('Profile Image'),
#         upload_to='profiles',
#         default='profiles/default.png',
#         blank=True,
#         null=True,
#         help_text='Upload image size less than 2.0MB'
#     )
#     firstname = models.CharField(_('Firstname'), max_length=125)
#     lastname = models.CharField(_('Lastname'), max_length=125)
#     email = models.EmailField(default="default@example.com")
#     date_of_birth = models.DateField(null=True, blank=True, help_text="Enter date of birth in YYYY-MM-DD format")
#     gender = models.CharField(_('Gender'), max_length=15, choices=GENDER, default=NOT_KNOWN)
#     location = models.CharField(max_length=255, null=True, blank=True)
#     address = models.TextField(blank=True, max_length=500)
#     phone_number = models.CharField(max_length=15, blank=True)
#
#     department = models.ForeignKey("Department", verbose_name=_('Department'), on_delete=models.SET_NULL, null=True)
#     role = models.ForeignKey("Role", verbose_name=_('Role'), on_delete=models.SET_NULL, null=True, default=None)
#
#     employeetype = models.CharField(_('Employee Type'), max_length=15, default=FULL_TIME, choices=EMPLOYEETYPE)
#     employeeid = models.CharField(_('Employee ID Number'), max_length=8, null=True, blank=True)
#
#     dateissued = models.DateField(_('Date Issued'), help_text='Date staff ID was issued', null=True)
#     degree = models.CharField(max_length=255, null=True, blank=True)
#
#     # App related
#     is_blocked = models.BooleanField(default=False)
#     is_deleted = models.BooleanField(default=False)  # Ensure this exists
#
#     created = models.DateTimeField(auto_now_add=True, null=True)
#     updated = models.DateTimeField(auto_now=True, null=True)
#
#     objects = EmployeeManager()
#
#     class Meta:
#         verbose_name = _('Employee')
#         verbose_name_plural = _('Employees')
#         ordering = ['-created']
#
#     def __str__(self):
#         return self.get_full_name or 'Employee'
#
#     @property
#     def get_full_name(self):
#         return f"{self.firstname} {self.lastname}".strip()
#
#     @property
#     def get_age(self):
#         if self.date_of_birth:
#             today = datetime.date.today()
#             return (
#                 today.year - self.date_of_birth.year -
#                 ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
#             )
#         return None  # Return None if no `date_of_birth` is set
#
#     @property
#     def get_gender_display(self):
#         return dict(self.GENDER).get(self.gender, 'Not Known')
#
#     def clean(self):
#         """Validation: Date of Birth & Image Size"""
#         if self.date_of_birth and self.date_of_birth >= datetime.date.today():
#             raise ValidationError("Date of birth cannot be in the future.")
#
#         if self.image:
#             try:
#                 if self.image.size > 5 * 1024 * 1024:  # 5MB size limit
#                     raise ValidationError("Profile image must be less than 5MB.")
#             except FileNotFoundError:
#                 raise ValidationError("Image file is missing.")
#
#         super().clean()
#
#     def save(self, *args, **kwargs):
#         """Format Employee ID"""
#         if self.employeeid:
#             self.employeeid = code_format(self.employeeid)
#         super().save(*args, **kwargs)

class Employee(models.Model):
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'
    NOT_KNOWN = 'Not Known'

    GENDER = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other'),
        (NOT_KNOWN, 'Not Known'),
    )

    FULL_TIME = 'Full-Time'
    PART_TIME = 'Part-Time'
    CONTRACT = 'Contract'
    INTERN = 'Intern'

    EMPLOYEETYPE = (
        (FULL_TIME, 'Full-Time'),
        (PART_TIME, 'Part-Time'),
        (CONTRACT, 'Contract'),
        (INTERN, 'Intern'),
    )

    # PERSONAL DATA
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    image = models.FileField(
        _('Profile Image'),
        upload_to='profiles',
        default='profiles/default.png',
        blank=True,
        null=True,
        help_text='Upload image size less than 2.0MB'
    )
    firstname = models.CharField(_('Firstname'), max_length=125)
    lastname = models.CharField(_('Lastname'), max_length=125)
    email = models.EmailField(default="default@example.com")
    date_of_birth = models.DateField(null=True, blank=True, help_text="Enter date of birth in YYYY-MM-DD format")
    gender = models.CharField(_('Gender'), max_length=15, choices=GENDER, default=NOT_KNOWN)
    location = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(blank=True, max_length=500)
    phone_number = models.CharField(max_length=15, blank=True)

    department = models.ForeignKey("Department", verbose_name=_('Department'), on_delete=models.SET_NULL, null=True)
    role = models.ForeignKey("Role", verbose_name=_('Role'), on_delete=models.SET_NULL, null=True, default=None)

    employeetype = models.CharField(_('Employee Type'), max_length=15, default=FULL_TIME, choices=EMPLOYEETYPE)
    employeeid = models.CharField(_('Employee ID Number'), max_length=8, null=True, blank=True)

    dateissued = models.DateField(_('Date Issued'), help_text='Date staff ID was issued', null=True)
    degree = models.CharField(max_length=255, null=True, blank=True)

    # App related
    is_blocked = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)  # Ensure this exists

    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    objects = EmployeeManager() # Attach the new manager here

    class Meta:
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')
        ordering = ['-created']

    def __str__(self):
        return self.get_full_name or 'Employee'

    @property
    def get_full_name(self):
        return f"{self.firstname} {self.lastname}".strip()

    @property
    def get_age(self):
        if self.date_of_birth:
            today = datetime.date.today()
            return (
                today.year - self.date_of_birth.year -
                ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            )
        return None  # Return None if no `date_of_birth` is set

    @property
    def get_gender_display(self):
        return dict(self.GENDER).get(self.gender, 'Not Known')

    def clean(self):
        """Validation: Date of Birth & Image Size"""
        if self.date_of_birth and self.date_of_birth >= datetime.date.today():
            raise ValidationError("Date of birth cannot be in the future.")

        if self.image:
            try:
                if self.image.size > 5 * 1024 * 1024:  # 5MB size limit
                    raise ValidationError("Profile image must be less than 5MB.")
            except FileNotFoundError:
                raise ValidationError("Image file is missing.")

        super().clean()

    def save(self, *args, **kwargs):
        """Format Employee ID"""
        if self.employeeid:
            self.employeeid = code_format(self.employeeid)
        super().save(*args, **kwargs)

# Leave Record Model
class LeaveRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    reason = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Leave for {self.employee.get_full_name} on {self.date}"



# Custom QuerySet for soft delete filtering
# class EmployeeQuerySet(models.QuerySet):
#     def active(self):
#         return self.filter(is_deleted=False)  # Get only active employees
#
#     def deleted_users(self):
#         return self.filter(is_deleted=True)  # Get only deleted users
#
#     def blocked_users(self):
#         return self.filter(is_blocked=True)  # Get only blocked users




# class EmployeeManager(models.Manager):
#     def get_queryset(self):
#         '''
#         Employee.objects.all() -> returns only active employees ie.is_deleted = False
#         '''
#         return super().get_queryset().filter(is_deleted=False)
#
#     def active(self):
#         return self.get_queryset().active()
#
#     def all_employees(self):
#         '''
#         Employee.objects.all_employee() -> returns all employees including deleted one's
#         NB: don't specify filter. ***
#         '''
#         return super().get_queryset()
#
#     def all_blocked_employees(self):
#         '''
#         Employee.objects.all_blocked_employees() -> returns list of blocked employees ie.is_blocked = True
#         '''
#         return super().get_queryset().filter(is_blocked=True)
#
#     def deleted_users(self):
#         return super().get_queryset().filter(is_deleted=True)


# class EmployeeManager(models.Manager):
#     def get_queryset(self):
#         return EmployeeQuerySet(self.model, using=self._db)  # Attach QuerySet
#
#     def active(self):
#         return self.get_queryset().active()
#
#     def deleted_users(self):
#         return self.get_queryset().deleted_users()
#
#     def blocked_users(self):
#         return self.get_queryset().blocked_users()

class EmployeeQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False)

    def deleted_users(self):
        return self.filter(is_deleted=True)

    def blocked_users(self):
        return self.filter(is_blocked=True)


# Custom Manager
class EmployeeManager(models.Manager):
    def get_queryset(self):
        return EmployeeQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def deleted_users(self):
        return self.get_queryset().deleted_users()

    def blocked_users(self):
        return self.get_queryset().blocked_users()
