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