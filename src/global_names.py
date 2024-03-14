# Soubor s globálními proměnnými
interface = ""
net = ""
ap = ""
cl = ""
ch = ""
password = ""

#==================================================================
# DEBUG abych se mohl posunout hned na skoro poslední tab =========
net = "KARMASIN"
interface = "wlan1"
password = "klara59501350"
cl = "BC:1A:E4:92:5E:25"    # HUAWEI PHONE
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


#print("=== DEBUG: Načetl jsem globalni proměnné ===")

# Globální flagy pro ukončování threadů
#stop_reading_file = False           # ukončení threadu se čtením ze souboru TODO jakého souboru? přejmenovat!
#stop_parse_handshake_cap = False    # ukončení threadu tsharku pro filtrování eapol rámců

# Pomocná proměnná, pomocí které vypisuju výstup z airodump an stdout.... TODO delete
#capture = None

# Názvy výstupních a pomocných souborů

# Uklidím případný soubor output_airodump-01.csv po předešlém spuštění
#file_name = output_airodump + "-01.csv"
#if os.path.isfile(file_name):
#    os.remove(file_name)

# Uklidím případný soubor output_handshake-01.csv po předešlém spuštění
#files_in_current_dir = os.listdir('src/tmp')
#output_handshake_prefix = "handshake"
# Filter files that start with the prefix
#files_to_delete = [file for file in files_in_current_dir if file.startswith(output_handshake_prefix)]

# Delete the filtered files
#for file in files_to_delete:
#    os.remove("tmp/"+file)

#file_name = output_password
#if os.path.isfile(file_name):
#    os.remove(file_name)
