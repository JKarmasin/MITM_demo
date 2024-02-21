import tkinter as tk
from tkinter import filedialog
import csv

def load_and_display_csv():
    """Load a CSV file and display its contents in the listbox, formatted in columns."""
    # Ask the user to select a CSV file
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    
    if not file_path:  # Check if the user cancelled the file selection
        return
    
    try:
        # Clear the current content in the listbox
        listbox.delete(0, tk.END)
        
        # Open and read the CSV file
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # Format each row as a string with padded values for a column-like appearance
                formatted_row = format_row(row)
                listbox.insert(tk.END, formatted_row)
    except Exception as e:
        listbox.insert(tk.END, f"An error occurred: {e}")

def format_row(row, col_width=15):
    """Format the row values to have a uniform column width."""
    # Pad each value in the row to ensure it fits into its 'column'
    return ' '.join(value.ljust(col_width) for value in row)

# Create the main window
root = tk.Tk()
root.title("CSV Viewer in Listbox")

# Create a scrollbar
scrollbar = tk.Scrollbar(root)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create a listbox with a scrollbar
listbox = tk.Listbox(root, yscrollcommand=scrollbar.set, width=80)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=listbox.yview)

# Create a "Load CSV" button
load_button = tk.Button(root, text="Load CSV", command=load_and_display_csv)
load_button.pack(pady=5)

# Start the GUI event loop
root.mainloop()
