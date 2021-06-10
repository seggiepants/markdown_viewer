import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter.font import Font

import re

patterns = {
    ("h1", R"^.+\n=+$", lambda s: s.splitlines()[0])
    , ("h1", R"^# .+$", lambda s: s[2:])
    , ("h2", R"^.+\n-+$", lambda s: s.splitlines()[0])
    , ("h2", R"^## .+$", lambda s: s[3:])
    , ("h3", R"^### .+$", lambda s: s[4:])
    , ("strike", R"~~.+~~", lambda s: s[2:-2])
    , ("bold", R"\*\*.+\*\*", lambda s: s[2:-2])
    , ("italic", R"_.+_", lambda s: s[1:-1])
    , ("italic", R"\*.+\*", lambda s: s[1:-1])
    , ("monospace", R"`.+`", lambda s: s[1:-1])
    #, ("img", R"\!\[(?P<alttext>.+)\]\((?P<url>[^\"\)]+)(?P<title> \".+\")?\)", lambda s: s)
    }

class Application(tk.Frame):    
    def __init__(self, root=None):
        super().__init__(root)
        self.root = root
        self.fontText = Font(family='Helvetica')
        self.fontH1 = Font(family='Helvetica', size=36, weight='bold')
        self.fontH2 = Font(family='Helvetica', size=21, weight='bold')
        self.fontH3 = Font(family='Helvetica', size=18, weight='bold')
        self.fontStrike = Font(family='Helvetica', overstrike=1)
        self.fontBold = Font(family='Helvetica', weight='bold')
        self.fontItalic = Font(family='Helvetica', slant='italic')
        self.fontMonospace = Font(family='Courier')
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
        self.text = scrolledtext.ScrolledText(self.root, font=self.fontText, wrap = tk.WORD)
        self.text.pack(side="left", fill="both", expand=True)
        
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
                        if tagName == 'img':
                            pass #special processing for an image
                        else:
                            newTokens.append((tagName, ''))
                            newTokens.append(('text', middle))
                            newTokens.append(('/' + tagName, ''))
                    
                    end = textBuffer[indexEnd:]
                    if len(end) > 0:
                        newTokens.append(('text', end))
                    tokens = tokens[:index] + newTokens + tokens[index:]                
                    tokens.pop(index + len(newTokens))
                else:                    
                    index += 1
        print(tokens)
        self.text['state'] = 'normal'
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
        self.text.tag_config('h3', font=self.fontH3)
        self.text.tag_config('strike', font=self.fontStrike)
        self.text.tag_config('bold', font=self.fontBold)
        self.text.tag_config('italic', font=self.fontItalic)
        self.text.tag_config('monospace', font=self.fontMonospace)
        self.text['state'] = 'disabled'
        
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
