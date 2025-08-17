from django.apps import AppConfig

class MedicineReminderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'medicine_reminder'

    def ready(self):
        from . import scheduler
        scheduler.start()

