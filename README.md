# Spamhaus Monitor

Sistema de monitoramento contínuo de IPs e blocos de rede nas blacklists do Spamhaus com notificações via Telegram e **pesquisa hierárquica avançada**.

## 📋 Funcionalidades

- ✅ **Monitoramento contínuo** de IPs e blocos de rede
- 🔍 **Verificação em múltiplas blacklists** do Spamhaus (SBL, XBL, PBL, CSS)
- 🌐 **Pesquisa hierárquica CIDR** - expande blocos grandes em sub-blocos menores
- 📱 **Notificações em tempo real** via bot do Telegram
- 📊 **Relatórios diários** automáticos unificados por CIDR
- 🔄 **Detecção inteligente de mudanças** (novos IPs listados/removidos)
- 🐛 **Modo debug verbose** para análise detalhada
- 📝 **Logging detalhado** com rotação automática
- ⚙️ **Configuração flexível** via arquivo YAML
- 🚀 **Execução como serviço systemd**

## 📦 Requisitos

- Python 3.7+
- Linux (testado no Ubuntu/Debian)
- Acesso à internet para consultas DNS
- Bot do Telegram configurado

## 📚 Documentação Completa

Este README fornece uma visão geral. Para documentação detalhada, consulte:

- 📖 **[Guia de Instalação](docs/INSTALLATION.md)** - Processo completo de instalação e configuração
- 🔍 **[Pesquisa Hierárquica](docs/HIERARCHICAL_SEARCH.md)** - Como funciona a expansão de blocos CIDR
- 💡 **[Exemplos de Uso](docs/EXAMPLES.md)** - Casos práticos e configurações
- 🛡️ **[Referência de Blacklists](docs/BLACKLISTS.md)** - Guia completo das listas do Spamhaus

## 🚀 Instalação Rápida

### 1. Clone ou baixe o projeto

```bash
# Se você já tem os arquivos no diretório
cd /opt/spamhaus-monitor

# Ou clone de um repositório
git clone <seu-repositorio> /opt/spamhaus-monitor
cd /opt/spamhaus-monitor
```

### 2. Execute o script de instalação

```bash
sudo ./install.sh
```

Este script irá:
- Instalar dependências do sistema
- Criar ambiente virtual Python
- Instalar bibliotecas Python necessárias
- Configurar serviço systemd

## ⚙️ Configuração

### 1. Configurar Bot do Telegram

Siga o **[Guia de Instalação](docs/INSTALLATION.md)** para configuração completa do bot.

### 2. Editar configuração

```bash
sudo nano /opt/spamhaus-monitor/config.yaml
```

**Configuração básica:**
```yaml
telegram:
  bot_token: "SEU_BOT_TOKEN_AQUI"
  chat_id: "SEU_CHAT_ID_AQUI"

networks:
  - "203.0.113.0/24"    # Exemplo de rede
  - "198.51.100.100"    # Exemplo de IP individual

# Para pesquisa hierárquica (recomendado):
hierarchical_search: true
expand_large_networks: true
max_ips_per_subnet: 256
```

### 3. Iniciar o serviço

```bash
sudo systemctl start spamhaus-monitor
sudo systemctl enable spamhaus-monitor
```

## 🔍 Pesquisa Hierárquica CIDR

**Novidade:** O sistema agora expande automaticamente blocos CIDR grandes:

- **Bloco /22** → 2 sub-blocos /23 + 4 sub-blocos /24 + até 80 IPs individuais
- **Bloco /23** → 2 sub-blocos /24 + até 40 IPs individuais  
- **Bloco /24** → até 256 IPs individuais

Consulte **[Pesquisa Hierárquica](docs/HIERARCHICAL_SEARCH.md)** para detalhes completos.

1. **Criar Bot:**
   - Abra o Telegram e procure por `@BotFather`
   - Digite `/newbot` e siga as instruções
   - Anote o token do bot

2. **Obter Chat ID:**
   - Envie uma mensagem para o seu bot
   - Acesse: `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
   - Procure pelo `chat.id` na resposta

### 2. Editar arquivo de configuração

```bash
nano /opt/spamhaus-monitor/config.yaml
```

Configure os seguintes campos obrigatórios:

```yaml
telegram:
  bot_token: "1234567890:AAbbCCddEEffGGhhIIjjKKllMMnnOOppQQ"
  chat_id: "123456789"

ips_to_monitor:
  - "8.8.8.8"           # IP individual
  - "1.1.1.1" 
  - "192.168.1.0/24"    # Bloco de rede
  - "10.0.0.0/16"
```

### 3. Testar configuração

```bash
cd /opt/spamhaus-monitor
source venv/bin/activate
python3 utils.py test-telegram
```

Se tudo estiver correto, você receberá uma mensagem de teste no Telegram.

## 🎯 Como Usar

### Execução Manual

```bash
cd /opt/spamhaus-monitor
source venv/bin/activate

# Verificar um IP específico
python3 utils.py check-ip --ip 8.8.8.8

# Executar uma verificação única de todos os IPs
python3 utils.py run-once

# Iniciar monitoramento contínuo
python3 spamhaus_monitor.py
```

### Execução como Serviço

```bash
# Habilitar e iniciar o serviço
sudo systemctl enable spamhaus-monitor
sudo systemctl start spamhaus-monitor

# Verificar status
sudo systemctl status spamhaus-monitor

# Ver logs
sudo journalctl -u spamhaus-monitor -f

# Parar o serviço
sudo systemctl stop spamhaus-monitor
```

## 📊 Tipos de Notificações

### 🚨 Novo IP Listado
Quando um IP é detectado pela primeira vez em alguma blacklist:
```
🚨 NOVO IP LISTADO: 192.168.1.100

📝 Blacklist: SBL (Spamhaus Block List)
🌐 Zona: sbl.spamhaus.org
📊 Códigos: 127.0.0.2
⏰ Timestamp: 2025-05-26T10:30:00
```

### ⚠️ Nova Blacklist
Quando um IP já monitorado é listado em uma nova blacklist:
```
⚠️ NOVA BLACKLIST: 192.168.1.100

📝 Blacklist: XBL (Exploits Block List)
🌐 Zona: xbl.spamhaus.org
📊 Códigos: 127.0.0.3
⏰ Timestamp: 2025-05-26T10:35:00
```

### ✅ IP Removido
Quando um IP é removido de todas as blacklists:
```
✅ IP REMOVIDO DAS BLACKLISTS: 192.168.1.100

⏰ Verificado em: 2025-05-26 10:40:00
```

### 📊 Relatório Diário
Enviado automaticamente às 9:00 todos os dias:
```
🚨 RELATÓRIO SPAMHAUS

2 IP(s) encontrado(s) em blacklists:

🔴 192.168.1.100
  • SBL (Spamhaus Block List)
  • XBL (Exploits Block List)

🔴 192.168.1.101
  • PBL (Policy Block List)

⏰ Verificado em: 2025-05-26 09:00:00
```

## 📁 Estrutura de Arquivos

```
/opt/spamhaus-monitor/
├── spamhaus_monitor.py              # Script principal
├── utils.py                         # Utilitários e comandos auxiliares
├── config.yaml                      # Configuração principal
├── config.yaml.example              # Exemplo de configuração
├── config_production_hierarchical.yaml # Configuração de produção com hierarquia
├── requirements.txt                 # Dependências Python
├── install.sh                       # Script de instalação automatizada
├── backup.sh                        # Script de backup
├── spamhaus-monitor.service         # Serviço systemd
├── README.md                        # Esta documentação
├── docs/                            # Documentação detalhada
│   ├── INSTALLATION.md              # Guia completo de instalação
│   ├── EXAMPLES.md                  # Exemplos de uso e configuração
│   ├── HIERARCHICAL_SEARCH.md       # Documentação da pesquisa hierárquica
│   └── BLACKLISTS.md               # Referência das blacklists
├── venv/                            # Ambiente virtual (criado na instalação)
├── spamhaus_monitor.log             # Logs (criado automaticamente)
└── previous_results.json            # Cache de resultados anteriores
```

## 🔧 Configurações Avançadas

### Intervalo de Verificação

```yaml
monitoring:
  interval_minutes: 30  # Verificar a cada 30 minutos
  timeout_seconds: 15   # Timeout de 15 segundos para DNS
  max_retries: 5        # 5 tentativas máximas
```

### Logging

```yaml
logging:
  level: "DEBUG"        # DEBUG, INFO, WARNING, ERROR
  file: "monitor.log"   # Nome do arquivo de log
  max_size_mb: 20       # Tamanho máximo 20MB
  backup_count: 10      # Manter 10 backups
```

### Blacklists Personalizadas

```yaml
spamhaus_lists:
  - name: "CUSTOM"
    zone: "custom.blacklist.org"
    description: "Minha blacklist personalizada"
```

## 🐛 Solução de Problemas

### Erro de Token do Telegram
```
TelegramError: Unauthorized
```
**Solução:** Verifique se o token do bot está correto no `config.yaml`

### Erro de DNS Timeout
```
Timeout ao verificar IP em blacklist
```
**Solução:** Aumente o `timeout_seconds` no `config.yaml` ou verifique a conectividade

### Serviço não inicia
```bash
sudo systemctl status spamhaus-monitor
```
**Verificar:**
- Permissões dos arquivos
- Configuração do `config.yaml`
- Logs em `/var/log/syslog`

### IP não encontrado
O sistema só reporta IPs que **estão** listados. Se um IP não aparece nos relatórios, significa que está limpo.

## 📝 Logs

Os logs são salvos em `/opt/spamhaus-monitor/spamhaus_monitor.log` com rotação automática.

**Exemplo de log:**
```
2025-05-26 10:30:00,123 - SpamhausMonitor - INFO - Iniciando verificação de IPs no Spamhaus
2025-05-26 10:30:01,456 - SpamhausMonitor - INFO - IP 192.168.1.100 encontrado em SBL (sbl.spamhaus.org)
2025-05-26 10:30:02,789 - SpamhausMonitor - INFO - Notificação enviada via Telegram
2025-05-26 10:30:05,012 - SpamhausMonitor - INFO - Verificação concluída. 1 IPs encontrados em blacklists
```

## 🔐 Segurança

- ⚠️ Nunca compartilhe o token do bot do Telegram
- 🔒 Mantenha o arquivo `config.yaml` com permissões restritas:
  ```bash
  chmod 600 /opt/spamhaus-monitor/config.yaml
  ```
- 🛡️ Execute o serviço com usuário de baixo privilégio (modifique o service file se necessário)

## 📊 Performance

- **Redes grandes:** O sistema limita automaticamente a verificação de redes grandes (>256 IPs) para evitar sobrecarga
- **Rate Limiting:** Pequenas pausas entre verificações para respeitar limites do Spamhaus
- **Cache:** Resultados são comparados com verificação anterior para enviar apenas mudanças

## 🤝 Contribuição

Para contribuir com o projeto:

1. Fork o repositório
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a MIT License.

## 📞 Suporte

Para suporte e dúvidas:
- 📧 Abra uma issue no repositório
- 📖 Consulte os logs para diagnosticar problemas
- 🔍 Verifique a seção de solução de problemas acima

---

**Desenvolvido para monitoramento proativo de segurança de rede** 🛡️
