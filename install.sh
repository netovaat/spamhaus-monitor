#!/bin/bash

# Script de instalação do Spamhaus Monitor

set -e

echo "🚀 Iniciando instalação do Spamhaus Monitor..."

# Verificar se está executando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script deve ser executado como root"
    exit 1
fi

# Instalar dependências do sistema
echo "📦 Instalando dependências do sistema..."
apt-get update
apt-get install -y python3 python3-pip python3-venv

# Criar ambiente virtual
echo "🐍 Criando ambiente virtual Python..."
cd /opt/spamhaus-monitor
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
echo "📚 Instalando dependências Python..."
pip install -r requirements.txt

# Tornar scripts executáveis
chmod +x spamhaus_monitor.py
chmod +x utils.py

# Instalar serviço systemd
echo "⚙️ Configurando serviço systemd..."
cp spamhaus-monitor.service /etc/systemd/system/
systemctl daemon-reload

echo "✅ Instalação concluída!"
echo ""
echo "📋 Próximos passos:"
echo "1. Edite o arquivo config.yaml com suas configurações"
echo "2. Configure o bot do Telegram"
echo "3. Teste a configuração: python3 utils.py test-telegram"
echo "4. Inicie o serviço: systemctl enable --now spamhaus-monitor"
echo ""
echo "📖 Consulte o README.md para mais detalhes"
