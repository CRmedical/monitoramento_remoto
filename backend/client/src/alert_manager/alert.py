from typing import Set
from .entities import Fault
from .interfaces import AlertRepository, Sender
from .process import ProcessData

class AlertManager:

    def __init__(self, 
                 repository: AlertRepository, 
                
                 sender: Sender,
                 timeout_seconds: int = 300):
        
        self.repository = repository
        self.timeout_seconds = timeout_seconds
        self.active_alerts: dict[tuple, Fault] = dict()
        
        self.sender = sender

    def trigger(self, fault: Fault) -> bool:
        """
        Dispara alerta se ainda não estiver ativo.
        Retorna True se for novo alerta.
        """
        identifier = (fault.hospital, fault.key)

        if identifier in self.active_alerts:
            return False
        
        self.active_alerts[identifier] = fault
        self.repository.save(fault)
        self.sender.send_fault(fault)
        return True

    def recover(self, fault: Fault) -> bool:
        """
        Remove alerta se voltou ao normal.
        """
        identifier = (fault.hospital, fault.key)

        if identifier not in self.active_alerts:
            return False

        stored_fault = self.active_alerts.pop(identifier)
        
        self.repository.remove(stored_fault)
        self.sender.send_fault(stored_fault, True)
        return True

    def cleanup_expired(self) -> None:
        """
        Remove alertas que passaram do timeout.
        """
        expired_keys = [
            key for key, fault in self.active_alerts.items()
            if fault.is_expired(self.timeout_seconds)
        ]
        
        for key in expired_keys:
            fault = self.active_alerts[key] 
            self.recover(fault)

    def is_active(self, fault: Fault) -> bool:
        return fault in self.active_alerts
    
    

class AlertService:

    def __init__(self, manager):
        self.manager = manager

    def process_usina(self, data):
        psa = data["Data"]

        faults = ProcessData.generate_fault_objects(
            name="Oxygen Plant",
            hospital=data["Hospital"],
            values=psa,
            rules=ProcessData.USINA_RULES + ProcessData.FLAG_RULES,
            safe_get=ProcessData._safe_get
        )

        self._handle_faults(faults, data.name, "Oxygen Plant")


    def process_hospital(self, data):
        hospital_data = data.data

        faults = ProcessData.generate_fault_objects(
            name="Hospital",
            hospital=data.name,
            values=hospital_data,
            rules=ProcessData.HOSPITAL_RULES + ProcessData.FLAG_RULES,
            safe_get=ProcessData._safe_get
        )

        self._handle_faults(faults, data.name, "Hospital")


    def _handle_faults(self, faults: list[Fault], hospital: str, source: str):

        active_now = {
            (f.hospital, f.source, f.key): f
            for f in faults
        }

        active_before = {
            key: fault
            for key, fault in self.manager.active_alerts.items()
            if key[0] == hospital and key[1] == source
        }

        # Novos
        for key, fault in active_now.items():
            if key not in active_before:
                self.manager.trigger(fault)

        # Recuperados
        for key, fault in active_before.items():
            if key not in active_now:
                self.manager.recover(fault)