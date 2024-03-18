# Soubor s globálními proměnnými
interface = ""
net = ""
ap = ""
cl = ""
ch = ""
password = ""

#==================================================================
# DEBUG abych se mohl posunout hned na skoro poslední tab =========
#net = "KARMASIN"
#interface = "wlan1"
#password = "klara59501350"
#cl = "BC:1A:E4:92:5E:25"    # HUAWEI PHONE
#cl = "3C:9C:0F:72:F5:F1"    # IMO ntb
##ap = "CC:2D:E0:C2:EE:6B"      # KARMASIN AP router
"""
# TEST =========
#interface = "wlan0"
#net = "HackMe"
#ap = "1E:58:AB:BE:DE:BD"    #Pixel
#cl = "BC:1A:E4:92:5E:25"    #Huawei
#ch = "11"
#password = "Hackme123"
# TEST==========
"""
# DEBUG ===========================================================
#==================================================================


# Externí pomocné soubory
# Globální proměnná pro uchování reference na nekončící procesy pro jejich pozdější ukončení
output_airodump = "tmp/airdump"
output_handshake = "tmp/handshake"
output_handshake_prefix = "handshake"
output_password = "password.txt"
output_traffic = "tmp/full_traffic.pcap"


# Proměnné uchovávající reference na procesy pro jejich ukončení
airodump_process = None
airodump_client_process = None
deauth_process = None
aircrack_process = None
arpspoof_cl_process = None
arpspoof_ap_process = None

#my_color = "#58b74d"
#my_color = "#a3c9b0"
my_color = "#49875e"


# Proměnná, ve které je číslo tabu, kde již byly splněny všechny potřebné kroky. Čísluje se od 0. Je potřeba ke správnému zvýrazňování framů.
finished_tab = -2

"""# Zabráním přepnutí na následující tab, dokud není splněná podmínka z předcházejícího tabu
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
        btn_prev.config(bg=global_names.my_color)"""