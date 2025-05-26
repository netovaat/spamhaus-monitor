#!/usr/bin/env python3
"""
Spamhaus Monitor - Sistema de monitoramento de IPs em blacklists do Spamhaus
"""

import dns.resolver
import ipaddress
import logging
import time
import schedule
import yaml
import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Set
from telegram import Bot
from telegram.error import TelegramError
import json
import os
import sys
from collections import defaultdict


class SpamhausMonitor:
    """Classe principal para monitoramento do Spamhaus"""
    
    def __init__(self, config_path: str = "config.yaml", debug: bool = False):
        """Inicializa o monitor com configurações do arquivo YAML"""
        self.config = self._load_config(config_path)
        self.debug = debug
        self._setup_logging()
        self.bot = Bot(token=self.config['telegram']['bot_token'])
        self.chat_id = self.config['telegram']['chat_id']
        self.previous_results = self._load_previous_results()
        self.original_networks = self._parse_original_networks()
        
    def _load_config(self, config_path: str) -> dict:
        """Carrega configurações do arquivo YAML"""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Erro ao ler arquivo de configuração: {e}")
    
    def _setup_logging(self):
        """Configura o sistema de logging"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', 'spamhaus_monitor.log')
        
        # Configurar rotating file handler
        from logging.handlers import RotatingFileHandler
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=log_config.get('max_size_mb', 10) * 1024 * 1024,
            backupCount=log_config.get('backup_count', 5)
        )
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Configure logger
        self.logger = logging.getLogger('SpamhausMonitor')
        self.logger.setLevel(log_level)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def _load_previous_results(self) -> dict:
        """Carrega resultados anteriores para comparação"""
        try:
            with open('previous_results.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_results(self, results: dict):
        """Salva resultados atuais para próxima comparação"""
        with open('previous_results.json', 'w') as f:
            json.dump(results, f, indent=2)
    
    def reverse_ip(self, ip: str) -> str:
        """Inverte um endereço IP para consulta DNS reversa"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.version == 4:
                parts = str(ip_obj).split('.')
                return '.'.join(reversed(parts))
            else:
                # IPv6 não suportado nesta versão
                return None
        except ValueError:
            return None
    
    def check_ip_in_spamhaus(self, ip: str) -> List[Dict]:
        """Verifica se um IP está listado em alguma blacklist do Spamhaus"""
        results = []
        reversed_ip = self.reverse_ip(ip)
        
        if not reversed_ip:
            self.logger.warning(f"Não foi possível processar o IP: {ip}")
            return results
        
        if self.debug:
            self.logger.debug(f"Verificando IP {ip} (reverso: {reversed_ip})")
        
        for bl_config in self.config['spamhaus_lists']:
            bl_name = bl_config['name']
            bl_zone = bl_config['zone']
            bl_description = bl_config['description']
            
            query = f"{reversed_ip}.{bl_zone}"
            
            if self.debug:
                self.logger.debug(f"Consultando: {query}")
            
            try:
                resolver = dns.resolver.Resolver()
                resolver.timeout = self.config['monitoring']['timeout_seconds']
                
                answers = resolver.resolve(query, 'A')
                
                # Se chegou aqui, o IP está listado
                return_codes = [str(answer) for answer in answers]
                
                result = {
                    'ip': ip,
                    'blacklist': bl_name,
                    'zone': bl_zone,
                    'description': bl_description,
                    'listed': True,
                    'return_codes': return_codes,
                    'timestamp': datetime.now().isoformat()
                }
                
                results.append(result)
                self.logger.info(f"IP {ip} encontrado em {bl_name} ({bl_zone})")
                if self.debug:
                    self.logger.debug(f"Retorno da consulta {query}: {return_codes}")
                
            except dns.resolver.NXDOMAIN:
                # IP não está listado nesta blacklist
                if self.debug:
                    self.logger.debug(f"NXDOMAIN para {query} - não listado")
                continue
            except dns.resolver.Timeout:
                self.logger.warning(f"Timeout ao verificar {ip} em {bl_name}")
                if self.debug:
                    self.logger.debug(f"Timeout na consulta {query}")
                continue
            except Exception as e:
                self.logger.error(f"Erro ao verificar {ip} em {bl_name}: {e}")
                if self.debug:
                    self.logger.debug(f"Erro na consulta {query}: {e}")
                continue
        
        return results
    
    def expand_network_hierarchical(self, network_str: str) -> List[str]:
        """Expande uma rede CIDR hierarquicamente em sub-blocos menores"""
        try:
            network = ipaddress.ip_network(network_str, strict=False)
            ips_to_check = []
            
            if self.debug:
                self.logger.debug(f"Iniciando expansão hierárquica de {network_str} (/{network.prefixlen})")
            
            # Para blocos muito grandes (/16 ou menores), expandir apenas alguns sub-blocos
            if network.prefixlen <= 16:
                if self.debug:
                    self.logger.debug(f"Bloco {network_str} muito grande, verificando apenas alguns sub-blocos")
                # Dividir em /24 e verificar apenas os primeiros 10
                subnets = list(network.subnets(new_prefix=24))[:10]
                for subnet in subnets:
                    ips_to_check.extend(self._expand_subnet_to_ips(subnet, limit=5))
                return ips_to_check
            
            # Para blocos /17 a /21, dividir em sub-blocos menores
            elif network.prefixlen <= 21:
                if self.debug:
                    self.logger.debug(f"Expandindo {network_str} em sub-blocos /24")
                subnets = list(network.subnets(new_prefix=24))
                for subnet in subnets:
                    ips_to_check.extend(self._expand_subnet_to_ips(subnet, limit=10))
                return ips_to_check
            
            # Para blocos /22 e /23, fazer expansão hierárquica completa
            elif network.prefixlen <= 23:
                if self.debug:
                    self.logger.debug(f"Expansão hierárquica completa para {network_str}")
                
                # Primeiro verificar sub-blocos maiores
                if network.prefixlen < 23:
                    # Dividir em /23
                    for subnet_23 in network.subnets(new_prefix=23):
                        ips_to_check.append(str(subnet_23))
                        if self.debug:
                            self.logger.debug(f"Adicionando sub-bloco /23: {subnet_23}")
                
                # Depois dividir em /24
                for subnet_24 in network.subnets(new_prefix=24):
                    ips_to_check.append(str(subnet_24))
                    if self.debug:
                        self.logger.debug(f"Adicionando sub-bloco /24: {subnet_24}")
                
                # Finalmente verificar alguns IPs individuais de cada /24
                for subnet_24 in network.subnets(new_prefix=24):
                    individual_ips = self._expand_subnet_to_ips(subnet_24, limit=20)
                    ips_to_check.extend(individual_ips)
                
                return ips_to_check
            
            # Para blocos /24 e menores, verificar todos os IPs
            else:
                return self._expand_subnet_to_ips(network)
                
        except ValueError as e:
            self.logger.error(f"Erro ao processar rede {network_str}: {e}")
            return []
    
    def _expand_subnet_to_ips(self, subnet, limit=None) -> List[str]:
        """Expande uma subnet em lista de IPs individuais"""
        ips = []
        for i, ip in enumerate(subnet.hosts()):
            if limit and i >= limit:
                break
            ips.append(str(ip))
        
        if self.debug and limit and len(list(subnet.hosts())) > limit:
            self.logger.debug(f"Limitando verificação de {subnet} a {limit} IPs (total: {subnet.num_addresses-2})")
        
        return ips
    
    def expand_network(self, network_str: str) -> List[str]:
        """Expande uma rede CIDR em lista de IPs (método antigo para compatibilidade)"""
        try:
            network = ipaddress.ip_network(network_str, strict=False)
            
            # Limitar a expansão para evitar sobrecarga
            if network.num_addresses > 256:
                self.logger.warning(f"Rede {network_str} muito grande, verificando apenas alguns IPs")
                # Verificar apenas alguns IPs da rede
                ips = []
                for i, ip in enumerate(network.hosts()):
                    if i >= 10:  # Limitar a 10 IPs
                        break
                    ips.append(str(ip))
                return ips
            else:
                return [str(ip) for ip in network.hosts()]
                
        except ValueError as e:
            self.logger.error(f"Erro ao processar rede {network_str}: {e}")
            return []
    
    def monitor_ips(self) -> Dict:
        """Monitora todos os IPs configurados"""
        self.logger.info("Iniciando verificação de IPs no Spamhaus")
        
        all_results = {}
        ips_to_check = []
        
        # Expandir IPs e redes com pesquisa hierárquica
        for ip_or_network in self.config['ips_to_monitor']:
            if '/' in ip_or_network:
                # É uma rede - usar expansão hierárquica
                if self.debug:
                    self.logger.debug(f"Processando rede: {ip_or_network}")
                hierarchical_ips = self.expand_network_hierarchical(ip_or_network)
                ips_to_check.extend(hierarchical_ips)
                if self.debug:
                    self.logger.debug(f"Rede {ip_or_network} expandida em {len(hierarchical_ips)} itens para verificação")
            else:
                # É um IP individual
                ips_to_check.append(ip_or_network)
        
        if self.debug:
            self.logger.debug(f"Total de {len(ips_to_check)} itens para verificação (incluindo sub-blocos e IPs)")
        
        # Verificar cada IP/bloco
        for ip in ips_to_check:
            if self.debug:
                self.logger.debug(f"Verificando: {ip}")
            
            results = self.check_ip_in_spamhaus(ip)
            if results:
                all_results[ip] = results
                if self.debug:
                    self.logger.debug(f"ENCONTRADO em blacklist: {ip} -> {[r['blacklist'] for r in results]}")
            elif self.debug:
                # No modo debug, também registrar IPs limpos
                all_results[ip] = []
                self.logger.debug(f"Limpo: {ip}")
            
            # Pequena pausa entre verificações para evitar rate limiting
            time.sleep(0.3)
        
        # Unificar resultados por CIDR original
        unified_results = self._unify_results_by_cidr({k: v for k, v in all_results.items() if v})
        
        # Modo debug: mostrar resultados detalhados
        if self.debug:
            self._print_debug_results({k: v for k, v in all_results.items() if v}, unified_results)
        
        # Salvar resultados (apenas IPs com problemas)
        results_to_save = {k: v for k, v in all_results.items() if v}
        self._save_results(results_to_save)
        
        # Verificar mudanças e enviar notificações apenas se necessário
        if self._should_send_telegram_notification(results_to_save, self.previous_results):
            self._check_changes_and_notify_unified(results_to_save, unified_results)
        
        self.logger.info(f"Verificação concluída. {len(results_to_save)} IPs/blocos encontrados em blacklists")
        return results_to_save
    
    def _check_changes_and_notify(self, current_results: Dict):
        """Verifica mudanças em relação à verificação anterior e envia notificações"""
        # Novos IPs listados
        for ip, results in current_results.items():
            if ip not in self.previous_results:
                # IP recém-listado
                self._send_alert(ip, results, "NOVO")
            else:
                # Verificar se há novas blacklists
                previous_bls = {r['blacklist'] for r in self.previous_results[ip]}
                current_bls = {r['blacklist'] for r in results}
                new_bls = current_bls - previous_bls
                
                if new_bls:
                    new_results = [r for r in results if r['blacklist'] in new_bls]
                    self._send_alert(ip, new_results, "NOVA_BLACKLIST")
        
        # IPs removidos das blacklists
        for ip in self.previous_results:
            if ip not in current_results:
                self._send_removal_alert(ip)
        
        self.previous_results = current_results.copy()
    
    def _send_alert(self, ip: str, results: List[Dict], alert_type: str):
        """Envia alerta via Telegram"""
        if alert_type == "NOVO":
            title = f"🚨 NOVO IP LISTADO: {ip}"
        else:
            title = f"⚠️ NOVA BLACKLIST: {ip}"
        
        message = f"{title}\n\n"
        
        for result in results:
            message += f"📝 **Blacklist:** {result['blacklist']} ({result['description']})\n"
            message += f"🌐 **Zona:** {result['zone']}\n"
            message += f"📊 **Códigos:** {', '.join(result['return_codes'])}\n"
            message += f"⏰ **Timestamp:** {result['timestamp']}\n\n"
        
        self._send_telegram_message(message)
    
    def _send_removal_alert(self, ip: str):
        """Envia alerta de remoção via Telegram"""
        message = f"✅ IP REMOVIDO DAS BLACKLISTS: {ip}\n\n"
        message += f"⏰ Verificado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self._send_telegram_message(message)
    
    def _send_telegram_message(self, message: str):
        """Envia mensagem via Telegram"""
        try:
            asyncio.create_task(self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            ))
            self.logger.info("Notificação enviada via Telegram")
        except TelegramError as e:
            self.logger.error(f"Erro ao enviar notificação Telegram: {e}")
        except Exception as e:
            self.logger.error(f"Erro inesperado ao enviar Telegram: {e}")
    
    def send_status_report(self):
        """Envia relatório de status atual"""
        # Temporariamente desabilitar debug para relatórios
        original_debug = self.debug
        self.debug = False
        
        results = self.monitor_ips()
        
        # Restaurar debug
        self.debug = original_debug
        
        if not results:
            message = "✅ **RELATÓRIO SPAMHAUS**\n\n"
            message += "Todos os IPs monitorados estão limpos! 🎉\n\n"
            message += f"⏰ Verificado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            unified_results = self._unify_results_by_cidr(results)
            message = f"🚨 **RELATÓRIO SPAMHAUS**\n\n"
            message += f"**{len(results)} IP(s) encontrado(s) em blacklists:**\n\n"
            
            for key, data in unified_results.items():
                if '/' in key:
                    message += f"🌐 **Rede:** {key}\n"
                    message += f"📊 **IPs afetados:** {len(data['ips'])}\n"
                else:
                    message += f"🔴 **IP:** {key}\n"
                
                for bl_name, affected_ips in data['blacklists'].items():
                    message += f"  📝 {bl_name}: {len(affected_ips)} IP(s)\n"
                
                message += "\n"
            
            message += f"⏰ Verificado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self._send_telegram_message(message)
    
    def run_continuous_monitoring(self):
        """Executa monitoramento contínuo"""
        interval = self.config['monitoring']['interval_minutes']
        
        # Agendar verificações
        schedule.every(interval).minutes.do(self.monitor_ips)
        
        # Relatório diário às 9:00
        schedule.every().day.at("09:00").do(self.send_status_report)
        
        self.logger.info(f"Monitoramento iniciado. Verificações a cada {interval} minutos")
        
        # Executar primeira verificação
        self.monitor_ips()
        
        # Loop principal
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar schedule a cada minuto
        except KeyboardInterrupt:
            self.logger.info("Monitoramento interrompido pelo usuário")
        except Exception as e:
            self.logger.error(f"Erro no monitoramento: {e}")
    
    def _parse_original_networks(self) -> Dict[str, ipaddress.IPv4Network]:
        """Parseia as redes originais configuradas para mapeamento CIDR"""
        networks = {}
        for ip_or_network in self.config['ips_to_monitor']:
            if '/' in ip_or_network:
                try:
                    network = ipaddress.ip_network(ip_or_network, strict=False)
                    networks[ip_or_network] = network
                except ValueError:
                    self.logger.warning(f"Rede inválida ignorada: {ip_or_network}")
        return networks
    
    def _find_matching_network(self, ip: str) -> Optional[str]:
        """Encontra qual rede CIDR original contém este IP"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            for cidr_str, network in self.original_networks.items():
                if ip_obj in network:
                    return cidr_str
        except ValueError:
            pass
        return None
    
    def _unify_results_by_cidr(self, results: Dict) -> Dict:
        """Unifica resultados agrupando IPs por suas redes CIDR originais"""
        unified = defaultdict(lambda: {
            'ips': set(),
            'blocks': set(),  # Para rastrear sub-blocos encontrados
            'blacklists': defaultdict(set),
            'details': []
        })
        
        for ip_or_block, ip_results in results.items():
            # Determinar se é um IP individual ou um bloco CIDR
            if '/' in ip_or_block:
                # É um bloco CIDR - tentar encontrar o CIDR original que o contém
                cidr = self._find_matching_network_for_block(ip_or_block)
                key = cidr if cidr else ip_or_block
                unified[key]['blocks'].add(ip_or_block)
            else:
                # É um IP individual - encontrar a rede CIDR original
                cidr = self._find_matching_network(ip_or_block)
                key = cidr if cidr else ip_or_block
                unified[key]['ips'].add(ip_or_block)
            
            for result in ip_results:
                bl_name = result['blacklist']
                unified[key]['blacklists'][bl_name].add(ip_or_block)
                unified[key]['details'].append(result)
        
        # Converter sets para listas para serialização
        for key in unified:
            unified[key]['ips'] = sorted(list(unified[key]['ips']))
            unified[key]['blocks'] = sorted(list(unified[key]['blocks']))
            for bl in unified[key]['blacklists']:
                unified[key]['blacklists'][bl] = sorted(list(unified[key]['blacklists'][bl]))
        
        return dict(unified)
    
    def _find_matching_network_for_block(self, block_str: str) -> Optional[str]:
        """Encontra qual rede CIDR original contém este bloco CIDR"""
        try:
            block = ipaddress.ip_network(block_str, strict=False)
            for cidr_str, network in self.original_networks.items():
                # Verificar se o bloco está contido na rede original
                if block.subnet_of(network):
                    return cidr_str
        except ValueError:
            pass
        return None
    
    def _print_debug_results(self, results: Dict, unified_results: Dict):
        """Imprime resultados detalhados no modo debug"""
        if not results and not unified_results:
            print("\n✅ Todos os IPs monitorados estão limpos!")
            return
        
        print(f"\n🔍 RESULTADOS DETALHADOS (DEBUG MODE)")
        print("=" * 60)
        
        # Mostrar resultados unificados por CIDR
        for key, data in unified_results.items():
            if '/' in key:
                print(f"\n🌐 REDE ORIGINAL: {key}")
                print(f"   📊 IPs individuais afetados: {len(data['ips'])}")
                print(f"   📦 Sub-blocos afetados: {len(data['blocks'])}")
                
                # Listar sub-blocos afetados
                if data['blocks']:
                    print(f"   🔶 Sub-blocos CIDR em blacklist:")
                    for block in data['blocks']:
                        print(f"      • {block}")
                
                # Listar IPs individuais afetados
                if data['ips']:
                    print(f"   🔴 IPs individuais em blacklist:")
                    for ip in data['ips']:
                        print(f"      • {ip}")
            else:
                print(f"\n🔴 IP INDIVIDUAL: {key}")
            
            # Mostrar blacklists e IPs/blocos afetados
            for bl_name, affected_items in data['blacklists'].items():
                print(f"   📝 {bl_name}: {len(affected_items)} item(s)")
                if self.debug:
                    for item in affected_items:
                        # Encontrar detalhes específicos
                        item_details = [d for d in data['details'] if d['ip'] == item and d['blacklist'] == bl_name]
                        if item_details:
                            detail = item_details[0]
                            item_type = "BLOCO" if '/' in item else "IP"
                            print(f"      • {item_type}: {item} -> {', '.join(detail['return_codes'])}")
        
        print("\n" + "=" * 60)
        total_blacklists = len(set().union(*[d['blacklists'].keys() for d in unified_results.values()]))
        total_ips = sum(len(d['ips']) for d in unified_results.values())
        total_blocks = sum(len(d['blocks']) for d in unified_results.values())
        print(f"📈 RESUMO: {total_ips} IP(s) e {total_blocks} bloco(s) listados em {total_blacklists} blacklist(s)")
        print(f"🎯 Itens únicos verificados: {len(results)}")
        print(f"🌐 Redes CIDR originais afetadas: {len([k for k in unified_results.keys() if '/' in k])}")
    
    def _should_send_telegram_notification(self, current_results: Dict, previous_results: Dict) -> bool:
        """Determina se deve enviar notificação do Telegram baseado em mudanças"""
        # Enviar se houver novos IPs listados ou novas blacklists
        for ip, results in current_results.items():
            if ip not in previous_results:
                return True  # Novo IP listado
            
            # Verificar novas blacklists para IP existente
            previous_bls = {r['blacklist'] for r in previous_results[ip]}
            current_bls = {r['blacklist'] for r in results}
            if current_bls - previous_bls:
                return True  # Nova blacklist para IP existente
        
        # Verificar IPs removidos (também notificar)
        if set(previous_results.keys()) - set(current_results.keys()):
            return True
        
        return False
    
    def _check_changes_and_notify_unified(self, current_results: Dict, unified_results: Dict):
        """Verifica mudanças e envia notificações unificadas por CIDR"""
        # Verificar novos IPs ou novas blacklists
        new_listings = {}
        new_blacklists = {}
        
        for ip, results in current_results.items():
            if ip not in self.previous_results:
                # IP recém-listado
                new_listings[ip] = results
            else:
                # Verificar se há novas blacklists
                previous_bls = {r['blacklist'] for r in self.previous_results[ip]}
                current_bls = {r['blacklist'] for r in results}
                new_bls = current_bls - previous_bls
                
                if new_bls:
                    new_results = [r for r in results if r['blacklist'] in new_bls]
                    new_blacklists[ip] = new_results
        
        # Enviar notificações unificadas para novos listings
        if new_listings:
            self._send_unified_alert(new_listings, unified_results, "NOVO")
        
        # Enviar notificações unificadas para novas blacklists
        if new_blacklists:
            self._send_unified_alert(new_blacklists, unified_results, "NOVA_BLACKLIST")
        
        # IPs removidos das blacklists
        removed_ips = set(self.previous_results.keys()) - set(current_results.keys())
        if removed_ips:
            self._send_unified_removal_alert(removed_ips)
        
        # Atualizar cache em memória e arquivo
        self.previous_results = current_results.copy()
        self._save_results(current_results)
    
    def _send_unified_alert(self, affected_items: Dict, unified_results: Dict, alert_type: str):
        """Envia alerta unificado via Telegram"""
        if alert_type == "NOVO":
            title = "🚨 NOVOS ITENS LISTADOS EM BLACKLISTS"
        else:
            title = "⚠️ NOVAS BLACKLISTS DETECTADAS"
        
        message = f"{title}\n\n"
        
        # Agrupar por CIDR para a notificação usando dados unificados
        processed_cidrs = set()
        
        for key, data in unified_results.items():
            # Verificar se algum item afetado pertence a este CIDR
            has_affected_items = False
            for item in affected_items.keys():
                if key == item or (('/' in key) and self._item_belongs_to_cidr(item, key)):
                    has_affected_items = True
                    break
            
            if not has_affected_items:
                continue
                
            if key in processed_cidrs:
                continue
            processed_cidrs.add(key)
            
            if '/' in key:
                message += f"🌐 **Rede:** {key}\n"
                total_affected = len(data['ips']) + len(data['blocks'])
                message += f"📊 **Itens afetados:** {total_affected}\n"
                
                if data['blocks']:
                    message += f"📦 **Sub-blocos listados:** {len(data['blocks'])}\n"
                    for block in sorted(data['blocks'])[:3]:  # Mostrar apenas 3 primeiros
                        message += f"   • {block}\n"
                    if len(data['blocks']) > 3:
                        message += f"   • ... e mais {len(data['blocks']) - 3} blocos\n"
                
                if data['ips']:
                    message += f"🔴 **IPs individuais:** {len(data['ips'])}\n"
                    for ip in sorted(data['ips'])[:5]:  # Mostrar apenas 5 primeiros
                        message += f"   • {ip}\n"
                    if len(data['ips']) > 5:
                        message += f"   • ... e mais {len(data['ips']) - 5} IPs\n"
            else:
                message += f"🔴 **IP Individual:** {key}\n"
            
            # Listar blacklists
            message += f"📝 **Blacklists:** {', '.join(data['blacklists'].keys())}\n\n"
        
        message += f"⏰ **Detectado em:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self._send_telegram_message(message)
    
    def _item_belongs_to_cidr(self, item: str, cidr: str) -> bool:
        """Verifica se um IP ou bloco pertence a um CIDR"""
        try:
            if '/' in item:
                # Item é um bloco CIDR
                item_net = ipaddress.ip_network(item, strict=False)
                cidr_net = ipaddress.ip_network(cidr, strict=False)
                return item_net.subnet_of(cidr_net)
            else:
                # Item é um IP individual
                ip = ipaddress.ip_address(item)
                network = ipaddress.ip_network(cidr, strict=False)
                return ip in network
        except ValueError:
            return False
            for bl_name, affected_ips_in_bl in data['blacklists'].items():
                message += f"  📝 {bl_name}: {len(affected_ips_in_bl)} IP(s)\n"
                
                # No Telegram, não listar todos os IPs para evitar spam
                if len(affected_ips_in_bl) <= 3:
                    for ip in sorted(affected_ips_in_bl):
                        message += f"    • {ip}\n"
                else:
                    sample_ips = sorted(list(affected_ips_in_bl))[:2]
                    message += f"    • {', '.join(sample_ips)} e mais {len(affected_ips_in_bl)-2}\n"
            
            message += "\n"
        
        message += f"⏰ Detectado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self._send_telegram_message(message)
    
    def _send_unified_removal_alert(self, removed_ips: Set[str]):
        """Envia alerta unificado de remoção via Telegram"""
        message = f"✅ IPs REMOVIDOS DAS BLACKLISTS\n\n"
        
        # Agrupar por CIDR
        cidr_groups = defaultdict(set)
        for ip in removed_ips:
            cidr = self._find_matching_network(ip)
            key = cidr if cidr else ip
            cidr_groups[key].add(ip)
        
        for key, ips in cidr_groups.items():
            if '/' in key:
                message += f"🌐 **Rede:** {key}\n"
                message += f"📊 **IPs limpos:** {len(ips)}\n"
            else:
                message += f"✅ **IP:** {key}\n"
            
            if len(ips) <= 5:
                for ip in sorted(ips):
                    message += f"  • {ip}\n"
            else:
                sample_ips = sorted(list(ips))[:3]
                message += f"  • {', '.join(sample_ips)} e mais {len(ips)-3}\n"
            
            message += "\n"
        
        message += f"⏰ Verificado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self._send_telegram_message(message)
    
def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Spamhaus Monitor - Monitoramento de blacklists")
    parser.add_argument('--debug', '-d', action='store_true', 
                       help='Modo debug com saída detalhada')
    parser.add_argument('--config', '-c', default='config.yaml',
                       help='Arquivo de configuração (padrão: config.yaml)')
    parser.add_argument('--run-once', action='store_true',
                       help='Executar uma única verificação e sair')
    
    args = parser.parse_args()
    
    try:
        monitor = SpamhausMonitor(config_path=args.config, debug=args.debug)
        
        if args.run_once:
            # Executar uma única verificação
            results = monitor.monitor_ips()
            if not args.debug and results:
                print(f"\n🚨 {len(results)} IP(s) encontrado(s) em blacklists")
                # Mostrar resumo unificado mesmo fora do debug
                unified = monitor._unify_results_by_cidr(results)
                for key, data in unified.items():
                    if '/' in key:
                        print(f"🌐 Rede {key}: {len(data['ips'])} IP(s)")
                    else:
                        print(f"🔴 IP {key}")
                    for bl in data['blacklists']:
                        print(f"  • {bl}: {len(data['blacklists'][bl])} IP(s)")
            elif not args.debug:
                print("\n✅ Todos os IPs estão limpos!")
        else:
            # Monitoramento contínuo
            monitor.run_continuous_monitoring()
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Monitoramento interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro ao iniciar o monitor: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
