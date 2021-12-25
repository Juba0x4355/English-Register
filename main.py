#!/usr/bin/python3.9
# -*- coding: UTF-8 -*-
# ? importing modules

from tkinter import ttk, END, StringVar, Text, Toplevel, NORMAL, DISABLED, Label, Button, CENTER, RIGHT, Y, NONE, PhotoImage, BooleanVar
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

# ?######################################
Themes = ['adapta', 'alt', 'aquativo', 'arc', 'breeze', 'black', 'blue', 'clam', 'classic', 'clearlooks', 'default',
          'equilux', 'itft1', 'keramik', 'keramik_alt', 'kroc', 'plastik', 'radiance', 'scidblue', 'scidgreen',
          'scidgrey', 'scidmint', 'scidpink', 'scidpurple', 'scidsand', 'smog', 'winxpblue', 'yaru']
theme = Themes[18]
# ! Creating the main objects/components
root = ThemedTk(theme=theme, themebg=True)
SelectedTheme = StringVar()
ThemesCombo = ttk.Combobox(root)
ThemeLabel = ttk.Label(root)
s = ttk.Style()
########################################
scroll = ttk.Scrollbar(root)
Output = Text(root)
# ? Search box objects
SearchBox = ttk.Entry(root)
SearchBoxContent = StringVar()
SearchBtn = ttk.Button(root)  # ? Search Button objects
ClearBtn = ttk.Button(root)  # ?  Button object
SaveBtn = ttk.Button(root)  # ? Save Button object
BtnBgColor = StringVar()  # ! Buttons color
#################################
Mode = BooleanVar()
ReadingModeRbtn = ttk.Radiobutton(root)
SearchingModeRbtn = ttk.Radiobutton(root)
# ! windows colors
WindowsBgColor = StringVar()  # for error window and saving window
UserName = getlogin()  # * os.getlogin()
file_name = "English_" + str(datetime.now().date())
translator = Translator()
OnlineSearchBtn = ttk.Button(root)
ArDict = {}  # dictionary for linux only,
LastClipboard = paste()


def show_error_window(error_message):
    ErrorWin = Toplevel(root)
    ErrorWin.geometry('250x100')
    ErrorWin.config(bg=WindowsBgColor.get())
    ErrorWin.resizable(False, False)
    ErrorWin.title('Error')
    Error = Label(ErrorWin,
                  text=error_message,
                  font=('Ubuntu', 15),
                  bg=WindowsBgColor.get(),
                  fg='red'
                  )
    Error.pack()
    ErrorWin.after(3000, lambda: ErrorWin.destroy())


def clear():
    Output.config(state=NORMAL)
    Output.delete(1.0, END)
    Output.config(state=DISABLED)


def insert(repeats, translation):
    Output.config(state=NORMAL)
    Output.tag_config('center text', justify='center')
    Output.insert(END, f"{SearchBox.get()} -> {repeats} <- {translation}\n")
    Output.tag_add("center text", 1.0, END)
    Output.config(state=DISABLED)
    SearchBoxContent.set('')


def running_os():
    # ? platform is a variable in sys Module
    if platform == 'linux' or platform == 'Linux':
        return 'linux'
    elif platform == 'win32' or platform == 'windows':
        return 'windows'
    elif platform == 'Darwin':
        return 'mac'
    else:
        show_error_window("can't detect the operating system :( ")


def translate():
    arabic = translator.translate(SearchBox.get(), src='en', dest='ar')
    if running_os() == 'linux':
        merged_letters = reshape(arabic.text)  # ? merge the arabic letters together
        ordered_letters = get_display(merged_letters)  # ? put the arabic letters in the right order
        global ArDict
        ArDict[str(SearchBox.get())] = str(arabic.text)
        return ordered_letters
    else:
        return arabic.text


def empty_search():
    if SearchBoxContent.get() == '':
        show_error_window("Empty Search !!")
        return True
    else:
        return False


def repeated_search():
    if str(Output.get(1.0, END)).lower().__contains__(SearchBoxContent.get().lower()):
        # ? use .lower() to handle the repeated search with different letter case
        show_error_window("Repeated Search")
        return True
    else:
        return False


def handle_trans():
    try:
        translation = translate()
        if translation.lower() == SearchBoxContent.get().lower() + ".":
            translation = 'Translation error'
            show_error_window('Error, Check the spelling')
        return translation
    except:
        show_error_window("Translation Error")


def handle_repeats():
    try:
        page = get("https://youglish.com/pronounce/" + SearchBoxContent.get() + "/english?")
        # ! get is a function in requests module (HTTP GET method)
        repeats = page.text.split("<span id='ttl_total'>")[1].split("</span>")[0]
        return repeats
    except:
        SearchBoxContent.set('')
        show_error_window('Not Found')


def you_are_online():
    try:
        return get('http://google.com')
    except:
        pass


def search(*args):
    # *args to take all The arguments passed to the function (root.bind) method pass one parameter by default
    if empty_search() or repeated_search():
        SearchBoxContent.set('')
    else:
        insert(translation=handle_trans(),
               repeats=handle_repeats()) if you_are_online() is not None else show_error_window(
            'No internet connection')
        # ! you_online() returns None if there is no internet connection


def open_file():
    if running_os() == 'linux':
        try:
            system(f' gedit {file_name}')

        except:
            system(
                f'gnome-terminal -- sudo apt-get install gedit  && gedit {file_name}')
            # ! install gedit then open the file
    elif running_os() == 'mac':  # ? macOS
        system(f'open -e {file_name}')
    elif running_os() == 'windows':
        system(f'notepad {file_name}')


def os_path():
    if running_os() == 'linux':
        return f'/home/{UserName}/Documents'
    elif running_os() == 'mac':
        return f'/Users/{UserName}/Documents'
    elif running_os() == 'windows':
        return f'C:\\Users\\{UserName}\\Documents'


def check_english_dir():
    if running_os() == 'linux':
        return path.exists(f'{os_path()}/EnglishResults')
    elif running_os() == 'mac':
        return path.exists(f'{os_path()}/EnglishResults')
    elif running_os() == 'windows':
        return path.exists(f'{os_path()}\\EnglishResults')
    else:
        return mkdir('EnglishResults')


def check_today_file():
    if not path.exists(file_name):
        open(file_name, 'w').close()


def show_saving_win():
    SavingWindow = Toplevel(root)
    SavingWindow.title('English Register')
    SavingWindow.geometry('400x50')
    SavingWindow.config(bg=WindowsBgColor.get())
    SavingText = Label(SavingWindow,
                       text=f'Saved to {file_name}',
                       font=("Ubuntu", 15),
                       bg=WindowsBgColor.get(),
                       fg='white'
                       )
    SavingText.pack()
    OpenFileBtn = Button(SavingWindow,
                         text='Open the file',
                         bg=BtnBgColor.get(),
                         command=lambda: [SavingWindow.destroy(), open_file()]
                         )
    OpenFileBtn.pack()


def show_exst_win(word):
    ExstWin = Toplevel(root)
    ExstWin.title('Existed word')
    ExstWin.geometry('400x70')
    ExstWin.config(bg=WindowsBgColor.get())

    ExstText = Label(ExstWin,
                     text=word,
                     font=("Ubuntu", 15),
                     bg=WindowsBgColor.get(),
                     fg='red'
                     )
    ExstText.pack()
    IgnoreBtn = Button(ExstWin,
                       text='Ignore it',
                       bg=BtnBgColor.get(),
                       command=lambda: ExstWin.destroy()
                       )
    Save = Button(ExstWin,
                  text='Save',
                  bg=BtnBgColor.get(),
                  command=lambda: [ExstWin.destroy(), save_file(Repeated=True, RepWord=word)]  # ? Important
                  )

    IgnoreBtn.place(x=100, y=30)
    Save.place(x=220, y=30)


def save_file(Repeated=False, RepWord=''):
    file = open(file_name, 'r+', encoding='utf-8')
    FileLines, OutputLines = file.readlines(), Output.get(1.0, END).split('\n')[:-2]
    SavedEnWords = [line.split(' -')[0] for line in FileLines]
    if Repeated:
        file.close()
        open(file_name, 'w', encoding='utf-8').writelines(
            [f'{line[:-1]} *--IMPORTANT--*\n' if line.split(' -')[0] == RepWord else line for line in FileLines])

    else:
        for line in OutputLines:
            ar, line, En = line.split()[-1], ''.join(line.split("<-")[:-1]), line.split(' -')[0]
            # ! three assignment in one line to make the program faster
            if En in SavedEnWords:
                show_exst_win(En)
            elif line == '':
                pass
            else:
                if running_os() == 'linux':
                    file.write(f"{line}<- {ArDict[En]}\n")
                else:
                    file.write(f'{line}<- {ar}\n')

        file.close()


def handle_cwd():
    if Output.get(1.0, END) == '\n' or Output.get(1.0, END) == '':  # ! check empty output case
        show_error_window('Nothing to save in a file')
    else:
        if check_english_dir():
            chdir(f"{os_path()}/EnglishResults")

        elif not getcwd().__contains__('English_Results'):
            chdir(f'{os_path()}')
            mkdir("EnglishResults")
            chdir("EnglishResults")

        check_today_file()
        save_file()
        show_saving_win()


def change_theme(*args):
    global theme
    theme = Themes[Themes.index(SelectedTheme.get())]
    root.config(theme=theme, themebg=True)
    Output.config(bg=s.lookup('TFrame', 'background'))
    s.theme_use(theme)
    ThemeLabel.config(background=s.lookup('TFrame', 'background'),
                      foreground=s.lookup('TFrame', 'foreground')
                      )


def check_clipboard():
    global LastClipboard
    if LastClipboard != paste():
        SearchBoxContent.set(paste())
        LastClipboard = paste()
        search()
    if Mode.get():
        Timer(2, check_clipboard).start()  # ? create a Timer object to check the clipboard every two seconds
    # ? Timer is a class in threading module


def start_ui():
    WindowsBgColor.set("#2e2b32")
    # ? Configuring the window
    root.geometry('800x800')
    root.resizable(False, False)
    root.title('English Register')
    root.set_theme(theme, themebg=True)
    s.theme_use(theme)
    root.bind('<Return>', search)  # make  Enter key call search function
    # ? Configuring the Search box
    SearchBox.config(textvariable=SearchBoxContent, font=("Ubuntu", 14))
    SearchBoxContent.set(paste())
    SearchBox.place(relx=0.5, rely=0.1, anchor=CENTER, width=500, height=40)
    # ? Configuring the Search button
    BtnBgColor.set('#2775f6')
    SearchBtn.config(text='Search', command=search)
    SearchBtn.place(x=150, y=130, width=100)
    OnlineSearchBtn.config(text='Videos',
                           command=lambda: webbrowser.open(
                               f'https://youglish.com/pronounce/{SearchBoxContent.get()}/english/?',
                               new=1) if not empty_search() else None)
    OnlineSearchBtn.place(x=283, y=130, width=100)
    # ? Configuring the clear button
    ClearBtn.config(text='Clear', command=clear)
    ClearBtn.place(x=416, y=130, width=100)
    # ? Configuring Save button
    SaveBtn.config(text='Save', command=handle_cwd)
    SaveBtn.place(x=549, y=130, width=100)
    # ? configuring the output label
    scroll.pack(side=RIGHT, fill=Y)
    Output.config(wrap=NONE,
                  yscrollcommand=scroll.set,
                  state=DISABLED,
                  bg=s.lookup('TFrame', 'background'),
                  fg=s.lookup('TFrame', 'foreground'),
                  bd=5,
                  font=('Ubuntu', 13)
                  )
    Output.place(x=150, y=180, width=500)
    scroll.config(command=Output.yview)
    ThemeLabel.config(text='Themes: ',
                      background=s.lookup('TFrame', 'background'),
                      foreground=s.lookup('TFrame', 'foreground'),
                      font=('Ubuntu', 12, 'bold')
                      )
    ThemeLabel.place(x=230, y=1)
    ThemesCombo.config(values=Themes,
                       textvariable=SelectedTheme,
                       state='readonly')
    ThemesCombo.current(18)
    SelectedTheme.trace('w', change_theme)  # ? Trace the writing case of SelectedTheme object to  change the theme
    ThemesCombo.pack()
    Mode.set(False)
    ReadingModeRbtn.config(text='Reading Mode',
                           value=True,
                           variable=Mode,
                           command=check_clipboard)
    SearchingModeRbtn.config(text='Searching Mode',
                             value=False,
                             variable=Mode)
    ReadingModeRbtn.place(x=150, y=30)
    SearchingModeRbtn.place(x=500, y=30)
    search()
    root.mainloop()


start_ui()

