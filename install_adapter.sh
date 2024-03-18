#!/bin/bash
echo "\n
        =================================================
        =   xxx   xxxx  x   x  x  xxxxx  x   x   xxx    = 
        =   x  x  x     xx xx  x    x    xx xx  x   x   =
        =   x  x  xxxx  x x x  x    x    x x x  x   x   =
        =   x  x  x     x   x  x    x    x   x  x   x   =
        =   xxx   xxxx  x   x  x    x    x   x   xxx    =
        =                                               =
        =================================================
Tento skript nainstaluje ovladače pro Wi-Fi adapté s čipem Realtek 8812au.
Ovladače budoub staženy z úložiště fithub.com/aicrack-ng a umožňují adaptéru
spustit monitorovací mód. Tento příkaz vyžaduje k instalaci root oprávnění a 
restart počítače.
Budou také staženy potřebné balíky dkms, pythíon3.11-venv a linux-headers-6.6.9-amd64

Možnosti:
[1] - stáhnout ovladače, potřebné balíky a vše nainstalovat
[2] - pouze stáhnout ovladače a nic neinstalovat
[3] - konec
"
read -p "Vaše volba?: " answer
case $answer in
    [1]* )
        # Kontrola exinstence adresáře 'tmp'
        if [ ! -d "tmp" ]; then
            echo "Adresář 'tmp' neexistuje, vytvářím..."
            mkdir tmp
        fi

        # Stahuji balíčky
        sudo apt -y install python3.11-venv dkms linux-headers-6.6.9-amd64

        # Stahuji balíček s ovladači
        echo "\nStahuji ovladače do adresáře 'tmp'..."
        cd tmp
        git clone https://github.com/aircrack-ng/rtl8812au

        # Instalace
        echo "\nÚspěšně staženo. Instaluji..."
        cd rtl8812au
        sudo make dkms_install

        # Resrart?
        read -p "\nJe třeba restartovat stanici. Restarotvat ihned? (a/n)?: " answer2
        case $answer2 in
            [aA]* )
                sudo reboot
                ;;
            * )
                echo "\nUkončuji skript. Před používáním Wi-Fi adaptéru je třeba restartovat stanici."
                exit
                ;;
        esac
        ;;
    [2]* )
        # Kontrola exinstence adresáře 'tmp'
        if [ ! -d "tmp" ]; then
            echo "Adresář 'tmp' neexistuje, vytvářím..."
            mkdir tmp
        fi

        # Stahuji balíček s ovladači
        echo "\nStahuji ovladače do adresáře 'tmp'..."
        cd tmp
        git clone https://github.com/aircrack-ng/rtl8812au
        echo "\nOvladače jsou staženy. Ukončuji skript."
        exit
        ;;
    [3]* )
        echo "\nUkončuji skript."
        exit
        ;;
    * )
        echo "\nNeplatný vstup. Ukončuji skript."
        exit
        ;;





