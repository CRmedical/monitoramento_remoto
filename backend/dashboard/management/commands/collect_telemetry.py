import json
import os
import time

import redis

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from dotenv import load_dotenv

from dashboard.models import Hospital, TelemetryHistory


load_dotenv()


class Command(BaseCommand):

    help = "Coleta uma amostra da telemetria do Redis a cada minuto"

    def handle(self, *args, **options):

        redis_host = os.getenv(
            "REDIS_HOST",
            "localhost"
        )

        redis_password = os.getenv(
            "REDIS_PASSWORD"
        )

        r = redis.Redis(
            host=redis_host,
            port=6379,
            db=0,
            password=redis_password,
            decode_responses=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Coletor de telemetria iniciado..."
            )
        )

        # Controla quando foi realizada a última limpeza
        ultima_limpeza = None

        while True:

            try:

                # =====================================================
                # LIMPEZA DIÁRIA
                # =====================================================

                agora = timezone.now()

                data_atual = agora.date()

                if (
                    ultima_limpeza is None
                    or data_atual != ultima_limpeza
                ):

                    self.limpar_historico()

                    ultima_limpeza = data_atual


                # =====================================================
                # COLETA
                # =====================================================

                self.coletar(r)

            except Exception as e:

                self.stderr.write(
                    self.style.ERROR(
                        f"Erro na coleta: {e}"
                    )
                )

            # Aguarda 60 segundos
            time.sleep(60)


    # =============================================================
    # LIMPEZA DO HISTÓRICO
    # =============================================================

    def limpar_historico(self):

        limite = (
            timezone.now()
            - timedelta(days=45)
        )

        self.stdout.write(
            f"[LIMPEZA] Removendo registros anteriores a "
            f"{limite}..."
        )

        removidos, detalhes = (
            TelemetryHistory.objects
            .filter(timestamp__lt=limite)
            .delete()
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"[LIMPEZA] {removidos} registros removidos."
            )
        )


    # =============================================================
    # COLETA DA TELEMETRIA
    # =============================================================

    def coletar(self, redis_client):

        agora = timezone.now()

        # Arredonda para o início do minuto
        timestamp = agora.replace(
            second=0,
            microsecond=0
        )

        hospitais = Hospital.objects.all()

        total = 0

        for hospital in hospitais:

            dados = None

            # =====================================================
            # PRIMEIRO PROCURA NA USINA
            # =====================================================

            redis_data = redis_client.hget(
                "Usina",
                hospital.nome
            )

            if redis_data:

                dados = redis_data

            else:

                # =================================================
                # DEPOIS PROCURA NA CENTRAL
                # =================================================

                redis_data = redis_client.hget(
                    "Central",
                    hospital.nome
                )

                if redis_data:

                    dados = redis_data


            if not dados:
                continue


            # =====================================================
            # CONVERTE JSON
            # =====================================================

            try:

                detalhes = json.loads(
                    dados
                )

            except (
                json.JSONDecodeError,
                TypeError
            ):

                continue


            # =====================================================
            # CONVERSÃO NUMÉRICA
            # =====================================================

            def numero(campo):

                valor = detalhes.get(
                    campo
                )

                if valor is None:

                    return None

                try:

                    return float(valor)

                except (
                    TypeError,
                    ValueError
                ):

                    return None


            # =====================================================
            # SALVA / ATUALIZA REGISTRO
            # =====================================================

            TelemetryHistory.objects.update_or_create(

                hospital=hospital,

                timestamp=timestamp,

                defaults={

                    "pressure": numero(
                        "pressure"
                    ),

                    "product_pressure": numero(
                        "product_pressure"
                    ),

                    "purity": numero(
                        "purity"
                    ),

                    "flow": numero(
                        "flow"
                    ),

                    "accumulated": numero(
                        "accumulated"
                    ),

                }
            )

            total += 1


        # =========================================================
        # LOG
        # =========================================================

        self.stdout.write(
            f"[{timestamp}] "
            f"{total} hospitais registrados."
        )