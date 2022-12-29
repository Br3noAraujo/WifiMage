#!/usr/bin/python3
#! encoding: utf-8

'''Code By Br3noAraujo'''

import os, sys
from colorama import Fore, Style

def banner():
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
   {Fore.GREEN}`----'{Fore.LIGHTRED_EX}`=-='   {Fore.YELLOW}|    ''')
    
def monitor(iface):
    os.system(f'sudo ip link set {iface} down')
    os.system(f'sudo iw {iface} set type monitor')
    os.system(f'sudo ip link set {iface} name wmg0mon')
    os.system(f'sudo ip link set wmg0mon up')
    banner()
    print(f'the interface {Fore.LIGHTCYAN_EX}wmg0mon{Fore.YELLOW} is now on monitor mode')
def managed(iface):
    os.system(f'sudo ip link set {iface} down')
    os.system(f'sudo iw {iface} set type managed')
    managed_name = iface.replace('mon', '')
    os.system(f'sudo ip link set {iface} name {managed_name}')
    os.system(f'sudo ip link set {managed_name} up')
    banner()
    print(f'the interface {Fore.LIGHTCYAN_EX + iface + Fore.YELLOW} is now on managed mode')
def rename(iface, name):
    os.system(f'sudo ip link set {iface} down')
    os.system(f'sudo ip link set {iface} name {name}')
    os.system(f'sudo ip link set {name} up')
    banner()
    print(f'the interface {Fore.LIGHTCYAN_EX + iface + Fore.YELLOW} is now {Fore.LIGHTCYAN_EX + name + Fore.YELLOW}')
def help():
    banner()
    print(f'Usage: python3 {sys.argv[0]} <option> <iface> <complement>')
    print('Options:\n\t-r or --rename: rename the interface')
    print('\n\t-mon or --monitor: set monitor mode the interface')
    print('\n\t-man or --managed: set managed mode the interface')
    sys.exit(1)


def main():
    if len(sys.argv) <= 2:
        help()
    else:
        options = ['-r', '--rename', '-mon', '--monitor', '-man', '--managed']
        option = sys.argv[1]
        if option in options:
            iface = sys.argv[2]
            if option == '-r' or option == '--rename':
                rename(iface, sys.argv[3])
            if option == '-mon' or option == '--monitor':
                monitor(iface)
            if option == '-man' or option == '--managed':
                managed(iface)
            sys.exit(0)
        else:
            help()

if __name__ == '__main__':
    main()
    print(Style.RESET_ALL)