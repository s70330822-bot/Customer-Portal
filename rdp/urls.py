from django.urls import path
from .views import rdp_list , current_active_users


urlpatterns = [
   
    path('rdp-activity/', rdp_list, name='rdp_list'),
    path("rdp-current-users/", current_active_users, name="rdp_current_users"),

]

