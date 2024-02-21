import tkinter as tk
from tkinter import filedialog, ttk
import csv

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

def load_and_display_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    print(f"Loading file: {file_path}")  # Debugging print statement
    if not file_path:
        print("No file selected.")  # Debugging print statement
        return

    for item in tree.get_children():
        tree.delete(item)
    
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)
            print(f"Headers: {headers}")  # Debugging print statement
            
            tree["columns"] = headers
            tree["show"] = "headings"
            for header in headers:
                tree.heading(header, text=header)
                # Set the column's width to the header's length
                #tree.column(header, anchor='center')
                tree.column(header, width=len(header), anchor='center')

            for row in reader:
                tree.insert('', tk.END, values=row)
                print(f"Inserted row: {row}")  # Debugging print statement
    except Exception as e:
        print(f"An error occurred: {e}")

root = tk.Tk()
root.title("CSV Viewer with Treeview")

process_csv("output-01.csv")

tree = ttk.Treeview(root)
tree.pack(expand=True, fill='both')

scrollbarv = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
scrollbarv.pack(side='right', fill='y')
tree.configure(yscrollcommand=scrollbarv.set)

#scrollbarh = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
#scrollbarh.pack(side='bottom', fill='x')
#tree.configure(xscrollcommand=scrollbarh.set)

load_button = tk.Button(root, text="Load CSV", command=load_and_display_csv)
load_button.pack(pady=5)

root.mainloop()
