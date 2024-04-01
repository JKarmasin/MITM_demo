
# Bakalářská práce
<img src="https://knihovna.vspj.cz/2017/images/vspj_logo_symbol.svg" alt="drawing" width="200"/>

## Demonstrační nástroj Man-in-the-middle útoků

### Cíl práce:
Cílem práce je navrhnout a implementovat demonstrační nástroj k popisu a  vysvětlení principu Man-in-the-middle (MITM) útoků na bezdrátové sítě. Tento nástroj poslouží k názorným ukázkám během školení kybernetické bezpečnosti především pro příslušníky Armády České republiky, proto musí být uživatelské rozhraní dostatečně intuitivní a přehledné. Součástí nástroje bude i popis relevantních protiopatření, které zvyšují imunitu proti MITM útokům. Nástroj bude implementován na platformě KALI Linux. Rovněž budou vytvořeny návodné a dokumentační nástroje (poster, brožura) pro cílové publikum pro zvýšení účinku školení s využitím tohoto nástroje.


### Základní technologie:
- Kali Linux ![Kali](https://img.shields.io/badge/Kali-268BEE?style=for-the-badge&logo=kalilinux&logoColor=white)
    - airdump-ng, aireplay-ng, aircrack-ng
- externí USB Wi-Fi adaptér s možností přepuntí do monitorovacího módu
- vnitřní funkcionalita v Pythonu - interaktivní script ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
- GUI nadstavba v Pythonu
- nutnost vlastnit USB Wi-Fi Adaptér umožňující monitorovací mód
- testváno s Atheros Archer 1200AU
  ![adapter](images/infos/archer.jpg)
---
# Instalace
```
git clone https://github.com/JKarmasin/MITM_demo.git
cd MITM_demo
sudo ./install_adapter.sh
(reboot)

cd MITM_demo
./setup.sh
./start.sh
```


---
# Manuální instalace driveru Atheros Archer T4u v2

### Fungující postup:
```
https://github.com/aircrack-ng/rtl8812au
cd rtl*
sudo make dkms_install
sudo reboot
```
```
(odinstalace sudo dkms_remove)
make && make install
```
- záloha: https://github.com/cilynx/rtl88x2bu
- záloha: https://github.com/RinCat/RTL88x2BU-Linux-Driver

## Otázky:
- zdrojový kód bude někdo zkoumat? Mám ho okomentovávat? Dávat do textu BP nějaké zajímavé části zdrojového kódu anebo architekturu?
- uživatelská dokumentace bude. Programátorská má být? 
