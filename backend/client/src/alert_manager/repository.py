from .interfaces import Fault

# REPOSITÓRIO EM MEMÓRIA (TESTE)
class InMemoryAlertRepository:
    def __init__(self):
        self.storage: list[Fault] = []

    def save(self, fault: Fault) -> None:
        self.storage.append(fault)

    def remove(self, fault: Fault) -> None:
        self.storage = [f for f in self.storage if f != fault]
