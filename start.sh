#!/bin/bash
echo "
=============
=  DeMITMo  =
=============
"
# Kontrola exinstence adresáře 'tmp'
if [ ! -d "tmp" ]; then
    echo "Vytvářím adresář 'tmp'..."
    mkdir tmp
fi

source venv/bin/activate
sudo venv/bin/python3 DeMITMo.py
deactivate
