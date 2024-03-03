import tkinter as tk
from tkinter import *
import pyshark

pcap_file = "tmp/traffic_capture_full.pcap"

# ========================================================================================================================================
# Tab "Odposlech DNS dotazů" =============================================================================================================

# Function to extract DNS queries from the pcap file
def extract_dns_queries(pcap_file):
    cap = pyshark.FileCapture(pcap_file, display_filter='dns')
    dns_queries = {}  # Use a dictionary to store site and its earliest timestamp

    for packet in cap:
        try:
            # Check if it's a response packet and has the queried name field
            if int(packet.dns.flags_response) == 1 and hasattr(packet.dns, 'qry_name'):
                site_name = packet.dns.qry_name
                timestamp = packet.sniff_time.strftime("%Y-%m-%d %H:%M:%S")

                # If the site is not in the dictionary or the current packet's timestamp is earlier, update it
                if site_name not in dns_queries or timestamp < dns_queries[site_name]:
                    dns_queries[site_name] = timestamp
        except AttributeError:
            # Skip packets that don't have DNS layer
            continue

    return dns_queries

# Function to display the DNS queries
def display_dns_queries(dns_field, dns_queries):

    for site_name, timestamp in sorted(dns_queries.items(), key=lambda item: item[1]):  # Sort by timestamp
        dns_field.insert(tk.END, f"{timestamp} - {site_name}\n")


def reload_dns(dns_field):
    global pcap_file
    dns_queries = extract_dns_queries(pcap_file)
    display_dns_queries(dns_field, dns_queries)


def draw_dns(frame):
    dns_label = Label(frame, text="Navštívené weby:", font=('Helvetica', 16))
    dns_field = tk.Listbox(frame, width=60, height=32)
    dns_reload_button = tk.Button(frame, text="Načíst", width=20, command=lambda: reload_dns(dns_field))

    dns_label.grid(row=0, column=0, padx=5, pady=5)
    dns_field.grid(row=1, column=0, padx=5, pady=5)
    dns_reload_button.grid(row=2, column=0, padx=5, pady=5)

    global pcap_file





