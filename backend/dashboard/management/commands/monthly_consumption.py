from decimal import Decimal
from datetime import datetime, time

from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Hospital, TelemetryHistory, MonthlyConsumption


class Command(BaseCommand):

    help = "Calcula o consumo mensal dos hospitais."

    def handle(self, *args, **options):

        agora = timezone.localtime()

        # Primeiro dia do mês atual
        inicio_mes_atual = agora.replace(
            day=1,
            # hour=0,
            # minute=0,
            # second=0,
            # microsecond=0
        )

        # Estamos fechando o mês anterior
        if inicio_mes_atual.month == 1:

            ano_anterior = inicio_mes_atual.year - 1
            mes_anterior = 12

        else:

            ano_anterior = inicio_mes_atual.year
            mes_anterior = inicio_mes_atual.month - 1

        # Primeiro dia do mês anterior
        inicio_mes_anterior = inicio_mes_atual.replace(
            year=ano_anterior,
            month=mes_anterior
        )

        self.stdout.write(
            f"Calculando consumo "
            f"{mes_anterior:02d}/{ano_anterior}"
        )

        hospitais = Hospital.objects.all()

        for hospital in hospitais:

            # -------------------------------------------------
            # Leitura inicial
            # -------------------------------------------------

            leitura_inicial = (
                TelemetryHistory.objects
                .filter(
                    hospital=hospital,
                    timestamp__gte=inicio_mes_anterior,
                    timestamp__lt=inicio_mes_atual,
                    accumulated__isnull=False
                )
                .order_by("timestamp")
                .first()
            )

            # -------------------------------------------------
            # Leitura final
            # -------------------------------------------------

            leitura_final = (
                TelemetryHistory.objects
                .filter(
                    hospital=hospital,
                    timestamp__gte=inicio_mes_atual,
                    accumulated__isnull=False
                )
                .order_by("timestamp")
                .first()
            )

            if not leitura_inicial:
                self.stdout.write(
                    self.style.WARNING(
                        f"{hospital.nome}: "
                        f"sem leitura inicial."
                    )
                )
                continue

            if not leitura_final:
                self.stdout.write(
                    self.style.WARNING(
                        f"{hospital.nome}: "
                        f"sem leitura final."
                    )
                )
                continue

            acumulado_inicial = Decimal(
                str(leitura_inicial.accumulated)
            )

            acumulado_final = Decimal(
                str(leitura_final.accumulated)
            )

            # -------------------------------------------------
            # Aplicar multiplicador
            # -------------------------------------------------

            fator = Decimal(
                str(hospital.multiplicador_acumulado)
            )

            offset = Decimal(
                str(hospital.offset_acumulado)
            )

            acumulado_inicial = (
                acumulado_inicial * fator
            ) + offset

            acumulado_final = (
                acumulado_final * fator
            ) + offset

            # -------------------------------------------------
            # Consumo
            # -------------------------------------------------

            consumo = (
                acumulado_final -
                acumulado_inicial
            )

            consumo = max(
                consumo,
                Decimal("0.00")
            )

            # -------------------------------------------------
            # Salvar
            # -------------------------------------------------

            MonthlyConsumption.objects.update_or_create(

                hospital=hospital,

                ano=ano_anterior,

                mes=mes_anterior,

                defaults={

                    "consumo": consumo,

                    "acumulado_inicial":
                        acumulado_inicial,

                    "acumulado_final":
                        acumulado_final,

                }
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"{hospital.nome}: "
                    f"{consumo:.2f} m³"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Consumo mensal calculado."
            )
        )