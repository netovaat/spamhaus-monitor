# Guia de Instalação e Configuração - Spamhaus Monitor

## 📋 Pré-requisitos

### Sistema Operacional
- **Linux** (Ubuntu 18.04+, Debian 9+, CentOS 7+, ou similar)
- **Python 3.7+**
- **Acesso root/sudo**
- **Conexão à internet** para consultas DNS

### Dependências do Sistema
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# CentOS/RHEL
sudo yum install python3 python3-pip git
# ou para versões mais novas:
sudo dnf install python3 python3-pip git
```

## 🚀 Instalação Automatizada

### Método 1: Script de Instalação (Recomendado)

```bash
# 1. Baixar e entrar no diretório
cd /opt
sudo git clone <seu-repositorio> spamhaus-monitor
cd spamhaus-monitor

# 2. Executar instalação automatizada
sudo chmod +x install.sh
sudo ./install.sh
```

O script automatizado irá:
- ✅ Verificar dependências do sistema
- ✅ Criar ambiente virtual Python
- ✅ Instalar bibliotecas necessárias
- ✅ Configurar serviço systemd
- ✅ Criar estrutura de diretórios
- ✅ Definir permissões adequadas

### Método 2: Instalação Manual

```bash
# 1. Criar diretório e ambiente virtual
sudo mkdir -p /opt/spamhaus-monitor
cd /opt/spamhaus-monitor
sudo python3 -m venv venv
sudo chown -R $USER:$USER venv

# 2. Ativar ambiente e instalar dependências
source venv/bin/activate
pip install -r requirements.txt

# 3. Configurar serviço
sudo cp spamhaus-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable spamhaus-monitor
```

## ⚙️ Configuração Inicial

### 1. Configurar Bot do Telegram

#### Criar Bot
1. Abra o Telegram e procure por `@BotFather`
2. Digite `/newbot` e siga as instruções
3. Escolha um nome e username para o bot
4. **Anote o token** fornecido (formato: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### Obter Chat ID
```bash
# Método 1: Via API (depois de enviar mensagem para o bot)
curl "https://api.telegram.org/bot<SEU_TOKEN>/getUpdates"

# Método 2: Usar bot @userinfobot
# Envie /start para @userinfobot no Telegram
```

### 2. Configurar Arquivo Principal

```bash
# Copiar exemplo de configuração
cp /opt/spamhaus-monitor/config.yaml.example /opt/spamhaus-monitor/config.yaml

# Editar configuração
nano /opt/spamhaus-monitor/config.yaml
```

#### Configuração Mínima Obrigatória

```yaml
telegram:
  bot_token: "SEU_TOKEN_AQUI"     # Token do BotFather
  chat_id: "SEU_CHAT_ID_AQUI"    # Seu Chat ID

ips_to_monitor:
  - "8.8.8.8"                    # IP de teste (substitua pelos seus)
  - "1.1.1.1"                    # Outro IP de teste
```

### 3. Teste Inicial

```bash
cd /opt/spamhaus-monitor
source venv/bin/activate

# Testar conectividade com Telegram
python3 utils.py test-telegram

# Testar verificação de IP
python3 utils.py check-ip --ip 8.8.8.8

# Teste completo único
python3 utils.py run-once
```

## 🛠️ Configuração Avançada

### Configuração de Produção Completa

```yaml
telegram:
  bot_token: "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
  chat_id: "123456789"

# IPs e redes para monitoramento
ips_to_monitor:
  # IPs individuais críticos
  - "203.0.113.10"              # Servidor web principal
  - "203.0.113.11"              # Servidor email
  
  # Blocos de rede (pesquisa hierárquica)
  - "203.0.113.0/24"            # Rede DMZ
  - "198.51.100.0/25"           # Servidores aplicação
  
  # Blocos maiores (verificação limitada)
  - "10.0.0.0/22"               # Rede interna principal

# Configurações de monitoramento
monitoring:
  interval_minutes: 60          # Verificar a cada hora
  timeout_seconds: 30           # Timeout DNS
  max_retries: 3                # Tentativas por consulta

# Sistema de logging
logging:
  level: "INFO"                 # INFO, DEBUG, WARNING, ERROR
  file: "/opt/spamhaus-monitor/logs/production.log"
  max_size_mb: 50               # Rotação aos 50MB
  backup_count: 10              # Manter 10 backups

# Blacklists Spamhaus (configuração padrão)
spamhaus_lists:
  - name: "SBL"
    zone: "sbl.spamhaus.org"
    description: "Spamhaus Block List"
  - name: "XBL"
    zone: "xbl.spamhaus.org"
    description: "Exploits Block List"
  - name: "PBL"
    zone: "pbl.spamhaus.org"
    description: "Policy Block List"
  - name: "CSS"
    zone: "css.spamhaus.org"
    description: "Compromised Systems List"
```

### Configurações Especializadas

#### Para Provedores de Email
```yaml
ips_to_monitor:
  - "203.0.113.0/28"            # Pool SMTP
  
monitoring:
  interval_minutes: 30          # Verificação mais frequente
  
# Adicionar blacklist específica para email
spamhaus_lists:
  - name: "ZEN"
    zone: "zen.spamhaus.org"
    description: "Combined Blacklist"
```

#### Para Datacenters/Hosting
```yaml
ips_to_monitor:
  - "203.0.113.0/22"            # Bloco principal
  - "198.51.100.0/23"           # Bloco secundário
  
monitoring:
  interval_minutes: 120         # Verificação menos frequente
  timeout_seconds: 45           # Timeout maior para blocos grandes
```

## 🔧 Gerenciamento do Serviço

### Comandos Básicos

```bash
# Iniciar serviço
sudo systemctl start spamhaus-monitor

# Verificar status
sudo systemctl status spamhaus-monitor

# Parar serviço
sudo systemctl stop spamhaus-monitor

# Reiniciar serviço
sudo systemctl restart spamhaus-monitor

# Habilitar inicialização automática
sudo systemctl enable spamhaus-monitor

# Desabilitar inicialização automática
sudo systemctl disable spamhaus-monitor
```

### Monitoramento de Logs

```bash
# Logs em tempo real
sudo journalctl -u spamhaus-monitor -f

# Últimas 100 linhas
sudo journalctl -u spamhaus-monitor -n 100

# Logs da aplicação
tail -f /opt/spamhaus-monitor/logs/production.log

# Filtrar erros
grep "ERROR" /opt/spamhaus-monitor/logs/production.log
```

## 🔒 Configurações de Segurança

### Permissões de Arquivos

```bash
# Aplicar permissões seguras
sudo chown -R spamhaus-monitor:spamhaus-monitor /opt/spamhaus-monitor
sudo chmod 750 /opt/spamhaus-monitor
sudo chmod 640 /opt/spamhaus-monitor/config.yaml
sudo chmod +x /opt/spamhaus-monitor/*.py
```

### Criar Usuário Dedicado

```bash
# Criar usuário específico (opcional)
sudo useradd -r -s /bin/false -d /opt/spamhaus-monitor spamhaus-monitor

# Ajustar service file
sudo sed -i 's/User=root/User=spamhaus-monitor/' /etc/systemd/system/spamhaus-monitor.service
sudo systemctl daemon-reload
```

### Configurar Firewall (se necessário)

```bash
# UFW (Ubuntu)
sudo ufw allow out 53/udp comment "DNS for Spamhaus queries"

# iptables
sudo iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
```

## 📊 Monitoramento e Manutenção

### Backup Automatizado

```bash
# Executar backup
sudo /opt/spamhaus-monitor/backup.sh

# Configurar cron para backup diário
echo "0 2 * * * root /opt/spamhaus-monitor/backup.sh" | sudo tee -a /etc/crontab
```

### Rotação de Logs Manual

```bash
# Se necessário, rodar rotação manual
sudo logrotate -f /etc/logrotate.d/spamhaus-monitor
```

### Monitoramento de Performance

```bash
# Verificar uso de recursos
sudo systemctl status spamhaus-monitor
ps aux | grep spamhaus

# Verificar espaço em disco
du -sh /opt/spamhaus-monitor/logs/
```

## 🐛 Solução de Problemas Comuns

### Erro: Token do Telegram inválido
```bash
# Verificar token
python3 utils.py test-telegram

# Revisar configuração
nano /opt/spamhaus-monitor/config.yaml
```

### Erro: DNS timeout
```bash
# Testar DNS manualmente
nslookup 8.8.8.8.zen.spamhaus.org

# Aumentar timeout
# Editar config.yaml: timeout_seconds: 45
```

### Serviço não inicia
```bash
# Verificar logs de erro
sudo journalctl -u spamhaus-monitor -n 50

# Testar execução manual
cd /opt/spamhaus-monitor
source venv/bin/activate
python3 spamhaus_monitor.py --debug
```

### Problemas de permissão
```bash
# Corrigir permissões
sudo chown -R $(whoami):$(whoami) /opt/spamhaus-monitor
chmod +x /opt/spamhaus-monitor/*.py
```

## 📈 Otimização de Performance

### Para Redes Grandes
```yaml
monitoring:
  interval_minutes: 180         # Menos frequente
  timeout_seconds: 60           # Timeout maior
```

### Para Ambientes de Alta Disponibilidade
```yaml
monitoring:
  interval_minutes: 15          # Mais frequente
  max_retries: 5                # Mais tentativas
```

## 🔄 Atualizações

### Processo de Atualização
```bash
# 1. Parar serviço
sudo systemctl stop spamhaus-monitor

# 2. Backup
sudo /opt/spamhaus-monitor/backup.sh

# 3. Atualizar código
cd /opt/spamhaus-monitor
sudo git pull

# 4. Atualizar dependências
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 5. Reiniciar serviço
sudo systemctl start spamhaus-monitor
```

---

**📚 Próximos passos: [Exemplos de Uso](EXAMPLES.md) | [Pesquisa Hierárquica](HIERARCHICAL_SEARCH.md)**
