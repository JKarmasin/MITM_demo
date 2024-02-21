import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import *
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
# Globální proměnná pro uchování reference na proces airodump-ng
airodump_process = None
airodump_client_process = None
# Globální flag pro ukončení threadu se čtením ze souboru
stop_reading_file = False
capture = None

ap = ""
cl = ""
ch = ""

output_airodump = "out_airdump"
output_wpa = "out_wpa"

file_name = output_airodump + "-01.csv"
# Uklidím případný soubor output_airodump-01.csv po předešlém spuštění
if os.path.isfile(file_name):
    os.remove(file_name)

# ========================================================================================================================
# ==== T1 ================================================================================================================
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
    monitor_on_button.configure(state=NORMAL)
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

        monitor_off_button.configure(state=NORMAL) #######################################################################
        monitor_on_button.configure(state=DISABLED) ######################################################################
        airodump_on_button.configure(state=NORMAL) #######################################################################

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

        monitor_on_button.configure(state=NORMAL) ########################################################################
        monitor_off_button.configure(state=DISABLED) #####################################################################

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
def start_airodump():
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
def stop_airodump():
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
    #time.sleep(2)  # Krátká pauza, aby se stihl vytvořit zdrojový soubor
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
def tree_cl_selected(Event):
    # Get selected item(s) on treeview_a
    selected_items = tree_cl.selection()
    item = selected_items[0]
    item_values = tree_cl.item(item, "values")

    global ap       
    global cl
    global ch

    ap = item_values[1].strip()
    cl = item_values[0].strip()
    ch = str(find_channel_by_bssid(item_values[1])).strip()

    target_ap.configure(text=ap)
    target_cl.configure(text=cl)
    target_ch.configure(text=ch)
# ========================================================================================================================
# === T2 =================================================================================================================
def start_wpa_catch():
    wpa_catch_progress.start(10)
    command_catch_wpa = f"sudo airodump-ng -c{ch} -d {ap} -w {output_wpa} {interface}"
    #wpa_command_label.configure(text="Spouštěný příkaz: ")
    wpa_command.configure(text=command_catch_wpa)

    global airodump_client_process
    global capture

    wpa_catch_on_button.configure(state=DISABLED) 
    wpa_catch_off_button.configure(state=NORMAL) 

    airodump_client_process = subprocess.Popen(command_catch_wpa, shell=True, stdout=capture, stderr=subprocess.PIPE, preexec_fn=os.setsid)



# ========================================================================================================================
def stop_wpa_catch():
    wpa_catch_progress.stop()
    wpa_catch_on_button.configure(state=NORMAL) 
    wpa_catch_off_button.configure(state=DISABLED) 

# ========================================================================================================================
def start_deauth():
    deauth_progress.start(10)
    deauth_cadency = 0
    command_deauth = f"sudo aireplay-ng --deauth {deauth_cadency} -c {cl} -a {ap} {interface}"
    #deauth_command_label.configure(text="Spouštěný příkaz: ")
    deauth_command.configure(text=command_deauth)

# ========================================================================================================================
def stop_deauth():
    deauth_progress.stop()
    deauth_on_button.configure(state=NORMAL) 
    deauth_off_button.configure(state=DISABLED) 
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
root.geometry("1500x900")
#global filename

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
frame_t1 = ttk.Frame(tab1)
frame_t2 = ttk.Frame(tab2)
frame_t3 = ttk.Frame(tab3)
frame_t4 = ttk.Frame(tab4)
frame_t5 = ttk.Frame(tab5)
frame_t1.pack()
frame_t2.pack()
frame_t3.pack()
frame_t4.pack()
frame_t5.pack()


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
interface_frame = LabelFrame(frame_t1, text="Vyhledání a výběr požadovaného interfacu")
interface_frame.pack(padx=10,pady=5, fill='x', expand=1)  # WTF Todle není rozatežný po celé šířce?!

# Create a button to run iwconfig command
interface_button = tk.Button(interface_frame, text="Show Wireless Interfaces", command=run_iwconfig)
interface_button.grid(row=0, column=0)

# Create a scrolled text area widget
interfaces_field = tk.Listbox(interface_frame, width=30, height=5)  # Adjusted size for interface names
interfaces_field.bind('<<ListboxSelect>>', interfaces_on_select)
interfaces_field.grid(row=0, column= 1, pady=5)

# Monitor mode frame ========================================================================
monitor_frame = LabelFrame(frame_t1, text="Přepnutí interfacu do monitorovacího módu")
monitor_frame.pack(padx=10,pady=5, fill='x')

monitor_on_button = tk.Button(monitor_frame, text="Turn monitor mode ON", state=DISABLED, command=run_airmon_on)
monitor_off_button = tk.Button(monitor_frame, text="Turn monitor mode OFF", state=DISABLED, command=run_airmon_off)
monitor_on_button.grid(row=0, column=0)
monitor_off_button.grid(row=0, column=1)

# Airodump frame ========================================================================
airodump_frame = LabelFrame(frame_t1, text="Záchyt airodump-ng")
airodump_frame.pack(padx=10,pady=5, fill='x')

airodump_on_button = tk.Button(airodump_frame, text="Run airodump-ng", state=DISABLED, command=lambda: Thread(target=start_airodump).start())
airodump_off_button = tk.Button(airodump_frame, text="Stop airodump-ng", state=DISABLED, command=stop_airodump)
airodump_on_button.grid(row=0, column=0)
airodump_off_button.grid(row=0, column=1)

# Zobrazeni labelu s informaci o zapnuti/vypnuti monitorovaciho modu
#airodump_field = scrolledtext.ScrolledText(airodump_frame)
#airodump_field.pack(padx=10,pady=5, fill='x')

#load_and_display_csv()
# Treeview pro Access Pointy
tree_ap_label = Label(airodump_frame, text="Seznam Access pointů")
tree_ap_label.grid(row=1, column=0, columnspan=3)

tree_ap = ttk.Treeview(airodump_frame, selectmode='browse')
tree_ap.bind('<<TreeviewSelect>>', tree_ap_selected)
tree_ap.grid(row=2, column=0, columnspan=3, sticky=W)
#scrollbarv_ap = ttk.Scrollbar(airodump_frame, orient="vertical", command=tree_ap.yview)
#scrollbarv_ap.pack(side='right', fill='y')
#tree_ap.configure(yscrollcommand=scrollbarv_ap.set)

# Treeview pro Clienty
tree_cl_label = Label(airodump_frame, text="Seznam klientů")
tree_cl_label.grid(row=3, column=0, columnspan=3)
tree_cl = ttk.Treeview(airodump_frame, selectmode='browse')
tree_cl.bind('<<TreeviewSelect>>', tree_cl_selected)
tree_cl.grid(row=4, column=0, columnspan=3, sticky=W)
#scrollbarv_cl = ttk.Scrollbar(airodump_frame, orient="vertical", command=tree_cl.yview)
#scrollbarv_cl.pack(side='right', fill='y')
#tree_cl.configure(yscrollcommand=scrollbarv_cl.set)

target_ap_label = Label(airodump_frame, text="TARGET ACCES POINT:", font=('Helvetica', 20))
target_ap = Label(airodump_frame, text="", font=('Helvetica', 20), fg='green')
target_cl_label = Label(airodump_frame, text="TARGET CLIENT:", font=('Helvetica', 20))
target_cl = Label(airodump_frame, text="", font=('Helvetica', 20), fg='green')
target_ch_label = Label(airodump_frame, text="TARGET CHANNEL:", font=('Helvetica', 20))
target_ch = Label(airodump_frame, text="", font=('Helvetica', 20), fg='green')
target_ap_label.grid(row=5, column=0, sticky=W)
target_ap.grid(row=5, column=1, sticky=W)
target_cl_label.grid(row=6, column=0, sticky=W)
target_cl.grid(row=6, column=1, sticky=W)
target_ch_label.grid(row=7, column=0, sticky=W)
target_ch.grid(row=7, column=1, sticky=W)

# ========================================================================================================================================
# Tab "Záchyt handshaku" =================================================================================================================

# WPA Catch Frame ========================================================================================================================
wpa_catch_frame = LabelFrame(frame_t2, text="Záchyt WPA handshaku")
wpa_catch_frame.pack(padx=10,pady=5, fill='x')

wpa_catch_label = Label(wpa_catch_frame, text="Spustit proces na zachytávání komunikace Clienta s AP a zachycením WPA handshaku:")
wpa_catch_on_button = Button(wpa_catch_frame, text="Spustit", command=start_wpa_catch)
wpa_catch_off_button = Button(wpa_catch_frame, text="Zastavit", state=DISABLED, command=stop_wpa_catch)
wpa_catch_label.grid(row=0, column=0)
wpa_catch_on_button.grid(row=0,column=1, pady=5)
wpa_catch_off_button.grid(row=0,column=2, pady=5)

wpa_catch_progress = ttk.Progressbar(wpa_catch_frame, orient=HORIZONTAL, length=800, mode='indeterminate')
wpa_catch_progress.step(0)
wpa_catch_progress.grid(row=1,column=0,columnspan=3)

#wpa_command_label = Label(wpa_catch_frame, text="")
wpa_command = Label(wpa_catch_frame, text="")
#wpa_command_label.grid(row=2, column=1)
wpa_command.grid(row=2, column=0, columnspan=3)

WPA_catch_textarea = scrolledtext.ScrolledText(wpa_catch_frame, wrap=tk.WORD, width=98, height=20)
WPA_catch_textarea.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

# Deauthificate Frame ========================================================================================================================
deauth_frame = LabelFrame(frame_t2, text="Deauthentifikace target klienta")
deauth_frame.pack(padx=10,pady=5, fill='x')

deauth_label = Label(deauth_frame, text="Spustit proces odpojování komunikace Clienta s AP pro opětovné zaslání handshake:")
deauth_on_button = Button(deauth_frame, text="Spustit", command=start_deauth)
deauth_off_button = Button(deauth_frame, text="Zastavit", state=DISABLED, command=stop_deauth)
deauth_label.grid(row=0, column=0)
deauth_on_button.grid(row=0,column=1, pady=5)
deauth_off_button.grid(row=0,column=2, pady=5)

deauth_progress = ttk.Progressbar(deauth_frame, orient=HORIZONTAL, length=800, mode='indeterminate')
deauth_progress.step(0)
deauth_progress.grid(row=1,column=0,columnspan=3)

#deauth_command_label = Label(deauth_frame, text="")
deauth_command = Label(deauth_frame, text="")
#deauth_command_label.grid(row=2, column=1)
deauth_command.grid(row=2, column=0, columnspan=3)


# Tab "Prolomení hesla" ==================================================================================================================


# Tab "Man-in-the-middle" ================================================================================================================


# Tab "Odposlech DNS dotazů" =============================================================================================================


# Status bar =============================================================================================================================
status = Label(root, text="OK", bd=2, relief=SUNKEN, anchor=SW)
status.pack(fill='x', side=BOTTOM)

# Start the GUI event loop ===============================================================================================================
root.mainloop()
