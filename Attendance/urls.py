from django.urls import path
from . import views

app_name = 'attendance'
urlpatterns = [
    path('my_attendance/my/<int:employee_id>/', views.my_attendance, name='my_attendance'),
    path('clock_in/', views.clock_in, name='clock_in'),
    path('clock_out/', views.clock_out, name='clock_out'),
    path('my-attendance/', views.all_attendance_history, name='all_attendance_history'),

]


