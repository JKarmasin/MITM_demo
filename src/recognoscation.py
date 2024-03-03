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

capture = None

output_airodump = "../tmp/airdump"
global airodump_process
stop_reading_file = False           # ukončení threadu se čtením ze souboru pro full airodump

global interface

# Globální proměnné nutné pro připojení k síti:
# Název sítě (net), MAC adresa Access Pointu (ap), MAC adresa klienta (cl), Kanál, na kterém se vysílá (ch), Heslo pro připojení (password)
global net
global ap
global cl
global ch

# Uklidím případný soubor output_airodump-01.csv po předešlém spuštění
file_name = output_airodump + "-01.csv"
if os.path.isfile(file_name):
    os.remove(file_name)

# ========================================================================================================================
# Globální proměnná s názvem interface pro monitorovací mód
#interface = ""

# Globální proměnné nutné pro připojení k síti:
# Název sítě (net), MAC adresa Access Pointu (ap), MAC adresa klienta (cl), Kanál, na kterém se vysílá (ch), Heslo pro připojení (password)
#net = ""
#ap = ""
#cl = ""
#ch = ""
#password = ""

# Globální proměnná pro uchování reference na nekončící procesy pro jejich pozdější ukončení
#airodump_process = None


#stop_reading_file = False           # ukončení threadu se čtením ze souboru TODO jakého souboru? přejmenovat!

#capture = None

#global output_airodump
#output_airodump = "tmp/airdump"
#global airodump_process
#stop_reading_file = False           
#output_handshake = "tmp/handshake"
#output_password = "password.txt"


#global interface_frame
#global interface_button
#global interfaces_field

# Monitor mode frame =======
#global monitor_frame
#global monitor_on_button
#global monitor_off_button

# Airodump frame ===========
#global airodump_frame
#global airodump_on_button
#global airodump_off_button
#global tree_ap_label
#global tree_ap
#global scrollbarv_ap
#global tree_cl_label
#global tree_cl
#global scrollbarv_cl

# Target frame =============
#global target_frame
#global target_net_label
#global target_ap_label
#global target_cl_label
#global target_ch_label


global status




def draw_tab1(frame_t1):
    #interface_frame = LabelFrame(frame_t1, text="Vyhledání a výběr požadovaného rozhraní", borderwidth=4)
    interface_frame = LabelFrame(frame_t1, text="Vyhledání a výběr požadovaného rozhraní", borderwidth=4)
    interface_frame.pack_propagate(0)
    interface_frame.pack(padx=10,pady=5, fill=X, expand=True, side=TOP)

    # Create a button to run iwconfig command
    interface_button = tk.Button(interface_frame, text="Najít Wi-fi rozhraní", width=20, command=find_wifi_interfaces)
    interface_button.grid(row=0, column=0, sticky=N, padx=5, pady=5)

    # Create a scrolled text area widget
    global interfaces_field
    interfaces_field = tk.Listbox(interface_frame, width=30, height=3)  # Adjusted size for interface names
    interfaces_field.bind('<<ListboxSelect>>', interfaces_on_select)
    interfaces_field.grid(row=0, column= 1, pady=5)

    # Monitor mode frame ========================================================================
    monitor_frame = LabelFrame(frame_t1, text="Přepnutí rozhraní do monitorovacího módu", borderwidth=4)
    monitor_frame.pack(padx=10,pady=5, fill='x')

    global monitor_on_button
    global monitor_off_button
    monitor_on_button = tk.Button(monitor_frame, text="Spustit monitorovací mód", width=20, state=DISABLED, command=start_monitor_mode)
    monitor_off_button = tk.Button(monitor_frame, text="Vypnout monitorovací mód", width=20, state=DISABLED, command=stop_monitor_mode)
    monitor_on_button.grid(row=0, column=0, padx=5, pady=5)
    monitor_off_button.grid(row=0, column=1, pady=5)

    # Airodump frame ========================================================================
    airodump_frame = LabelFrame(frame_t1, text="Záchyt komunikace v okolí", borderwidth=4)
    airodump_frame.pack(padx=10,pady=5, fill='x', expand=True)

    global airodump_on_button
    global airodump_off_button
    airodump_on_button = tk.Button(airodump_frame, text="Spustit airodump-ng", width=20, state=DISABLED, command=lambda: Thread(target=start_airodump_full).start())
    airodump_off_button = tk.Button(airodump_frame, text="Zastavit airodump-ng", width=20, state=DISABLED, command=stop_airodump_full)
    airodump_on_button.grid(row=0, column=0,  sticky=W, padx=5, pady=5)
    airodump_off_button.grid(row=0, column=1, sticky=W, pady=5)

    # Treeview pro Access Pointy
    tree_ap_label = Label(airodump_frame, text="Seznam Access Pointů")
    tree_ap_label.grid(row=1, column=0, columnspan=4)

    global tree_ap
    tree_ap = ttk.Treeview(airodump_frame, selectmode='browse')
    tree_ap.bind('<<TreeviewSelect>>', tree_ap_selected)
    tree_ap.grid(row=2, column=0, columnspan=3, sticky=EW, padx=5, pady=5)

    scrollbarv_ap = ttk.Scrollbar(airodump_frame, orient="vertical", command=tree_ap.yview)
    scrollbarv_ap.grid(row=2, column=3,sticky=NS, pady=5)
    tree_ap.configure(yscrollcommand=scrollbarv_ap.set)

    # Treeview pro Clienty
    tree_cl_label = Label(airodump_frame, text="Seznam klientů")
    tree_cl_label.grid(row=3, column=0, columnspan=4)

    global tree_cl
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
    global target_net
    global target_ap
    global target_cl
    global target_ch
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
    #global status
    global monitor_on_button
    interface = interfaces_field.get(ANCHOR).split()[0]
    #print(f"Interface po selectu: {interface}")
    #interface_label.config(text=interfaces_field.get(ANCHOR).split()[0])
    #status.config(text=interfaces_field.get(ANCHOR).split()[0])
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
        #status.config(text=f"Rozhraní {interface} bylo úspěšně přepnuto do monitorovacího módu.")
        print(f"Rozhraní {interface} bylo úspěšně přepnuto do monitorovacího módu.")

        monitor_off_button.configure(state=NORMAL) 
        monitor_on_button.configure(state=DISABLED)
        airodump_on_button.configure(state=NORMAL) 

    except subprocess.CalledProcessError as e:
        #monitor_label.config(text=f"Chyba při nastavování monitorovacího módu: {e}")
        #status.config(text=f"Chyba při nastavování monitorovacího módu: {e}")
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
        #status.config(text=f"Rozhraní {interface} bylo úspěšně přepnuto do normálního módu.")
        print(f"Rozhraní {interface} bylo úspěšně přepnuto do normálního módu.")

        monitor_on_button.configure(state=NORMAL) 
        monitor_off_button.configure(state=DISABLED) 

    except subprocess.CalledProcessError as e:
        #status.config(text=f"Chyba při nastavování normálního módu: {e}")
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
    global output_airodump
    global interface
    global capture

    airodump_on_button.configure(state=DISABLED) 
    airodump_off_button.configure(state=NORMAL) 

    command = f"sudo airodump-ng {interface} -w {output_airodump} --output-format csv"
    print("COMMAND: " + command)
    
    #airodump_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    airodump_process = subprocess.Popen(command, shell=True, stdout=capture, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    
    # Spustí zpracovávání souboru v samostatném vlákně
    print("     ++ Spuštím vlákno process_csv...")
    #Thread(target=process_csv, daemon=True).start()
# ========================================================================================================================
# Funkce pro ukončení airodump-ng
def stop_airodump_full():
    print("     -- Ukončuji airodump.")
    global airodump_process
    airodump_off_button.configure(state=DISABLED) 
    airodump_on_button.configure(state=NORMAL) 

    if airodump_process:
        os.killpg(os.getpgid(airodump_process.pid), signal.SIGTERM)
        print("     xx Airodump-ng byl ukončen.")
    print("     -- Ukončuji zpracovávání CSV souboru.")
    global stop_reading_file
    stop_reading_file = True
    #print("Čtení ze souboru bylo ukončeno.")
# ========================================================================================================================
# Funkce pro načtení csv souboru a jeho následné zpracování
def process_csv():
    print("-- Začínám zpracovávat CSV.")

    global stop_reading_file
    global output_airodump
    #global status
    output_airodump = output_airodump+"-01.csv"
    while True:
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
            print("     xx Vlákno zpracovávání CSV bylo ukončeno.")
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

    global target_net

    target_net.configure(text=net)
    target_ap.configure(text=ap)
    target_cl.configure(text=cl)
    target_ch.configure(text=ch)