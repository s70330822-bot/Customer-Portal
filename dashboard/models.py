from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random, os, string


def generate_userid(length=8):
    while True:
        uid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if not Profile.objects.filter(userid=uid).exists():
            return uid


def profile_pic_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.userid}_profile.{ext}"
    return os.path.join("profile_pics", filename)


class Profile(models.Model):
    # 🔥----- USER BASIC DETAILS -----
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    userid = models.CharField(max_length=12, unique=True, blank=True)
    company = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    
    # OTP Verification
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True)
    otp_created = models.DateTimeField(null=True, blank=True)

    # Profile Pic
    profile_pic = models.ImageField(upload_to=profile_pic_upload_path, null=True, blank=True)

    # 🔥----- ACCOUNT DETAILS -----
    current_plan = models.CharField(max_length=100, blank=True)
    account_status = models.CharField(max_length=50, blank=True)

    # 🔥----- SUBSCRIPTION DETAILS -----
    plan_name = models.CharField(max_length=150, blank=True)
    number_of_users = models.IntegerField(null=True, blank=True)
    duration = models.CharField(max_length=50, blank=True)  
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # ---------------------------------------------------
    # METHODS
    # ---------------------------------------------------

    def save(self, *args, **kwargs):
        if not self.userid:
            self.userid = generate_userid()
        super().save(*args, **kwargs)

    def generate_otp(self):
        code = f"{random.randint(0, 999999):06d}"
        self.otp = code
        self.otp_created = timezone.now()
        self.save()
        return code

    def otp_is_valid(self, code, expiry_seconds=600):
        if not self.otp or not self.otp_created:
            return False
        if self.otp != code:
            return False
        return (timezone.now() - self.otp_created).total_seconds() <= expiry_seconds

    def clear_otp(self):
        self.otp = ''
        self.otp_created = None
        self.save()

    def __str__(self):
        return f"{self.user.email} / {self.userid}"
