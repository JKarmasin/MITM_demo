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

    text = "\n\
Rozhraní je adaptér pro připojení k datovým sítím - bezdrátovým nebo ethernetovým.\n\
V této demonstaci je to Archer AU1200 v2 s čipsetem Realtek 8812AU.\n\
K tomu je možné stáhnout ovladače, které umožňují přepnutí do monitorovacího módu.\n\
To u většiny moderních ovladačů není možné kvůli potenciálnímu zneužití?\n\
\n    Jakému?\n\n\
Viz tato demonstrace.\n\n\
(MAC adresa tohoto adaptéru není konstantní a mění se)"

    image = ctk.CTkImage(Image.open('images/infos/archer.jpg'), size=(250,250)) 
    image_label = ctk.CTkLabel(master=iface_w, text="", image=image)

    title_main = ctk.CTkLabel(iface_w, text="Rozhraní", font=('Open Sans', 30, "bold"))
    title_sub = ctk.CTkLabel(iface_w, text=text, justify="left", font=('Open Sans', 16))

    image_label.grid(row=0,column=0, rowspan=2, padx=15, pady=15)
    title_main.grid(row=0 ,column=1, padx=5, pady=5, sticky="S")
    title_sub.grid(row=1 ,column=1, padx=10, pady=5, sticky="NW")
    
    iface_w.mainloop()

# =========================================
def info_monitor():
    monitor_w = ctk.CTkToplevel()
    monitor_w.title("INFO")
    icon = PhotoImage(master=monitor_w,file='images/sword.png')     
    monitor_w.tk.call('wm', 'iconphoto', monitor_w._w, icon)

    text = "\n\
Monitorovací mód (také RFMON - Radio Frequency MONitor) je schopnost bezdrátového adaptéru přijímat\n\
všechny rámce v dosahu bez ohledu na to, komu jsou určeny. Standardně adaptér každý zachycený\n\
rámec analyzuje a pokud není určen pro něj (jako cílová MAC adresa není adresa tohoto adaptéru)\n\
tento rámec zahazuje. To je prováděno příslušným nastavením RX filtru v adaptéru. V monitorovacím módu\n\
ovšem všechny zachycené pakety adaptér přijímá k dalšímu zpracování.\n\
\nObdobou je tzv. promiskuitní mód, který může kromě Wi-Fi sítí fungovat i na Ethernetu. K dalšímu zpracování\n\
pouští všechny pakety, které k němu po kabelu dorazí. Proto už se nepoužívají zastaralé huby, ale switche,\n\
které rámce samy přeposílají pouze správným příjemcům.\n\n\
Obranou je používání šifrování v komunikaci. Přestože nezabrání odposlechu, zajistí, že útočník ze zachycených\n\
rámců nepřečte žádné informace."

    image = ctk.CTkImage(Image.open('images/infos/monitor2.png'), size=(600,500)) 
    image_label = ctk.CTkLabel(master=monitor_w, text="", image=image)

    title_main = ctk.CTkLabel(monitor_w, text="Monitorovací mód", font=('Open Sans', 30, "bold"))
    title_sub = ctk.CTkLabel(monitor_w, text=text, justify="left", font=('Open Sans', 16))

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

    text = "\
Four-way Handshake je způsob, jak si klient a AP navzájem vymění informace s heslem\n\
k síti, aniž by toto heslo bylo přímo odesláno. Vychází z úvahy, že i klient i AP\n\
heslo znají a dokáží pomocí něj zašifrovat náhodně zvolené číslo a shodnost tohoto zašifrování\n\
ověřit. K prolomení tohoto přístupového hesla je třeba zachytit všechny 4 zprávy handshaku\n\
a pomocí speciálních nástrojů se je pokusit dešifrovat například hrubou silou (slovníkem hesel).\n\
\n\
\n\
1. zpráva: není nijak šifrovaná. AP vygeneruje náhodné číslo \"ANonce\", které odesílá klientovi.\n\
                Klient vygeneruje \"SAnonce\" a pomocí něj a ANonce a PMK vygeneruje svůj PTK.\n\n\
2. zpráva: klient odesílá sebou vygenerovaný \"SNonce\" Access Pointu. Ten ti tak také můžeš vygenerovat\n\
                stejný PTK ze svého ANonce, PMK a SNonce.\n\n\
3. zpráva: AP posílá klientovi potvrzení o vytvoření společného šifrovacího kláče PTK a popřípadě posílá GTK.\n\n\
4. zpráva: Klient oznamuje AP, že má aktivní stejný PTK a popípadě GTK.\n\
\n\
HANDSHAKE JE DOKONČEN. AP I KLIENT MAJÍ STEJNÝ ŠIFROVACÍ KLÍČ PRO KOMUNIKACI.\n\
\n\n\n\
Legenda:\n\
- PMK (Private Master Key) = PSK (Pre-shared Key) - \"heslo\" k Wi-Fi síti\n\
- PTK (Pairwise Temporal Key) - klíč používaný k šifrování unicast komunikace\n\
- GTK (Group Temporal Key) - klíč používaný k šifrování broadcast/multicast komunikace"

    image = ctk.CTkImage(Image.open('images/infos/handshake.png'), size=(700,600)) 
    image_label = ctk.CTkLabel(master=handshake_w, text="", image=image)

    title_main = ctk.CTkLabel(handshake_w, text="Handshake", font=('Open Sans', 30, "bold"))
    title_sub = ctk.CTkLabel(handshake_w, text=text, justify="left", font=('Open Sans', 16))

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

    text = "\
Deauthentifikace je zranitelnost v návrhu a funkcionalitě Wi-Fi protokolu\n\
802.11, kdy je možné zaslat AP speciálně vytvořený rámec s MAC adresou zařízení,\n\
u kterého požadujeme odpojení od sítě. Tento rámec zpravidla posílá samo zařízení,\n\
aby oznámilo AP, že se odpojuje. Nicméně lze tento rámec podvrhnout útočníkem a AP\n\
nemá možnost, jak pravost tohoto rámce ověřit. Pravidelné zasílání těchto rámců\n\
pro všechny zařízení v síti efektivně znefunkční celou Wi-Fi síť.\n\n\
Obranou proti tomu je používání takzvaných Protected Management Frames, které byly\n\
představeny ve standardu šifrování WPA3."

    image = ctk.CTkImage(Image.open('images/infos/deauthentication.png'), size=(350,400)) 
    image_label = ctk.CTkLabel(master=deauth_w, text="", image=image)

    title_main = ctk.CTkLabel(deauth_w, text="Deauthentifikace", font=('Open Sans', 30, "bold"))
    title_sub = ctk.CTkLabel(deauth_w, text=text, justify="left", font=('Open Sans', 16))

    image_label.grid(row=0,column=0, rowspan=2, padx=30, pady=30)
    title_main.grid(row=0 ,column=1, padx=5, pady=5, sticky="S")
    title_sub.grid(row=1 ,column=1, padx=15, pady=15, sticky ="N")
    
    deauth_w.mainloop()
# =========================================
def info_pw():
    pw_w = ctk.CTkToplevel()
    pw_w.title("INFO")
    icon = PhotoImage(master=pw_w,file='images/sword.png')     
    pw_w.tk.call('wm', 'iconphoto', pw_w._w, icon)

    text = "\
Při generování všech možných kombinací znaků k vytvoření hesel brzy narazíme\n\
na limity paměťvých nároků (slovník bude mít mnoho terabytů) a výpočetních nároků (trvá\n\
neúměrně dlouho, než se slovník projde). Je proto lepší místo hloupě generovaných\n\
řetězců používat na míru vytvořené slovníky - například pomocí informací získaných OSINTem, \n\
nebo slovník nejčastěji používaných hesel (slavný slovník \"rockyou.txt\" s 14 miliony hesly)\n\n\
\n\
OSINT (Open Source Intelligence)\n\n\
- získávání (zpravodajských) informací z otevřených zdrojů, především internetu\n\
- nejčastěji sociální sítě a blogy, metadata audiovizuálních souborů, geolokace\n\
- snadno se dají najít jména dětí, domácích mazlíčků, telefonních čísel, datumů narození, adres apod.\n\
    --> ty jsou často součástí hesel\n\
- NIKDY SI NEDÁVAT DO HESLA ŽÁDNÉ OSOBNÍ INFORMACE, CO JSOU DOHLEDATELNÉ NA INTERNETU!\n\
    - včetně oblíbených kapel, filmů, hlášek, sportovních týmů a hráčů..."

    image = ctk.CTkImage(Image.open('images/infos/digitalfootprint.png'), size=(300,450)) 
    image_label = ctk.CTkLabel(master=pw_w, text="", image=image)

    title_main = ctk.CTkLabel(pw_w, text="Slovník hesel", font=('Open Sans', 30, "bold"))
    title_sub = ctk.CTkLabel(pw_w, text=text, justify="left", font=('Open Sans', 16))

    image_label.grid(row=0,column=0, rowspan=2, padx=30, pady=30)
    title_main.grid(row=0 ,column=1, padx=5, pady=5, sticky="S")
    title_sub.grid(row=1 ,column=1, padx=15, pady=15, sticky ="N")
    
    pw_w.mainloop()
# =========================================
def info_crack():
    crack_w = ctk.CTkToplevel()
    crack_w.title("INFO")
    icon = PhotoImage(master=crack_w,file='images/sword.png')     
    crack_w.tk.call('wm', 'iconphoto', crack_w._w, icon)

    text = "\
Nejdůležitějším prvkem v bezpečnosti bezdrátových sítí je používání\n\
dostatečně složitých hesel. Tato tabulka ukazuje časovou náročnost pro\n\
prolomení různě složitých hesel. \n\n\
Prioritou je používat hesla dlouhá obsahujicí vše ze skupin\n\
VELKÝCH, malých, $p€c|ální@h zanků a číslic.\n\n\
Prioritním aspektem by měla být delka hesla. Je bezpečnější delší, ale méně\n\
složité heslo, než extrémně složité, ale krátké. Méně složité heslo je i \n\
snadnější na zapamatování a rychlejší na napsání. Složitá hesla mají uživatelé\n\
tendenci si zapisovat na papírky pod klávesnicí apod."

    image = ctk.CTkImage(Image.open('images/infos/passwords.jpg'), size=(600,600)) 
    image_label = ctk.CTkLabel(master=crack_w, text="", image=image)

    title_main = ctk.CTkLabel(crack_w, text="Lámání hesla", font=('Open Sans', 30, "bold"))
    title_sub = ctk.CTkLabel(crack_w, text=text, justify="left", font=('Open Sans', 16))

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

    text = "\
Ke správné funkcionalitě ARP spoofingu je třeba, aby útočníkův počítač\n\
sloužil jako přemostění v komunikaci mezi klientem a AP. Tedy aby přeposílal\n\
pakety od jednoho zařázení k druhému a naopak. Tento tzv. IP forwarding je\n\
možné zapnout v systému Linux pomocí příkazu \"sysctl net.ipv4.ip_forward=1\"\n\
Využívá se například pokud počítač slouží jako firewall, NAT nebo router."


    title_main = ctk.CTkLabel(forward_w, text="Přeposílání paketů", font=('Open Sans', 30, "bold"))
    title_sub = ctk.CTkLabel(forward_w, text=text, justify="left", font=('Open Sans', 16))

    title_main.grid(row=0 ,column=1, padx=5, pady=5, sticky="S")
    title_sub.grid(row=1 ,column=1, padx=10, pady=5, sticky ="N")
    
    forward_w.mainloop()
# =========================================
def info_arp():
    arp_w = ctk.CTkToplevel()
    arp_w.title("INFO")
    icon = PhotoImage(master=arp_w,file='images/sword.png')     
    arp_w.tk.call('wm', 'iconphoto', arp_w._w, icon)

    text = "\
ARP spoofing je zneužití zranitelnosti protokolu ARP. Ten slouží k překladu\n\
IP adres (např. 192.168.105.99) na fyzické MAC adresy (např. A6:FF:13:2B:87:FC) na\n\
lokální síti, tedy na vrstě L2 OSI modelu.\n\n\n\
Princip standardního ARP dotazování:\n\n\
- Pepův počítač (PC1) se všech ptá: \"Jak se jmenuje Frantův počítač? Řekni to mně (PC1)\"\n\
- Frantův počítač (PC9) odpovídá: \"Teď vím, že Pepův počítač je PC1, já jsem Frantův počítač PC9\"\n\
\n\
ARP spoofing:\n\n\
- Útočník (NTB666) volá: \"Frantův počítači PC9, já jsem Pepův počítač a jsem nově NTB666\"\n\
- Útočník (NTB666) volá: \"Pepův počítači PC1, já jsem Frantův počítač a jsem nově NTB666\"\n\n\
Tím obě oběti donutí si přepsat jejich ARP tabulky, kde si uchovávají adresy známých zařízení v okolí,\n\
a docílí toho, že obě zařízení nevědomky posílají pakety jemu namísto Pepovi nebo Frantovi."

    image = ctk.CTkImage(Image.open('images/infos/arp.png'), size=(600,400)) 
    image_label = ctk.CTkLabel(master=arp_w, text="", image=image)

    title_main = ctk.CTkLabel(arp_w, text="ARP spoofing", font=('Open Sans', 30, "bold"))
    title_sub = ctk.CTkLabel(arp_w, text=text, justify="left", font=('Open Sans', 16))

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

    text = "\
Do souboru full_traffic.pcap je zachycována všechna komunikace od oběti k AP a naopak. Je zachycen každý paket.\n\
Tento datový balík pak může být analyzován. Většina komunikace naštěstí probíhá šifrovaně (HTTPS),\n\
a proto není snadné kompletní komunikaci přečíst. I tak z ní lze ale vyčíst mnoho zajímavých informací.\n\
\n\
Těmi mohou být například DNS dotazy...\n\n\
Částečnou ochranou proti zneužití takového zachycení je používání VPN (Virtual Private Network). Jedná se o\n\
zašifrování kompletní komunikace směrem do internetu, kdy se klient nepřipojuje přímo k jednotlivým serverům, \n\
ale připojuje se přes prostředníka - VPN server. Ten se stará o zašifrování komunikace. Tato ochrana nezabrání\n\
zachycení komunikace útočníkem, ale přidává další vrstu ochtrany tím, že všechna data budou pro útočníka nečitelná.\n\n\
(Pozor na velikost souboru, kam se komunikace zachytává. Při silném datovém provozu oběti, může nabývat\n\
rychle na objemu!)"

    image = ctk.CTkImage(Image.open('images/infos/wireshark.png'), size=(300,300)) 
    image_label = ctk.CTkLabel(master=catch_w, text="", image=image)

    title_main = ctk.CTkLabel(catch_w, text="Zachycení datového toku", font=('Open Sans', 30, "bold"))
    title_sub = ctk.CTkLabel(catch_w, text=text, justify="left", font=('Open Sans', 16))

    image_label.grid(row=0,column=0, rowspan=2, padx=15, pady=15)
    title_main.grid(row=0 ,column=1, padx=5, pady=5, sticky="S")
    title_sub.grid(row=1 ,column=1, padx=10, pady=5, sticky ="N")
    
    catch_w.mainloop()
# =========================================
def info_dns():
    dns_w = ctk.CTkToplevel()
    dns_w.title("INFO")
    icon = PhotoImage(master=dns_w,file='images/sword.png')     
    dns_w.tk.call('wm', 'iconphoto', dns_w._w, icon)

    text = "\
DNS neboli Domain Name Service je služba překládající pro člověka čitelné názvy webů\n\
na jejich číselnou IP adresu. Při jejich analýze jsou tedy vidět všechny weby, které\n\
oběť navštívila. DNS běží standardně na portu 53 v nezašifrované podobě.\n\
Proto je po útočníka jakýkoliv dotaz snadno čitelný. Doporučuje se všude, kde je to\n\
jen možné, používat DNSSEC, což jebezpečnější varianta využívající digitální podpis.\n\
Zařízení si proto může ověřit, že DNS záznam není podvrhnutý."
    text2 = "\
Bezpečnější variantou je pak oět využívat VPN, kdy je kompletní tok dat pro útočníka\n\
nečitelný. Existují bezplatné varianty VPN, ale doporučuje se využívat placené služby.\n\
Rozdíl je v rychlosti a množství serverů VPN využitelných pro připojení v různých státech.\n\
Důležitým faktorem je také důveryhodnost. Placené služby jsou zpravidla zůvěryhodnější, než\n\
bezplatné varitanty. U těch není jistota, že samy provoz neanalyzují a dál data nepřeprodávají."

    image = ctk.CTkImage(Image.open('images/infos/dns.png'), size=(300,250)) 
    image_label = ctk.CTkLabel(master=dns_w, text="", image=image)
    image = ctk.CTkImage(Image.open('images/infos/vpn.jpg'), size=(450,250)) 
    image_label2 = ctk.CTkLabel(master=dns_w, text="", image=image)

    title_main = ctk.CTkLabel(dns_w, text="DNS", font=('Open Sans', 30, "bold"))
    title_sub = ctk.CTkLabel(dns_w, text=text, justify="left", font=('Open Sans', 16))
    title_main2 = ctk.CTkLabel(dns_w, text="VPN", font=('Open Sans', 30, "bold"))
    title_sub2 = ctk.CTkLabel(dns_w, text=text2, justify="left", font=('Open Sans', 16))

    image_label.grid(row=0,column=0, rowspan=2, padx=15, pady=15)
    image_label2.grid(row=2,column=0, rowspan=2, padx=15, pady=15)
    title_main.grid(row=0 ,column=1, padx=5, pady=5, sticky="S")
    title_sub.grid(row=1, column=1, padx=10, pady=5, sticky ="N")
    title_main2.grid(row=2 ,column=1, padx=5, pady=5, sticky="S")
    title_sub2.grid(row=3, column=1, padx=10, pady=5, sticky ="N")
    dns_w.mainloop()


