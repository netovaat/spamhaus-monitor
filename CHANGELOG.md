# Changelog - Spamhaus Monitor

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [1.0.0] - 2025-05-26

### 🆕 Adicionado
- **Sistema Base de Monitoramento**: Monitoramento contínuo de IPs e blocos nas blacklists do Spamhaus
- **Pesquisa Hierárquica CIDR**: Sistema avançado de expansão de blocos de rede
  - Blocos /22 → 2 sub-blocos /23 + 4 sub-blocos /24 + até 80 IPs individuais
  - Blocos /23 → 2 sub-blocos /24 + até 40 IPs individuais
  - Blocos /24 → até 256 IPs individuais
- **Integração Telegram**: Notificações em tempo real via bot do Telegram
- **Múltiplas Blacklists**: Verificação em SBL, XBL, PBL, CSS do Spamhaus
- **Modo Debug Verbose**: Saída detalhada para análise e troubleshooting
- **Notificações Unificadas por CIDR**: Agrupamento inteligente de resultados
- **Detecção de Mudanças**: Notificações apenas quando há alterações
- **Sistema de Logging**: Logs rotativos com níveis configuráveis
- **Monitoramento Contínuo**: Agendamento automático com schedule
- **Script de Backup**: Sistema automatizado de backup
- **Configuração Flexível**: Configuração via arquivos YAML
- **Serviço Systemd**: Execução como serviço do sistema
- **Scripts de Instalação**: Instalação automatizada
- **Unificação de Resultados**: IPs agrupados por CIDR original para relatórios limpos
- **Performance Otimizada**: Rate limiting e timeouts configuráveis
- **CLI Avançada**: Argumentos `--debug`, `--config`, `--run-once`
- **Estrutura Organizada**: Arquivos e documentação bem estruturados
- **Implementação Técnica**:
  - Classe `SpamhausMonitor` com modo debug
  - Métodos `expand_network_hierarchical()` para expansão CIDR
  - Sistema `_unify_results_by_cidr()` para agrupamento inteligente
  - Logging com `RotatingFileHandler`
  - Argumentos CLI com `argparse`
- **Documentação Completa**:
  - **INSTALLATION.md**: Guia completo de instalação
  - **HIERARCHICAL_SEARCH.md**: Documentação da pesquisa hierárquica  
  - **EXAMPLES.md**: Exemplos práticos de uso
  - **BLACKLISTS.md**: Referência das blacklists do Spamhaus
  - **README.md**: Documentação principal completa

---

**Formato**: [Semantic Versioning](https://semver.org/)
**Tipos**: 🆕 Adicionado
