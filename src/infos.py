import tkinter as tk
import customtkinter as ctk
from PIL import Image
from tkinter import PhotoImage


# # =========================================
def info_interface():
    iface_w = ctk.CTkToplevel()
    iface_w.title("INFO")
    icon = PhotoImage(master=iface_w,file='images/sword.png')     
    iface_w.tk.call('wm', 'iconphoto', iface_w._w, icon)

    text = "Rozhraní je adaptér pro připojení k Wi-fi sítím. V našem případě je to Archer AU1200 v2 s čipsetem Realtek 8812AU, \n\
         ke kterému je možné stáhnout ovladače, které umožňují monitorovací mód.\n\
             To u většiny moderních ovladačů není možné kvůli potenciálnímu zneužití - viz tato demonstrace."

    image = ctk.CTkImage(Image.open('images/infos/archer.jpg'), size=(250,250)) 
    image_label = ctk.CTkLabel(master=iface_w, text="", image=image)

    title_main = ctk.CTkLabel(iface_w, text="Rozhraní", font=('Open Sans', 30, "bold"))
    title_sub = ctk.CTkLabel(iface_w, text=text, font=('Open Sans', 16))

    image_label.grid(row=0,column=0, rowspan=2, padx=15, pady=15)
    title_main.grid(row=0 ,column=1, padx=5, pady=5, sticky="S")
    title_sub.grid(row=1 ,column=1, padx=10, pady=5, sticky ="N")
    
    iface_w.mainloop()

# =========================================
def info_monitor():
    monitor_w = ctk.CTkToplevel()
    monitor_w.title("INFO")
    icon = PhotoImage(master=monitor_w,file='images/sword.png')     
    monitor_w.tk.call('wm', 'iconphoto', monitor_w._w, icon)

    text = "Monitorovací mód (také promiskuitní mód) je schopnost bezdrátového adaptéru přijímat\n\
        všechny rámce v dosahu bez ohledu na to, komu jsou určeny. Standardně adaptér každý zachycený\n\
            rámec analyzuje a pokud není určen pro něj - jako cílová MAC adresa není adresa adaptéru,\n\
                tento rámec zahazuje. V monitorovacím módu ovšem všechny zachycené pakety přijímá k dalšímu\n\
                    zpracování."

    image = ctk.CTkImage(Image.open('images/infos/monitor.png'), size=(250,250)) 
    image_label = ctk.CTkLabel(master=monitor_w, text="", image=image)

    title_main = ctk.CTkLabel(monitor_w, text="Monitorovací mód", font=('Open Sans', 30, "bold"))
    title_sub = ctk.CTkLabel(monitor_w, text=text, font=('Open Sans', 16))

    image_label.grid(row=0,column=0, rowspan=2, padx=15, pady=15)
    title_main.grid(row=0 ,column=1, padx=5, pady=5, sticky="S")
    title_sub.grid(row=1 ,column=1, padx=10, pady=5, sticky ="N")
    
    monitor_w.mainloop()
# =========================================
def info_handshake():
    handshake_w = ctk.CTkToplevel()
    handshake_w.title("INFO")
    icon = PhotoImage(master=handshake_w,file='images/sword.png')     
    handshake_w.tk.call('wm', 'iconphoto', handshake_w._w, icon)

    text = "4-way Handshake je způsob, jak si klient a AP navzájem vymění informace\n\
        s heslem k síti, aniž by toto heslo bylo přímo odesláno. Vychází z úvahy, že i klient\n\
            i AP heslo znají a dokáží pomocí něj zašifrovat náhodně zvolené číslo a toto zašifrování ověřit.\n\
                K prolomení tohoto přístupového hesla je třeba zachytit všechny 4 zprávy handshaku a pomocí\n\
                    speciálních nástrojů se je pokusit dešifrovat například slovníkem hesel."

    image = ctk.CTkImage(Image.open('images/infos/handshake.png'), size=(250,250)) 
    image_label = ctk.CTkLabel(master=handshake_w, text="", image=image)

    title_main = ctk.CTkLabel(handshake_w, text="Handshake", font=('Open Sans', 30, "bold"))
    title_sub = ctk.CTkLabel(handshake_w, text=text, font=('Open Sans', 16))

    image_label.grid(row=0,column=0, rowspan=2, padx=15, pady=15)
    title_main.grid(row=0 ,column=1, padx=5, pady=5, sticky="S")
    title_sub.grid(row=1 ,column=1, padx=10, pady=5, sticky ="N")
    
    handshake_w.mainloop()
# =========================================
def info_deauth():
    deauth_w = ctk.CTkToplevel()
    deauth_w.title("INFO")
    icon = PhotoImage(master=deauth_w,file='images/sword.png')     
    deauth_w.tk.call('wm', 'iconphoto', deauth_w._w, icon)

    text = "Deauthentifikace je zranitelnost v návrhu a funkcionalitě wi-fi protokolu\n\
        802.11, kdy je možné zaslat AP speciálně vytvořený rámec a MAC adresou zařízení,\n\
            u kterého požadujeme odpojení od sítě. Tento rámec zpravidla posílá samo zařízení,\n\
                aby oznámilo AP, že se odpojuje. Nicméně lze tento rámec podvrhnout útočníkem a AP\n\
                    nemá možnost, jak pravost tohoto rámce ověřit. Pravidelné zasílání těchto rámců\n\
                        pro všechny zařízení v síti efektivně znefunkční celou Wi-Fi síť. Obranou proti tomu\n\
                            je ..."

    image = ctk.CTkImage(Image.open('images/infos/deauthentication.png'), size=(250,250)) 
    image_label = ctk.CTkLabel(master=deauth_w, text="", image=image)

    title_main = ctk.CTkLabel(deauth_w, text="Deauthentifikace", font=('Open Sans', 30, "bold"))
    title_sub = ctk.CTkLabel(deauth_w, text=text, font=('Open Sans', 16))

    image_label.grid(row=0,column=0, rowspan=2, padx=15, pady=15)
    title_main.grid(row=0 ,column=1, padx=5, pady=5, sticky="S")
    title_sub.grid(row=1 ,column=1, padx=10, pady=5, sticky ="N")
    
    deauth_w.mainloop()
# =========================================
def info_pw():
    pw_w = ctk.CTkToplevel()
    pw_w.title("INFO")
    icon = PhotoImage(master=pw_w,file='images/sword.png')     
    pw_w.tk.call('wm', 'iconphoto', pw_w._w, icon)

    text = "Při generování všech možných kombinací znaků k vytvoření hesel brzy narazíme\n\
        na limity paměťvých nároků (slovník má mnoho teravytů) a výpočetních nároků (trvá\n\
            neúměrně dlouho, než se slovník projde). Je proto lepší používat místo tupě generovaných\n\
                řetězců na míru vytvořené slovníky - například pomocí informací získaných OSINTem, \n\
                    nebo slovník nejčastěji používaných hesel (rockyou.txt (13 GB))"

    #image = ctk.CTkImage(Image.open('images/infos/archer.jpg'), size=(250,250)) 
    #image_label = ctk.CTkLabel(master=pw_w, text="", image=image)

    title_main = ctk.CTkLabel(pw_w, text="Slovník hesel", font=('Open Sans', 30, "bold"))
    title_sub = ctk.CTkLabel(pw_w, text=text, font=('Open Sans', 16))

    #image_label.grid(row=0,column=0, rowspan=2, padx=15, pady=15)
    title_main.grid(row=0 ,column=1, padx=5, pady=5, sticky="S")
    title_sub.grid(row=1 ,column=1, padx=10, pady=5, sticky ="N")
    
    pw_w.mainloop()
# =========================================
def info_crack():
    crack_w = ctk.CTkToplevel()
    crack_w.title("INFO")
    icon = PhotoImage(master=crack_w,file='images/sword.png')     
    crack_w.tk.call('wm', 'iconphoto', crack_w._w, icon)

    text = "Nejdůležitějším prvkem v bezpečnosti bezdrátových sítí je používání\n\
        dostatečně složitých hesel. Tato tabulka ukazuje časovou náročnost pro\n\
            prolomení různě složitých hesel. \n\n\
                Prioritou je používat hesla dlouhá! obsahujicí vše ze skupin\n\
                    VELKÝCH, malých, $p€c\ální@h zanků a číslic."

    image = ctk.CTkImage(Image.open('images/infos/passwords.jpg'), size=(250,250)) 
    image_label = ctk.CTkLabel(master=crack_w, text="", image=image)

    title_main = ctk.CTkLabel(crack_w, text="Hesla", font=('Open Sans', 30, "bold"))
    title_sub = ctk.CTkLabel(crack_w, text=text, font=('Open Sans', 16))

    image_label.grid(row=0,column=0, rowspan=2, padx=15, pady=15)
    title_main.grid(row=0 ,column=1, padx=5, pady=5, sticky="S")
    title_sub.grid(row=1 ,column=1, padx=10, pady=5, sticky ="N")
    
    crack_w.mainloop()
# =========================================
def info_forward():
    forward_w = ctk.CTkToplevel()
    forward_w.title("INFO")
    icon = PhotoImage(master=forward_w,file='images/sword.png')     
    forward_w.tk.call('wm', 'iconphoto', forward_w._w, icon)

    text = "Ke správné funkcionalitě ARP spoofingu je třeba, aby útočníkův počítač\n\
        sloužil jako přemostění v komunikaci mezi klientem a AP. To je možné zapnout \n\
            v systému Linux pomocí příkazu \"sysctl net.ipv4.ip_forward=1\""

    #image = ctk.CTkImage(Image.open('images/infos/archer.jpg'), size=(250,250)) 
    #image_label = ctk.CTkLabel(master=forward_w, text="", image=image)

    title_main = ctk.CTkLabel(forward_w, text="Rozhraní", font=('Open Sans', 30, "bold"))
    title_sub = ctk.CTkLabel(forward_w, text=text, font=('Open Sans', 16))

    #image_label.grid(row=0,column=0, rowspan=2, padx=15, pady=15)
    title_main.grid(row=0 ,column=1, padx=5, pady=5, sticky="S")
    title_sub.grid(row=1 ,column=1, padx=10, pady=5, sticky ="N")
    
    forward_w.mainloop()
# =========================================
def info_arp():
    arp_w = ctk.CTkToplevel()
    arp_w.title("INFO")
    icon = PhotoImage(master=arp_w,file='images/sword.png')     
    arp_w.tk.call('wm', 'iconphoto', arp_w._w, icon)

    text = "ARP poisoning text"

    image = ctk.CTkImage(Image.open('images/infos/arp.png'), size=(250,250)) 
    image_label = ctk.CTkLabel(master=arp_w, text="", image=image)

    title_main = ctk.CTkLabel(arp_w, text="ARP spoofing", font=('Open Sans', 30, "bold"))
    title_sub = ctk.CTkLabel(arp_w, text=text, font=('Open Sans', 16))

    image_label.grid(row=0,column=0, rowspan=2, padx=15, pady=15)
    title_main.grid(row=0 ,column=1, padx=5, pady=5, sticky="S")
    title_sub.grid(row=1 ,column=1, padx=10, pady=5, sticky ="N")
    
    arp_w.mainloop()
# =========================================
def info_catch():
    catch_w = ctk.CTkToplevel()
    catch_w.title("INFO")
    icon = PhotoImage(master=catch_w,file='images/sword.png')     
    catch_w.tk.call('wm', 'iconphoto', catch_w._w, icon)

    text = "Do souboru .pcap je zacována všechno kominakce od oběti k AP a naopak. Je zachycen každý paket.\n\
        Tento datový balík pak může být analyzován. Většina komunikace naštěstí probíhá šifrovaně (HTTPS)\n\
            a proto není snadné kompletní komunikaci přečíst. I tak z ní lze ale vyčíst mnoho zajímavých informací.\n\
            Temi mohou být například DNS dotazy."

    #image = ctk.CTkImage(Image.open('images/infos/.jpg'), size=(250,250)) 
    #image_label = ctk.CTkLabel(master=catch_w, text="", image=image)

    title_main = ctk.CTkLabel(catch_w, text="Zachycení datového toku", font=('Open Sans', 30, "bold"))
    title_sub = ctk.CTkLabel(catch_w, text=text, font=('Open Sans', 16))

    #image_label.grid(row=0,column=0, rowspan=2, padx=15, pady=15)
    title_main.grid(row=0 ,column=1, padx=5, pady=5, sticky="S")
    title_sub.grid(row=1 ,column=1, padx=10, pady=5, sticky ="N")
    
    catch_w.mainloop()
# =========================================
def info_dns():
    dns_w = ctk.CTkToplevel()
    dns_w.title("INFO")
    icon = PhotoImage(master=dns_w,file='images/sword.png')     
    dns_w.tk.call('wm', 'iconphoto', dns_w._w, icon)

    text = "DNS neboli Domain Name Service běží standardně na portu 53 pod protokolem UDPa je nezašifrován. \n\
        Proto je po útočníka jakýkoliv dotaz snadno čitelný. Doporučuje se všude, kde je to jen možné,\n\
            používat DNSSEC, což je zabezpečená varianta běžící na portu 553 a protokolu TCP."

    image = ctk.CTkImage(Image.open('images/infos/dns.png'), size=(250,250)) 
    image_label = ctk.CTkLabel(master=dns_w, text="", image=image)

    title_main = ctk.CTkLabel(dns_w, text="DNS", font=('Open Sans', 30, "bold"))
    title_sub = ctk.CTkLabel(dns_w, text=text, font=('Open Sans', 16))

    image_label.grid(row=0,column=0, rowspan=2, padx=15, pady=15)
    title_main.grid(row=0 ,column=1, padx=5, pady=5, sticky="S")
    title_sub.grid(row=1 ,column=1, padx=10, pady=5, sticky ="N")
    
    dns_w.mainloop()


