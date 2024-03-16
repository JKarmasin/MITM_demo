import customtkinter
from PIL import Image
from tkinter import PhotoImage
from src import c_T1_reco
from src import c_T2_capture
from src import c_T3_crack
from src import c_T4_arp_spoof
from src import c_T5_dns_spoof



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("DeMITMo")
        images_path = "images/"
        icon = PhotoImage(file=images_path + "sword.png")   
        self.tk.call('wm', 'iconphoto', self._w, icon)

        width=1500
        height=1000
        x=700
        y=1445
        self.geometry('%dx%d+%d+%d' % (width, height, x, y))
        
        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        customtkinter.set_appearance_mode("Dark")

        # load images with light and dark mode image
        self.logo_image = customtkinter.CTkImage(Image.open(images_path + "sword.png"), size=(26, 26))
        self.large_test_image = customtkinter.CTkImage(Image.open(images_path + "large_test_image.png"), size=(500, 150))
        self.image_icon_image = customtkinter.CTkImage(Image.open(images_path + "image_icon_light.png"), size=(20, 20))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(images_path + "home_dark.png"),
                                                 dark_image=Image.open(images_path + "home_light.png"), size=(20, 20))
        self.chat_image = customtkinter.CTkImage(light_image=Image.open(images_path + "chat_dark.png"),
                                                 dark_image=Image.open(images_path + "chat_light.png"), size=(20, 20))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(images_path + "add_user_dark.png"),
                                                     dark_image=Image.open(images_path + "add_user_light.png"), size=(20, 20))
        
        
        #===================================================================================================================================
        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(6, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  DeMITMo", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        #============================================
        self.frame_1_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Vyhledání cílů",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.home_image, anchor="w", command=self.frame_1_button_event)
        self.frame_1_button.grid(row=1, column=0, sticky="ew")

        self.frame_2_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Záchyt handshaku",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.chat_image, anchor="w", command=self.frame_2_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        self.frame_3_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Prolomení hesla",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.add_user_image, anchor="w", command=self.frame_3_button_event)
        self.frame_3_button.grid(row=3, column=0, sticky="ew")

        self.frame_4_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Man-in-the-middle",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.add_user_image, anchor="w", command=self.frame_4_button_event)
        self.frame_4_button.grid(row=4, column=0, sticky="ew")

        self.frame_5_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Záchyt DNS dotazů",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.add_user_image, anchor="w", command=self.frame_5_button_event)
        self.frame_5_button.grid(row=5, column=0, sticky="ew")

        # Appearence menu
        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Dark", "Light", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")
#===================================================

        # create first frame
        self.T1_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        c_T1_reco.draw_reco(self.T1_frame, self.frame_1_button)

        # create second frame
        self.T2_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        c_T2_capture.draw_capture(self.T2_frame, self.frame_2_button)

        # create third frame
        self.T3_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        c_T3_crack.draw_crack(self.T3_frame, self, self.frame_3_button)
        
         # create fourth frame
        self.T4_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        c_T4_arp_spoof.draw_arp_spoof(self.T4_frame, self.frame_4_button)       
        
         # create fourth frame
        self.T5_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        c_T5_dns_spoof.draw_dns(self.T5_frame)         
        
        
        
        
        
        
        
        
        
        
        # select default frame
        self.select_frame_by_name("frame_1")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.frame_1_button.configure(fg_color=("gray75", "gray25") if name == "frame_1" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")
        self.frame_4_button.configure(fg_color=("gray75", "gray25") if name == "frame_4" else "transparent")
        self.frame_5_button.configure(fg_color=("gray75", "gray25") if name == "frame_5" else "transparent")

        # show selected frame
        if name == "frame_1":
            self.T1_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.T1_frame.grid_forget()
        if name == "frame_2":
            self.T2_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.T2_frame.grid_forget()
        if name == "frame_3":
            self.T3_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.T3_frame.grid_forget()
        if name == "frame_4":
            self.T4_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.T4_frame.grid_forget()
        if name == "frame_5":
            self.T5_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.T5_frame.grid_forget()


    def frame_1_button_event(self):
        self.select_frame_by_name("frame_1")

    def frame_2_button_event(self):
        self.select_frame_by_name("frame_2")

    def frame_3_button_event(self):
        self.select_frame_by_name("frame_3")

    def frame_4_button_event(self):
        self.select_frame_by_name("frame_4")

    def frame_5_button_event(self):
        self.select_frame_by_name("frame_5")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)


#if __name__ == "__main__":
#    app = App()
#    app.mainloop()
