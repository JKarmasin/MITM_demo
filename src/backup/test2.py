import tkinter as tk
from threading import Thread
import subprocess
import os
import signal

# Funkce pro spuštění airodump-ng
def start_airodump():
    global airodump_process
    # Ujistěte se, že zadáváte správné rozhraní
    command = "sudo airodump-ng wlan0 -w output --output-format csv"
    airodump_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)

# Funkce pro ukončení airodump-ng
def stop_airodump():
    if airodump_process:
        os.killpg(os.getpgid(airodump_process.pid), signal.SIGTERM)
        print("Airodump-ng byl ukončen.")

# Vytvoření GUI
def create_gui():
    root = tk.Tk()
    root.title("Airodump-ng Control")

    # Tlačítko pro spuštění airodump-ng
    start_button = tk.Button(root, text="Start airodump-ng", command=lambda: Thread(target=start_airodump).start())
    start_button.pack(pady=5)

    # Tlačítko pro ukončení airodump-ng
    stop_button = tk.Button(root, text="Stop airodump-ng", command=stop_airodump)
    stop_button.pack(pady=5)

    root.mainloop()

# Hlavní proměnná pro proces
airodump_process = None

if __name__ == "__main__":
    create_gui()
