#!/usr/bin/python3
#! encoding: utf-8

'''
WifiMage - Wireless Network Interface Management Tool
Author: Br3noAraujo
Version: 4.0
'''

import os
import sys
import subprocess
import argparse
import json
import time
import threading
import signal
from typing import Optional, Dict, List, Set
from colorama import Fore, Style, init
from datetime import datetime

# Initialize colorama
init(autoreset=True)

class WifiMage:
    def __init__(self):
        self.original_interface: Optional[str] = None
        self.current_interface: Optional[str] = None
        self.scan_results: List[Dict] = []
        self.interface_info: Dict = {}
        self.monitoring: bool = False
        self.known_networks: Set[str] = set()
        self.connected_clients: Dict[str, List[str]] = {}
        self.running: bool = True

    def run_command(self, command: str) -> bool:
        """Execute a system command and return True if successful."""
        try:
            subprocess.run(command, shell=True, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Error executing command: {command}")
            print(f"{Fore.RED}Error: {e.stderr.decode()}")
            return False

    def get_command_output(self, command: str) -> str:
        """Execute a command and return its output."""
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Error executing command: {command}")
            print(f"{Fore.RED}Error: {e.stderr.decode()}")
            return ""

    def banner(self) -> None:
        """Display the program banner."""
        print(f'''
            {Fore.LIGHTGREEN_EX},   {Fore.LIGHTYELLOW_EX} _
           {Fore.LIGHTGREEN_EX}/|   {Fore.LIGHTYELLOW_EX}| |
        {Fore.LIGHTGREEN_EX} _/_\_ {Fore.YELLOW} >_<
        {Fore.GREEN}.-{Fore.WHITE}\-/{Fore.GREEN}.   {Fore.YELLOW}|
       {Fore.GREEN}/  {Fore.WHITE}| |{Fore.GREEN} \_ {Fore.YELLOW}|    TAA DAAAH!!!
       {Fore.GREEN}\ \{Fore.WHITE}| |{Fore.GREEN}\__(/      I'M WIFI MAGE
       /{Fore.LIGHTRED_EX}(`---')  {Fore.YELLOW}|
      {Fore.GREEN}/ {Fore.LIGHTRED_EX}/     \  {Fore.YELLOW}|
   {Fore.GREEN}_.'  {Fore.LIGHTRED_EX}\\'-'  /  {Fore.YELLOW}|
   {Fore.GREEN}`----'{Fore.LIGHTRED_EX}`=-='   {Fore.YELLOW}|   by Br3noAraujo ''')

    def check_interface_exists(self, iface: str) -> bool:
        """Check if the interface exists in the system."""
        result = subprocess.run(f"ip link show {iface}", shell=True, capture_output=True)
        return result.returncode == 0

    def get_interface_info(self, iface: str) -> None:
        """Get detailed information about the interface."""
        if not self.check_interface_exists(iface):
            print(f"{Fore.RED}Interface {iface} not found!")
            return

        self.interface_info = {
            'name': iface,
            'status': self.get_command_output(f"ip link show {iface} | grep -o 'state [A-Z]*' | cut -d' ' -f2"),
            'mac': self.get_command_output(f"ip link show {iface} | grep -o 'ether [0-9a-f:]*' | cut -d' ' -f2"),
            'mode': self.get_command_output(f"iwconfig {iface} 2>/dev/null | grep -o 'Mode:[A-Z]*' | cut -d':' -f2"),
            'channel': self.get_command_output(f"iwconfig {iface} 2>/dev/null | grep -o 'Channel [0-9]*' | cut -d' ' -f2"),
            'frequency': self.get_command_output(f"iwconfig {iface} 2>/dev/null | grep -o 'Frequency=[0-9.]* GHz' | cut -d'=' -f2"),
            'signal': self.get_command_output(f"iwconfig {iface} 2>/dev/null | grep -o 'Signal level=[-0-9]* dBm' | cut -d'=' -f2")
        }

    def show_interface_info(self, iface: str) -> None:
        """Display detailed information about the interface."""
        self.get_interface_info(iface)
        self.banner()
        print(f"{Fore.YELLOW}Interface Information for {Fore.LIGHTCYAN_EX}{iface}{Fore.YELLOW}:")
        print(f"{Fore.GREEN}Status: {Fore.WHITE}{self.interface_info.get('status', 'N/A')}")
        print(f"{Fore.GREEN}MAC Address: {Fore.WHITE}{self.interface_info.get('mac', 'N/A')}")
        print(f"{Fore.GREEN}Mode: {Fore.WHITE}{self.interface_info.get('mode', 'N/A')}")
        print(f"{Fore.GREEN}Channel: {Fore.WHITE}{self.interface_info.get('channel', 'N/A')}")
        print(f"{Fore.GREEN}Frequency: {Fore.WHITE}{self.interface_info.get('frequency', 'N/A')}")
        print(f"{Fore.GREEN}Signal Level: {Fore.WHITE}{self.interface_info.get('signal', 'N/A')}")

    def scan_networks(self, iface: str) -> None:
        """Scan for available wireless networks."""
        if not self.check_interface_exists(iface):
            print(f"{Fore.RED}Interface {iface} not found!")
            return

        print(f"{Fore.YELLOW}Scanning for networks... This may take a few seconds.")
        scan_output = self.get_command_output(f"sudo iwlist {iface} scan 2>/dev/null")
        
        networks = []
        current_network = {}
        
        for line in scan_output.split('\n'):
            if 'Cell' in line:
                if current_network:
                    networks.append(current_network)
                current_network = {}
            elif 'ESSID' in line:
                current_network['ssid'] = line.split('"')[1]
            elif 'Channel' in line:
                current_network['channel'] = line.split(':')[1].strip()
            elif 'Quality' in line:
                current_network['signal'] = line.split('=')[1].split()[0]
            elif 'Encryption key' in line:
                current_network['encryption'] = 'Yes' if 'on' in line else 'No'

        if current_network:
            networks.append(current_network)

        self.scan_results = networks
        self.banner()
        print(f"{Fore.YELLOW}Found {Fore.LIGHTCYAN_EX}{len(networks)}{Fore.YELLOW} networks:")
        for network in networks:
            print(f"\n{Fore.GREEN}SSID: {Fore.WHITE}{network.get('ssid', 'N/A')}")
            print(f"{Fore.GREEN}Channel: {Fore.WHITE}{network.get('channel', 'N/A')}")
            print(f"{Fore.GREEN}Signal: {Fore.WHITE}{network.get('signal', 'N/A')}")
            print(f"{Fore.GREEN}Encryption: {Fore.WHITE}{network.get('encryption', 'N/A')}")

    def save_scan_results(self, filename: str = None) -> None:
        """Save scan results to a JSON file."""
        if not self.scan_results:
            print(f"{Fore.RED}No scan results to save!")
            return

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wifi_scan_{timestamp}.json"

        try:
            with open(filename, 'w') as f:
                json.dump(self.scan_results, f, indent=4)
            print(f"{Fore.GREEN}Scan results saved to {Fore.LIGHTCYAN_EX}{filename}")
        except Exception as e:
            print(f"{Fore.RED}Error saving scan results: {str(e)}")

    def monitor(self, iface: str) -> None:
        """Set interface to monitor mode."""
        if not self.check_interface_exists(iface):
            print(f"{Fore.RED}Interface {iface} not found!")
            return

        self.original_interface = iface
        commands = [
            f"sudo ip link set {iface} down",
            f"sudo iw {iface} set type monitor",
            f"sudo ip link set {iface} name wmg0mon",
            f"sudo ip link set wmg0mon up"
        ]

        for cmd in commands:
            if not self.run_command(cmd):
                return

        self.current_interface = "wmg0mon"
        self.banner()
        print(f"{Fore.GREEN}Interface {Fore.LIGHTCYAN_EX}wmg0mon{Fore.GREEN} is now in monitor mode")

    def managed(self, iface: str) -> None:
        """Set interface to managed mode."""
        if not self.check_interface_exists(iface):
            print(f"{Fore.RED}Interface {iface} not found!")
            return

        managed_name = iface.replace('mon', '')
        commands = [
            f"sudo ip link set {iface} down",
            f"sudo iw {iface} set type managed",
            f"sudo ip link set {iface} name {managed_name}",
            f"sudo ip link set {managed_name} up"
        ]

        for cmd in commands:
            if not self.run_command(cmd):
                return

        self.current_interface = managed_name
        self.banner()
        print(f"{Fore.GREEN}Interface {Fore.LIGHTCYAN_EX}{managed_name}{Fore.GREEN} is now in managed mode")

    def rename(self, iface: str, new_name: str) -> None:
        """Rename a network interface."""
        if not self.check_interface_exists(iface):
            print(f"{Fore.RED}Interface {iface} not found!")
            return

        commands = [
            f"sudo ip link set {iface} down",
            f"sudo ip link set {iface} name {new_name}",
            f"sudo ip link set {new_name} up"
        ]

        for cmd in commands:
            if not self.run_command(cmd):
                return

        self.current_interface = new_name
        self.banner()
        print(f"{Fore.GREEN}Interface {Fore.LIGHTCYAN_EX}{iface}{Fore.GREEN} has been renamed to {Fore.LIGHTCYAN_EX}{new_name}")

    def list_interfaces(self) -> None:
        """List all available network interfaces."""
        self.banner()
        print(f"{Fore.YELLOW}Available network interfaces:")
        subprocess.run("ip link show | grep -E '^[0-9]+:'", shell=True)

    def restore_original(self) -> None:
        """Restore interface to its original state."""
        if self.original_interface and self.current_interface:
            self.managed(self.current_interface)

    def start_monitoring(self, iface: str) -> None:
        """Start real-time network monitoring."""
        if not self.check_interface_exists(iface):
            print(f"{Fore.RED}Interface {iface} not found!")
            return

        self.monitoring = True
        self.banner()
        print(f"{Fore.YELLOW}Starting real-time monitoring on {Fore.LIGHTCYAN_EX}{iface}{Fore.YELLOW}...")
        print(f"{Fore.YELLOW}Press Ctrl+C to stop monitoring")

        def monitor_thread():
            while self.monitoring and self.running:
                try:
                    # Get current networks
                    try:
                        scan_result = subprocess.run(f"sudo iwlist {iface} scan 2>/dev/null", 
                                                   shell=True, capture_output=True, text=True)
                        if scan_result.returncode == 0:
                            current_networks = set()
                            
                            for line in scan_result.stdout.split('\n'):
                                if 'ESSID' in line:
                                    ssid = line.split('"')[1]
                                    current_networks.add(ssid)
                            
                            # Check for new networks
                            new_networks = current_networks - self.known_networks
                            if new_networks:
                                print(f"\n{Fore.GREEN}New networks detected:")
                                for network in new_networks:
                                    print(f"{Fore.LIGHTCYAN_EX}* {network}")
                            
                            # Update known networks
                            self.known_networks = current_networks
                    except Exception as e:
                        print(f"{Fore.RED}Error scanning networks: {str(e)}")
                    
                    # Get connected clients
                    try:
                        clients_output = subprocess.run("sudo arp -n", shell=True, capture_output=True, text=True)
                        if clients_output.returncode == 0:
                            current_clients = {}
                            
                            for line in clients_output.stdout.split('\n'):
                                if 'ether' in line:
                                    parts = line.split()
                                    if len(parts) >= 3:
                                        ip = parts[0]
                                        mac = parts[2]
                                        if ip not in current_clients:
                                            current_clients[ip] = []
                                        current_clients[ip].append(mac)
                            
                            # Check for new clients
                            for ip, macs in current_clients.items():
                                if ip not in self.connected_clients:
                                    print(f"\n{Fore.GREEN}New client connected:")
                                    print(f"{Fore.LIGHTCYAN_EX}IP: {ip}")
                                    print(f"{Fore.LIGHTCYAN_EX}MAC: {', '.join(macs)}")
                            
                            self.connected_clients = current_clients
                    except Exception as e:
                        print(f"{Fore.RED}Error getting client information: {str(e)}")
                    
                    time.sleep(5)  # Wait 5 seconds before next scan
                    
                except Exception as e:
                    print(f"{Fore.RED}Error during monitoring: {str(e)}")
                    self.monitoring = False
                    break

        def signal_handler(signum, frame):
            self.monitoring = False
            self.running = False
            print(f"\n{Fore.YELLOW}Monitoring stopped")

        signal.signal(signal.SIGINT, signal_handler)
        
        monitor_thread()

    def analyze_security(self, iface: str) -> None:
        """Analyze network security settings."""
        if not self.check_interface_exists(iface):
            print(f"{Fore.RED}Interface {iface} not found!")
            return

        self.banner()
        print(f"{Fore.YELLOW}Analyzing security settings for {Fore.LIGHTCYAN_EX}{iface}{Fore.YELLOW}...")

        # Check interface security
        security_info = {
            'encryption': self.get_command_output(f"iwconfig {iface} 2>/dev/null | grep -o 'Encryption key:[a-z]*' | cut -d':' -f2"),
            'authentication': self.get_command_output(f"iwconfig {iface} 2>/dev/null | grep -o 'Authentication Suites : [A-Z]*' | cut -d':' -f2"),
            'power_management': self.get_command_output(f"iwconfig {iface} 2>/dev/null | grep -o 'Power Management:[a-z]*' | cut -d':' -f2")
        }

        print(f"\n{Fore.GREEN}Security Analysis:")
        print(f"{Fore.WHITE}Encryption: {Fore.LIGHTCYAN_EX}{security_info['encryption'] or 'N/A'}")
        print(f"{Fore.WHITE}Authentication: {Fore.LIGHTCYAN_EX}{security_info['authentication'] or 'N/A'}")
        print(f"{Fore.WHITE}Power Management: {Fore.LIGHTCYAN_EX}{security_info['power_management'] or 'N/A'}")

        # Check for common security issues
        issues = []
        if security_info['encryption'] == 'off':
            issues.append("No encryption enabled")
        if security_info['power_management'] == 'on':
            issues.append("Power management is enabled (may affect performance)")

        if issues:
            print(f"\n{Fore.RED}Potential Security Issues:")
            for issue in issues:
                print(f"{Fore.RED}* {issue}")
        else:
            print(f"\n{Fore.GREEN}No major security issues detected")

    def diagnose_connection(self, iface: str) -> None:
        """Diagnose connection issues."""
        if not self.check_interface_exists(iface):
            print(f"{Fore.RED}Interface {iface} not found!")
            return

        self.banner()
        print(f"{Fore.YELLOW}Diagnosing connection for {Fore.LIGHTCYAN_EX}{iface}{Fore.YELLOW}...")

        # Check interface status
        status = self.get_command_output(f"ip link show {iface} | grep -o 'state [A-Z]*' | cut -d' ' -f2")
        print(f"\n{Fore.GREEN}Interface Status: {Fore.LIGHTCYAN_EX}{status}")

        # Check signal strength
        signal = self.get_command_output(f"iwconfig {iface} 2>/dev/null | grep -o 'Signal level=[-0-9]* dBm' | cut -d'=' -f2")
        print(f"{Fore.GREEN}Signal Strength: {Fore.LIGHTCYAN_EX}{signal or 'N/A'}")

        # Check connection quality
        quality = self.get_command_output(f"iwconfig {iface} 2>/dev/null | grep -o 'Link Quality=[0-9]*/[0-9]*' | cut -d'=' -f2")
        print(f"{Fore.GREEN}Link Quality: {Fore.LIGHTCYAN_EX}{quality or 'N/A'}")

        # Check for common issues
        issues = []
        if status != 'UP':
            issues.append("Interface is not up")
        if signal and int(signal.split()[0]) < -70:
            issues.append("Signal strength is weak")
        if quality and int(quality.split('/')[0]) < 50:
            issues.append("Link quality is poor")

        if issues:
            print(f"\n{Fore.RED}Detected Issues:")
            for issue in issues:
                print(f"{Fore.RED}* {issue}")
            
            print(f"\n{Fore.YELLOW}Recommended Actions:")
            if "Interface is not up" in issues:
                print(f"{Fore.WHITE}* Try bringing the interface up: sudo ip link set {iface} up")
            if "Signal strength is weak" in issues:
                print(f"{Fore.WHITE}* Try moving closer to the access point")
                print(f"{Fore.WHITE}* Check for physical obstacles")
            if "Link quality is poor" in issues:
                print(f"{Fore.WHITE}* Try changing the channel")
                print(f"{Fore.WHITE}* Check for interference from other devices")
        else:
            print(f"\n{Fore.GREEN}No connection issues detected")

def main():
    parser = argparse.ArgumentParser(description='WifiMage - Wireless Network Interface Manager')
    parser.add_argument('-r', '--rename', nargs=2, metavar=('INTERFACE', 'NEW_NAME'),
                      help='Rename an interface')
    parser.add_argument('-mon', '--monitor', metavar='INTERFACE',
                      help='Set interface to monitor mode')
    parser.add_argument('-man', '--managed', metavar='INTERFACE',
                      help='Set interface to managed mode')
    parser.add_argument('-l', '--list', action='store_true',
                      help='List available interfaces')
    parser.add_argument('-i', '--info', metavar='INTERFACE',
                      help='Show detailed interface information')
    parser.add_argument('-s', '--scan', metavar='INTERFACE',
                      help='Scan available networks')
    parser.add_argument('-save', '--save-scan', metavar='FILENAME',
                      help='Save scan results to a JSON file')
    parser.add_argument('-rt', '--realtime', metavar='INTERFACE',
                      help='Start real-time network monitoring')
    parser.add_argument('-sec', '--security', metavar='INTERFACE',
                      help='Analyze network security settings')
    parser.add_argument('-d', '--diagnose', metavar='INTERFACE',
                      help='Diagnose connection issues')

    args = parser.parse_args()
    wm = WifiMage()

    try:
        if len(sys.argv) == 1:
            wm.banner()
            parser.print_help()
            sys.exit(0)
            
        if args.rename:
            wm.rename(args.rename[0], args.rename[1])
        elif args.monitor:
            wm.monitor(args.monitor)
        elif args.managed:
            wm.managed(args.managed)
        elif args.list:
            wm.list_interfaces()
        elif args.info:
            wm.show_interface_info(args.info)
        elif args.scan:
            wm.scan_networks(args.scan)
            if args.save_scan:
                wm.save_scan_results(args.save_scan)
        elif args.realtime:
            wm.start_monitoring(args.realtime)
        elif args.security:
            wm.analyze_security(args.security)
        elif args.diagnose:
            wm.diagnose_connection(args.diagnose)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Operation interrupted by user")
        wm.restore_original()
    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {str(e)}")
        wm.restore_original()
    finally:
        print(Style.RESET_ALL)

if __name__ == '__main__':
    main()
