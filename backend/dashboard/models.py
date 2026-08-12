from django.db import models
from django.db import models
from django.conf import settings
from decimal import Decimal

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

    multiplicador_acumulado = models.DecimalField(
                                                max_digits=12,
                                                decimal_places=2, 
                                                default=Decimal("1.00"),
                                                verbose_name="Multiplicador do acumulado"
                                                )

    multiplicador_pressao = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        default=Decimal("1.000"),
        verbose_name="Multiplicador da pressão"
    )

    multiplicador_pressao_produto = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        default=Decimal("1.000"),
        verbose_name="Multiplicador da pressão do produto"
    )

    multiplicador_pureza = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        default=Decimal("1.000"),
        verbose_name="Multiplicador da pureza"
    )

    offset_pressao = models.DecimalField(
    max_digits=8,
    decimal_places=2,
    default=Decimal("0.00")
    )

    offset_pressao_produto = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00")
    )

    offset_pureza = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00")
    )

    offset_acumulado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
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


class TelemetryHistory(models.Model):
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name="historico_telemetria"
    )

    timestamp = models.DateTimeField(db_index=True)

    pressure = models.FloatField(null=True, blank=True)
    product_pressure = models.FloatField(null=True, blank=True)
    purity = models.FloatField(null=True, blank=True)
    flow = models.FloatField(null=True, blank=True)
    accumulated = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["timestamp"]

        constraints = [
            models.UniqueConstraint(
                fields=["hospital", "timestamp"],
                name="unique_hospital_telemetry_timestamp"
            )
        ]

        indexes = [
            models.Index(
                fields=["hospital", "-timestamp"]
            ),
            models.Index(
                fields=["timestamp"]
            ),
        ]

    def __str__(self):
        return f"{self.hospital.nome} - {self.timestamp}"


class MonthlyConsumption(models.Model):
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name="consumos_mensais"
    )

    ano = models.PositiveIntegerField()
    mes = models.PositiveIntegerField()

    consumo = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00")
    )

    acumulado_inicial = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True
    )

    acumulado_final = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True
    )

    calculado_em = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-ano", "-mes"]

        constraints = [
            models.UniqueConstraint(
                fields=["hospital", "ano", "mes"],
                name="unique_hospital_monthly_consumption"
            )
        ]

    def __str__(self):
        return (
            f"{self.hospital.nome} - "
            f"{self.mes:02d}/{self.ano} - "
            f"{self.consumo} m³"
        )
