# Exemplos de Uso - Spamhaus Monitor

## 🚀 Exemplos Práticos

### 1. Verificação Rápida de um IP

```bash
cd /opt/spamhaus-monitor
source venv/bin/activate
python3 utils.py check-ip --ip 8.8.8.8
```

**Saída esperada (IP limpo):**
```
✅ IP 8.8.8.8 não está listado em nenhuma blacklist do Spamhaus
```

**Saída esperada (IP listado):**
```
🚨 IP 192.168.1.100 encontrado nas seguintes blacklists:
  • SBL (Spamhaus Block List)
    Zona: sbl.spamhaus.org
    Códigos: 127.0.0.2
  • XBL (Exploits Block List)
    Zona: xbl.spamhaus.org
    Códigos: 127.0.0.4
```

### 2. Verificação com Modo Debug

```bash
python3 utils.py check-ip --ip 8.8.8.8 --debug
```

**Saída com debug (inclui timestamp):**
```
🚨 IP 192.168.1.100 encontrado nas seguintes blacklists:
  • SBL (Spamhaus Block List)
    Zona: sbl.spamhaus.org
    Códigos: 127.0.0.2
    Timestamp: 2025-05-26T10:30:00.123456
```

### 3. Verificação de Todos os IPs Configurados

```bash
python3 utils.py run-once
```

**Saída exemplo (modo normal - unificado):**
```
🚨 2 IP(s) encontrado(s) em blacklists:

🌐 REDE: 192.168.1.0/24
   📊 IPs afetados: 3
   📝 SBL: 2 IP(s)
      • 192.168.1.100, 192.168.1.101
   📝 XBL: 1 IP(s)
      • 192.168.1.100

🔴 IP: 10.0.0.50
   📝 PBL: 1 IP(s)
      • 10.0.0.50
```

### 4. Verificação com Modo Debug Detalhado

```bash
python3 utils.py run-once --debug
```

**Saída exemplo (modo debug - verbose):**
```
🔍 RESULTADOS DETALHADOS (DEBUG MODE)
============================================================

🌐 REDE: 192.168.1.0/24
   📊 IPs afetados: 3
   🔴 192.168.1.100
   🔴 192.168.1.101
   🔴 192.168.1.102
   📝 SBL: 2 IP(s)
      • 192.168.1.100 -> 127.0.0.2
      • 192.168.1.101 -> 127.0.0.3
   📝 XBL: 1 IP(s)
      • 192.168.1.100 -> 127.0.0.4

🔴 IP INDIVIDUAL: 10.0.0.50
   📝 PBL: 1 IP(s)
      • 10.0.0.50 -> 127.0.0.10

============================================================
📈 RESUMO: 4 IP(s) listados em 3 blacklist(s)
```

### 5. Monitoramento com Debug via Script Principal

```bash
# Monitoramento contínuo com debug
python3 spamhaus_monitor.py --debug

# Uma verificação única com debug
python3 spamhaus_monitor.py --debug --run-once

# Especificar arquivo de configuração
python3 spamhaus_monitor.py --config custom_config.yaml --debug
```

### 6. Teste do Bot Telegram

```bash
python3 utils.py test-telegram
```

### 7. Monitoramento Manual (Foreground)

```bash
python3 spamhaus_monitor.py
```

Pressione `Ctrl+C` para parar.

## 📱 Exemplos de Notificações Telegram (Unificadas)

### Novos IPs Detectados (Unificado por CIDR)
```
🚨 NOVOS IPs LISTADOS EM BLACKLISTS

🌐 **Rede:** 192.168.1.0/24
📊 **IPs afetados:** 3
  📝 SBL: 2 IP(s)
    • 192.168.1.100
    • 192.168.1.101
  📝 XBL: 1 IP(s)
    • 192.168.1.100

🔴 **IP:** 10.0.0.50
  📝 PBL: 1 IP(s)
    • 10.0.0.50

⏰ Detectado em: 2025-05-26 10:30:00
```

### IPs Removidos das Listas (Unificado)
```
✅ IPs REMOVIDOS DAS BLACKLISTS

🌐 **Rede:** 192.168.1.0/24
📊 **IPs limpos:** 2
  • 192.168.1.100
  • 192.168.1.101

⏰ Verificado em: 2025-05-26 10:45:00
```

### Relatório Diário (9:00 AM) - Unificado
```
🚨 **RELATÓRIO SPAMHAUS**

**4 IP(s) encontrado(s) em blacklists:**

🌐 **Rede:** 192.168.1.0/24
📊 **IPs afetados:** 3
  📝 SBL: 2 IP(s)
  📝 XBL: 1 IP(s)

🔴 **IP:** 10.0.0.50
  📝 PBL: 1 IP(s)

⏰ Verificado em: 2025-05-26 09:00:00
```

ou (quando limpo):

```
✅ **RELATÓRIO SPAMHAUS**

Todos os IPs monitorados estão limpos! 🎉

⏰ Verificado em: 2025-05-26 09:00:00

```bash
python3 spamhaus_monitor.py
```

Pressione `Ctrl+C` para parar.

## 📱 Exemplos de Notificações Telegram

### Novo IP Detectado
```
🚨 NOVO IP LISTADO: 192.168.1.100

📝 **Blacklist:** SBL (Spamhaus Block List)
🌐 **Zona:** sbl.spamhaus.org
📊 **Códigos:** 127.0.0.2
⏰ **Timestamp:** 2025-05-26T10:30:00.123456

📝 **Blacklist:** XBL (Exploits Block List)
🌐 **Zona:** xbl.spamhaus.org
📊 **Códigos:** 127.0.0.4
⏰ **Timestamp:** 2025-05-26T10:30:00.123456
```

### IP Removido das Listas
```
✅ IP REMOVIDO DAS BLACKLISTS: 192.168.1.100

⏰ Verificado em: 2025-05-26 10:45:00
```

### Relatório Diário (9:00 AM)
```
✅ **RELATÓRIO SPAMHAUS**

Todos os IPs monitorados estão limpos! 🎉

⏰ Verificado em: 2025-05-26 09:00:00
```

ou

```
🚨 **RELATÓRIO SPAMHAUS**

**2 IP(s) encontrado(s) em blacklists:**

🔴 **192.168.1.100**
  • SBL (Spamhaus Block List)
  • XBL (Exploits Block List)

🔴 **10.0.0.50**
  • PBL (Policy Block List)

⏰ Verificado em: 2025-05-26 09:00:00
```

## ⚙️ Exemplos de Configuração

### Configuração Básica (config.yaml)
```yaml
telegram:
  bot_token: "1234567890:AAbbCCddEEffGGhhIIjjKKllMMnnOOppQQ"
  chat_id: "123456789"

ips_to_monitor:
  - "203.0.113.1"      # IP do servidor web
  - "203.0.113.2"      # IP do servidor email
  - "192.168.1.0/24"   # Rede interna
```

### Configuração Avançada
```yaml
telegram:
  bot_token: "seu_token_aqui"
  chat_id: "seu_chat_id"

ips_to_monitor:
  - "203.0.113.0/28"   # Bloco público pequeno
  - "10.0.1.0/24"      # Rede DMZ
  - "172.16.0.100"     # Servidor crítico
  - "172.16.0.101"     # Backup server

monitoring:
  interval_minutes: 30  # Verificar a cada 30 minutos
  timeout_seconds: 15   # Timeout maior para redes lentas
  max_retries: 5        # Mais tentativas

logging:
  level: "DEBUG"        # Log detalhado para troubleshooting
  file: "debug.log"
  max_size_mb: 50       # Logs maiores
  backup_count: 10
```

## 🔧 Comandos de Gerenciamento

### Gerenciar Serviço
```bash
# Status do serviço
sudo systemctl status spamhaus-monitor

# Iniciar serviço
sudo systemctl start spamhaus-monitor

# Parar serviço
sudo systemctl stop spamhaus-monitor

# Reiniciar serviço
sudo systemctl restart spamhaus-monitor

# Habilitar inicialização automática
sudo systemctl enable spamhaus-monitor

# Desabilitar inicialização automática
sudo systemctl disable spamhaus-monitor
```

### Visualizar Logs
```bash
# Logs do systemd (tempo real)
sudo journalctl -u spamhaus-monitor -f

# Logs do systemd (últimas 100 linhas)
sudo journalctl -u spamhaus-monitor -n 100

# Logs da aplicação
tail -f /opt/spamhaus-monitor/spamhaus_monitor.log

# Logs com filtro
grep "ERROR" /opt/spamhaus-monitor/spamhaus_monitor.log
```

### Backup e Restore
```bash
# Criar backup
sudo /opt/spamhaus-monitor/backup.sh

# Restaurar backup (exemplo)
cd /opt
sudo tar -xzf /backup/spamhaus-monitor/spamhaus_monitor_backup_20250526_100000.tar.gz
```

## 🐛 Troubleshooting Comum

### Problema: Bot não envia mensagens
```bash
# Testar conectividade
python3 utils.py test-telegram

# Verificar token e chat_id no config.yaml
# Verificar logs para erros específicos
```

### Problema: DNS timeout
```bash
# Testar resolução DNS manual
nslookup 2.8.8.8.sbl.spamhaus.org

# Aumentar timeout no config.yaml:
monitoring:
  timeout_seconds: 20
```

### Problema: Serviço não inicia
```bash
# Verificar logs de erro
sudo journalctl -u spamhaus-monitor -n 50

# Verificar permissões
ls -la /opt/spamhaus-monitor/

# Testar execução manual
cd /opt/spamhaus-monitor
source venv/bin/activate
python3 spamhaus_monitor.py
```

## 📊 Casos de Uso Comuns

### 1. Monitoramento de Infraestrutura Corporativa
```yaml
ips_to_monitor:
  - "203.0.113.0/28"   # Bloco público da empresa
  - "172.16.0.0/24"    # Servidores DMZ
  - "10.0.0.0/16"      # Rede interna (sample)
```

### 2. Monitoramento de Provedores de Email
```yaml
ips_to_monitor:
  - "203.0.113.10"     # Servidor SMTP primário
  - "203.0.113.11"     # Servidor SMTP secundário
  - "203.0.113.12"     # Servidor webmail
```

### 3. Monitoramento de CDN/Proxy
```yaml
ips_to_monitor:
  - "203.0.113.20"     # Load balancer
  - "203.0.113.21"     # Proxy reverso
  - "203.0.113.22"     # CDN endpoint
```

### 4. Monitoramento Residencial/SOHO
```yaml
ips_to_monitor:
  - "203.0.113.100"    # IP público residencial

monitoring:
  interval_minutes: 120  # Verificar a cada 2 horas
```

## 📈 Personalização Avançada

### Adicionar Nova Blacklist
```yaml
spamhaus_lists:
  # ... listas existentes ...
  - name: "SURBL"
    zone: "multi.surbl.org"
    description: "SURBL Multi"
```

### Horários Personalizados
Edite `spamhaus_monitor.py` para alterar horários:
```python
# Relatório às 8:00 e 17:00
schedule.every().day.at("08:00").do(self.send_status_report)
schedule.every().day.at("17:00").do(self.send_status_report)

# Verificação a cada 15 minutos apenas durante horário comercial
schedule.every(15).minutes.do(self.monitor_ips).tag('business_hours')
```

### Filtros de Notificação
Adicione lógica para filtrar notificações por tipo de lista:
```python
# Notificar apenas para SBL e XBL (não PBL)
if result['blacklist'] in ['SBL', 'XBL']:
    self._send_alert(ip, results, "NOVO")
```

# 🌐 Funcionalidade Hierárquica CIDR

## 📋 Pesquisa Hierárquica de Blocos

A partir da versão 2.0, o sistema implementa **pesquisa hierárquica de blocos CIDR**, expandindo automaticamente um bloco maior em sub-blocos menores e IPs individuais.

### Como funciona

Quando você configura um bloco como `192.0.2.0/22`, o sistema automaticamente verifica:

1. **Sub-blocos /23** (se aplicável)
2. **Sub-blocos /24** 
3. **IPs individuais** (limitado para performance)

### Exemplo prático

**Configuração:**
```yaml
ips_to_monitor:
  - "192.0.2.0/22"    # Bloco que será expandido hierarquicamente
  - "8.8.8.8"         # IP individual
```

**Verificação com debug:**
```bash
python3 utils.py run-once --debug
```

**Saída exemplo:**
```
🔍 RESULTADOS DETALHADOS (DEBUG MODE)
============================================================

🌐 REDE ORIGINAL: 192.0.2.0/22
   📊 IPs individuais afetados: 0
   📦 Sub-blocos afetados: 0
   🔶 Sub-blocos CIDR verificados:
      • 192.0.0.0/23
      • 192.0.2.0/23
      • 192.0.0.0/24
      • 192.0.1.0/24
      • 192.0.2.0/24
      • 192.0.3.0/24
   🔴 IPs individuais verificados: 80 IPs

🔴 IP INDIVIDUAL: 8.8.8.8
   ✅ Limpo em todas as blacklists

============================================================
📈 RESUMO: 0 IP(s) e 0 bloco(s) listados em 0 blacklist(s)
🎯 Itens únicos verificados: 86
🌐 Redes CIDR originais afetadas: 0
```

### Estratégia por tamanho de bloco

| Tamanho do Bloco | Estratégia |
|------------------|------------|
| ≤/16 | Verifica apenas alguns sub-blocos /24 |
| /17 a /21 | Divide em /24 e verifica IPs limitados |
| /22 a /23 | **Expansão hierárquica completa** |
| ≥/24 | Verifica todos os IPs individuais |

### Exemplo com bloco listado

Se um sub-bloco for encontrado em blacklist:

```
🌐 REDE ORIGINAL: 10.0.0.0/22
   📦 Sub-blocos afetados: 1
   🔴 IPs individuais afetados: 5
   
   🔶 Sub-blocos CIDR em blacklist:
      • 10.0.1.0/24
   
   🔴 IPs individuais em blacklist:
      • 10.0.0.5
      • 10.0.0.10
      • 10.0.2.15
      
   📝 SBL: 6 item(s)
      • BLOCO: 10.0.1.0/24 -> 127.0.0.2
      • IP: 10.0.0.5 -> 127.0.0.2
      • IP: 10.0.0.10 -> 127.0.0.2
```

### Notificações Telegram hierárquicas

Quando um bloco é afetado, a notificação mostra:

```
🚨 NOVOS ITENS LISTADOS EM BLACKLISTS

🌐 Rede: 10.0.0.0/22
📊 Itens afetados: 6
📦 Sub-blocos listados: 1
   • 10.0.1.0/24
🔴 IPs individuais: 5
   • 10.0.0.5
   • 10.0.0.10
   • 10.0.2.15
   • ... e mais 2 IPs
📝 Blacklists: SBL

⏰ Detectado em: 2025-05-26 10:30:00
```

---
