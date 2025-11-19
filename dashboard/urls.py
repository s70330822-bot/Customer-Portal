from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),           # root -> login page
    path('register/', views.register_view, name='register'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('logout/', views.logout_view, name='logout'), 
    path('home/', views.dashboard, name='dashboard'),
    path('invoices/', views.invoices, name='invoices'),
    path('payments/', views.payments, name='payments'),
    path('support/', views.support, name='support'),
    path('refer/', views.refer, name='refer'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings_page, name='settings'),
    path("forgot-password/", views.forgot_password_view, name="forgot_password"),
    path("reset-otp/", views.reset_otp_verify_view, name="reset_otp_verify"),
    path("reset-password/", views.reset_password_view, name="reset_password"),
    path('user-management/', views.user_management, name='user_management'),



]

