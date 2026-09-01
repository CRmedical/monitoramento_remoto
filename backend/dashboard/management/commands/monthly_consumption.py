from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import (
    Hospital,
    TelemetryHistory,
    MonthlyConsumption
)


class Command(BaseCommand):

    help = "Calcula o consumo mensal dos hospitais."

    def handle(self, *args, **options):

        agora = timezone.localtime()

        # -------------------------------------------------
        # Primeiro dia do mês atual
        # -------------------------------------------------

        inicio_mes_atual = agora.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        # -------------------------------------------------
        # Mês anterior
        # -------------------------------------------------

        if inicio_mes_atual.month == 1:

            ano_anterior = inicio_mes_atual.year - 1
            mes_anterior = 12

        else:

            ano_anterior = inicio_mes_atual.year
            mes_anterior = inicio_mes_atual.month - 1

        # -------------------------------------------------
        # Primeiro dia do mês anterior
        # -------------------------------------------------

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

            # =================================================
            # LEITURA INICIAL
            # =================================================
            #
            # Pega a última leitura ANTES do início do
            # mês anterior.
            #
            # Exemplo:
            #
            # Fechando agosto/2026
            #
            # pega a última leitura disponível antes de
            # 01/08/2026.
            #
            # Se não existir, começa em ZERO.
            # =================================================

            leitura_inicial = (
                TelemetryHistory.objects
                .filter(
                    hospital=hospital,
                    timestamp__lt=inicio_mes_anterior,
                    accumulated__isnull=False
                )
                .order_by("-timestamp")
                .first()
            )

            if leitura_inicial:

                acumulado_inicial = Decimal(
                    str(leitura_inicial.accumulated)
                )

                self.stdout.write(
                    f"{hospital.nome}: "
                    f"leitura inicial encontrada: "
                    f"{acumulado_inicial}"
                )

            else:

                acumulado_inicial = Decimal("0.00")

                self.stdout.write(
                    self.style.WARNING(
                        f"{hospital.nome}: "
                        f"sem leitura anterior. "
                        f"Usando acumulado inicial = 0."
                    )
                )

            # =================================================
            # LEITURA FINAL
            # =================================================
            #
            # Pega a leitura MAIS RECENTE disponível.
            #
            # Isso faz com que o comando considere o valor
            # acumulado no momento da execução.
            # =================================================

            leitura_final = (
                TelemetryHistory.objects
                .filter(
                    hospital=hospital,
                    timestamp__lt=agora,
                    accumulated__isnull=False
                )
                .order_by("-timestamp")
                .first()
            )

            if not leitura_final:

                self.stdout.write(
                    self.style.WARNING(
                        f"{hospital.nome}: "
                        f"sem nenhuma leitura disponível."
                    )
                )

                continue

            acumulado_final = Decimal(
                str(leitura_final.accumulated)
            )

            # =================================================
            # APLICAR MULTIPLICADOR E OFFSET
            # =================================================

            fator = Decimal(
                str(hospital.multiplicador_acumulado)
            )

            offset = Decimal(
                str(hospital.offset_acumulado)
            )

            acumulado_inicial_calculado = (
                acumulado_inicial
            )

            acumulado_final_calculado = (
                acumulado_final
            )

            # =================================================
            # CONSUMO
            # =================================================

            consumo = (
                acumulado_final_calculado
                - acumulado_inicial_calculado
            )

            # Evita consumo negativo
            if consumo < Decimal("0.00"):
                consumo = Decimal("0.00")

            consumo = consumo.quantize(
                Decimal("0.01")
            )

            # =================================================
            # SALVAR
            # =================================================

            MonthlyConsumption.objects.update_or_create(

                hospital=hospital,

                ano=ano_anterior,

                mes=mes_anterior,

                defaults={

                    "consumo": consumo,

                    "acumulado_inicial":
                        acumulado_inicial_calculado,

                    "acumulado_final":
                        acumulado_final_calculado,

                }
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"{hospital.nome}: "
                    f"{consumo:.2f} m³ "
                    f"(Inicial: "
                    f"{acumulado_inicial_calculado:.2f} | "
                    f"Final: "
                    f"{acumulado_final_calculado:.2f})"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Consumo mensal calculado."
            )
        )