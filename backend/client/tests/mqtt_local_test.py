
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

# Configurações do broker local
BROKER = "192.168.0.151"
PORT = 1883

TOPICO_PUBLICAR = "teste/python/dados"
TOPICO_RECEBER = "teste/python/comandos"

CLIENT_ID = "cliente_python_teste"

# Executada quando o cliente conecta ao broker
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Conectado ao broker MQTT!")

        # Inscreve-se no tópico para receber mensagens
        client.subscribe(TOPICO_RECEBER)
        print(f"Inscrito no tópico: {TOPICO_RECEBER}")
    else:
        print(f"Falha na conexão. Código: {reason_code}")

# Executada quando uma mensagem chega
def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8")

    print("\nMensagem recebida!")
    print(f"Tópico: {message.topic}")
    print(f"Mensagem: {payload}")

# Cria o cliente MQTT usando a API atual do Paho
client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2, #type: ignore
    client_id=CLIENT_ID,
    protocol=mqtt.MQTTv311
)

client.on_connect = on_connect
client.on_message = on_message

try:
    print(f"Conectando a {BROKER}:{PORT}...")

    client.connect(BROKER, PORT, keepalive=60)

    # Inicia o processamento de mensagens em segundo plano
    client.loop_start()

    while True:
        dados = {
            "dispositivo": "ESP32_TESTE",
            "temperatura": 25.5,
            "pressao": 7.2,
            "status": "online",
            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            )
        }

        mensagem = json.dumps(dados, ensure_ascii=False)

        resultado = client.publish(
            TOPICO_PUBLICAR,
            mensagem,
            qos=0
        )

        if resultado.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"\nPublicado em {TOPICO_PUBLICAR}:")
            print(mensagem)
        else:
            print("Erro ao publicar mensagem.")

        time.sleep(5)

except KeyboardInterrupt:
    print("\nEncerrando cliente MQTT...")

except Exception as erro:
    print(f"Erro: {erro}")

finally:
    client.loop_stop()
    client.disconnect()
    print("Cliente desconectado.")