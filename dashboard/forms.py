from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox


import re

PHONE_RE = re.compile(r'^[6-9]\d{9}$')

def validate_indian_phone(value):
    if not PHONE_RE.match(value):
        raise forms.ValidationError("Enter valid 10 digit Indian phone starting with 6-9.")

def validate_strong_password(pw):
    # at least 8 chars, uppercase, lowercase, digit, special
    import re
    if len(pw) < 8:
        raise forms.ValidationError("Password must be at least 8 characters.")
    if not re.search(r'[A-Z]', pw):
        raise forms.ValidationError("Password must contain an uppercase letter.")
    if not re.search(r'[a-z]', pw):
        raise forms.ValidationError("Password must contain a lowercase letter.")
    if not re.search(r'\d', pw):
        raise forms.ValidationError("Password must contain a digit.")
    if not re.search(r'[^A-Za-z0-9]', pw):
        raise forms.ValidationError("Password must contain a special character.")

class RegisterForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Full Name"})
    )
    company = forms.CharField(
        max_length=200, required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Company"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
    )
    phone = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm Password"})
    )


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter registered email"
        })
    )

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Enter 6-digit OTP"
        })
    )

class LoginForm(forms.Form):
    userid_or_email = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "User ID or Email"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Password"
        })
    )

    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox(attrs={"class": "mb-3"})
    )

    def clean(self):
        cleaned = super().clean()
        return cleaned

