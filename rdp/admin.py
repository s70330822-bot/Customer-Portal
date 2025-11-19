from django.contrib import admin

# # Register your models here.
from .models import RDPLog

@admin.register(RDPLog)
class RDPLogAdmin(admin.ModelAdmin):
    list_display = ("event_time", "username", "ip_address", "workstation", "event_id", "received_at")
    list_filter = ("event_id", "username", "ip_address")
    search_fields = ("username", "ip_address", "workstation", "raw_message")
    date_hierarchy = "event_time"
