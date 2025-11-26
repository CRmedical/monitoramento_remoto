# Modulo Client

O modulo client cuida da regra de negocio desse projeto,
nele temos os handles: MQTT, EMAIL, DJANGO.

### MQTT
o modulo mqtt é um cliente paho.mqtt que se conecta ao broker e
monitora as mensagens.

### EMAIL
o modulo email cuida do envio de emails em caso de alguma falha
em alguma das centrais

### DJANGO
o modulo django cuida da conexão entre o modulo cliente e o
sistema django