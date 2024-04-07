
# Bakalářská práce
<img src="https://knihovna.vspj.cz/2017/images/vspj_logo_symbol.svg" alt="drawing" width="200"/>

## Demonstrační nástroj Man-in-the-middle útoků

### Cíl práce:
Cílem práce je navrhnout a implementovat demonstrační nástroj k popisu a  vysvětlení principu Man-in-the-middle (MITM) útoků na bezdrátové sítě. Tento nástroj poslouží k názorným ukázkám během školení kybernetické bezpečnosti především pro příslušníky Armády České republiky, proto musí být uživatelské rozhraní dostatečně intuitivní a přehledné. Součástí nástroje bude i popis relevantních protiopatření, které zvyšují imunitu proti MITM útokům. Nástroj bude implementován na platformě KALI Linux. Rovněž budou vytvořeny návodné a dokumentační nástroje (poster, brožura) pro cílové publikum pro zvýšení účinku školení s využitím tohoto nástroje.


### Základní technologie:
- Kali Linux ![Kali](https://img.shields.io/badge/Kali-268BEE?style=for-the-badge&logo=kalilinux&logoColor=white)
    - airdump-ng, aireplay-ng, aircrack-ng

- vnitřní funkcionalita v Pythonu - interaktivní script ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
- GUI nadstavba v Pythonu v Customtkinter
- nutnost vlastnit USB Wi-Fi Adaptér umožňující monitorovací mód
- testváno s Atheros Archer 1200AU  


# Instalace
Aplikace vyžaduje spuštění v Kali Linuxu.  
Ten je možní mít nainstalovaný přímo "na železe" (lepší chod aplikace), nebo jako virtuální stroj (bezpečnější)...  
### Zprovození Kali v VMware
- Instalace VMware Player
  - https://www.vmware.com/products/workstation-player.html
  - nutnost mít adminstrátorská práva
- Stažení image Kali Linux pro VMware
  - https://www.kali.org/get-kali/#kali-virtual-machines
  - rozbalit archiv do požadované složky
  - ve VMware "Open Virtual Machine" --> najít ve složce s rozbaleným archivem jediný použitelný soubor a ten vybrat
- spustit virtuální stroj
  - v případě problémů: je třeba mít povolenou virtualizaci v UEFI, Google for help
- defaultní pčihlašovací údaje: 
  - login: kali
  - heslo: kali
  
### Prvotní spuštění
- v Kali:
- spustit terminál a aktualizovat kompletně systém
```
sudo apt update
sudo apt upgrade
```
### Instalace DeMITMo:
- v konzoli přejít do nějaké pracovní složky a poté:  
```
git clone https://github.com/JKarmasin/MITM_demo.git
cd MITM_demo
sudo ./install_adapter.sh
```
- restartovat systém pro načtení ovladačů k USB adaptéru Archer 1200AU, v případě úspěchu po připojení začně zelezně blikat
- opět v teminálu:
```
cd MITM_demo
./setup.sh
```
- Tím se vytvoří virtuální prostředí pro běh python aplikace a stáhnou se požadované balíčky
### Spuštění aplikace
- aplikace se pouští pomocí spoštěcího skriptu. Ten aktivuje virtuální prostředí a spustí samotnou aplikaci
- ve složce s apliakcí v konzoli:
```
./start.sh
```
# Před prvotní reálnou prezentací:
- vyzkoušet, že aplikace jde správně spustit
- otestovat možnost přepnutí adaptéru do monitorovacího módu
- v souboru "src/global_names.py" je možné zapnout developer mod, který odemkne všechny tlačítka už po spuštění aplikace. To je vhodné pro seznámení se s aplikací
- **zjistit si MAC adresy AP a zařízení, na které se bude útočit**
  - jinak by se mohlo jednat o trestnou činnost. Demonstrujte pouze na svých zařízeních!
- nastavit na AP heslo, které může být prozrazeno (jednorázové "Hackme123" apod.)
- aplikace má v kořenovém adresáři soubor *hesla.txt*, kam je třeba manuálně dopsat reálně použité heslo k Wi-Fi 
- při generování vlastního slovníku pozor na velikost výsledného souboru a délku prolamování! Viz kapitola 7.3.3 bakalářské práce.
- pro lepší fungování vymazat DNS cache na cíleném zařízení:
  - ve Windows: ipconfig /flushdns
  - v telefonu: chrome://net-internals/#dns
# Během demonstrace:
- mnoho kroků potřebuje k úspěšnému provedení datovou komunikaci na síti - ideálně na klientovi pustit online video - tím se zajistí nepřetržitý tok dat
- po spuštění monitoringu okolí počkat, dokud se neobjeví ve spodní tabulce MAC adresa požadovaného koncového zařízení 
- při zachytávání handshaku je nezbytné zapnout posílání deauthentifikačních rámců na cca 4 sekundy. Poté ji vypnout a počkat, dokud aplikace neoznámí, že zachytila handshake (bývá to do 10 sekund)
- při zapínání ARP spoofingu nemůže někdy aplikace najít k MAC příslušní IP adresy, stačí příslušné tlalčítko zmáčknout opakovaně, dokud se nezobrazí progress bar -> success
- apliakce má tmavý a světlý motiv (tlačítko vlevo dole)
- aplikaci vypínat tlačítkem Ukončit vlevo dole (vrátí vše do původního stavu)
- 


# Manuální instalace driveru Atheros Archer T4u v2
https://github.com/aircrack-ng/rtl8812au

### Fungující postup:
```
git clone https://github.com/aircrack-ng/rtl8812au
cd rtl*
sudo make dkms_install
sudo reboot
```
```
(odinstalace sudo dkms_remove)
make && make install
```

