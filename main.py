import os
import tkinter as tk
from tkinter import PhotoImage, scrolledtext
from tkinter import filedialog
from tkinter.font import Font
import urllib.request
import base64
import re
from MarkdownParser import MarkdownParser
from MarkdownRenderTk import MarkdownRenderTk
       
class Application(tk.Frame):    
    def __init__(self, root=None):        
        super().__init__(root)
        self.root = root
        self.create_widgets()
        self.parser = MarkdownParser()
        self.renderer = MarkdownRenderTk(self.text)

    def create_widgets(self):
        menu = tk.Menu(self.root)        
        menu_file = tk.Menu(menu, tearoff=0)
        menu_file.add_command(label='Open', command=self.command_dialog_open)
        menu_file.add_separator()
        menu_file.add_command(label='Exit', command=self.command_exit)
        menu.add_cascade(label='File', menu=menu_file)
        menu_help = tk.Menu(menu, tearoff=0)
        menu_help.add_command(label='About', command=self.command_about)
        menu.add_cascade(label='Help', menu=menu_help)

        self.text = scrolledtext.ScrolledText(self.root, wrap = tk.WORD)
        self.text.pack(side="left", fill="both", expand=True)
        
        self.root.geometry('640x480')
        self.root.minsize(width=320, height=240)
        self.root.config(menu=menu)
        self.root.title('Markdown Viewer')

    def say_hi(self):
        print('Hi there, everyone!')

    def command_dialog_open(self):
        fileName = filedialog.askopenfilename(title='Open Markdown', filetypes = [('Markdown', '*.md'), ('All Files', '*.*')])
        if (len(fileName) > 0):
            self.root.title(f"Markdown Viewer: {fileName}")
            file = open(fileName, 'r')
            fileText = file.read()
            file.close()
            tokens = self.parser.parse(fileText)
            self.renderer.render(tokens, path, self.click)
    
    def command_exit(self):
        self.root.destroy()

    def command_about(self):
        print('Not yet implemented')

    def click(url, title):
        print(f"URL: {url}, TITLE: {title}")

path = os.path.dirname(os.path.realpath(__file__))   
root = tk.Tk()
app = Application(root)
app.mainloop()
