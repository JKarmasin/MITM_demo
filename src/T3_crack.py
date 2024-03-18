import customtkinter as ctk
from customtkinter import COMMAND, DISABLED, E, EW, HORIZONTAL, N, NE, NO, ON, S, SW, W, WORD, Y
import subprocess
#from tkinter import ttk
#from tkinter import *
from tkinter import filedialog
import re
from threading import Thread
import os
from src import global_names

# ========================================================================================================================
# Globální proměnná pro uchování reference na nekončící procesy pro jejich pozdější ukončení
aircrack_process = None

# Globální flagy pro ukončování threadů
stop_reading_file = False           # ukončení threadu se čtením ze souboru TODO jakého souboru? přejmenovat!
stop_parse_handshake_cap = False    # ukončení threadu tsharku pro filtrování eapol rámců

# Pomocná proměnná, pomocí které vypisuju výstup z airodump an stdout.... TODO delete
capture = None

# Názvy výstupních a pomocných souborů
output_handshake = global_names.output_handshake
output_password = global_names.output_password

# Uklidím soubory po předchozím spuštění
file_name = output_password
if os.path.isfile(file_name):
    os.remove(file_name)

# ========================================================================================================================
# ========================================================================================================================
def crunch(min, max, chars, output):
    command = f"crunch {min} {max} {chars} -o {output}"
    print("COMMAND: " + command)
    subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)

# ========================================================================================================================
def create_wordlist():
    print("===== CREATING PASSWORDS WORDLIST =====================")
    #global create_wl_progress
    create_wl_progress.grid(row=5,column=0,columnspan=4)
    create_wl_progress.start()
    min = wl_min_entry.get()
    max = wl_max_entry.get()
    chars = wl_char_entry.get()
    output = wl_name_entry.get()
    #print("after button: " + min + ", " + max + ", " + chars + ", " + output)
    # Je nutné to tady vůbec dávat do samostatného vlákna? TODO otestovat na obrovském souboru hesel....
    thr = Thread(target=crunch(min, max, chars, output), daemon=True)
    thr.start()
    thr.join()
    create_wl_progress.stop()
    create_wl_progress.grid_forget()

    wordlist_name_label.configure(text=os.getcwd()+"/"+output)
    global create_wordlist_frame
    create_wordlist_frame.configure(highlightthickness=0)

# ========================================================================================================================
def load_wordlist(root):
    root.filename = filedialog.askopenfilename(title="Zvol textový soubor se slovníkem hesel")  
    global wordlist_name
    wordlist_name = root.filename
    #print("Wordlist: "+wordlist_name) 
    wordlist_name_label.configure(text=wordlist_name)

    global crack_pw_frame
    global load_wordlist_frame
    global create_wordlist_frame
    crack_pw_frame.configure(fg_color=global_names.my_color) 
    load_wordlist_frame.configure(fg_color=("gray75", "gray25"))
    create_wordlist_frame.configure(fg_color=("gray75", "gray25"))

# ========================================================================================================================
def secs_to_str(seconds):
        """Human-readable seconds. 193 -> 3m13s"""
        if seconds < 0:
            return '-%ds' % seconds

        rem = int(seconds)
        hours = rem // 3600
        mins = int((rem % 3600) / 60)
        secs = rem % 60
        if hours > 0:
            return '%dh%dm%ds' % (hours, mins, secs)
        elif mins > 0:
            return '%dm%ds' % (mins, secs)
        else:
            return '%ds' % secs

# ========================================================================================================================
def grep_aircrack_process():
    # Report progress of cracking
    #print("     -- DEBUG: started grep process")

    global aircrack_process         # TODO
    global load_wordlist_frame
    global connect_frame
    global crack_pw_frame
    global create_wordlist_frame

    aircrack_nums_re = re.compile(r'(\d+)/(\d+) keys tested.*\(([\d.]+)\s+k/s')
    aircrack_key_re = re.compile(r'Current passphrase:\s*(\S.*\S)\s*$')
    num_tried = num_total = 0
    percent = num_kps = 0.0
    eta_str = 'unknown'
    current_key = ''
    while aircrack_process.poll() is None:
        line = aircrack_process.stdout.readline()
        match_nums = aircrack_nums_re.search(line.decode('utf-8'))
        match_keys = aircrack_key_re.search(line.decode('utf-8'))
        if match_nums:
            num_tried = int(match_nums[1])
            num_total = int(match_nums[2])
            num_kps = float(match_nums[3])
            eta_seconds = (num_total - num_tried) / num_kps
            eta_str = secs_to_str(eta_seconds)
            percent = 100.0 * float(num_tried) / float(num_total)
        elif match_keys:
            current_key = match_keys[1]
        else:
            continue

        progress = 'Lámání WPA Handshaku: %0.2f%%' % percent
        progress += ' ETA: %s' % eta_str
        progress += ' (aktuální klíč: %s)' % current_key
        #crack_pw_progress['value']=int(percent)
        crack_pw_progress.set(int(percent)/100)
        crack_pw_current_line_label.configure(text=progress)

    if not os.path.isfile(output_password):
        #status.configure(text="Heslo nebylo prolomeno...")
        print("     ----------------------------") 
        print("     -- HESLO NEBYLO PROLOMENO --")
        print("     ----------------------------")

        load_wordlist_frame.configure(fg_color=global_names.my_color) 
        create_wordlist_frame.configure(fg_color=global_names.my_color) 
        return

    # Vypíšu nalezené heslo do odpovídajícího labelu
    if os.path.isfile(output_password):
        with open(output_password, 'r', encoding='utf-8') as file:
            global password
            password = file.readline()
            password_label.configure(text=password)
            global_names.password = password
            print("     ----------------------------------") 
            print("     -- HESLO BYLO ÚSPĚŠNĚ PROLOMENO --")
            print("     ----------------------------------")

            crack_pw_frame.configure(fg_color=("gray75", "gray25"))
            load_wordlist_frame.configure(fg_color=("gray75", "gray25"))
            connect_frame.configure(fg_color=global_names.my_color)

    # Ukončím běhání progress baru
    print("     -- Konec lámání hesla!")
    crack_pw_progress.stop()
    crack_pw_progress.grid_forget()
# ========================================================================================================================
def crack_pw():
    crack_pw_progress.grid(row=4,column=0,columnspan=4, sticky=EW)
    #status.configure(text="Lámání hesla")

    #capfile = "wpa-good.cap"        # TODO změnit na fungující hovno !!!!!!!!!!!!!!!!
    capfile = output_handshake + "-01.cap"
    command = f"aircrack-ng {capfile} -w {wordlist_name} -l {output_password}"
    print("===== PASSWORD CRACKING ===================================")
    print("COMMAND: "+command)

    global aircrack_process
    aircrack_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    Thread(target=grep_aircrack_process, daemon=True).start()

# ========================================================================================================================
def connect_to_wifi():
    print("===== WI-FI CONNECTION ====================================")
    try:
        interface = global_names.interface
        net = global_names.net
        password = global_names.password

        is_monitor = False
        try:
            # Spustí příkaz `iw` a získá informace o rozhraní
            vystup = subprocess.check_output(["iw", interface, "info"], text=True)
       
            # Zkontroluje, zda je výstup obsahuje "type monitor"
            if "type monitor" in vystup:
                is_monitor = True

        except subprocess.CalledProcessError as e:
            print("     -- Nastala chyba při spouštění příkazu:", e)
        except Exception as e:
            print("     -- Nastala neočekávaná chyba:", e)
        
        if is_monitor:
            # Deaktivujte rozhraní
            subprocess.run(['ifconfig', interface, 'down'], check=True)
            # Zastavit monitorovací mód
            subprocess.run(['airmon-ng', 'stop', interface], check=True)
            # Restartuji službu NetworkManager
            subprocess.run(['service', 'NetworkManager', 'restart'], check=True)
        
            print(f"Rozhraní {interface} bylo úspěšně přepnuto do normálního módu.")

        command = f"nmcli wifi connect {net} password {password} ifname {interface}"
        print("COMMAND: " + command)

        # Připojení se k Wi-Fi síti
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)

        #status.configure(text=f"Úspěšně připojeno k cílové Wi-fi síti!")
        connect_button.configure(state=DISABLED)
        print("     -------------------------------------") 
        print("     -- ÚSPĚŠNĚ PŘIPOJENO K WI-FI SÍTI! --")
        print("     -------------------------------------")

        #global connect_frame
        #connect_frame.configure(highlightthickness=0)
        global_names.finished_tab = 2
        global menu_button
        menu_button.configure(fg_color="transparent", text_color=("green", "green"), image=check_image)
        next_menu_button.configure(state=ctk.NORMAL)
        connect_frame.configure(fg_color=("gray75", "gray25"))

    except subprocess.CalledProcessError as e:
        #status.configure(text=f"Chyba při připojování k síti: {e}")
        print(f"Chyba při připojování k síti: {e}")

# ===========================================================
def disconnect_from_wifi():
    command = f"nmcli con donw id {global_names.net}"
    print("COMMAND: " + command)    
    subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    print(f"Úspěšně odpojeno od sítě {global_names.net}")

# ===========================================================
def finish():
    # Funkce vrátí všechny činnosti z tohoto tabu do původního stavu
    disconnect_from_wifi()

# ========================================================================================================================================
# Tab "Prolomení hesla" ==================================================================================================================
def draw_crack(window):
    global menu_button
    global check_image
    global next_menu_button
    menu_button = window.frame_3_button
    check_image = window.done_image
    next_menu_button = window.frame_4_button

    # Create Wordlist Frame ==============================================================================================================
    global create_wordlist_frame
    create_wordlist_frame = ctk.CTkFrame(window.T3_frame)
    create_wordlist_frame.pack(padx=10,pady=5, fill='x')

    create_wordlist_frame_label = ctk.CTkLabel(create_wordlist_frame, text="Vytvořit slovník hesel")
    create_wordlist_frame_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
    
    #if global_names.finished_tab == 1:
    create_wordlist_frame.configure(fg_color=global_names.my_color)

    global wl_char_entry
    global wl_min_entry
    global wl_max_entry
    global wl_name_entry
    wl_label = ctk.CTkLabel(create_wordlist_frame, text="Parametry vytvářeného slovníku hesel:")
    wl_min_label = ctk.CTkLabel(create_wordlist_frame, text="Minimální počet znaků:")
    wl_max_label = ctk.CTkLabel(create_wordlist_frame, text="Maximální počet znaků:")
    wl_char_label = ctk.CTkLabel(create_wordlist_frame, text="Použité znaky:")
    wl_name_label = ctk.CTkLabel(create_wordlist_frame, text="Název souboru:")
    wl_min_entry = ctk.CTkEntry(create_wordlist_frame, width=200)
    wl_max_entry = ctk.CTkEntry(create_wordlist_frame, width=200)
    wl_char_entry = ctk.CTkEntry(create_wordlist_frame, width=200)
    wl_name_entry = ctk.CTkEntry(create_wordlist_frame, width=200)

    wl_label.grid(row=1, column=0, columnspan=4, padx=5, pady=5)
    wl_min_label.grid(row=2, column=0, sticky=W, padx=5, pady=5)
    wl_max_label.grid(row=2, column=2, sticky=W, padx=5, pady=5)
    wl_char_label.grid(row=3, column=0, sticky=W, padx=5, pady=5)
    wl_name_label.grid(row=3, column=2, sticky=W, padx=5, pady=5)
    wl_min_entry.grid(row=2, column=1, sticky=W, padx=5, pady=5)
    wl_max_entry.grid(row=2, column=3, sticky=W, padx=5, pady=5)
    wl_char_entry.grid(row=3, column=1, sticky=W, padx=5, pady=5)
    wl_name_entry.grid(row=3, column=3, sticky=W, padx=5, pady=5)

    create_wl_button = ctk.CTkButton(create_wordlist_frame, text="Vytvořit", width= 200, command=create_wordlist)
    create_wl_button.grid(row=4, column=0, columnspan=4)

    # WTF s progress barem u vytváření slovníku? TODO test, jestli je potřeba
    global create_wl_progress
    create_wl_progress = ctk.CTkProgressBar(create_wordlist_frame, orientation=HORIZONTAL, mode='indeterminate')
    #create_wl_progress.step(0)

    # Load Wordlist Frame ==================================================================================================================
    global load_wordlist_frame
    load_wordlist_frame = ctk.CTkFrame(window.T3_frame)
    load_wordlist_frame.pack(padx=10,pady=5, fill='x')
    load_wordlist_frame_label = ctk.CTkLabel(load_wordlist_frame, text="Načíst hotový slovník hesel")
    load_wordlist_frame_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)  
    #if global_names.finished_tab == 1:
    #load_wordlist_frame.configure(highlightbackground=global_names.my_color, highlightthickness=3, highlightcolor=global_names.my_color)
    #load_wordlist_frame.pack(padx=10,pady=5, fill='x')

    load_wl_button = ctk.CTkButton(load_wordlist_frame, text="Načíst slovník hesel", width= 200, command=lambda: load_wordlist(window))
    load_wl_button.grid(row=1, column=0, padx=5, pady=5)

    # Crack the password Frame ========================================================================================================================
    global crack_pw_frame
    crack_pw_frame = ctk.CTkFrame(window.T3_frame)
    crack_pw_frame.pack(padx=10,pady=5, fill='x')
    crack_pw_frame_label = ctk.CTkLabel(crack_pw_frame, text="Prolomit heslo sítě hrubou silou")
    crack_pw_frame_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)  


    global wordlist_name_label
    crack_pw_label  =ctk.CTkLabel(crack_pw_frame, text="Zvolený soubor:")
    wordlist_name = ""
    wordlist_name_label = ctk.CTkLabel(crack_pw_frame, text=wordlist_name)
    crack_pw_label.grid(row=1, column=0, padx=5, pady=5)
    wordlist_name_label.grid(row=1, column=1, padx=5, pady=5)

    crack_pw_button = ctk.CTkButton(crack_pw_frame, text="Prolomit heslo", width= 200, command=crack_pw)
    crack_pw_button.grid(row=2, column=0, columnspan=2, sticky=W, padx=5, pady=5)

    #crack_pw_progress = ctk.CTkProgressbar(crack_pw_frame, orient=HORIZONTAL, length=800, mode='determinate')
    global crack_pw_progress
    crack_pw_progress = ctk.CTkProgressBar(crack_pw_frame, orientation=HORIZONTAL, mode='determinate')
    #crack_pw_progress.step(0)

    global crack_pw_current_line_label
    crack_pw_current_line_label = ctk.CTkLabel(crack_pw_frame, text="")  
    crack_pw_current_line_label.grid(row=3, column=0, columnspan=2)

    crack_pw_frame.grid_columnconfigure(2, weight=1)

    # Network Connection Frame ===============================================================================================================
    global connect_frame
    connect_frame = ctk.CTkFrame(window.T3_frame)
    connect_frame.pack(padx=10,pady=5, fill='x')
    connect_frame_label = ctk.CTkLabel(connect_frame, text="Připojit se k cílové Wi-Fi síti")
    connect_frame_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5) 

    password_info_label = ctk.CTkLabel(connect_frame, text="Heslo k Wi-fi síti: ")
    global password_label
    password_label = ctk.CTkLabel(connect_frame, text="", font=('Helvetica', 16), text_color='green')
    password_info_label.grid(row=1, column=0, padx=5, pady=5, sticky=W)
    password_label.grid(row=1, column=1, padx=5, pady=5)

    global connect_button
    connect_button = ctk.CTkButton(connect_frame, text="Připojit se k síti", width= 200, command=connect_to_wifi)
    connect_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

