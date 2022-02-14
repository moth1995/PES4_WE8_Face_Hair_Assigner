import pymem
import pymem.process
from editor import Player
from tkinter import Tk, messagebox, ttk, Button, Label, Menu, Spinbox, filedialog, IntVar
from pathlib import Path

class Gui:
    def __init__(self, master):
        self.master = master
        self.filename = ""
        self.appname='PES4/WE8 Face/Hair assigner'
        master.title(self.appname)
        w = 350 # width for the Tk root
        h = 250 # height for the Tk root
        # get screen width and height
        ws = master.winfo_screenwidth() # width of the screen
        hs = master.winfo_screenheight() # height of the screen
        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        # set the dimensions of the screen 
        # and where it is placed
        master.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
        self.my_menu=Menu(master)
        master.config(menu=self.my_menu)
        self.file_menu = Menu(self.my_menu, tearoff=0)
        self.help_menu = Menu(self.my_menu, tearoff=0)
        self.my_menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open", command=self.search_exe)
        self.file_menu.add_command(label="Exit", command=master.quit)
        self.my_menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="Manual", command=self.show_help)
        self.help_menu.add_command(label="About", command=self.show_thanks)
        self.player_lbl = Label(master, text="Player Name: ")
        self.player_lbl.pack()

        self.face_type_lbl = Label(master, text="Face Type").pack()
        self.face_type_dropdown = ttk.Combobox(master,values=["Build", "Original", "Preset"],state="readonly")
        self.face_type_dropdown.bind('<<ComboboxSelected>>', lambda event: self.set_param())
        self.face_type_dropdown.pack()

        self.skin_lbl = Label(master,text="Skin Colour").pack()
        self.skin_spb_var = IntVar()
        self.skin_spb_var.set(1)
        self.skin_spb = Spinbox(master, textvariable=self.skin_spb_var, from_=1, to=4,command = self.set_param)
        self.skin_spb.bind('<Return>', lambda event: self.set_param())
        self.skin_spb.pack()


        self.face_id_lbl = Label(master,text="Face ID").pack()
        self.face_spb_var = IntVar()
        self.face_spb_var.set(1)
        self.face_id_spb = Spinbox(master, textvariable=self.face_spb_var, from_=1, to=256,command = self.set_param)
        self.face_id_spb.bind('<Return>', lambda event: self.set_param())
        self.face_id_spb.pack()

        self.hair_id_lbl = Label(master,text="Special Hairstyle ID").pack()
        self.hair_spb_var = IntVar()
        self.hair_spb_var.set(0)
        self.hair_id_spb = Spinbox(master, textvariable=self.hair_spb_var, from_=0, to=2047,command = self.set_param)
        self.hair_id_spb.bind('<Return>', lambda event: self.set_param())
        self.hair_id_spb.pack()
        self.read_values = Button(master,text="Read data", command=self.read_player).pack()

    def search_exe(self):
        self.filename = filedialog.askopenfilename(initialdir=".",title=self.appname, filetypes=([("PES4/WE8 Executable", ".exe"),]))
        if self.filename!="":
            self.load_data()

    def show_help(self):
        messagebox.showinfo(title=self.appname,message=
        """
        This is a small guide to use this tool\n
        This tool was created to use with face/hair server so you can assign faces and hairs in a easy way, 
        but it can be use with the original version of the game

        First of all, you need to start your game first, then you select your exe file location, go into edit mode
        and then go to edit the player you want to edit.

        Faces ids go from 1 to 256, please don't input any other value, or your game may crash, of course this is if you do have
        installed the faceserver, otherwise 
        if skin color = 1 and face type = original then max value will be 105 or face type = preset then max value will be 232
        if skin color = 2 and face type = original then max value will be 71 or face type = preset then max value will be 129
        if skin color = 3 and face type = original then max value will be 24 or face type = preset then max value will be 49
        if skin color = 4 and face type = original then max value will be 12 or face type = preset then max value will be 26
        If you have face type = build then face id spinbox won't affect your game, in fact, probably will get some bug strings (wont cause any crash)
        inside the internal editor.
        Hairs ids go from 0 to 2047, special hairstyles start at 1026 please don't input any other value, 
        or your game may crash, of course this is if you do have installed the hairserver, otherwise the max value allowed will be 1053
        Have fun creating new patches for PES4 and WE8I!
        """.replace('        ', ''))

    def show_thanks(self):
        messagebox.showinfo(title=self.appname,message="Developed by PES Indie")

    def check_version(self):
        if Path(self.filename).stat().st_size == 8511488:
            file = open(self.filename, 'rb')
            version = int.from_bytes(bytearray(file.read())[60:62],'little')
            file.close()
            if version == 140:
                """
                If we lay here it is WE8I
                """
                self.player_edit_mode = 33668644
            elif version == 2320:
                """
                If we lay here it is PES4 1.10
                """                
                self.player_edit_mode = 33668324
            else:
                """
                We shouldn't be here
                """
                messagebox.showerror(title=self.appname,message="Unknown game version")
                return 0
        elif Path(self.filename).stat().st_size == 8503296:
            """
            If we lay here it is PES4 1.00
            """
            self.player_edit_mode = 33660268
        else:
            """
            We shouldn't be here
            """
            messagebox.showerror(title=self.appname,message="Unknown game version")
            return 0

    def load_data(self):
        if self.check_version()==0:
            return 0
        self.pes_we_exe = Path(self.filename).name
        self.player_bytes_size = 124
        try:
            self.pm = pymem.Pymem(self.pes_we_exe)
            self.client = pymem.process.module_from_name(self.pm.process_handle, self.pes_we_exe).lpBaseOfDll
            self.read_player()
        except pymem.exception.ProcessNotFound as e:
            messagebox.showerror(title=self.appname, message=f"pymem error code {e}")
            return 0

    def read_player(self):
        if self.filename=="":
            messagebox.showerror(title=self.appname, message="You must select your exe file first or run your game\nbefore trying to read or set any data")
            return 0
        try:
            self.player = Player(bytearray(self.pm.read_bytes(self.client + self.player_edit_mode, self.player_bytes_size)))
        except pymem.exception.MemoryReadError as e:
            messagebox.showerror(title=self.appname, message=f"pymem error code {e}")
            return 0
        except pymem.exception.ProcessError as e:
            messagebox.showerror(title=self.appname, message=f"pymem error code {e}")
            return 0
        self.player_lbl.config(text=f"Player Name: {self.player.name}")
        self.face_type_dropdown.current(self.player.face_type.get_value())
        self.skin_spb_var.set(self.player.skin_colour.get_value() + 1)
        self.face_spb_var.set(self.player.face_id.get_value() + 1)
        self.hair_spb_var.set(self.player.hair_id.get_value())

    def set_param(self):
        if self.filename=="":
            messagebox.showerror(title=self.appname, message="You must select your exe file first or run your game\nbefore trying to read or set any data")
            return 0
        if self.check_val(self.face_type_dropdown.current(),0,2):
            self.player.face_type.set_value(self.face_type_dropdown.current())
        else:
            messagebox.showerror(title=self.appname, message=f"Value for {self.player.face_type.name} out of range, check Help-> Manual")
        if self.check_val(self.skin_spb_var.get()-1, 0, 3):
            self.player.skin_colour.set_value(self.skin_spb_var.get()-1)
        else:
            messagebox.showerror(title=self.appname, message=f"Value for {self.player.skin_colour.name} out of range, check Help-> Manual")
        if self.check_val(self.face_spb_var.get()-1, 0, 511):
            self.player.face_id.set_value(self.face_spb_var.get()-1)
        else:
            messagebox.showerror(title=self.appname, message=f"Value for {self.player.face_id.name} out of range, check Help-> Manual")
        if self.check_val(self.hair_spb_var.get(), 0,2047):
            self.player.hair_id.set_value(self.hair_spb_var.get())
        else:
            messagebox.showerror(title=self.appname, message=f"Value for {self.player.hair_id.name} out of range, check Help-> Manual")
        try:
            self.pm.write_bytes(self.client + self.player_edit_mode,bytes(self.player.data),self.player_bytes_size)
        except pymem.exception.MemoryWriteError as e:
            messagebox.showerror(title=self.appname, message=f"pymem error code {e}")
        except pymem.exception.ProcessError as e:
            messagebox.showerror(title=self.appname, message=f"pymem error code {e}")
        except pymem.exception.TypeError as e:
            messagebox.showerror(title=self.appname, message=f"pymem error code {e}")

    def check_val(self, val, min, max): 
        return min<=val<=max

    def start(self):
        self.master.resizable(False, False)
        self.master.mainloop()

def main():
    Gui(Tk()).start()

if __name__ == '__main__':
    main()