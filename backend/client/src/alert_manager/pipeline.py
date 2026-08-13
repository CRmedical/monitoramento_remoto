from .entities import Hospital
from .repository import InMemoryAlertRepository
from .alert import AlertManager, AlertService
from .process import Handles
from .telegram import Telegram
from .entities import Connection

from django.utils import timezone

from dashboard import models

class AlertPipeline:
    def __init__(self) -> None:
        han = Handles()
        tel = Telegram(han)
        self.repo = InMemoryAlertRepository()
        self.manager = AlertManager(self.repo, tel)
        self.service = AlertService(self.manager)

    def check_hospital(self, payload: dict):
        hos = Hospital(payload)
        self.service.process_hospital(hos.central)
        self.manager.cleanup_expired()
        
        

class ConnectionAlertPipeline:

    def __init__(self) -> None:
        handle = Handles()
        self.tel = Telegram(handle)

    def check_hospital(self, payload: str):

        connection = Connection.from_str(payload)
        
        try:

            hospital = models.Hospital.objects.get(
                nome__iexact=connection.hospital.strip()
            )
            
        except models.Hospital.DoesNotExist:

            print(
                f"Hospital não encontrado: "
                f"{connection.hospital}"
            )

            return

        status = connection.status.lower()

        if status not in ("online", "offline"):
            print(
                f"Status desconhecido: {connection.status}"
            )
            return
        
        device, created = models.DeviceConnection.objects.get_or_create(
            hospital=hospital,
            defaults={
                "status": status,
                "ultimo_evento": timezone.now(),
            }
        )

        if not created:

            status_anterior = device.status

            device.status = status
            device.ultimo_evento = timezone.now()
            device.save(
                update_fields=[
                    "status",
                    "ultimo_evento",
                    "atualizado_em",
                ]
            )

            # Só envia alerta quando realmente mudou
            if status_anterior != status:

                self.tel.send_connection_alert(
                    connection
                )