from apscheduler.schedulers.background import BackgroundScheduler
from django.utils.timezone import localtime
from .models import MedicineRequest
from .utils import send_sms
import atexit

def send_reminder_job():
    now = localtime()  # <-- converts to TIME_ZONE in settings.py
    print("⏰ Running reminder job...")

    upcoming = MedicineRequest.objects.filter(status='approved', sent=False)

    for req in upcoming:
        diff_seconds = (localtime(req.scheduled_time) - now).total_seconds()
        print(f"🔍 Checking {req.patient_name} | Scheduled: {localtime(req.scheduled_time)} | Now: {now} | Diff: {diff_seconds}")

        if 0 <= diff_seconds <= 300:
            try:
                message = (
    f"Hi {req.patient_name}, this is a reminder to take your medicine "
    f"'{req.medicine_name}' as advised by Dr. {req.doctor.first_name}. "
    f"Dosage: {req.dosage}."
)

                if send_sms(f'+91{req.patient_phone}', message):
                    req.sent = True
                    req.save()
                    print(f"✅ SMS sent to {req.patient_name}")
            except Exception as e:
                print(f"❌ SMS failed for {req.patient_name}: {e}")
        else:
            print(f"⏳ Too early or too late for {req.patient_name} (Diff: {diff_seconds})")

# Singleton scheduler
scheduler = BackgroundScheduler()
scheduler_started = False

def start():
    global scheduler_started
    if not scheduler_started:
        scheduler.add_job(send_reminder_job, 'interval', seconds=60)
        scheduler.start()
        scheduler_started = True
        atexit.register(lambda: scheduler.shutdown())
