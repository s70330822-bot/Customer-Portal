from django.shortcuts import render, redirect
from .forms import (
    RegisterForm, 
    LoginForm, 
    ForgotPasswordForm, 
    OTPVerificationForm,
)
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from .models import Profile
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required

# ---------------- Dashboard pages ----------------

def dashboard(request):
    return render(request, "dashboard/dashboard.html")

def invoices(request):
    return render(request, "dashboard/invoices.html")

def payments(request):
    return render(request, "dashboard/payments.html")

def support(request):
    return render(request, "dashboard/support.html")

def refer(request):
    return render(request, "dashboard/refer.html")

def profile(request):
    return render(request, "dashboard/profile.html")

def settings_page(request):
    return render(request, "dashboard/settings.html")

def user_management(request):
    return render(request, "dashboard/usermanagement.html")



# ---------------- Utility: Send OTP ----------------

def send_otp_email(email, otp, userid):
    subject = "Your verification OTP"
    message = f"Hello,\n\nYour OTP for account verification (UserID: {userid}) is: {otp}\nIt expires in 10 minutes.\n\nThanks."
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
    send_mail(subject, message, from_email, [email], fail_silently=False)


# ---------------- Register ----------------

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():

            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            company = form.cleaned_data['company']
            password = form.cleaned_data['password']

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )
            user.is_active = False
            user.save()

            profile = user.profile
            profile.company = company
            profile.phone = phone
            profile.save()

            otp = profile.generate_otp()
            send_otp_email(email, otp, profile.userid)

            request.session["register_email"] = email
            return redirect("verify_otp")

    else:
        form = RegisterForm()
    return render(request, "dashboard/register.html", {"form": form})


# ---------------- OTP Verification ----------------

def verify_otp_view(request):
    email = request.session.get("register_email")
    if not email:
        return redirect("register")

    if request.method == "POST":
        form = OTPVerificationForm(request.POST)
        if form.is_valid():

            otp = form.cleaned_data["otp"]

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "User not found.")
                return redirect("register")

            profile = user.profile

            if profile.otp_is_valid(otp):
                user.is_active = True
                user.save()

                profile.is_verified = True
                profile.clear_otp()
                profile.save()

                messages.success(request, "Account verified successfully. Please login.")
                return redirect("login")
            else:
                messages.error(request, "Invalid or expired OTP.")
    else:
        form = OTPVerificationForm()

    return render(request, "dashboard/verify_otp.html", {"form": form, "email": email})


# ---------------- Login ----------------

@csrf_protect
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():

            uid = form.cleaned_data["userid_or_email"]
            pw = form.cleaned_data["password"]

            user = None

            if "@" in uid:    
                try:
                    user = User.objects.get(email=uid)
                except User.DoesNotExist:
                    user = None
            else:
                try:
                    profile = Profile.objects.get(userid=uid)
                    user = profile.user
                except Profile.DoesNotExist:
                    user = None

            if user:
                if not user.is_active:
                    messages.error(request, "Account not active. Verify email first.")
                    return render(request, "dashboard/login.html", {"form": form})

                user = authenticate(request, username=user.username, password=pw)
                if user:
                    auth_login(request, user)
                    return redirect("dashboard")

            messages.error(request, "Login failed. Invalid credentials.")

    else:
        form = LoginForm()

    return render(request, "dashboard/login.html", {"form": form})


# ---------------- Forget Password----------------
def forgot_password_view(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]

            try:
                user = User.objects.get(email=email)
                profile = user.profile
            except User.DoesNotExist:
                messages.error(request, "Email not found.")
                return redirect("forgot_password")

            otp = profile.generate_otp()
            send_otp_email(email, otp, profile.userid)

            request.session["reset_email"] = email
            messages.success(request, "OTP sent to your email.")
            return redirect("reset_otp_verify")

    else:
        form = ForgotPasswordForm()

    return render(request, "dashboard/forgot_password.html", {"form": form})
#---------------reset otp verification--------------

def reset_otp_verify_view(request):
    email = request.session.get("reset_email")
    if not email:
        return redirect("forgot_password")

    if request.method == "POST":
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data["otp"]

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "User not found.")
                return redirect("forgot_password")

            profile = user.profile

            if profile.otp_is_valid(otp):
                profile.clear_otp()
                profile.save()

                request.session["allow_password_reset"] = True
                return redirect("reset_password")

            else:
                messages.error(request, "Invalid or expired OTP.")

    else:
        form = OTPVerificationForm()

    return render(request, "dashboard/reset_otp_verify.html", {"form": form, "email": email})

#-----------------Reset New password -------------
def reset_password_view(request):
    email = request.session.get("reset_email")
    allowed = request.session.get("allow_password_reset")

    if not email or not allowed:
        return redirect("forgot_password")

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("reset_password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect("forgot_password")

        user.password = make_password(new_password)
        user.save()

        del request.session["allow_password_reset"]
        del request.session["reset_email"]

        messages.success(request, "Password reset successfully. Login now.")
        return redirect("login")

    return render(request, "dashboard/reset_password.html")


# ---------------- Logout ----------------

def logout_view(request):
    auth_logout(request)
    return redirect("login")

#----------------profile-------------

@login_required
def profile_view(request):
    user = request.user
    profile = user.profile

    return render(request, "dashboard/profile.html", {
        "profile": profile,
        "user": user,
    })

