import customtkinter as ctk
from customtkinter import N, S
import tkinter as tk
from tkinter import PhotoImage, Message
from src import c_mitm
from PIL import Image

def open_main_window():
    # Zavření původního okna
    splash.destroy()
    # Otevření hlavního okna
    app = c_mitm.App()
    app.mainloop()


# Vytvoření kořenového okna

splash = ctk.CTk()
splash.title("DeMITMo")
icon = PhotoImage(file='images/sword.png')     
splash.tk.call('wm', 'iconphoto', splash._w, icon)

icon = ctk.CTkImage(Image.open('images/sword.png'), size=(150,150))  
#icon = icon.subsample(3, 3)
image_label = ctk.CTkLabel(splash, text="", image=icon)

title_main = ctk.CTkLabel(splash, text="DeMITMo", font=('Helvetica', 50, "bold"), text_color='green')
title_sub = ctk.CTkLabel(splash, text="Demonstrační nástroj Man-in-the-middle útoku", font=('Helvetica', 16))
title_law = ctk.CTkLabel(splash, text="Důležité upozornění:", font=('Helvetica', 16))

#message_law = tk.Message(splash, width=500,text="Demonstraci provádějte pouze na své vlastní síti a svém zařízení nebo na síti někoho jiného pouze pokud máte písemný souhlas vlastníka této sítě. Získání neoprávěněného přístupu k počítačovému systému a nebo síti je tresné podle § 230 odst. 1 Zákona číslo 40/2009 Sb. trestního zákoníku, ve znění pozdějších předpisů. Zachytávání komunikace na síti je tresné podle § 182 odst. 1 téhož zákona (Porušení tajemství dopravovaných zpráv).")
#message_law = ctk.CTkTextbox(splash, width=500)
message_law = ctk.CTkLabel(splash, font=('Helvetica',14), text="Demonstraci provádějte pouze na své vlastní síti a svém zařízení nebo na síti \nněkoho jiného pouze, pokud máte písemný souhlas vlastníka této sítě. \nZískání neoprávěněného přístupu k počítačovému systému a nebo síti je tresné \npodle § 230 odst. 1 Zákona číslo 40/2009 Sb. trestního zákoníku, \nve znění pozdějších předpisů. Zachytávání komunikace na síti je tresné \npodle § 182 odst. 1 téhož zákona (Porušení tajemství dopravovaných zpráv).")
# Přidání tlačítka "Pokračuj", které otevře nové okno
continue_button = ctk.CTkButton(splash, text="Pokračuj", command=open_main_window)

image_label.grid(row=0,column=0, rowspan=2, padx=15, pady=15)
title_main.grid(row=0 ,column=1, padx=5, pady=5, sticky="S")
title_sub.grid(row=1 ,column=1, padx=10, pady=5, sticky ="N")
title_law.grid(row=2 ,column=0, columnspan=2, padx=5, pady=5)
message_law.grid(row=3 ,column=0, columnspan=2)
#message_law.insert("0.0", "Demonstraci provádějte pouze na své vlastní síti a svém zařízení nebo na síti někoho jiného pouze pokud máte písemný souhlas vlastníka této sítě. Získání neoprávěněného přístupu k počítačovému systému a nebo síti je tresné podle § 230 odst. 1 Zákona číslo 40/2009 Sb. trestního zákoníku, ve znění pozdějších předpisů. Zachytávání komunikace na síti je tresné podle § 182 odst. 1 téhož zákona (Porušení tajemství dopravovaných zpráv).")
continue_button.grid(row=9, column=0, columnspan=2, pady=10)

# Spuštění hlavní smyčky
splash.mainloop()
