import json
import time
from datetime import datetime

import paho.mqtt.client as mqtt


# Configurações do broker
BROKER = "200.241.55.229"
PORT = 1883

USERNAME = "mqttadmin"
PASSWORD = "Da32525291"

TOPICO_PUBLICAR = "teste/python/dados"
TOPICO_RECEBER = "teste/python/comandos"

CLIENT_ID = "cliente_python_teste"


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Conectado ao broker MQTT!")

        resultado, mid = client.subscribe(TOPICO_RECEBER)

        if resultado == mqtt.MQTT_ERR_SUCCESS:
            print(f"Inscrito no tópico: {TOPICO_RECEBER}")
        else:
            print(f"Falha ao assinar tópico: {resultado}")
    else:
        print(f"Falha na conexão: {reason_code}")


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    if reason_code != 0:
        print(f"Desconexão inesperada: {reason_code}")


def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8")

    print("\nMensagem recebida!")
    print(f"Tópico: {message.topic}")
    print(f"Mensagem: {payload}")


client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id=CLIENT_ID,
    protocol=mqtt.MQTTv311,
)

# Autenticação obrigatória
client.username_pw_set(USERNAME, PASSWORD)

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

try:
    print(f"Conectando a {BROKER}:{PORT}...")

    client.connect(BROKER, PORT, keepalive=60)
    client.loop_start()

    while not client.is_connected():
        time.sleep(0.1)

    while True:
        dados = {
            "dispositivo": "ESP32_TESTE",
            "temperatura": 25.5,
            "pressao": 7.2,
            "status": "online",
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

        mensagem = json.dumps(dados, ensure_ascii=False)

        resultado = client.publish(
            TOPICO_PUBLICAR,
            mensagem,
            qos=0,
        )

        if resultado.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"\nMensagem enfileirada para {TOPICO_PUBLICAR}:")
            print(mensagem)
        else:
            print(f"Falha ao enfileirar mensagem: código {resultado.rc}")

        time.sleep(5)

except KeyboardInterrupt:
    print("\nEncerrando cliente MQTT...")

except Exception as erro:
    print(f"Erro: {erro}")

finally:
    client.loop_stop()
    client.disconnect()
    print("Cliente desconectado.")