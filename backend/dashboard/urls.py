from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path("dashboard/grupo/", views.group_dashboard, name="group_dashboard",),
    path("dashboard/grupo/<int:grupo_id>/", views.group_dashboard_admin, name="group_dashboard_admin"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('faults/', views.faults_admin_view, name='faults'),
    path("telemetry-history/", views.telemetry_history_page, name="telemetry_history_page"),
    path("device-connections/", views.device_connections_page, name="device_connections_page"),
    path('api/hospital-data/', views.hospital_data, name='hospital_data'),
    path('api/all-data/', views.get_all_data, name='get_all_data'),
    path("api/telemetry-history/", views.telemetry_history, name="telemetry_history"),
    path("api/accumulated-history/", views.accumulated_history, name="accumulated_history"),
    path("api/monthly-consumption/", views.monthly_consumption, name="monthly_consumption"),
    path("api/device-connections/", views.device_connections, name="device_connections"),
]