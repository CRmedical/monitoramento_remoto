from django.contrib.auth.models import AbstractUser
from django.db import models
from dashboard.models import Hospital, HospitalGroup

class CustomUser(AbstractUser):
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    grupo = models.ForeignKey(
        HospitalGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )