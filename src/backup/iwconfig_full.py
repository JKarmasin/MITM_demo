import subprocess
import tkinter as tk
from tkinter import scrolledtext

def run_iwconfig():
    # Clear the text area
    text_area.delete('1.0', tk.END)
    
    # Run the iwconfig command
    try:
        # For Python 3.5 and later, use run() instead of call()
        result = subprocess.run(['iwconfig'], capture_output=True, text=True)
        output = result.stdout
    except Exception as e:
        output = f"Failed to run iwconfig: {e}"
    
    # Insert the command output into the text area
    text_area.insert(tk.INSERT, output)

# Create the main window
root = tk.Tk()
root.title("iwconfig Output")

# Create a button to run iwconfig command
run_button = tk.Button(root, text="Run iwconfig", command=run_iwconfig)
run_button.pack(pady=10)

# Create a scrolled text area widget
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
text_area.pack(padx=10, pady=10)

# Start the GUI event loop
root.mainloop()
