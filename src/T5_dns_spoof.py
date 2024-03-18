import customtkinter as ctk
from customtkinter import E, END, N, NS, S, Y, EW
import tkinter as tk
import pyshark
import os
from src import global_names
import sys
sys.path.append('/usr/local/lib/python3.11/dist-packages')
from CTkListbox import *

# ========================================================================================================================================
pcap_file = global_names.output_traffic
#if os.path.isfile(pcap_file):
#    os.remove(pcap_file)

# ========================================================================================================================================
# Tab "Odposlech DNS dotazů" =============================================================================================================

# Function to extract DNS queries from the pcap file
def extract_dns_queries(pcap_file):
    cap = pyshark.FileCapture(pcap_file, display_filter='dns')
    dns_queries = {}  # Use a dictionary to store site and its earliest timestamp

    for packet in cap:
        try:
            # Check if it's a response packet and has the queried name field
            #if int(packet.dns.flags_response) == 1 and hasattr(packet.dns, 'qry_name'):    # backup
            if packet.dns.flags_response and hasattr(packet.dns, 'qry_name'):
                site_name = packet.dns.qry_name
                timestamp = packet.sniff_time.strftime("%Y-%m-%d %H:%M:%S")

                # If the site is not in the dictionary or the current packet's timestamp is earlier, update it
                if site_name not in dns_queries or timestamp < dns_queries[site_name]:
                    dns_queries[site_name] = timestamp
        except AttributeError:
            # Skip packets that don't have DNS layer
            continue

    return dns_queries

# ========================================================================================================================================
# Function to display the DNS queries
def display_dns_queries(dns_field, dns_queries):
    #dns_field.delete(0, tk.END)
    dns_field.delete("all")

    idx = 0
    for site_name, timestamp in sorted(dns_queries.items(), key=lambda item: item[1]):  # Sort by timestamp
        #dns_field.insert(tk.END, f"{timestamp} - {site_name}\n")
        dns_field.insert(idx, f"{timestamp} - {site_name}")
        idx += 1

# ========================================================================================================================================
def reload_dns(dns_field):
    global pcap_file
    if os.path.isfile(pcap_file):
        dns_queries = extract_dns_queries(pcap_file)
        display_dns_queries(dns_field, dns_queries)

# ========================================================================================================================================
def draw_dns(window):
    dns_frame = ctk.CTkFrame(window.T5_frame)
    dns_frame.pack(padx=10,pady=5, fill='x')
    dns_frame_label = ctk.CTkLabel(dns_frame, text="DNS dotazy", font=('Open Sans', 16, 'bold'))
    dns_frame_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)

    dns_label = ctk.CTkLabel(dns_frame, text="Navštívené weby:", font=('Helvetica', 16))
    #dns_field = tk.Listbox(dns_frame, width=100, height=32)
    dns_field = CTkListbox(dns_frame, width=1200 , height=600, text_color=("black","white"))

    dns_reload_button = ctk.CTkButton(dns_frame, text="Načíst", width=200, command=lambda: reload_dns(dns_field))

    dns_label.grid(row=1, column=0, padx=5, pady=5)
    dns_field.grid(row=2, column=0, padx=5, pady=5, sticky=EW)
    dns_reload_button.grid(row=3, column=0, padx=5, pady=10)

    global pcap_file





