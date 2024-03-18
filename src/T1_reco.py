import customtkinter as ctk
from customtkinter import ANCHOR, COMMAND, DISABLED, E, END, EW, N, NO, NORMAL, NS, ON, S, TOP, W, X
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import *
import re
from threading import Thread
import time
import signal
import os
import csv
from src import global_names

# ========================================================================================================================
# Globální proměnná s názvem interface pro monitorovací mód
global interface

# Globální proměnné nutné pro připojení k síti:
# Název sítě (net), MAC adresa Access Pointu (ap), MAC adresa klienta (cl), Kanál, na kterém se vysílá (ch), Heslo pro připojení (password)
global net
global ap
global cl
global ch

# Globální proměnná pro uchování reference na nekončící procesy pro jejich pozdější ukončení
airodump_process = None

# Globální flagy pro ukončování threadů
stop_reading_file = False           # ukončení threadu se čtením ze souboru airodum_full

# Pomocná proměnná, pomocí které vypisuju výstup z airodump an stdout.... TODO delete
capture = None

# Názvy výstupních a pomocných souborů
output_airodump = global_names.output_airodump


# Uklidím případný soubor output_airodump-01.csv po předešlém spuštění
file_name = output_airodump + "-01.csv"
if os.path.isfile(file_name):
    os.remove(file_name)


# ========================================================================================================================
# ==== T1 ================================================================================================================
def find_wifi_interfaces(interfaces_field):    
    
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
                interfaces.append(interface_name + " (" + interface_mac + ")")

        interfaces_field.configure(values=interfaces)
    except Exception as e:
        interfaces_field.set(f"Failed to run iwconfig: {e}")
        print(e)
# ========================================================================================================================
def interfaces_on_select(event):
    global interface
    #global interfaces_field
    #global status       # TODO =========
    #global monitor_on_button

    #interface = interfaces_field.get(ANCHOR).split()[0]
    interface = interfaces_field.get().split()[0]
    global_names.interface = interface  

    #print(f"=== DEBUG: Interface po selectu: {interface} ===")

    #status.configure(text=interfaces_field.get(ANCHOR).split()[0])
    monitor_on_button.configure(state=NORMAL)

    # Nastavím zvýraznění udělaných rámců činností
    global interface_frame
    global monitor_frame
    interface_frame.configure(fg_color='transparent')     
    monitor_frame.configure(fg_color=global_names.my_color)
# ========================================================================================================================
# ========================================================================================================================

def start_monitor_mode():
    print("===== START MONITOR MODE =================================")
    #print(f"=== DEBUG: Interface v airmonu_on: {interface} ===")
    try:
        # Deaktivujte rozhraní
        subprocess.run(['ifconfig', interface, 'down'], check=True)
        # Vypne konfliktni procesy
        subprocess.run(['airmon-ng', 'check', 'kill'], check=True)
        # Nastavte monitorovací mód
        subprocess.run(['airmon-ng', 'start', interface], check=True)
        # Restartuji službu NetworkManager
        subprocess.run(['service', 'NetworkManager', 'restart'], check=True)

        #status.configure(text=f"Rozhraní {interface} bylo úspěšně přepnuto do monitorovacího módu.")
        print(f"Rozhraní {interface} bylo úspěšně přepnuto do monitorovacího módu.")

        monitor_off_button.configure(state=NORMAL) 
        monitor_on_button.configure(state=DISABLED)
        airodump_on_button.configure(state=NORMAL) 

        # Nastavím zvýraznění udělaných rámců činností
        global airodump_frame
        global monitor_frame
        monitor_frame.configure(fg_color='transparent') 
        airodump_frame.configure(fg_color=global_names.my_color)

    except subprocess.CalledProcessError as e:
        #status.configure(text=f"Chyba při nastavování monitorovacího módu: {e}")
        print(f"Chyba při nastavování monitorovacího módu rozhraní: {e}")
# ========================================================================================================================
def stop_monitor_mode():
    print("===== STOP MONITOR MODE =================================")
    #print(f"=== DEBUG: Interface v airmonu_off: {interface} ===")
    is_monitor = False
    try:
        # Spustí příkaz `iw` a získá informace o rozhraní
        vystup = subprocess.check_output(["iw", interface, "info"], text=True)
       
        # Zkontroluje, zda je výstup obsahuje "type monitor"
        if "type monitor" in vystup:
            is_monitor = True

    except subprocess.CalledProcessError as e:
        print("     -- Nastala chyba při spouštění příkazu:", e)
    except Exception as e:
        print("     -- Nastala neočekávaná chyba:", e)
        
    monitor_on_button.configure(state=NORMAL) 
    monitor_off_button.configure(state=DISABLED)

    if is_monitor:
        try:
            # Deaktivujte rozhraní
            subprocess.run(['ifconfig', interface, 'down'], check=True)
            # Nastavte monitorovací mód
            subprocess.run(['airmon-ng', 'stop', interface], check=True)
            # Restartuji službu NetworkManager
            subprocess.run(['service', 'NetworkManager', 'restart'], check=True)
        
            #status.configure(text=f"Rozhraní {interface} bylo úspěšně přepnuto do normálního módu.")
            print(f"Rozhraní {interface} bylo úspěšně přepnuto do normálního módu.")

        except subprocess.CalledProcessError as e:
            #status.configure(text=f"Chyba při nastavování normálního módu: {e}")
            print(f"Chyba při nastavování normálního módu rozhraní: {e}")
# ========================================================================================================================
def get_mac_address(iface):

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
    print("===== START AIRODUMP-NG (FULL) =================================")
    global airodump_process
    #global capture

    airodump_on_button.configure(state=DISABLED) 
    airodump_off_button.configure(state=NORMAL) 

    command = f"sudo airodump-ng {interface} -w {output_airodump} --output-format csv"
    print(f"COMMAND: {command}")

    airodump_process = subprocess.Popen(command, shell=True, stdout=capture, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    
    # Spustí zpracovávání souboru v samostatném vlákně
    #print("-- Spuštím vlákno process_csv...")
    Thread(target=process_csv, daemon=True).start()
# ========================================================================================================================
# Funkce pro ukončení airodump-ng
def stop_airodump_full():
    print("===== STOP AIRODUM-NG (FULL) =================================")
    print("     -- Ukončuji airodump.")
    airodump_off_button.configure(state=DISABLED) 
    airodump_on_button.configure(state=NORMAL) 

    if airodump_process:
        os.killpg(os.getpgid(airodump_process.pid), signal.SIGTERM)
        print("     -- OK: Airodump-ng byl ukončen.")

    global stop_reading_file
    #print(f"=== DEBUG: stop_reading_file 2a: {stop_reading_file}")
    stop_reading_file = True
    #print(f"=== DEBUG: stop_reading_file 2b: {stop_reading_file}")

# ========================================================================================================================
# Funkce pro načtení csv souboru a jeho následné zpracování
def process_csv():
    print("===== CSV PROCESSING =================================")
    print("     -- Začínám zpracovávat CSV.")

    global stop_reading_file

    #print(f"=== DEBUG: stop_reading_file 1a: {stop_reading_file}")

    global output_airodump
    output_airodump = output_airodump+"-01.csv"

    while True:
        #print(f"=== DEBUG: stop_reading_file 1b: {stop_reading_file}")
        # Krátká pauza, aby se nezatěžoval systém a aby se poprvé stihnul vytvořit soubor csv
        time.sleep(1)
        try:
            if not os.path.isfile(output_airodump):
                #status.configure(text="Žádný CSV soubor není zatím vytvořený...")
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
            #print(f"=== DEBUG: stop_reading_file 3: {stop_reading_file}")
            print("     -- OK: Vlákno zpracovávání CSV bylo ukončeno.")
            break
    
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
        #status.configure(text=bssid_value) 
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

    global_names.net = net
    global_names.ap = ap
    global_names.cl = cl
    global_names.ch = ch

    target_net.configure(text=net)
    target_ap.configure(text=ap)
    target_cl.configure(text=cl)
    target_ch.configure(text=ch)

    # Nastavím zvýraznění udělaných rámců činností
    global airodump_frame
    global target_frame
    airodump_frame.configure(fg_color='transparent') 
    target_frame.configure(fg_color=global_names.my_color)
    global_names.finished_tab = 0
    
    menu_button.configure(fg_color="transparent", text_color=("green", "green"))

# ===========================================================
def finish():
    # Funkce vrátí všechny činnosti z tohoto tabu do původního stavu
    stop_airodump_full()
    stop_monitor_mode()

# ===========================================================
def draw_reco(frame_t1, frame_1_button):      # def draw_reco(frame_t1, btn_next):
    global menu_button
    menu_button = frame_1_button
    
    # Tab "Vyhledání cílů" ==================================================================================================================
    # Interface frame ========================================================================
    global interface_frame
    interface_frame = ctk.CTkFrame(frame_t1)
    interface_frame.pack_propagate(0)
    interface_frame.pack(padx=10,pady=5, fill=X, expand=True, side=TOP)
    
    interface_frame.configure(fg_color=global_names.my_color)
    
    interface_frame_label = ctk.CTkLabel(interface_frame, text="Vyhledání a výběr požadovaného rozhraní")
    interface_frame_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)

    # Create a button to run iwconfig command
    interface_button = ctk.CTkButton(interface_frame, text="Najít Wi-fi rozhraní", width=200, command=lambda: find_wifi_interfaces(interfaces_field))
    interface_button.grid(row=1, column=0, sticky=N, padx=5, pady=5)

    # Create a OptionMenu widget
    global interfaces_field
    interfaces_field = ctk.CTkOptionMenu(interface_frame, dynamic_resizing=False, values=[""], width=200, command=interfaces_on_select)
    find_wifi_interfaces(interfaces_field)
    interfaces_field.grid(row=1, column= 1, pady=5)
    interfaces_field.set("Vyber rozhraní...") 

    # Monitor mode frame ========================================================================
    global monitor_frame
    monitor_frame = ctk.CTkFrame(frame_t1)
    monitor_frame.pack(padx=10,pady=5, fill='x')

    monitor_frame_label = ctk.CTkLabel(monitor_frame, text="Přepnutí rozhraní do monitorovacího módu")
    monitor_frame_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)

    global monitor_on_button
    global monitor_off_button
    monitor_on_button = ctk.CTkButton(monitor_frame, text="Spustit monitorovací mód", width=200, state=DISABLED, command=start_monitor_mode)
    monitor_off_button = ctk.CTkButton(monitor_frame, text="Vypnout monitorovací mód", width=200, state=DISABLED, command=stop_monitor_mode)
    monitor_on_button.grid(row=1, column=0, padx=5, pady=5)
    monitor_off_button.grid(row=1, column=1, pady=5)

    # Airodump frame ========================================================================
    global airodump_frame
    airodump_frame = ctk.CTkFrame(frame_t1)
    airodump_frame.pack(padx=10,pady=5, fill='x', expand=True)

    airodump_frame_label = ctk.CTkLabel(airodump_frame, text="Záchyt komunikace v okolí")
    airodump_frame_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)

    global airodump_off_button
    global airodump_on_button
    airodump_on_button = ctk.CTkButton(airodump_frame, text="Spustit airodump-ng", width=200, state=DISABLED, command=lambda: Thread(target=start_airodump_full).start())
    airodump_off_button = ctk.CTkButton(airodump_frame, text="Zastavit airodump-ng", width=200, state=DISABLED, command=stop_airodump_full)
    airodump_on_button.grid(row=1, column=0,  sticky=W, padx=5, pady=5)
    airodump_off_button.grid(row=1, column=1, sticky=W, pady=5)

    # Treeview pro Access Pointy
    tree_ap_label = ctk.CTkLabel(airodump_frame, text="Seznam Access Pointů")
    tree_ap_label.grid(row=2, column=0, columnspan=4)

    global tree_ap
    #tree_ap = ctk.CTkTreeview(airodump_frame, selectmode='browse')
    tree_ap = ttk.Treeview(airodump_frame, selectmode='browse')
    tree_ap.bind('<<TreeviewSelect>>', tree_ap_selected)
    tree_ap.grid(row=3, column=0, columnspan=3, sticky=EW, padx=5, pady=5)

    # Treeview pro Clienty
    tree_cl_label = ctk.CTkLabel(airodump_frame, text="Seznam klientů")
    tree_cl_label.grid(row=4, column=0, columnspan=4)

    global tree_cl
    #tree_cl = ctk.CTkTreeview(airodump_frame, selectmode='browse')
    tree_cl = ttk.Treeview(airodump_frame, selectmode='browse')
    tree_cl.bind('<<TreeviewSelect>>', tree_cl_selected)
    tree_cl.grid(row=5, column=0, columnspan=3, sticky=EW, padx=5, pady=5)

    airodump_frame.grid_columnconfigure(2, weight=1)

    # Target frame ========================================================================
    global target_frame
    target_frame = ctk.CTkFrame(frame_t1)
    target_frame.pack(padx=10,pady=5, fill='x', expand=True)

    target_frame_label = ctk.CTkLabel(target_frame, text="Cíl MITM útoku")
    target_frame_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)

    global target_net
    global target_ap
    global target_cl
    global target_ch
    target_net_label = ctk.CTkLabel(target_frame, text="Cílová síť:", font=('Helvetica', 16))
    target_ap_label = ctk.CTkLabel(target_frame, text="Cílový Access Point:", font=('Helvetica', 16))
    target_cl_label = ctk.CTkLabel(target_frame, text="Cílové zařízení:", font=('Helvetica', 16))
    target_ch_label = ctk.CTkLabel(target_frame, text="Kanál komunikace:", font=('Helvetica', 16))
    target_net = ctk.CTkLabel(target_frame, text="", font=('Helvetica', 16), text_color='green')
    target_ap = ctk.CTkLabel(target_frame, text="", font=('Helvetica', 16), text_color='green')
    target_cl = ctk.CTkLabel(target_frame, text="", font=('Helvetica', 16), text_color='green')
    target_ch = ctk.CTkLabel(target_frame, text="", font=('Helvetica', 16), text_color='green')
    target_net_label.grid(row=6, column=0, sticky=W, padx=5, pady=5)
    target_ap_label.grid(row=7, column=0, sticky=W, padx=5, pady=5)
    target_cl_label.grid(row=8, column=0, sticky=W, padx=5, pady=5)
    target_ch_label.grid(row=9, column=0, sticky=W, padx=5, pady=5)
    target_net.grid(row=6, column=1, sticky=W, padx=5)
    target_ap.grid(row=7, column=1, sticky=W, padx=5)
    target_cl.grid(row=8, column=1, sticky=W, padx=5)
    target_ch.grid(row=9, column=1, sticky=W, padx=5)

    