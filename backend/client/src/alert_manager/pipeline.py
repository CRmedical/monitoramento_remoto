from .entities import Hospital
from .repository import InMemoryAlertRepository
from .alert import AlertManager, AlertService
from .process import Handles
from .telegram import Telegram
from .entities import Connection

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
        self.tel.send_connection_alert(connection)
        