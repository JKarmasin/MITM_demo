import tkinter as tk
from tkinter import PhotoImage, Message
from src import mitm


def open_main_window():
    # Zavření původního okna
    splash.destroy()
    # Otevření hlavního okna
    mitm.main()

# Vytvoření kořenového okna

splash = tk.Tk()
splash.title("DeMITMo")
icon = PhotoImage(file='images/sword.png')   
splash.tk.call('wm', 'iconphoto', splash._w, icon)

icon = icon.subsample(3, 3)
image_label = tk.Label(splash, image=icon)

title_main = tk.Label(splash, text="DeMITMo", font=('Helvetica', 50, "bold"), fg='green')
title_sub = tk.Label(splash, text="Demonstrační nástroj Man-in-the-middle útoku", font=('Helvetica', 16))
title_law = tk.Label(splash, text="Důležité upozornění:", font=('Helvetica', 16))

message_law = Message(splash, width=500,text="Demonstraci provádějte pouze na své vlastní síti a svém zařízení nebo na síti někoho jiného pouze pokud máte písemný souhlas vlastníka této sítě. Získání neoprávěněného přístupu k počítačovému systému a nebo síti je tresné podle § 230 odst. 1 Zákona číslo 40/2009 Sb. trestního zákoníku, ve znění pozdějších předpisů. Zachytávání komunikace na síti je tresné podle § 182 odst. 1 téhož zákona (Porušení tajemství dopravovaných zpráv).")
# Přidání tlačítka "Pokračuj", které otevře nové okno
continue_button = tk.Button(splash, text="Pokračuj", command=open_main_window)

image_label.grid(row=0,column=0, rowspan=2, padx=15, pady=15)
title_main.grid(row=0 ,column=1, padx=5, pady=5, sticky="S")
title_sub.grid(row=1 ,column=1, padx=10, pady=5, sticky ="N")
title_law.grid(row=2 ,column=0, columnspan=2, padx=5, pady=5)
message_law.grid(row=3 ,column=0, columnspan=2)
continue_button.grid(row=9, column=0, columnspan=2, pady=10)

# Spuštění hlavní smyčky
splash.mainloop()
