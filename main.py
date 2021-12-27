# -*- coding: UTF-8 -*-
# ? importing modules

from tkinter import ttk, END, StringVar, Text, Toplevel, NORMAL, DISABLED, Label, Button, CENTER, RIGHT, Y, NONE, \
    BooleanVar
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
from json import loads
from functools import partial


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
        self.SuggestLabel = ttk.Label()
        self.SuggestBtnsY = 185
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
                                        new=1) if not self.EmptySearch else None)
        self.OnlineSearchBtn.place(x=283, y=130, width=100)
        # ? Configuring the clear button
        self.ClearBtn.config(text='Clear', command=self.Clear)
        self.ClearBtn.place(x=416, y=130, width=100)
        # ? Configuring Save button
        self.SaveBtn.config(text='Save', command=self.HandleCWD())
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
                                 self.ChangeTheme)
        # ? Trace the writing case of SelectedTheme object to  change the theme
        self.ThemesCombo.pack()
        self.Mode.set(False)
        self.ReadingModeRbtn.config(text='Reading Mode',
                                    value=True,
                                    variable=self.Mode,
                                    command=self.CheckClipboard)
        self.SearchingModeRbtn.config(text='Searching Mode',
                                      value=False,
                                      variable=self.Mode)
        self.ReadingModeRbtn.place(x=150, y=30)
        self.SearchingModeRbtn.place(x=500, y=30)
        self.SuggestLabel.config(text='Suggest words',
                                 font=('Ubuntu', 14),
                                 background=self.style.lookup('TFrame', 'background'),
                                 foreground=self.style.lookup('TFrame', 'foreground')
                                 )
        self.SuggestLabel.place(x=650, y=160)
        self.search()
        self.mainloop()

    def ShowErrorWin(self, error_message):
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

    def Clear(self):
        self.Output.config(state=NORMAL)
        self.Output.delete(1.0, END)
        self.Output.config(state=DISABLED)

    def Insert(self, repeats, translation):
        self.Output.config(state=NORMAL)
        self.Output.tag_config('center text', justify='center')
        self.Output.insert(END, f"{self.SearchBoxContent.get()} -> {repeats} <- {translation}\n")
        self.Output.tag_add("center text", 1.0, END)
        self.Output.config(state=DISABLED)
        self.CreateButton(self.SearchBoxContent.get())
        self.SearchBoxContent.set('')

    def CreateButton(self, word):
        b = ttk.Button(self, text=word, command=partial(self.ShowSuggestionsWin, word))
        b.place(x=650, y=self.SuggestBtnsY, height=22, width=131)
        self.SuggestBtnsY += 22

    @staticmethod
    def GetSuggestion(query):
        data = loads(get(f'https://skell.sketchengine.eu/api/run.cgi/thesaurus?lang=English&query={query}&format=json',
                         headers={"Host": "skell.sketchengine.eu",
                                  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
                                  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                                  "Accept-Language": "en-US,en;q=0.5",
                                  "Accept-Encoding": "gzip, deflate",
                                  "Referer": "https://www.google.com/",
                                  "Cookie": "_ga_DHRPD3K2JP=GS1.1.1640596256.1.1.1640596461.0; "
                                            "_ga=GA1.1.151944092.1640596257; "
                                            "_gcl_au=1.1.2131992169.1640596257; "
                                            "__gads=ID=243d09fe812600d4-2260341cdbce0047:T=1640596258:RT=1640596258:S"
                                            "=ALNI_MaHq8vf0ItatI5wJt-GhOn6V32Sww",
                                  "Connection": "close",
                                  "Upgrade-Insecure-Requests": "1",
                                  "If-Modified-Since": "Mon, 01 Nov 2021 16:27:43 GMT",
                                  "If-None-Match": '"aaf-5cfbca8011dc0-gzip"',
                                  "Cache-Control": "max-age=0"}).text)['Words']
        return data

    def ShowSuggestionsWin(self, query):
        data = self.GetSuggestion(query)
        Win = Toplevel(self)
        Win.geometry('800x800')
        Win.title('Suggestions')
        Words_Freqs = [[dictionary['Word'], dictionary['Freq']] for dictionary in data]
        SuggestionsVar = StringVar()
        SuggestionsLabel = Label(Win, textvariable=SuggestionsVar, font=('Ubuntu', 14))
        for element in Words_Freqs:
            SuggestionsVar.set(SuggestionsVar.get() + f'{element[0]}  =>  {element[1]}\n')
        SuggestionsLabel.pack()
        Win.mainloop()

    @property
    def RunningOs(self):
        # ? platform is a variable in sys Module
        if platform == 'linux' or platform == 'Linux':
            return 'linux'
        elif platform == 'win32' or platform == 'windows':
            return 'windows'
        elif platform == 'Darwin':
            return 'mac'
        else:
            self.ShowErrorWin("can't detect the operating system :( ")
            return None

    @property
    def Translate(self):
        arabic = self.translator.translate(self.SearchBox.get(), src='en', dest='ar')
        if self.RunningOs == 'linux':
            merged_letters = reshape(arabic.text)  # ? merge the arabic letters together
            ordered_letters = get_display(merged_letters)  # ? put the arabic letters in the right order
            self.ArDict[str(self.SearchBox.get())] = str(arabic.text)
            return ordered_letters
        else:
            return arabic.text

    @property
    def EmptySearch(self):
        if self.SearchBoxContent.get() == '':
            self.ShowErrorWin("Empty Search !!")
            return True
        else:
            return False

    @property
    def RepeatedSearch(self):
        if str(self.Output.get(1.0, END)).lower().__contains__(self.SearchBoxContent.get().lower()):
            # ? use .lower() to handle the repeated search with different letter case
            self.ShowErrorWin("Repeated Search")
            return True
        else:
            return False

    @property
    def handle_trans(self):
        try:
            translation = self.Translate
            if translation.lower() == self.SearchBoxContent.get().lower() + ".":
                translation = 'Translation error'
                self.ShowErrorWin('Error, Check the spelling')
            return translation
        except:
            self.ShowErrorWin("Translation Error")

    @property
    def HandleRepeats(self):
        try:
            page = get("https://youglish.com/pronounce/" + self.SearchBoxContent.get() + "/english?")
            # ! get is a function in requests module (HTTP GET method)
            repeats = page.text.split("<span id='ttl_total'>")[1].split("</span>")[0]
            return repeats
        except:
            self.SearchBoxContent.set('')
            self.ShowErrorWin('Not Found')

    @staticmethod
    def YouROnline():
        try:
            return get('http://google.com')
        except:
            pass

    def search(self, *args):
        # *args to take all The arguments passed to the function (root.bind) method pass one parameter by default
        if self.EmptySearch or self.RepeatedSearch:
            self.SearchBoxContent.set('')
        else:
            self.Insert(translation=self.handle_trans,
                        repeats=self.HandleRepeats) if self.YouROnline() is not None else self.ShowErrorWin(
                'No internet connection')
            # ! you_online() returns None if there is no internet connection

    def OpenFile(self):
        if self.RunningOs == 'linux':
            try:
                system(f' gedit {self.file_name}')

            except:
                system(
                    f'gnome-terminal -- sudo apt-get install gedit  && gedit {self.file_name}')
                # ! install gedit then open the file
        elif self.RunningOs == 'mac':  # ? macOS
            system(f'open -e {self.file_name}')
        elif self.RunningOs == 'windows':
            system(f'notepad {self.file_name}')

    @property
    def OsPath(self):
        if self.RunningOs == 'linux':
            return f'/home/{self.UserName}/Documents'
        elif self.RunningOs == 'mac':
            return f'/Users/{self.UserName}/Documents'
        elif self.RunningOs == 'windows':
            return f'C:\\Users\\{self.UserName}\\Documents'

    @property
    def CheckEngDir(self):
        if self.RunningOs == 'linux':
            return path.exists(f'{self.OsPath}/EnglishResults')
        elif self.RunningOs == 'mac':
            return path.exists(f'{self.OsPath}/EnglishResults')
        elif self.RunningOs == 'windows':
            return path.exists(f'{self.OsPath}\\EnglishResults')
        else:
            return mkdir('EnglishResults')

    def CheckTodayFile(self):
        if not path.exists(self.file_name):
            open(self.file_name, 'w').close()

    def ShowSaveWin(self):
        SavingWindow = Toplevel(self)
        SavingWindow.title('English Counter')
        SavingWindow.geometry('400x50')
        SavingWindow.config(bg=self.WindowsBgColor.get())
        SavingText = Label(SavingWindow, text=f'Saved to {self.file_name}', bg=self.WindowsBgColor.get(), fg='white')
        SavingText.pack()
        OpenFileBtn = Button(SavingWindow,
                             text='Open the file',
                             command=self.OpenFile
                             )
        OpenFileBtn.pack()

    def ShowExstWin(self, word):
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
                      command=lambda: [ExstWin.destroy(), self.SaveFile(Repeated=True, RepWord=word)]  # ? Important
                      )

        IgnoreBtn.place(x=100, y=30)
        Save.place(x=220, y=30)

    def SaveFile(self, Repeated=False, RepWord=''):
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
                    self.ShowExstWin(En)
                elif line == '':
                    pass
                else:
                    if self.RunningOs == 'linux':
                        file.write(
                            f"{line}<- {self.ArDict[En]}\n")
                    else:
                        file.write(f'{line}<- {ar}\n')

            file.close()

    def HandleCWD(self):
        if self.Output.get(1.0, END) == '\n' or self.Output.get(1.0, END) == '':  # ! check empty output case
            self.ShowErrorWin('Nothing to save in a file')
        else:
            if self.CheckEngDir:
                chdir(f"{self.OsPath}/EnglishResults")

            elif not getcwd().__contains__('English_Results'):
                chdir(f'{self.OsPath}')
                mkdir("EnglishResults")
                chdir("EnglishResults")

            self.CheckTodayFile()
            self.SaveFile()
            self.ShowSaveWin()

    def ChangeTheme(self, *args):
        self.theme = self.Themes[self.Themes.index(self.SelectedTheme.get())]
        self.config(theme=self.theme, themebg=True)
        self.Output.config(bg=self.style.lookup('TFrame', 'background'))
        self.style.theme_use(self.theme)
        self.ThemeLabel.config(background=self.style.lookup('TFrame', 'background'),
                               foreground=self.style.lookup('TFrame', 'foreground')
                               )
        self.SuggestLabel.config(background=self.style.lookup('TFrame', 'background'),
                                 foreground=self.style.lookup('TFrame', 'foreground')
                                 )

    def CheckClipboard(self):
        if self.LastClipboard != paste():
            self.SearchBoxContent.set(paste())
            self.LastClipboard = paste()
            self.search()

        if self.Mode.get():
            Timer(2, self.CheckClipboard).start()  # ? create a Timer object to check the clipboard every two seconds
        # ? Timer is a class in threading module


mainwindow = GUI()

