import subprocess
import tkinter as tk
from tkinter import scrolledtext

def run_iwconfig():
    # Clear the text area
    text_area.delete('1.0', tk.END)
    
    try:
        # Run the iwconfig command
        result = subprocess.run(['iwconfig'], capture_output=True, text=True)
        output = result.stdout

        # Parse the output to extract interface names
        interfaces = []
        for line in output.split('\n'):
            if line and not line.startswith(' '):  # Check if line starts with interface name
                interface_name = line.split()[0]  # Extract interface name
                interfaces.append(interface_name)

        # Join the interface names with newlines for display
        interface_names = '\n'.join(interfaces)
    except Exception as e:
        interface_names = f"Failed to run iwconfig: {e}"
    
    # Insert the interface names into the text area
    text_area.insert(tk.INSERT, interface_names)

# Create the main window
root = tk.Tk()
root.title("Wireless Interface Names")

# Create a button to run iwconfig command
run_button = tk.Button(root, text="Show Wireless Interfaces", command=run_iwconfig)
run_button.pack(pady=10)

# Create a scrolled text area widget
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=40, height=10)  # Adjusted size for interface names
text_area.pack(padx=10, pady=10)

# Start the GUI event loop
root.mainloop()
