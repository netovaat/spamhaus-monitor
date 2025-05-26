# Pesquisa Hierárquica CIDR - Spamhaus Monitor

## 🌐 Visão Geral

A funcionalidade de **Pesquisa Hierárquica CIDR** permite monitorar blocos de rede de forma inteligente, expandindo automaticamente blocos maiores em sub-blocos menores e IPs individuais para verificação abrangente no Spamhaus.

## 🎯 Como Funciona

### Expansão Automática por Tamanho do Bloco

| Bloco CIDR | Estratégia de Expansão | Exemplo |
|------------|----------------------|---------|
| `/16` ou menor | Sub-blocos `/24` limitados | `/16` → 10 primeiros `/24` (50 IPs) |
| `/17` a `/21` | Sub-blocos `/24` completos | `/20` → todos os `/24` (10 IPs cada) |
| `/22` a `/23` | **Expansão Hierárquica Completa** | `/22` → `/23` + `/24` + IPs individuais |
| `/24` ou maior | IPs individuais | `/24` → todos os IPs da rede |

### Exemplo Prático: Bloco /22

```
192.0.2.0/22 é expandido em:
├── 192.0.0.0/23 (sub-bloco verificado diretamente)
├── 192.0.2.0/23 (sub-bloco verificado diretamente)
├── 192.0.0.0/24 (sub-bloco verificado diretamente)
├── 192.0.1.0/24 (sub-bloco verificado diretamente)
├── 192.0.2.0/24 (sub-bloco verificado diretamente)
├── 192.0.3.0/24 (sub-bloco verificado diretamente)
├── 192.0.0.1 (IP individual)
├── 192.0.0.2 (IP individual)
├── ... (mais 18 IPs do /24)
├── 192.0.1.1 (IP individual)
└── ... (total: ~86 verificações)
```

## 🔧 Configuração

### Arquivo de Configuração (config.yaml)

```yaml
ips_to_monitor:
  - "203.0.113.0/22"    # Será expandido hierarquicamente
  - "198.51.100.0/24"   # IPs individuais
  - "192.0.2.100"       # IP único

monitoring:
  interval_minutes: 60   # Ajuste conforme necessário
  timeout_seconds: 30    # Timeout maior para blocos grandes
```

## 🚀 Uso Prático

### 1. Verificação Única com Debug

```bash
# Ver expansão hierárquica detalhada
python3 utils.py run-once --debug --config config.yaml
```

**Saída de exemplo:**
```
🔍 RESULTADOS DETALHADOS (DEBUG MODE)
============================================================

🌐 REDE ORIGINAL: 203.0.113.0/22
   📊 IPs individuais afetados: 3
   📦 Sub-blocos afetados: 2
   🔶 Sub-blocos CIDR em blacklist:
      • 203.0.113.0/24
      • 203.0.113.64/24
   🔴 IPs individuais em blacklist:
      • 203.0.113.15
      • 203.0.113.67
      • 203.0.113.128
```

### 2. Monitoramento Contínuo

```bash
# Produção com logs informativos
python3 spamhaus_monitor.py --config config_production.yaml

# Debug para troubleshooting
python3 spamhaus_monitor.py --debug --config config_production.yaml
```

## 📱 Notificações Telegram Unificadas

### Exemplo de Notificação para Bloco /22

```
🚨 NOVOS ITENS LISTADOS EM BLACKLISTS

🌐 **Rede:** 203.0.113.0/22
📊 **Itens afetados:** 5
📦 **Sub-blocos listados:** 2
   • 203.0.113.0/24
   • 203.0.113.64/24
🔴 **IPs individuais:** 3
   • 203.0.113.15
   • 203.0.113.67
   • 203.0.113.128
📝 **Blacklists:** SBL, XBL

⏰ **Detectado em:** 2025-05-26 10:30:00
```

## 📈 Vantagens da Pesquisa Hierárquica

### ✅ **Detecção Abrangente**
- Verifica tanto blocos quanto IPs individuais
- Detecta padrões de blacklist em diferentes níveis
- Maior cobertura de monitoramento

### ✅ **Eficiência Inteligente**
- Limitação automática para blocos muito grandes
- Estratégias diferentes por tamanho de bloco
- Evita sobrecarga do sistema

### ✅ **Resultados Unificados**
- Agrupa resultados por CIDR original
- Notificações consolidadas no Telegram
- Relatórios organizados e legíveis

## ⚙️ Configurações Avançadas

### Personalizar Limites de Verificação

Para modificar os limites, edite o arquivo `spamhaus_monitor.py`:

```python
# Exemplo: Aumentar limite de IPs por /24
def _expand_subnet_to_ips(self, subnet, limit=30):  # Era 20
```

### Ajustar Timeouts para Blocos Grandes

```yaml
monitoring:
  timeout_seconds: 45    # Aumentar para redes grandes
  interval_minutes: 90   # Intervalo maior para processar blocos
```

## 🐛 Troubleshooting

### Problema: Muitas verificações em blocos grandes

**Solução:** Ajustar limites no código ou usar blocos menores

```yaml
# Em vez de:
ips_to_monitor:
  - "10.0.0.0/16"  # Muito grande

# Use:
ips_to_monitor:
  - "10.0.0.0/24"  # Específico
  - "10.0.1.0/24"  # Controlado
```

### Problema: Timeout em verificações

**Solução:** Aumentar timeout e reduzir frequência

```yaml
monitoring:
  timeout_seconds: 60
  interval_minutes: 120
```

## 📊 Métricas e Performance

### Estimativas de Verificação

| Bloco | Sub-blocos | IPs Individuais | Total de Verificações |
|-------|------------|-----------------|----------------------|
| /22   | 6          | 80              | ~86                  |
| /23   | 2          | 40              | ~42                  |
| /24   | 0          | 254             | ~254                 |
| /25   | 0          | 126             | ~126                 |

### Tempo Estimado (com pausa de 0.3s)

| Bloco | Tempo Aproximado |
|-------|-----------------|
| /22   | ~26 segundos    |
| /23   | ~13 segundos    |
| /24   | ~76 segundos    |

## 🔄 Integração com Sistema Existente

A funcionalidade hierárquica é **totalmente compatível** com o sistema existente:

- ✅ Configurações antigas continuam funcionando
- ✅ Notificações Telegram mantêm formato unificado
- ✅ Logs e relatórios incluem informações hierárquicas
- ✅ Modo debug fornece detalhes da expansão

## 🎯 Casos de Uso Recomendados

### 1. **Monitoramento Corporativo**
```yaml
ips_to_monitor:
  - "203.0.113.0/22"    # Bloco público principal
  - "198.51.100.0/24"   # Servidores DMZ
```

### 2. **Provedores de Internet**
```yaml
ips_to_monitor:
  - "203.0.113.0/20"    # Bloco de clientes
  - "198.51.100.0/22"   # Infraestrutura
```

### 3. **Hosting/Cloud**
```yaml
ips_to_monitor:
  - "203.0.113.0/24"    # Servidores web
  - "198.51.100.0/25"   # Banco de dados
```

---

**📚 Para mais exemplos, consulte: [`docs/EXAMPLES.md`](EXAMPLES.md)**
