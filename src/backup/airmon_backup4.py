import subprocess
import tkinter as tk
from tkinter import scrolledtext, ttk
from tkinter import *
import re
from threading import Thread
import time
import signal
import os
import csv
import pandas as pd

# ========================================================================================================================
# Globální proměnná s názvem interface pro monitorovací mód
interface = ""
# Globální proměnná pro uchování reference na proces airodump-ng
airodump_process = None
# Globální flag pro ukončení threadu se čtením ze souboru
stop_reading_file = False
capture = None
file_name = "output-01.csv"
# ========================================================================================================================
# ========================================================================================================================
def run_iwconfig():
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

# ========================================================================================================================
# ========================================================================================================================
def run_airmon_on():
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
    except subprocess.CalledProcessError as e:
        #monitor_label.config(text=f"Chyba při nastavování monitorovacího módu: {e}")
        status.config(text=f"Chyba při nastavování monitorovacího módu: {e}")
        print(f"Chyba při nastavování monitorovacího módu: {e}")

# ========================================================================================================================
def run_airmon_off():
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
# ========================================================================================================================

# ======================================================================================================================== 
# Spustí příkaz airodump-ng na zvoleném interfacu v samostatném procesu a výsledek zapisuje do souboru
def start_airodump():
    global airodump_process
    global capture
    command = f"sudo airodump-ng {interface} -w output --output-format csv"
    #airodump_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    airodump_process = subprocess.Popen(command, shell=True, stdout=capture, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    # Spustí zpracovávání souboru v samostatném vlákně
    print("-- Spuštím vlákno process_csv...")
    Thread(target=process_csv, daemon=True).start()

# ========================================================================================================================
# Funkce pro ukončení airodump-ng
def stop_airodump():
    print("-- Ukončuji airodump.")
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
    #time.sleep(2)  # Krátká pauza, aby se stihl vytvořit zdrojový soubor
    global stop_reading_file
    global file_name
    while True:
        # Krátká pauza, aby se nezatěžoval systém a aby se poprvé stihnul vytvořit soubor csv
        time.sleep(1)
        try:
            if not os.path.isfile(file_name):
                status.configure(text="Žádný CSV soubor není zatím vytvořený...")
                continue

            # Open the input file
            with open(file_name, 'r', encoding='utf-8') as file:
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
            
                # Vyselektuji jen relevantní sloupce kvůli přehlednosti:
                # Access Points: BSSID [0], channel [3], Privacy [5], Authentication [7], ESSID [13]
                selected_columns = [0, 3, 5, 7, 13]
                selected_headers = [headers[i] for i in selected_columns if i < len(headers)]

                tree_ap["columns"] = selected_headers
                tree_ap["show"] = "headings"

                for header in selected_headers:
                    tree_ap.heading(header, text=header)
                    # Set the column's width to the header's length
                    tree_ap.column(header, width=len(header), anchor='center')

                for row in reader:
                    selected_row = [row[i] for i in selected_columns if i < len(row)]
                    tree_ap.insert('', tk.END, values=selected_row)
            except Exception as e:
                print(f"An error occurred: {e}")

            try:
                reader = csv.reader(clients_lines)
                headers = next(reader)
            
                # Access Points: BSSID [0], channel [3], Privacy [5], Authentication [7], ESSID [13]
                # Clients: Station MAC [0], BSSID [5], Probed ESSIDs [6]  
                selected_columns = [0, 5, 6]
                selected_headers = [headers[i] for i in selected_columns if i < len(headers)]

                tree_cl["columns"] = selected_headers
                tree_cl["show"] = "headings"

                for header in selected_headers:
                    tree_cl.heading(header, text=header)
                    # Set the column's width to the header's length
                    tree_cl.column(header, width=len(header), anchor='center')

                for row in reader:
                    selected_row = [row[i] for i in selected_columns if i < len(row)]
                    tree_cl.insert('', tk.END, values=selected_row)

            except Exception as e:
                print(f"An error occurred: {e}")
        except FileNotFoundError:
            print("ERROR: při čtení ze souboru csv")

        #time.sleep(1)  # Krátká pauza, aby se nezatěžoval systém
        if stop_reading_file:
            break
    print("  -- Vlákno zpracovávání CSV bylo ukončeno.")

# ========================================================================================================================
def tree_ap_selected(Event):
    # Get selected item(s) on treeview_a
    selected_items = tree_ap.selection()
    
    # Clear existing selections in treeview_b
    tree_cl.selection_remove(tree_cl.selection())
    
    # For simplicity, assuming 'BSSID' is in the first column (index 0)
    bssid_column_index = tree_ap["columns"].index("BSSID")
    print("Index BBSID v AP: " + bssid_column_index) # DEBUGG

    selected_bssids = []
    for item in selected_items:
        # Get the BSSID value of the selected row in treeview_a
        item_values = tree_ap.item(item, "values")
        bssid_value = item_values[bssid_column_index]
        status.configure(text=bssid_value) # DEBUGG
        selected_bssids.append(bssid_value)
    
    #bssid_column_index = tree_cl["columns"].index("BSSID")
    bssid_column_index = 1
    # Now, select the rows in treeview_b with matching BSSID
    for item in tree_cl.get_children():
        item_values = tree_cl.item(item, "values")
        print("hledám v cl: " + str(item_values[bssid_column_index]))
        if item_values[bssid_column_index] in selected_bssids:
        #if item_values[1] in selected_bssids:
            tree_cl.selection_add(item)

# ========================================================================================================================
def tree_cl_selected(Event):
    pass
# ========================================================================================================================
        
# ========================================================================================================================
'''
def signal_handler(sig, frame):
    print('Ukončuji procesy...')
    if airodump_process:
        # Bezpečné ukončení airodump-ng procesu
        os.killpg(os.getpgid(airodump_process.pid), signal.SIGTERM)
    print('Procesy byly ukončeny.')
'''

# ========================================================================================
# Create the main window =================================================================
# ========================================================================================
root = tk.Tk()
root.title("Wireless Interface Names")
root.geometry("1500x900")
global filename
# Uklidím po předešlém spuštění
if os.path.isfile(file_name):
    os.remove(file_name)

# Registrace signal handleru pro SIGINT pro ukončení airodump-ng pomocí CTRL+C
#signal.signal(signal.SIGINT, signal_handler)

# Interface frame ========================================================================
interface_frame = LabelFrame(root, text="Vyhledání a výběr požadovaného interfacu")
interface_frame.pack(padx=10,pady=5, fill='x')

# Create a button to run iwconfig command
interface_button = tk.Button(interface_frame, text="Show Wireless Interfaces", command=run_iwconfig)
interface_button.grid(row=0, column=0)

# Create a scrolled text area widget
interfaces_field = tk.Listbox(interface_frame, width=30, height=5)  # Adjusted size for interface names
interfaces_field.bind('<<ListboxSelect>>', interfaces_on_select)
interfaces_field.grid(row=0, column= 1, pady=5)

# Monitor mode frame ========================================================================
monitor_frame = LabelFrame(root, text="Přepnutí interfacu do monitorovacího módu")
monitor_frame.pack(padx=10,pady=5, fill='x')

monitor_button = tk.Button(monitor_frame, text="Turn monitor mode ON", command=run_airmon_on)
monitor_off_button = tk.Button(monitor_frame, text="Turn monitor mode OFF", command=run_airmon_off)
monitor_button.grid(row=0, column=0)
monitor_off_button.grid(row=0, column=1)

# Airodump frame ========================================================================
airodump_frame = LabelFrame(root, text="Záchyt airodump-ng")
airodump_frame.pack(padx=10,pady=5, fill='x')

#print(f"Interface: {interface}")

airodump_on_button = tk.Button(airodump_frame, text="Run airodump-ng", command=lambda: Thread(target=start_airodump).start())
airodump_off_button = tk.Button(airodump_frame, text="Stop airodump-ng", command=stop_airodump)
airodump_on_button.pack()
airodump_off_button.pack()

# Zobrazeni labelu s informaci o zapnuti/vypnuti monitorovaciho modu
#airodump_field = scrolledtext.ScrolledText(airodump_frame)
#airodump_field.pack(padx=10,pady=5, fill='x')

#load_and_display_csv()
# Treeview pro Access Pointy
tree_ap_label = Label(airodump_frame, text="Seznam Access pointů")
tree_ap_label.pack()
tree_ap = ttk.Treeview(airodump_frame, selectmode='browse')
tree_ap.bind('<<TreeviewSelect>>', tree_ap_selected)
tree_ap.pack(expand=True, fill='x')
#scrollbarv_ap = ttk.Scrollbar(airodump_frame, orient="vertical", command=tree_ap.yview)
#scrollbarv_ap.pack(side='right', fill='y')
#tree_ap.configure(yscrollcommand=scrollbarv_ap.set)

# Treeview pro Clienty
tree_cl_label = Label(airodump_frame, text="Seznam klientů")
tree_cl_label.pack()
tree_cl = ttk.Treeview(airodump_frame)
tree_cl.bind('<<TreeviewSelect>>', tree_cl_selected)
tree_cl.pack(expand=True, fill='x')
#scrollbarv_cl = ttk.Scrollbar(airodump_frame, orient="vertical", command=tree_cl.yview)
#scrollbarv_cl.pack(side='right', fill='y')
#tree_cl.configure(yscrollcommand=scrollbarv_cl.set)



# Status bar
status = Label(root, text="OK", bd=2, relief=SUNKEN, anchor=SW)
status.pack(fill='x', side=BOTTOM)

# Start the GUI event loop ===============================================================
root.mainloop()
