from django.db import models
from django.db import models
from django.conf import settings

class HospitalGroup(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    usuarios = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="hospital_groups"
    )

    def __str__(self):
        return self.nome
    

class Hospital(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    grupo = models.ForeignKey(
        HospitalGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hospitais"
    )

    def __str__(self):
        return self.nome


class AirCentral(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)


class OxygenCentral(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)

class ChatTelegram(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    chat_id = models.CharField(verbose_name='Id chat', null=True, blank=True)

class Fault(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)
    falha = models.CharField(max_length=100)
    dados = models.CharField(max_length=200)

