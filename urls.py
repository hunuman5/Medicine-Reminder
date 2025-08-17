from django.urls import path
from .views import (
    home, login_view, register_view, logout_view,
    doctor_dashboard, staff_dashboard, patient_dashboard,
    add_medicine_from_request
)

urlpatterns = [
    # Public pages
    path('', home, name='home'),  # ✅ Home page with Login/Register options
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),

    # Dashboards
    path('doctor-dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('staff-dashboard/', staff_dashboard, name='staff_dashboard'),
    path('patient-dashboard/', patient_dashboard, name='patient_dashboard'),

    # Staff actions
    path('staff/add-medicine/<int:request_id>/', add_medicine_from_request, name='add_medicine_from_request'),
]

