import subprocess
import tkinter as tk
from tkinter import scrolledtext
from tkinter import *
import re

global interface
interface = ""

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

def interfaces_on_select(event):
    global interface
    interface = interfaces_field.get(ANCHOR).split()[0]
    #print(f"Interface po selectu: {interface}")
    interface_label.config(text=interfaces_field.get(ANCHOR).split()[0])

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
        monitor_label.config(text=f"Rozhraní {interface} bylo úspěšně přepnuto do monitorovacího módu.")
        print(f"Rozhraní {interface} bylo úspěšně přepnuto do monitorovacího módu.")
    except subprocess.CalledProcessError as e:
        monitor_label.config(text=f"Chyba při nastavování monitorovacího módu: {e}")
        print(f"Chyba při nastavování monitorovacího módu: {e}")

def run_airmon_off():
    print(f"Interface v airmonu_off: {interface}")
    try:
        # Deaktivujte rozhraní
        subprocess.run(['ifconfig', interface, 'down'], check=True)
        # Nastavte monitorovací mód
        subprocess.run(['airmon-ng', 'stop', interface], check=True)
        # Restartuji službu NetworkManager
        subprocess.run(['service', 'NetworkManager', 'restart'], check=True)
        monitor_label.config(text=f"Rozhraní {interface} bylo úspěšně přepnuto do normálního módu.")
        print(f"Rozhraní {interface} bylo úspěšně přepnuto do normálního módu.")
    except subprocess.CalledProcessError as e:
        monitor_label.config(text=f"Chyba při nastavování normálního módu: {e}")
        print(f"Chyba při nastavování normálního módu: {e}")

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
    
# Create the main window
root = tk.Tk()
root.title("Wireless Interface Names")
root.geometry("1200x1000")


# Interface frame ========================================================================
interface_frame = LabelFrame(root, text="Vyhledání a výběr požadovaného interfacu")
interface_frame.pack(padx=10,pady=5, fill='x')

# Create a button to run iwconfig command
interface_button = tk.Button(interface_frame, text="Show Wireless Interfaces", command=run_iwconfig)
interface_button.pack()

# Create a scrolled text area widget
interfaces_field = tk.Listbox(interface_frame, width=30, height=5)  # Adjusted size for interface names
interfaces_field.bind('<<ListboxSelect>>', interfaces_on_select)
interfaces_field.pack()

# Zobrazeni labelu s interfacem je pouze debugg
interface_label = Label(interface_frame, text="")
interface_label.pack()

# Interface frame ========================================================================
monitor_frame = LabelFrame(root, text="Přepnutí interfacu do monitorovacího módu")
monitor_frame.pack(padx=10,pady=5, fill='x')

print(f"Interface: {interface}")

monitor_button = tk.Button(monitor_frame, text="Turn monitor mode ON", command=run_airmon_on)
monitor_button.pack()
monitor_off_button = tk.Button(monitor_frame, text="Turn monitor mode OFF", command=run_airmon_off)
monitor_off_button.pack()

# Zobrazeni labelu s informaci o zapnuti/vypnuti monitorovaciho modu
monitor_label = Label(monitor_frame, text="")
monitor_label.pack()
# Start the GUI event loop ===============================================================
root.mainloop()
