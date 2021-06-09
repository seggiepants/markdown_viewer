import tkinter as tk
from tkinter import filedialog
from tkinter.font import Font

import re

patterns = {
    ("h1", R"^.+\n=+$", lambda s: s.splitlines()[0])
    , ("h1", R"^# .+$", lambda s: s[2:])
    , ("h2", R"^.+\n-+$", lambda s: s.splitlines()[0])
    , ("h2", R"^## .+$", lambda s: s[3:])
    }

class Application(tk.Frame):    
    def __init__(self, root=None):
        super().__init__(root)
        self.root = root
        self.fontH1 = Font(family='Helvetica', size=36, weight='bold')
        self.fontH2 = Font(family='Helvetica', size=21, weight='bold')
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
        self.vscroll = tk.Scrollbar(self.text, command=self.text.yview, orient=tk.VERTICAL)
        self.text.yscrollcommand = self.vscroll.set
        # self.scrollbar.grid(sticky = tk.N + tk.E + tk.S)

        # To make the textarea auto resizable
        #self.root.grid_rowconfigure(0, weight=1)
        #self.root.grid_columnconfigure(0, weight=1)
        #self.text.grid(sticky = tk.N + tk.E + tk.S + tk.W)

        self.vscroll.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)
        
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
            
            self.reformat(fileText)

    def reformat(self, buffer):
        tokens = [('text', buffer)]
        for patternRow in patterns:
            tagName = patternRow[0]
            pattern = patternRow[1]
            fnFormat = patternRow[2]            
            index = 0
            tagCount = 0
            while index < len(tokens):
                textBuffer = tokens[index][1]
                match = re.search(pattern, textBuffer, re.MULTILINE)            
                if match != None:
                    indexStart = match.start() #self.convert_index(textBuffer, match.start())
                    indexEnd = match.end() #self.convert_index(textBuffer, match.end())
                    
                    newTokens = []
                    start = textBuffer[:indexStart]
                    if len(start) > 0:
                        newTokens.append(('text', start))
                    
                    middle = fnFormat(textBuffer[indexStart:indexEnd])
                    if len(middle) > 0:
                        newTokens.append((tagName, ''))
                        newTokens.append(('text', middle))
                        newTokens.append(('/' + tagName, ''))
                    
                    end = textBuffer[indexEnd:]
                    if len(end) > 0:
                        newTokens.append(('text', end))
                    tokens = tokens[:index] + newTokens + tokens[index:]                
                    tokens.pop(index + len(newTokens))
                else:
                    #print(f"{indexStart} -> {indexEnd} : {match.start()} -> {match.end()}")
                    #tagName = f"Tag{tagCount}"
                    #self.text.tag_add(tagName, indexStart, indexEnd)
                    #self.text.tag_config(tagName, font=self.fontH1)
                    #tagCount = tagCount + 1
                    #start = start + match.end()
                    #match = re.search(pattern, buffer[start:], re.MULTILINE)
                    #print(match)
                    index += 1
        
        self.text.delete('1.0', tk.END)
        # self.text.insert(tk.INSERT, fileText)
        tags = []
        for token in tokens:            
            tokenType = token[0]
            tokenText = token[1]

            if tokenType == 'text':
                self.text.insert(tk.INSERT, tokenText, tuple(tags))
            else:
                if tokenType[0] == '/':
                    tags.remove(tokenType[1:])
                else:
                    tags.append(tokenType)
        self.text.tag_config('h1', font=self.fontH1)
        self.text.tag_config('h2', font=self.fontH2)
        
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
