import tkinter as tk
from tkinter import ttk

# Funkce pro změnu tabu
def change_tab(direction):
    current_tab = notebook.index(notebook.select())
    if direction == "next" and current_tab < notebook.index("end") - 1:
        notebook.select(current_tab + 1)
    elif direction == "prev" and current_tab > 0:
        notebook.select(current_tab - 1)
    update_button_state()

# Aktualizace stavu tlačítek
def update_button_state():
    current_tab = notebook.index(notebook.select())
    btn_prev['state'] = tk.NORMAL if current_tab > 0 else tk.DISABLED
    btn_next['state'] = tk.NORMAL if current_tab < notebook.index("end") - 1 else tk.DISABLED

# Vytvoření hlavního okna
root = tk.Tk()
root.title("Aplikace s taby")

# Frame pro notebook a tlačítka, aby bylo možné lépe kontrolovat layout
main_frame = tk.Frame(root)
main_frame.pack(expand=True, fill='both')

# Vytvoření panelu s taby
notebook = ttk.Notebook(main_frame)
tabs = [ttk.Frame(notebook) for _ in range(5)]

# Přidání tabů do notebooku
for i, tab in enumerate(tabs):
    notebook.add(tab, text=f"Tab {i+1}")
    # Přidání testovacích labelů do každého tabu
    for j in range(3):
        frame = ttk.Frame(tab)
        frame.pack(pady=10)
        ttk.Label(frame, text=f"Test Label {j+1} v Tabu {i+1}").pack()

# Tlačítka pro navigaci
btn_prev = ttk.Button(main_frame, text="Předchozí", command=lambda: change_tab("prev"))
btn_prev.pack(side=tk.LEFT, fill='y')

notebook.pack(side=tk.LEFT, expand=True, fill='both')



btn_next = ttk.Button(main_frame, text="Následující", command=lambda: change_tab("next"))
btn_next.pack(side=tk.RIGHT, fill='y')

# Inicializace stavu tlačítek
update_button_state()

# Spuštění hlavní smyčky aplikace
root.mainloop()
