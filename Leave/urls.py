from django.urls import path, include
from . import views
from .views import LeaveRequestCreateView

app_name = 'Leave'

urlpatterns = [
    path('leaves/list/', views.leaves_list, name='leaveslist'),
    path('leave/apply/', views.leave_creation, name='createleave'),
    path('leaves/pending/all/', views.leaves_list, name='leaveslist'),
    path('leaves/approved/', views.leaves_approved_list, name='leavesapprovedlist'),
    path('leaves/cancel/all/', views.cancel_leaves_list, name='canceleaveslist'),
    path('leaves/all/view/<int:id>/', views.leaves_view, name='userleaveview'),
    path('leaves/view/table/', views.view_my_leave_table, name='staffleavetable'),
    path('leave/approved/<int:id>/', views.approve_leave, name='userleaveapprove'),
    path('leave/unapprove/<int:id>/', views.unapprove_leave, name='userleaveunapprove'),
    path('leave/cancel/<int:id>/', views.cancel_leave, name='userleavecancel'),
    path('leave/uncancel/<int:id>/', views.uncancel_leave, name='userleaveuncancel'),
    path('leaves/rejected/all/', views.leave_rejected_list, name='leavesrejected'),
    path('leave/reject/<int:id>/', views.reject_leave, name='reject'),
    path('leave/unreject/<int:id>/', views.unreject_leave, name='unreject'),
    path('leave-balance/', views.leave_balance_view, name='leave_balance'),
    path('api/leaves/create/', views.api_create_leave, name='api_create_leave'),
    path('api/leave-request/', LeaveRequestCreateView.as_view(), name='createleave-api'),
    path('api/leaves/<int:id>/', views.api_leave_details, name='api_leave_details'),
    path('api/leaves/<int:id>/approve/', views.api_approve_leave, name='api_approve_leave'),
    path('api/leaves/<int:id>/reject/', views.api_reject_leave, name='api_reject_leave'),
    
    # path('leaves/approved/', views.approvedleaves, name='approvedleaves'),

    # Leave URLs
    path('leaves/', views.LeaveListCreateView.as_view(), name='leave-list-create'),
    path('leaves/<int:pk>/', views.LeaveRetrieveUpdateDestroyView.as_view(), name='leave-retrieve-update-destroy'),
    
    # LeaveRequest URLs
    path('leave-requests/', views.LeaveRequestListCreateView.as_view(), name='leave-request-list-create'),
    path('leave-requests/<int:pk>/', views.LeaveRequestRetrieveUpdateDestroyView.as_view(),
         name='leave-request-retrieve-update-destroy'),

    # Admin URLs
    path('admin/leaves/', views.AdminLeaveListView.as_view(), name='admin-leave-list'),
    path('admin/leave-requests/', views.AdminLeaveRequestListView.as_view(), name='admin-leave-request-list'),
    path('admin/leaves/<int:pk>/approve/', views.AdminApproveLeaveView.as_view(), name='admin-approve-leave'),
    path('admin/leaves/<int:pk>/reject/', views.AdminRejectLeaveView.as_view(), name='admin-reject-leave'),
    
    # path('leave/unapprove/<int:id>/', views.unapprove_leave, name='unapprove_leave'),

]
