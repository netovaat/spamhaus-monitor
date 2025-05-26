# Blacklists do Spamhaus - Referência

## 📚 Sobre as Blacklists

### SBL (Spamhaus Block List)
- **Zona:** sbl.spamhaus.org
- **Descrição:** Lista principal de IPs de spam conhecido
- **Conteúdo:** 
  - Servidores de spam identificados
  - Redes comprometidas conhecidas por enviar spam
  - IPs de botnet controllers

### XBL (Exploits Block List)  
- **Zona:** xbl.spamhaus.org
- **Descrição:** Lista de IPs com malware ou comprometidos
- **Conteúdo:**
  - Máquinas infectadas com malware
  - Servidores proxy abertos
  - IPs de botnet
  - Sistemas comprometidos

### PBL (Policy Block List)
- **Zona:** pbl.spamhaus.org  
- **Descrição:** Lista de blocos de IP que não deveriam enviar email
- **Conteúdo:**
  - Ranges de IP dinâmicos de ISPs
  - Blocos residenciais
  - IPs que não são servidores de email legítimos

### CSS (Composite Screening Service)
- **Zona:** css.spamhaus.org
- **Descrição:** Serviço combinado de todas as listas
- **Conteúdo:**
  - Combinação de SBL + XBL + PBL
  - Verificação unificada

## 🔍 Códigos de Retorno

Quando um IP é encontrado em uma blacklist, o DNS retorna códigos específicos:

### SBL Codes
- `127.0.0.2` - SBL CSS (spammer)
- `127.0.0.3` - SBL CSS (spammer)  
- `127.0.0.4` - SBL CSS (spammer)
- `127.0.0.9` - SBL CSS (spammer)
- `127.0.0.10` - PBL ISP Maintained
- `127.0.0.11` - PBL Spamhaus Maintained

### XBL Codes
- `127.0.0.4` - CBL (Composite Block List)
- `127.0.0.9` - CBL (Composite Block List)
- `127.0.0.10` - PBL ISP Maintained 
- `127.0.0.11` - PBL Spamhaus Maintained

### Interpretação Geral
- `127.0.0.2-127.0.0.9` = Listado em SBL (spam ativo)
- `127.0.0.10` = PBL ISP (política do ISP)
- `127.0.0.11` = PBL Spamhaus (política Spamhaus)

## ⚠️ Ações Recomendadas

### Se um IP próprio está listado:

1. **Investigar imediatamente:**
   - Verificar se há malware no sistema
   - Examinar logs de email/rede
   - Procurar por atividade suspeita

2. **Limpar o sistema:**
   - Remover malware se encontrado
   - Fechar portas/serviços desnecessários
   - Atualizar sistemas e patches

3. **Solicitar remoção:**
   - Acesse: https://www.spamhaus.org/lookup/
   - Siga o processo de deslisting
   - Aguarde remoção (pode levar algumas horas)

### Se um IP externo está listado:

1. **Bloquear tráfego:**
   - Implementar regras de firewall
   - Bloquear em proxies/gateways
   - Monitorar tentativas de conexão

2. **Documentar:**
   - Registrar quando foi detectado
   - Manter histórico de IPs problemáticos
   - Reportar se necessário

## 🔗 Links Úteis

- **Lookup Manual:** https://www.spamhaus.org/lookup/
- **Política de Deslisting:** https://www.spamhaus.org/sbl/removal/
- **FAQ:** https://www.spamhaus.org/faq/
- **Status do Serviço:** https://status.spamhaus.org/

## 📊 Estatísticas (Aproximadas)

- **SBL:** ~450,000 IPs listados
- **XBL:** ~15 milhões de IPs
- **PBL:** ~2 bilhões de IPs
- **Atualizações:** Em tempo real
- **Cobertura:** Global

## ⏱️ Tempos de Resposta

- **Consulta DNS:** < 100ms típico
- **Timeout recomendado:** 5-10 segundos
- **Rate limiting:** ~100 consultas/minuto por IP

## 🛡️ Boas Práticas

1. **Não abuse:** Respeite os limites de consulta
2. **Cache responsável:** Não consulte o mesmo IP repetidamente
3. **Use múltiplas fontes:** Combine com outras blacklists
4. **Monitore mudanças:** IPs podem ser adicionados/removidos rapidamente
5. **Automatize:** Use ferramentas como este monitor para acompanhamento contínuo
