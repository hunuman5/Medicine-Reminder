from django import forms
from .models import MedicineRequest

from django import forms
from .models import MedicineRequest


class MedicineRequestForm(forms.ModelForm):
    scheduled_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label='Scheduled Time'
    )

    class Meta:
        model = MedicineRequest
        exclude = ['doctor', 'staff', 'status', 'created_at']

from django import forms
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    role = forms.ChoiceField(choices=[('doctor', 'Doctor'), ('staff', 'Staff'), ('patient', 'Patient')])
    mobile = forms.CharField(max_length=15, required=True)
    patient_id = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

from .models import Medicine

class MedicineForm(forms.ModelForm):
    time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label='Scheduled Time'
    )

    class Meta:
        model = Medicine
        fields = [
            'medicine_name',
            'dosage',
            'time',
            'patient_name',
            'patient_phone',
            'patient_id',
        ]


