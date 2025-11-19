
from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "userid",
        "company",
        "phone",
        "current_plan",
        "account_status",
        "plan_name",
        "start_date",
        "end_date",
    )
    
    search_fields = ("user__email", "userid", "company", "phone")
    list_filter = ("current_plan", "account_status")
