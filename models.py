from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('staff', 'Staff'),
        ('patient', 'Patient'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    mobile = models.CharField(max_length=15)
    patient_id = models.CharField(max_length=20, blank=True, null=True)  # Only used if role is patient

    def __str__(self):
        return self.user.username


class MedicineSchedule(models.Model):
    patient = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'role': 'patient'})
    added_by = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='added_medicines')
    medicine_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    time = models.TimeField()

    def __str__(self):
        return f"{self.medicine_name} for {self.patient.user.username}"


class Medicine(models.Model):
    patient_name = models.CharField(max_length=100)
    patient_phone = models.CharField(max_length=15)
    patient_id = models.CharField(max_length=50)
    medicine_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    time = models.DateTimeField()
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.patient_name} - {self.medicine_name}"


class MedicineRequest(models.Model):
    patient_name = models.CharField(max_length=100)
    patient_phone = models.CharField(max_length=15)
    patient_id = models.CharField(max_length=50, default='UNKNOWN')
    medicine_name = models.CharField(max_length=100, default='N/A')
    dosage = models.CharField(max_length=100, default='1x')
    scheduled_time = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    doctor = models.ForeignKey(User, related_name='doctor_requests', on_delete=models.CASCADE)
    staff = models.ForeignKey(User, related_name='staff_requests', on_delete=models.CASCADE)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # For SMS notification tracking
    notified = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Request by {self.staff.username} for {self.patient_name} - {self.status}"
