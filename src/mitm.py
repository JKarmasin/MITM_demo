import tkinter as tk
from tkinter import ttk
from tkinter import *
import os
from src import T1_reco
from src import T2_capture
from src import T3_crack
from src import T4_arp_spoof
from src import T5_dns_spoof
from src import global_names

# ========================================================================================================================
# Globální proměnná s názvem interface pro monitorovací mód
#global interface

# Globální proměnné nutné pro připojení k síti:
# Název sítě (net), MAC adresa Access Pointu (ap), MAC adresa klienta (cl), Kanál, na kterém se vysílá (ch), Heslo pro připojení (password)
#global net
#global ap
#global cl
#global ch
#global password

# Globální proměnná pro uchování reference na nekončící procesy pro jejich pozdější ukončení
airodump_process = None
airodump_client_process = None
deauth_process = None
aircrack_process = None
arpspoof_cl_process = None
arpspoof_ap_process = None

# Pomocná proměnná, pomocí které vypisuju výstup z airodump an stdout.... TODO delete
capture = None


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

# Zabráním přepnutí na následující tab, dokud není splněná podmínka z předcházejícího tabu
def on_tab_change(event):
    current_tab = notebook.index(notebook.select())
    #print("=== DEBUG: curr tab: " + str(current_tab))
    #print("=== DEBUG: finn tab: " + str(global_names.finished_tab))

    # Nastavím defaultní barvu tlačítka
    btn_next.config(bg="lightgrey")
    btn_prev.config(bg="lightgrey")

    if global_names.finished_tab == current_tab:
        btn_next.config(bg=global_names.my_color)

    if global_names.finished_tab == (current_tab-1):
        btn_prev.config(bg=global_names.my_color)



# ========================================================================================================================
# Funkce pro ukončení aplikace při stisku CTRL+C
def destroyer(event):
    # TODO kill všechny procesy - asi zbytečně, protože to jsou všechny deamoni a skončí samy, ale je slušnost po sobě uklidit
    root.destroy()
    print('Končím po stiskuní CTRL + C')


# ========================================================================================================================================
# Create the main window =================================================================================================================
# ========================================================================================================================================
def main():
    global root
    root = tk.Tk()
    root.title("Man-in-the-middle Attack")
    icon = PhotoImage(file='images/sword.png')   
    root.tk.call('wm', 'iconphoto', root._w, icon)
    # Posunutí okna vedle konzole (na pravou stranu obrazovky)
    width=1500
    height=1000
    x=420
    y=0
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))

    # Registrace signal handleru pro SIGINT pro ukončení airodump-ng pomocí CTRL+C
    root.bind_all('<Control-c>', destroyer)

    # Frame pro notebook a navigační tlačítka, aby bylo možné lépe kontrolovat layout =======================================================
    main_frame = tk.Frame(root)
    main_frame.pack(expand=True, fill='both')

    # Vytvoření panelu s taby
    global notebook
    notebook = ttk.Notebook(main_frame)

    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)
    tab3 = ttk.Frame(notebook)
    tab4 = ttk.Frame(notebook)
    tab5 = ttk.Frame(notebook)
    tab6 = ttk.Frame(notebook)

    notebook.add(tab1, text="Vyhledání cílů")
    notebook.add(tab2, text="Záchyt handshaku")
    notebook.add(tab3, text="Prolomení hesla")
    notebook.add(tab4, text="Man-in-the-middle")
    notebook.add(tab5, text="Odposlech DNS dotazů")
    #notebook.add(tab6, text="DNS spoof")
    frame_t1 = Frame(tab1)
    frame_t2 = Frame(tab2)
    frame_t3 = Frame(tab3)
    frame_t4 = Frame(tab4)
    frame_t5 = Frame(tab5)
    #frame_t6 = Frame(tab6)
    frame_t1.pack(fill='both', expand=True)
    frame_t2.pack(fill='both', expand=True)
    frame_t3.pack(fill='both', expand=True)
    frame_t4.pack(fill='both', expand=True)
    frame_t5.pack(fill='both', expand=True)
    #frame_t6.pack(fill='both', expand=True)
    frame_t1.pack_propagate(0)
    frame_t2.pack_propagate(0)
    frame_t3.pack_propagate(0)
    frame_t4.pack_propagate(0)
    frame_t5.pack_propagate(0)
    #frame_t6.pack_propagate(0)

    # TODO zkrátit to později na:
    #tabs = [tab1, tab2, tab3, tab4, tab5, tab6]
    #frames = []
    #
    #for tab in tabs:
    #    frame = Frame(tab)
    #    frame.pack(fill='both', expand=True)
    #    frame.pack_propagate(0)
    #    frames.append(frame)


    # Tlačítka pro navigaci
    global btn_next, btn_prev

    btn_prev = tk.Button(main_frame, text="<<", command=lambda: change_tab("prev"))
    btn_prev.pack(side=tk.LEFT, fill='y')
    notebook.pack(side=tk.LEFT, expand=True, fill='both')

    #btn_next = ttk.Button(main_frame, text=">>", bg=global_names.my_color, command=lambda: change_tab("next"))
    btn_next = tk.Button(main_frame, text=">>", command=lambda: change_tab("next"))
    btn_next.pack(side=tk.RIGHT, fill='y')
    #btn_next.flash()

    # Inicializace stavu tlačítek
    update_button_state()
    notebook.bind("<<NotebookTabChanged>>", on_tab_change)

    # Tab 1 "Vyhledání cílů" ==================================================================================================================
    T1_reco.draw_reco(frame_t1, btn_next)

    # Tab 2 "Záchyt handshaku" =================================================================================================================
    T2_capture.draw_capture(frame_t2, btn_next)
    
    # Tab 3 "Prolomení hesla" ==================================================================================================================
    T3_crack.draw_crack(frame_t3, root, btn_next)

    # Tab 4 "Man-in-the-middle" ================================================================================================================
    T4_arp_spoof.draw_arp_spoof(frame_t4, btn_next)

    # Tab 5 "Odposlech DNS dotazů" =============================================================================================================
    T5_dns_spoof.draw_dns(frame_t5)

    # Status bar =============================================================================================================================
    status = Label(root, text="OK", bd=2, relief=SUNKEN, anchor=SW)
    status.pack(fill='x', side=BOTTOM)

    # Start the GUI event loop ===============================================================================================================
    root.mainloop()
