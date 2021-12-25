# -*- coding: UTF-8 -*-
# ? importing modules

from tkinter import ttk, END, StringVar, Text, Toplevel, NORMAL, DISABLED, Label, Button, CENTER, RIGHT, Y, NONE, \
    PhotoImage, BooleanVar
from arabic_reshaper import reshape
from bidi.algorithm import get_display  # * to reverse the arabic letter, so it will be in the right order
from ttkthemes import ThemedTk
from requests import get
from os import getcwd, getlogin, system, path, chdir, mkdir  # creating files and checking if the file exists
from datetime import datetime
from pyperclip import paste
from googletrans import Translator
# ? pip3 install googletrans / we can use conda instead
# ? pip3 install googletrans==4.0.0-rc1  TODO Very Important step

from sys import platform
from threading import Timer
import webbrowser  # ? we can't say "from webbrowser import open "
# !because there is a function called open we use to open a file


class GUI(ThemedTk):

    def __init__(self):
        super().__init__()
        self.Themes = ['adapta', 'alt', 'aquativo', 'arc', 'breeze', 'black', 'blue', 'clam', 'classic', 'clearlooks',
                       'default',
                       'equilux', 'itft1', 'keramik', 'keramik_alt', 'kroc', 'plastik', 'radiance', 'scidblue',
                       'scidgreen',
                       'scidgrey', 'scidmint', 'scidpink', 'scidpurple', 'scidsand', 'smog', 'winxpblue', 'yaru']
        self.theme = self.Themes[18]
        # ! Creating the main objects/components
        self.SelectedTheme = StringVar()
        self.ThemesCombo = ttk.Combobox()
        self.ThemeLabel = ttk.Label()
        self.style = ttk.Style()
        ########################################
        self.scroll = ttk.Scrollbar()
        self.Output = Text()
        # ? Search box objects
        self.SearchBox = ttk.Entry()
        self.SearchBoxContent = StringVar()
        self.SearchBtn = ttk.Button()  # ? Search Button objects
        self.ClearBtn = ttk.Button()  # ?  Button object
        self.SaveBtn = ttk.Button()  # ? Save Button object
        self.BtnBgColor = StringVar()  # ! Buttons color
        #################################
        self.Mode = BooleanVar()
        self.ReadingModeRbtn = ttk.Radiobutton()
        self.SearchingModeRbtn = ttk.Radiobutton()
        # ! windows colors
        self.WindowsBgColor = StringVar()  # for error window and saving window
        self.UserName = getlogin()  # * os.getlogin()
        self.file_name = "English_" + str(datetime.now().date())
        self.translator = Translator()
        self.OnlineSearchBtn = ttk.Button()
        self.ArDict = {}  # dictionary for linux only,
        self.LastClipboard = paste()
        #  ? ______________________Default values_________________________________  ? #

        # ? Configuring the window
        self.WindowsBgColor.set("#2e2b32")
        # ? Configuring the window
        self.geometry('800x800')
        self.resizable(False, False)
        self.title('English Register')
        self.set_theme(self.theme, themebg=True)
        self.style.theme_use(self.theme)
        self.bind('<Return>', self.search)  # make  Enter key call search function
        # ? Configuring the Search box
        self.SearchBox.config(textvariable=self.SearchBoxContent, font=("Ubuntu", 14))
        self.SearchBoxContent.set(paste())
        self.SearchBox.place(relx=0.5, rely=0.1, anchor=CENTER, width=500, height=40)
        # ? Configuring the Search button
        self.BtnBgColor.set('#2775f6')
        self.SearchBtn.config(text='Search', command=self.search)
        self.SearchBtn.place(x=150, y=130, width=100)
        self.OnlineSearchBtn.config(text='Videos',
                                    command=lambda: webbrowser.open(
                                        f'https://youglish.com/pronounce/{self.SearchBoxContent.get()}/english/?',
                                        new=1) if not self.empty_search else None)
        self.OnlineSearchBtn.place(x=283, y=130, width=100)
        # ? Configuring the clear button
        self.ClearBtn.config(text='Clear', command=self.clear)
        self.ClearBtn.place(x=416, y=130, width=100)
        # ? Configuring Save button
        self.SaveBtn.config(text='Save', command=self.handle_cwd)
        self.SaveBtn.place(x=549, y=130, width=100)
        # ? configuring the output label
        self.scroll.pack(side=RIGHT, fill=Y)
        self.Output.config(wrap=NONE,
                           yscrollcommand=self.scroll.set,
                           state=DISABLED,
                           bg=self.style.lookup('TFrame', 'background'),
                           fg=self.style.lookup('TFrame', 'foreground'),
                           bd=5,
                           font=('Ubuntu', 13)
                           )
        self.Output.place(x=150, y=180, width=500)
        self.scroll.config(command=self.Output.yview)
        self.ThemeLabel.config(text='Themes: ',
                               background=self.style.lookup('TFrame', 'background'),
                               foreground=self.style.lookup('TFrame', 'foreground'),
                               font=('Ubuntu', 12, 'bold')
                               )
        self.ThemeLabel.place(x=230, y=1)
        self.ThemesCombo.config(values=self.Themes,
                                textvariable=self.SelectedTheme,
                                state='readonly')
        self.ThemesCombo.current(18)
        self.SelectedTheme.trace('w',
                                 self.change_theme)  # ? Trace the writing case of SelectedTheme object to  change the theme
        self.ThemesCombo.pack()
        self.Mode.set(False)
        self.ReadingModeRbtn.config(text='Reading Mode',
                                    value=True,
                                    variable=self.Mode,
                                    command=self.check_clipboard)
        self.SearchingModeRbtn.config(text='Searching Mode',
                                      value=False,
                                      variable=self.Mode)
        self.ReadingModeRbtn.place(x=150, y=30)
        self.SearchingModeRbtn.place(x=500, y=30)
        self.search()
        self.mainloop()

    def show_error_window(self, error_message):
        ErrorWin = Toplevel(self)
        ErrorWin.config(width=1, height=1, bg=self.WindowsBgColor.get())
        ErrorWin.resizable(False, False)
        ErrorWin.title('Error')
        Error = Label(
            ErrorWin,
            text=error_message,
            font=('Ubuntu', 15),
            bg=self.WindowsBgColor.get(),
            fg='red'
        )
        Error.pack()
        ErrorWin.after(3000, lambda: ErrorWin.destroy())

    def clear(self):
        self.Output.config(state=NORMAL)
        self.Output.delete(1.0, END)
        self.Output.config(state=DISABLED)

    def insert(self, repeats, translation):
        self.Output.config(state=NORMAL)
        self.Output.tag_config('center text', justify='center')
        self.Output.insert(END, f"{self.SearchBox.get()} -> {repeats} <- {translation}\n")
        self.Output.tag_add("center text", 1.0, END)
        self.Output.config(state=DISABLED)
        self.SearchBoxContent.set('')

    @property
    def running_os(self):
        # ? platform is a variable in sys Module
        if platform == 'linux' or platform == 'Linux':
            return 'linux'
        elif platform == 'win32' or platform == 'windows':
            return 'windows'
        elif platform == 'Darwin':
            return 'mac'
        else:
            self.show_error_window("can't detect the operating system :( ")
            return None

    @property
    def translate(self):
        arabic = self.translator.translate(self.SearchBox.get(), src='en', dest='ar')
        if self.running_os == 'linux':
            merged_letters = reshape(arabic.text)  # ? merge the arabic letters together
            ordered_letters = get_display(merged_letters)  # ? put the arabic letters in the right order
            self.ArDict[str(self.SearchBox.get())] = str(arabic.text)
            return ordered_letters
        else:
            return arabic.text

    @property
    def empty_search(self):
        if self.SearchBoxContent.get() == '':
            self.show_error_window("Empty Search !!")
            return True
        else:
            return False

    @property
    def repeated_search(self):
        if str(self.Output.get(1.0, END)).lower().__contains__(self.SearchBoxContent.get().lower()):
            # ? use .lower() to handle the repeated search with different letter case
            self.show_error_window("Repeated Search")
            return True
        else:
            return False

    @property
    def handle_trans(self):
        try:
            translation = self.translate
            if translation.lower() == self.SearchBoxContent.get().lower() + ".":
                translation = 'Translation error'
                self.show_error_window('Error, Check the spelling')
            return translation
        except:
            self.show_error_window("Translation Error")

    @property
    def handle_repeats(self):
        try:
            page = get("https://youglish.com/pronounce/" + self.SearchBoxContent.get() + "/english?")
            # ! get is a function in requests module (HTTP GET method)
            repeats = page.text.split("<span id='ttl_total'>")[1].split("</span>")[0]
            return repeats
        except:
            self.SearchBoxContent.set('')
            self.show_error_window('Not Found')

    @staticmethod
    def you_are_online():
        try:
            return get('http://google.com')
        except:
            pass

    def search(self, *args):
        # *args to take all The arguments passed to the function (root.bind) method pass one parameter by default
        if self.empty_search or self.repeated_search:
            self.SearchBoxContent.set('')
        else:
            self.insert(translation=self.handle_trans,
                        repeats=self.handle_repeats) if self.you_are_online() is not None else self.show_error_window(
                'No internet connection')
            # ! you_online() returns None if there is no internet connection

    def open_file(self):
        if self.running_os == 'linux':
            try:
                system(f' gedit {self.file_name}')

            except:
                system(
                    f'gnome-terminal -- sudo apt-get install gedit  && gedit {self.file_name}')
                # ! install gedit then open the file
        elif self.running_os == 'mac':  # ? macOS
            system(f'open -e {self.file_name}')
        elif self.running_os == 'windows':
            system(f'notepad {self.file_name}')

    @property
    def os_path(self):
        if self.running_os == 'linux':
            return f'/home/{self.UserName}/Documents'
        elif self.running_os == 'mac':
            return f'/Users/{self.UserName}/Documents'
        elif self.running_os == 'windows':
            return f'C:\\Users\\{self.UserName}\\Documents'

    @property
    def check_english_dir(self):
        if self.running_os == 'linux':
            return path.exists(f'{self.os_path}/EnglishResults')
        elif self.running_os == 'mac':
            return path.exists(f'{self.os_path}/EnglishResults')
        elif self.running_os == 'windows':
            return path.exists(f'{self.os_path}\\EnglishResults')
        else:
            return mkdir('EnglishResults')

    def check_today_file(self):
        if not path.exists(self.file_name):
            open(self.file_name, 'w').close()

    def show_saving_win(self):
        SavingWindow = Toplevel(self)
        SavingWindow.title('English Counter')
        SavingWindow.geometry('400x50')
        SavingWindow.config(bg=self.WindowsBgColor.get())
        SavingText = Label(SavingWindow, text=f'Saved to {self.file_name}', bg=self.WindowsBgColor.get(), fg='white')
        SavingText.pack()
        OpenFileBtn = Button(SavingWindow,
                             text='Open the file',
                             command=self.open_file
                             )
        OpenFileBtn.pack()

    def show_exst_win(self, word):
        ExstWin = Toplevel()
        ExstWin.title('Existed word')
        ExstWin.geometry('400x70')
        ExstWin.config(bg=self.WindowsBgColor.get())

        ExstText = Label(ExstWin,
                         text=word,
                         font=("Ubuntu", 15),
                         bg=self.WindowsBgColor.get(),
                         fg='red'
                         )
        ExstText.pack()
        IgnoreBtn = Button(ExstWin,
                           text='Ignore it',
                           bg=self.BtnBgColor.get(),
                           command=lambda: ExstWin.destroy()
                           )
        Save = Button(ExstWin,
                      text='Save',
                      bg=self.BtnBgColor.get(),
                      command=lambda: [ExstWin.destroy(), self.save_file(Repeated=True, RepWord=word)]  # ? Important
                      )

        IgnoreBtn.place(x=100, y=30)
        Save.place(x=220, y=30)

    def save_file(self, Repeated=False, RepWord=''):
        file = open(self.file_name, 'r+', encoding='utf-8')
        FileLines, OutputLines = file.readlines(), self.Output.get(1.0, END).split('\n')[:-2]
        SavedEnWords = [line.split(' -')[0] for line in FileLines]
        if Repeated:
            file.close()
            open(self.file_name, 'w', encoding='utf-8').writelines(
                [f'{line[:-1]} *--IMPORTANT--*\n' if line.split(' -')[0] == RepWord else line for line in FileLines])

        else:
            for line in OutputLines:
                ar, line, En = line.split()[-1], ''.join(line.split("<-")[:-1]), line.split(' -')[0]
                # ! three assignment in one line to make the program faster
                if En in SavedEnWords:
                    self.show_exst_win(En)
                elif line == '':
                    pass
                else:
                    if self.running_os == 'linux':
                        file.write(
                            f"{line}<- {self.ArDict[En]}\n")
                    else:
                        file.write(f'{line}<- {ar}\n')

            file.close()

    def handle_cwd(self):
        if self.Output.get(1.0, END) == '\n' or self.Output.get(1.0, END) == '':  # ! check empty output case
            self.show_error_window('Nothing to save in a file')
        else:
            if self.check_english_dir:
                chdir(f"{self.os_path}/EnglishResults")

            elif not getcwd().__contains__('English_Results'):
                chdir(f'{self.os_path}')
                mkdir("EnglishResults")
                chdir("EnglishResults")

            self.check_today_file()
            self.save_file()
            self.show_saving_win()

    def change_theme(self, *args):
        self.theme = self.Themes[self.Themes.index(self.SelectedTheme.get())]
        self.config(theme=self.theme, themebg=True)
        self.Output.config(bg=self.style.lookup('TFrame', 'background'))
        self.style.theme_use(self.theme)
        self.ThemeLabel.config(background=self.style.lookup('TFrame', 'background'),
                               foreground=self.style.lookup('TFrame', 'foreground')
                               )

    def check_clipboard(self):
        if self.LastClipboard != paste():
            self.SearchBoxContent.set(paste())
            self.LastClipboard = paste()
            self.search()

        if self.Mode.get():
            Timer(2, self.check_clipboard).start()  # ? create a Timer object to check the clipboard every two seconds
        # ? Timer is a class in threading module


mainwindow = GUI()

