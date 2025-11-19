from django.db import models


# Create your models here.
#-------------------------for rdp--------------
class RDPLog(models.Model):
    EVENT_CHOICES = (
        (4624, 'Login Successful'),
        (4647, 'User Initiated Logoff'),
        (4625, 'Login Failed'),
        (4779, 'Session Disconnect'),
    )

    event_id = models.IntegerField(choices=EVENT_CHOICES)
    username = models.CharField(max_length=255, blank=True)
    ip_address = models.CharField(max_length=100, blank=True)
    workstation = models.CharField(max_length=255, blank=True)
    raw_message = models.TextField(blank=True)        # store original event text (optional)
    received_at = models.DateTimeField(auto_now_add=True)
    event_time = models.DateTimeField(null=True, blank=True)  # when event occurred on server

    class Meta:
        ordering = ['-received_at']

    def __str__(self):
        return f"{self.username} @ {self.ip_address} ({self.event_id})"
