import os
import sys
import django
from pathlib import Path

# Caminho absoluto da raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitoramento.settings")
django.setup()

from dashboard.models import ChatTelegram, Hospital, Fault

def get_chat_id(nome):
    try:
        hospital = Hospital.objects.get(nome=nome)
    except Hospital.DoesNotExist:
        print(f'Hospital "{nome}" não encontrado.')
        return
    
    chats = ChatTelegram.objects.filter(hospital=hospital)

    if chats:
        for chat in chats:
            return chat.chat_id
    else:
        print("Nenhum registro encontrado para este hospital.")
        print('Enviando pra o Supervisor...')

class DjangoAlertRepository:

    def __init__(self):
        self._hospital_cache = {}

    def _get_hospital(self, name: str):
        if name not in self._hospital_cache:
            hospital, _ = Hospital.objects.get_or_create(nome=name)
            self._hospital_cache[name] = hospital
        return self._hospital_cache[name]

    def save(self, fault):
        hospital = self._get_hospital(fault.hospital)

        Fault.objects.create(
            hospital=hospital,
            falha=fault.key,
            dados=fault.message
        )

if __name__ == '__main__':
    print(get_chat_id('Joao Machado - Natal/RN'))
