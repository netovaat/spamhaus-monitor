#!/bin/bash

# Script de backup do Spamhaus Monitor

BACKUP_DIR="/backup/spamhaus-monitor"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="spamhaus_monitor_backup_${TIMESTAMP}.tar.gz"

echo "🔄 Iniciando backup do Spamhaus Monitor..."

# Criar diretório de backup se não existir
mkdir -p $BACKUP_DIR

# Parar o serviço temporariamente
echo "⏸️ Parando serviço..."
systemctl stop spamhaus-monitor

# Criar backup
echo "📦 Criando backup..."
cd /opt
tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" \
    --exclude="spamhaus-monitor/venv" \
    --exclude="spamhaus-monitor/__pycache__" \
    --exclude="spamhaus-monitor/*.pyc" \
    spamhaus-monitor/

# Reiniciar o serviço
echo "▶️ Reiniciando serviço..."
systemctl start spamhaus-monitor

# Limpar backups antigos (manter apenas os últimos 7)
echo "🧹 Limpando backups antigos..."
cd $BACKUP_DIR
ls -t spamhaus_monitor_backup_*.tar.gz | tail -n +8 | xargs -r rm

echo "✅ Backup concluído: ${BACKUP_DIR}/${BACKUP_FILE}"
echo "📊 Tamanho do backup: $(du -h ${BACKUP_DIR}/${BACKUP_FILE} | cut -f1)"
