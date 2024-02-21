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

# ========================================================================================================================
# Globální proměnná s názvem interface pro monitorovací mód
interface = ""
# Globální proměnná pro uchování reference na proces airodump-ng
airodump_process = None
# Globální flag pro ukončení threadu se čtením ze souboru
stop_reading_file = False
capture = None

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
'''
def run_airodump():
    # Spustí hlavní funkci v samostatném vlákně
    thread = threading.Thread(target=airodump_thread, args=())
    thread.start()

def airodump_thread():
    global airodump_process
    global interface
    while True:
        #print("Spouštím airodump!!!")
        # Název souboru podle pořadového čísla
        filename = f"airodump-output.txt"
        # Spustí airodump-ng a zachytí výstup
        command = f"airodump-ng {interface} -w {filename} --output-format csv -a"
        # Spustí příkaz v bash shellu, umožňuje spuštění na pozadí
        airodump_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
        print(f"airodump process: {airodump_process}")
        # Čeká na specifikovanou dobu trvání
        time.sleep(1)
'''
# ======================================================================================================================== 
# Spustí příkaz airodump-ng na zvoleném interfacu v samostatném procesu a výsledek zapisuje do souboru
def start_airodump():
    global airodump_process
    global capture
    command = f"sudo airodump-ng {interface} -w output --output-format csv"
    #airodump_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    airodump_process = subprocess.Popen(command, shell=True, stdout=capture, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    # Spustí sledování souboru v samostatném vlákně
    Thread(target=watch_file, daemon=True).start()

# ========================================================================================================================
# Funkce pro ukončení airodump-ng
def stop_airodump():
    print('Ukončuji airodump...')
    if airodump_process:
        os.killpg(os.getpgid(airodump_process.pid), signal.SIGTERM)
        print("Airodump-ng byl ukončen.")
    print('Ukončuji čtení ze souboru...')
    global stop_reading_file
    stop_reading_file = True
    #print("Čtení ze souboru bylo ukončeno.")

# ========================================================================================================================
# Funkce pro sledování souboru a aktualizaci GUI
def watch_file():
    global stop_reading_file
    global capture
    previous_content = ""
    while True:
    #    airodump_field.delete(1.0, tk.END)  # Vymaže aktuální obsah
    #    airodump_field.insert(tk.END, str(capture)) 
        try:
            with open("output-01.csv", "r") as f:
                content = f.read()
                print("Čtu ze souboru a vypisuju...")
                # Pokud se obsah souboru změnil, aktualizuj GUI
                if content != previous_content:
                   # airodump_field.delete(1.0, tk.END)  # Vymaže aktuální obsah
                   # airodump_field.insert(tk.END, content)  # Vloží nový obsah souboru
                    previous_content = content
        except FileNotFoundError:
            print("ERROR při čtení ze souboru csv")
            #pass
        time.sleep(1)  # Krátká pauza, aby se nezatěžoval systém
        if stop_reading_file:
            break
    print("Čtení ze souboru bylo ukončeno.")

# ========================================================================================================================
# Funkce pro načtení csv souboru a jeho rozd+lení do dvou dalších souborů k následnému zpracování
def process_csv(input_filename="output-01.csv"):
    # Open the input file
    with open(input_filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Remove the first empty line
    lines = lines[1:]
    
    # Find the index of the empty line separating the two blocks
    try:
        separator_index = lines.index('\n')
    except ValueError:
        print("No separator found. Make sure there's an empty line between the blocks.")
        return

    # Split the lines into two blocks
    aps_lines = lines[:separator_index]
    clients_lines = lines[separator_index+1:]  # Skip the empty line
    
    # Save the first block to "output-aps"
    with open("output-aps-01.csv", 'w', encoding='utf-8') as aps_file:
        aps_file.writelines(aps_lines)
    
    # Save the second block to "output-clients"
    with open("output-clients-01.csv", 'w', encoding='utf-8') as clients_file:
        clients_file.writelines(clients_lines)

# ========================================================================================================================
# Funkce pro načtení dat ze souboru a jejich zobrazení v Treeview widgetu
def load_and_display_csv():
    #file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    #print(f"Loading file: {file_path}")  # Debugging print statement
    #if not file_path:
    #    print("No file selected.")  # Debugging print statement
    #    return
    global tree_ap
    for item in tree_ap.get_children():
        tree_ap.delete(item)
    
    try:
        with open("output-aps-01.csv", newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)
            print(f"Headers: {headers}")  # Debugging print statement
            
            tree_ap["columns"] = headers
            tree_ap["show"] = "headings"
            for header in headers:
                tree_ap.heading(header, text=header)
                # Set the column's width to the header's length
                #tree.column(header, anchor='center')
                tree_ap.column(header, width=len(header), anchor='center')

            for row in reader:
                tree_ap.insert('', tk.END, values=row)
                print(f"Inserted row: {row}")  # Debugging print statement
    except Exception as e:
        print(f"An error occurred: {e}")
# ========================================================================================================================

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

# Zobrazeni labelu s interfacem je pouze debugg
#interface_label = Label(interface_frame, text="")
#interface_label.pack()

# Monitor mode frame ========================================================================
monitor_frame = LabelFrame(root, text="Přepnutí interfacu do monitorovacího módu")
monitor_frame.pack(padx=10,pady=5, fill='x')

#print(f"Interface: {interface}")

monitor_button = tk.Button(monitor_frame, text="Turn monitor mode ON", command=run_airmon_on)
monitor_button.pack()
monitor_off_button = tk.Button(monitor_frame, text="Turn monitor mode OFF", command=run_airmon_off)
monitor_off_button.pack()

# Zobrazeni labelu s informaci o zapnuti/vypnuti monitorovaciho modu
#monitor_label = Label(monitor_frame, text="")
#monitor_label.pack()

# Airodump frame ========================================================================
airodump_frame = LabelFrame(root, text="Záchyt airodump-ng")
airodump_frame.pack(padx=10,pady=5, fill='x')

#print(f"Interface: {interface}")

airodump_on_button = tk.Button(airodump_frame, text="Run airodump-ng", command=lambda: Thread(target=start_airodump).start())
airodump_on_button.pack()
airodump_off_button = tk.Button(airodump_frame, text="Stop airodump-ng", command=stop_airodump)
airodump_off_button.pack()

# Zobrazeni labelu s informaci o zapnuti/vypnuti monitorovaciho modu
#airodump_field = scrolledtext.ScrolledText(airodump_frame)
#airodump_field.pack(padx=10,pady=5, fill='x')

#load_and_display_csv()
# Treeview pro Access Pointy
tree_ap = ttk.Treeview(airodump_frame)
tree_ap.pack(expand=True, fill='x')
scrollbarv_ap = ttk.Scrollbar(airodump_frame, orient="vertical", command=tree_ap.yview)
scrollbarv_ap.pack(side='right', fill='y')
tree_ap.configure(yscrollcommand=scrollbarv_ap.set)

# Treeview pro Clienty
tree_cl = ttk.Treeview(airodump_frame)
tree_cl.pack(expand=True, fill='x')
scrollbarv_cl = ttk.Scrollbar(airodump_frame, orient="vertical", command=tree_cl.yview)
scrollbarv_cl.pack(side='right', fill='y')
tree_cl.configure(yscrollcommand=scrollbarv_cl.set)

# Status bar
status = Label(root, text="Testovací řetězec", bd=1, relief=SUNKEN, anchor=SW)
status.pack(fill='x', side=BOTTOM)

# Start the GUI event loop ===============================================================
root.mainloop()
