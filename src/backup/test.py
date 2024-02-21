import subprocess
import threading
import time
import signal
import os

# Název rozhraní pro airodump-ng
interface = "wlan0"

# Globální proměnná pro sledování počtu výstupů
output_counter = 1

# Globální proměnná pro uchování reference na proces airodump-ng
airodump_process = None

def run_airodump(interface, duration=1):
    global output_counter
    global airodump_process
    while True:
        # Název souboru podle pořadového čísla
        filename = f"output{output_counter}.txt"
        
        # Spustí airodump-ng a zachytí výstup
        command = f"airodump-ng {interface} -w {filename} --output-format csv -a"
        
        # Spustí příkaz v bash shellu, umožňuje spuštění na pozadí
        #subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        airodump_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
        
        # Čeká na specifikovanou dobu trvání
        time.sleep(duration)

        # Ukončení airodump-ng a jeho podprocesů
        os.killpg(os.getpgid(airodump_process.pid), signal.SIGTERM)

        # Zvýší počítadlo výstupů pro další iteraci
        output_counter += 1

def signal_handler(sig, frame):
    print('Ukončuji procesy...')
    if airodump_process:
        # Bezpečné ukončení airodump-ng procesu
        os.killpg(os.getpgid(airodump_process.pid), signal.SIGTERM)
    print('Procesy byly ukončeny. Ukončuji skript.')
    exit(0)

# Registrace signal handleru pro SIGINT
signal.signal(signal.SIGINT, signal_handler)


# Spustí hlavní funkci v samostatném vlákně
thread = threading.Thread(target=run_airodump, args=(interface,))
thread.start()

