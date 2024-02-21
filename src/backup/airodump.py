import tkinter as tk
from subprocess import Popen, PIPE
import time

def refresh_networks():
    # Clear the current list in the ListBox
    network_list.delete(0, tk.END)
    
    # Here you would add code to initiate airodump-ng and direct its output to a file, e.g., a CSV file
    # Since running airodump-ng continuously is complex and requires root, we'll simulate it by reading from a static file
    # For actual use, replace the following line with code to read and parse airodump-ng output
    # Example: 
    process = Popen(["airodump-ng", "wlan0", "--write-interval", "1", "--output-format", "csv", "output_file_name"], stdout=PIPE, stderr=PIPE)
    time.sleep(5)  # Let airodump-ng run for a bit and gather data. Be careful with timing.
    
    # Simulating reading from a file that airodump-ng writes to (e.g., a CSV file with network details)
    try:
        with open("output_file_name-01.csv", "r") as file:  # Adjust the filename as needed
            lines = file.readlines()
            # Assuming the actual network data starts from a specific line. Adjust index based on your file's format
            for line in lines[2:]:
                if line.strip():  # Avoid adding empty lines
                    network_list.insert(tk.END, line.strip())
    except FileNotFoundError:
        network_list.insert(tk.END, "File not found. Ensure airodump-ng is running and outputting data.")
    
    # Schedule this function to be called again after 10000 milliseconds (10 seconds)
    root.after(10000, refresh_networks)

def on_select(event):
    # Event handler for selecting an item in the ListBox
    widget = event.widget
    selection = widget.curselection()
    if selection:
        selected_item = widget.get(selection[0])
        print(f"You selected: {selected_item}")
        # Further actions can be added here

# Create the main window
root = tk.Tk()
root.title("Airodump-ng Networks")

# Create a ListBox to show the network data
network_list = tk.Listbox(root, width=100, height=20)
network_list.bind('<<ListboxSelect>>', on_select)
network_list.pack(pady=10)

# Initialize the network display
refresh_networks()

# Start the GUI event loop
root.mainloop()
