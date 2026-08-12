#!/bin/sh

set -e

echo "=============================================="
echo "   CRON - HISTÓRICO DE CONSUMO MENSAL"
echo "=============================================="

echo "==> Aplicando migrações..."

python backend/manage.py migrate --noinput


while true
do

    AGORA=$(date '+%Y-%m-%d %H:%M:%S')

    echo ""
    echo "[$AGORA] Serviço de consumo mensal ativo."

    python backend/manage.py monthly_consumption

    echo "==> Aguardando 24 horas..."

    sleep 86400

done