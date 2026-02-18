from dataclasses import dataclass, field
from datetime import datetime, timedelta

@dataclass
class Data:
    compressor_1: str | None
    compressor_2: str | None
    emergency_btn: str | None
    phase_fault: str | None
    automatic: str | None
    line: float | None
    pressure: float | None
    dew_point: float | None
    vaccum: str | None
    purity: float | None
    
    @classmethod
    def from_dict(cls, payload: dict) -> "Data":
        return cls(
            compressor_1=payload.get("C1"),
            compressor_2=payload.get("C2"),
            emergency_btn=payload.get("BE"),
            phase_fault=payload.get("RST"),
            automatic=payload.get("auto"),
            line=payload.get("rede"),
            pressure=payload.get("pressure"),
            dew_point=payload.get("dew_point"),
            vaccum=payload.get("vacuo"),
            purity=payload.get("purity"),
        )

@dataclass
class Central:
    name: str
    data: Data

class Hospital:
    def __init__(self, payload: dict) -> None:
        if 'Hospital' not in payload:
            raise ValueError('Missing "Hospital" key')
        if 'Data' not in payload:
            raise ValueError('Missing "Data" key')

        data = Data.from_dict(payload['Data'])
        self.central = Central(payload['Hospital'], data)


@dataclass(eq=False)
class Fault:
    hospital: str
    source: str
    key: str
    message: str
    created_at: datetime = field(default_factory=datetime.now)

    def __eq__(self, other):
        if not isinstance(other, Fault):
            return False
        return (
            self.hospital == other.hospital and
            self.source == other.source and
            self.key == other.key
        )

    def __hash__(self):
        return hash((self.hospital, self.source, self.key))
    
    def is_expired(self, timeout_seconds: int) -> bool:
        return datetime.now() - self.created_at > timedelta(seconds=timeout_seconds)

@dataclass
class Connection:
    hospital: str
    status: str

    @classmethod
    def from_str(cls, payload: str) -> 'Connection':
        if payload.startswith('Online'):
            return cls(
                hospital = payload.split('Online ')[1],
                status = 'Online'
                )
            
        elif payload.startswith('Offline'):
            return cls(
                hospital = payload.split('Offline ')[1],
                status = 'Offline'
                )
        else:
            return cls(
                hospital = 'else',
                status = 'else'
            )