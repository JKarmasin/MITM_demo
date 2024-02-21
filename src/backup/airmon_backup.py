import subprocess
import tkinter as tk
from tkinter import scrolledtext
from tkinter import *

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
                #interfaces.append(interface_name)
                interfaces_field.insert(tk.END, interface_name)
        # Join the interface names with newlines for display
        #interface_names = '\n'.join(interfaces)
    except Exception as e:
        interface_names = f"Failed to run iwconfig: {e}"
    
    # Insert the interface names into the text area
    #interfaces_field.insert(tk.END, interface_names)

def interfaces_on_select(event):
    interface_label.config(text=interfaces_field.get(ANCHOR))

def run_airmon(iface):
    try:
        # Deaktivujte rozhraní
        subprocess.run(['ifconfig', iface, 'down'], check=True)
        # Nastavte monitorovací mód
        subprocess.run(['airmon-ng', 'start', iface], check=True)
        # Aktivujte rozhraní
        subprocess.run(['airmon-ng', 'chaeck', 'kill'], check=True)
        # Restartuji službu NetworkManager
        subprocess.run(['service', 'NetworkManager', 'restart'], check=True)
        print(f"Rozhraní {iface} bylo úspěšně přepnuto do monitorovacího módu.")
    except subprocess.CalledProcessError as e:
        print(f"Chyba při nastavování monitorovacího módu: {e}")

# Create the main window
root = tk.Tk()
root.title("Wireless Interface Names")
root.geometry("500x800")

# Interface frame ========================================================================
interface_frame = LabelFrame(root, text="Vyhledání a výběr požadovaného interfacu")
interface_frame.pack(pady=5)
# First label
#iwconfig_label = Label(root, text="1. Vyhledání a výběr požadovaného interfacu:")
#iwconfig_label.grid(row=0, column=0, columnspan=2)

# Create a button to run iwconfig command
interface_button = tk.Button(interface_frame, text="Show Wireless Interfaces", command=run_iwconfig)
#interface_button.grid(row=1,column=0, padx=5)
interface_button.pack(pady=5)

# Create a scrolled text area widget
interfaces_field = tk.Listbox(interface_frame, width=30, height=5)  # Adjusted size for interface names
interfaces_field.bind('<<ListboxSelect>>', interfaces_on_select)
#interfaces_field.grid(row=1,column=1,padx=5,pady=5)
interfaces_field.pack()

global interface
# Zobrazeni labelu s interfacem je pouze debugg
interface_label = Label(interface_frame, text="")
#interface_label.grid(row=2,column=0,columnspan=2)
interface_label.pack()

# Interface frame ========================================================================
monitor_frame = LabelFrame(root, text="Přepnutí interfacu do monitorovacího módu")
monitor_frame.pack(pady=5)

monitor_button = tk.Button(monitor_frame, text="Turn monitor mode ON", command=lambda: run_airmon(interface))
#interface_button.grid(row=1,column=0, padx=5)
interface_button.pack()
# Start the GUI event loop ===============================================================
root.mainloop()
