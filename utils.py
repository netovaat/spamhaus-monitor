#!/usr/bin/env python3
"""
Script de utilitários para o Spamhaus Monitor
"""

import argparse
import sys
from spamhaus_monitor import SpamhausMonitor


def check_single_ip(ip: str, debug: bool = False):
    """Verifica um único IP"""
    monitor = SpamhausMonitor(debug=debug)
    
    if debug:
        print(f"\n🔍 VERIFICANDO IP: {ip} (modo debug ativado)")
        print(f"📝 Blacklists configuradas: {len(monitor.config['spamhaus_lists'])}")
        for bl in monitor.config['spamhaus_lists']:
            print(f"   • {bl['name']} - {bl['zone']}")
        print("=" * 50)
    
    results = monitor.check_ip_in_spamhaus(ip)
    
    if results:
        print(f"\n🚨 IP {ip} encontrado nas seguintes blacklists:")
        for result in results:
            print(f"  • {result['blacklist']} ({result['description']})")
            print(f"    Zona: {result['zone']}")
            print(f"    Códigos: {', '.join(result['return_codes'])}")
            if debug:
                print(f"    Timestamp: {result['timestamp']}")
                print(f"    Query realizada: {monitor.reverse_ip(ip)}.{result['zone']}")
        if debug:
            print(f"\n📊 Total de blacklists onde foi encontrado: {len(results)}")
    else:
        print(f"\n✅ IP {ip} não está listado em nenhuma blacklist do Spamhaus")
        if debug:
            print(f"🔍 Verificações realizadas em {len(monitor.config['spamhaus_lists'])} blacklists")
            print(f"🌐 IP reverso usado nas consultas: {monitor.reverse_ip(ip)}")
            blacklists_checked = [f"{monitor.reverse_ip(ip)}.{bl['zone']}" for bl in monitor.config['spamhaus_lists']]
            print("📝 Consultas DNS realizadas:")
            for query in blacklists_checked:
                print(f"   • {query} -> NXDOMAIN (não listado)")


def run_single_check(debug: bool = False):
    """Executa uma única verificação de todos os IPs configurados"""
    monitor = SpamhausMonitor(debug=debug)
    results = monitor.monitor_ips()
    
    if not debug:
        # Modo normal: mostrar resumo unificado
        if results:
            unified = monitor._unify_results_by_cidr(results)
            print(f"\n🚨 {len(results)} IP(s) encontrado(s) em blacklists:")
            
            for key, data in unified.items():
                if '/' in key:
                    print(f"\n🌐 REDE: {key}")
                    print(f"   📊 IPs afetados: {len(data['ips'])}")
                else:
                    print(f"\n🔴 IP: {key}")
                
                for bl_name, affected_ips in data['blacklists'].items():
                    print(f"   📝 {bl_name}: {len(affected_ips)} IP(s)")
                    # Mostrar alguns IPs de exemplo
                    if len(affected_ips) <= 3:
                        for ip in sorted(affected_ips):
                            print(f"      • {ip}")
                    else:
                        sample_ips = sorted(list(affected_ips))[:2]
                        print(f"      • {', '.join(sample_ips)} e mais {len(affected_ips)-2}")
        else:
            print("\n✅ Todos os IPs estão limpos!")
    # Modo debug já imprime tudo no monitor_ips()


def send_test_message():
    """Envia uma mensagem de teste via Telegram"""
    monitor = SpamhausMonitor()
    test_message = "🧪 **TESTE DO SPAMHAUS MONITOR**\n\nSe você recebeu esta mensagem, o bot está funcionando corretamente!"
    monitor._send_telegram_message(test_message)
    print("Mensagem de teste enviada via Telegram")


def main():
    parser = argparse.ArgumentParser(description="Utilitários do Spamhaus Monitor")
    parser.add_argument('command', choices=['check-ip', 'run-once', 'test-telegram'], 
                       help='Comando a executar')
    parser.add_argument('--ip', help='IP para verificar (usado com check-ip)')
    parser.add_argument('--debug', '-d', action='store_true',
                       help='Modo debug com saída detalhada')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'check-ip':
            if not args.ip:
                print("Erro: --ip é obrigatório para o comando check-ip")
                sys.exit(1)
            check_single_ip(args.ip, debug=args.debug)
        
        elif args.command == 'run-once':
            run_single_check(debug=args.debug)
        
        elif args.command == 'test-telegram':
            send_test_message()
            
    except Exception as e:
        print(f"Erro: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
