from django.contrib import admin
from api import models

# Register your models here.

admin.site.register(models.SensorMonitor)
admin.site.register(models.ActuatorMonitor)