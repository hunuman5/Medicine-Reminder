from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import UserForm, MedicineForm, MedicineRequestForm
from .models import Profile, MedicineRequest
from .utils import send_sms
from datetime import datetime


def home(request):
    return render(request, 'home.html', {'now': datetime.now()})


def register_view(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()
            role = user_form.cleaned_data['role']
            mobile = user_form.cleaned_data['mobile']
            patient_id = user_form.cleaned_data['patient_id']
            Profile.objects.create(user=user, role=role, mobile=mobile, patient_id=patient_id)
            messages.success(request, "Registration successful!")
            return redirect('login')
    else:
        user_form = UserForm()
    return render(request, 'register.html', {'form': user_form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST.get('role')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)

            if role == 'doctor':
                return redirect('doctor_dashboard')
            elif role == 'staff':
                return redirect('staff_dashboard')
            elif role == 'patient':
                try:
                    profile = Profile.objects.get(user=user, role='patient')
                    request.session['patient_id'] = profile.patient_id
                except Profile.DoesNotExist:
                    messages.error(request, "Patient profile not found.")
                    return redirect('login')
                return redirect('patient_dashboard')
            else:
                messages.error(request, 'Invalid role selected.')
                return redirect('login')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')

    return render(request, 'login.html')


@login_required
def doctor_dashboard(request):
    requests_to_approve = MedicineRequest.objects.filter(doctor=request.user).order_by('-created_at')

    if request.method == "POST":
        request_id = request.POST.get("request_id")
        action = request.POST.get("action")

        medicine_request = get_object_or_404(MedicineRequest, id=request_id, doctor=request.user)

        if action == "approve":
            medicine_request.status = "approved"
            medicine_request.save()

            try:
                sms_body = (
                    f"Hello {medicine_request.patient_name}, your medicine '{medicine_request.medicine_name}' "
                    f"has been approved. Please follow the dosage: {medicine_request.dosage}."
                )
                send_sms(f'+91{medicine_request.patient_phone}', sms_body)
            except Exception as e:
                print(f"SMS sending failed: {e}")

            messages.success(request, "Request approved and SMS sent.")
        
        elif action == "decline":
            medicine_request.status = "declined"
            medicine_request.save()
            messages.info(request, "Request declined.")

        return redirect('doctor_dashboard')

    return render(request, 'doctor_dashboard.html', {'requests': requests_to_approve})


@login_required
def staff_dashboard(request):
    selected_patient = None

    if request.method == 'POST':
        form = MedicineRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.staff = request.user
            doctor_id = request.POST.get('doctor_id')
            if doctor_id:
                req.doctor = User.objects.get(id=doctor_id)
            req.save()
            return redirect('staff_dashboard')
    else:
        form = MedicineRequestForm()
        patient_id = request.GET.get('examine_patient')
        if patient_id:
            try:
                selected_patient = User.objects.get(id=patient_id)
            except User.DoesNotExist:
                selected_patient = None

    doctors = User.objects.filter(profile__role='doctor')
    my_requests = MedicineRequest.objects.filter(staff=request.user).order_by('-created_at')
    patients = User.objects.filter(profile__role='patient')

    return render(request, 'staff_dashboard.html', {
        'form': form,
        'requests': my_requests,
        'doctors': doctors,
        'patients': patients,
        'selected_patient': selected_patient
    })


@login_required
def add_medicine_from_request(request, request_id):
    req = get_object_or_404(MedicineRequest, id=request_id, staff=request.user, status='approved')

    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            medicine = form.save(commit=False)
            medicine.added_by = request.user
            medicine.save()
            req.status = 'handled'
            req.save()
            messages.success(request, f"Medicine for {req.patient_name} added successfully.")
            return redirect('staff_dashboard')
    else:
        form = MedicineForm(initial={
            'medicine_name': req.medicine_name,
            'dosage': req.dosage,
            'time': req.scheduled_time,
            'patient_name': req.patient_name,
            'patient_phone': req.patient_phone,
            'patient_id': req.patient_id,
        })

    return render(request, 'add_medicine_from_request.html', {'form': form, 'request_obj': req})


@login_required
def patient_dashboard(request):
    try:
        profile = Profile.objects.get(user=request.user, role='patient')
    except Profile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('login')

    patient_id = profile.patient_id

    medicines = MedicineRequest.objects.filter(
        patient_id=patient_id,
        status='approved'
    ).order_by('scheduled_time')

    return render(request, 'patient_dashboard.html', {
        'medicines': medicines,
        'patient_id': patient_id
    })


def logout_view(request):
    logout(request)
    return redirect('login')
