# Proměnná k odemčení všech poležek menu bez nutnosti splnit předešlé kroky v útoku MITM
# 0 = zamčená tlačítka menu
# 1 = odemčená kompletní aplikace už po spuštění
developer_mode = 1

# Soubor s globálními proměnnými
interface = ""
net = ""
ap = ""
cl = ""
ch = ""
password = ""

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
