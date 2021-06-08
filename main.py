import tkinter as tk
from tkinter import filedialog
from tkinter.font import Font

import re

patterns = {
    "H1": R"^.+\n=+$"
    , "H1_": R"^# .+$"
    }

class Application(tk.Frame):    
    def __init__(self, root=None):
        super().__init__(root)
        self.root = root
        self.fontH1 = Font(family='Helvetica',
        size=36, weight='bold')
        self.create_widgets()

    def create_widgets(self):
        menu = tk.Menu(self.root)        
        menu_file = tk.Menu(menu, tearoff=0)
        menu_file.add_command(label='Open', command=self.command_dialog_open)
        menu_file.add_separator()
        menu_file.add_command(label='Exit', command=self.command_exit)
        menu.add_cascade(label='File', menu=menu_file)
        menu_help = tk.Menu(menu, tearoff=0)
        menu_help_about = menu_help.add_command(label='About', command=self.command_about)
        menu.add_cascade(label='Help', menu=menu_help)

        """
        self.hi_there = tk.Button(self.root)
        self.hi_there['text'] = 'Hello World\n(click me)'
        self.hi_there['command'] = self.say_hi
        self.hi_there.pack(side = 'top')

        self.quit = tk.Button(self.root, text='QUIT', fg='red', command=self.command_exit)
        self.quit.pack(side='bottom')
        """
        self.text = tk.Text(self.root)
        self.scrollbar = tk.Scrollbar(self.text)
        self.text.insert(tk.INSERT, 'This is a test, this is only a test')

        # To make the textarea auto resizable
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.text.grid(sticky = tk.N + tk.E + tk.S + tk.W)
        # self.text.pack()
        self.root.geometry('640x480')
        self.root.minsize(width=320, height=240)
        self.root.config(menu=menu)
        self.root.title('Markdown Viewer')

    def say_hi(self):
        print('Hi there, everyone!')

    def command_dialog_open(self):
        fileName = filedialog.askopenfilename(title='Open Markdown', filetype = (('Markdown', '*.md'), ('All Files', '*.*')))
        if (len(fileName) > 0):
            self.root.title(f"Markdown Viewer: {fileName}")
            file = open(fileName, 'r')
            fileText = file.read()
            file.close()
            self.text.delete('1.0', tk.END)
            self.text.insert(tk.INSERT, fileText)
            self.reformat(fileText)

    def reformat(self, buffer):
        print('reformat')
        pattern = R"^.+\n=+$"
        start = 0
        match = re.search(pattern, buffer[start:], re.MULTILINE)
        tagCount = 0
        print(match)
        while match != None:
            tagName = f"Tag{tagCount}"
            indexStart = self.convert_index(buffer, match.start())
            indexEnd = self.convert_index(buffer, match.end())
            
            print(f"{indexStart} -> {indexEnd} : {match.start()} -> {match.end()}")
            self.text.tag_add(tagName, indexStart, indexEnd)
            self.text.tag_config(tagName, font=self.fontH1)
            tagCount = tagCount + 1
            start = start + match.end()
            match = re.search(pattern, buffer[start:], re.MULTILINE)
            print(match)
            
    def convert_index(self, string, count):
        lines = string.splitlines()
        pos = 0
        row = 0
        col = 0
        for line in lines:
            row = row + 1
            if pos + len(line) + 1 >= count:
                col = count - pos
                return f"{row}.{col}"
            else:
                pos += len(line) + 1
        return "0.0"
    
    def command_exit(self):
        self.root.destroy();

    def command_about(self):
        print('Not yet implemented')

root = tk.Tk()
app = Application(root)
app.mainloop()
