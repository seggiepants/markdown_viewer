import os
import tkinter as tk
from tkinter import PhotoImage, scrolledtext
from tkinter import filedialog
from tkinter.font import Font
import urllib.request
import base64
import re

patterns = [
    ("img", R"\!\[(?P<alttext>.+)\]\((?P<url>[^\"\)]+)(?P<title> \".+\")?\)", lambda s: s)
    , ("a", R"\[(?P<title>.+)\]\((?P<url>[^\"\)]+)\)", lambda s: s)
    , ("url", R"\<.+\>", lambda s: s[1:-1]) # R"\<[a-zA-Z0-9\.\\~:\/\_]+\>"
    , ("br", R" [ ]+\n", lambda s: s)
    , ("ul", R"\n(?P<level> *)[\*+-]\s(?P<item>.*$)", lambda s: s)
    , ("ol", R"\n(?P<level> *)[0-9]+.?\s(?P<item>.*$)", lambda s: s)
    , ("p", R"\n[\n]+", lambda s: s)
    , ("h1", R"^.+\n=+$", lambda s: s.splitlines()[0])
    , ("h1", R"^# .+$", lambda s: s[2:])
    , ("h2", R"^.+\n-+$", lambda s: s.splitlines()[0])
    , ("h2", R"^## .+$", lambda s: s[3:])
    , ("h3", R"^### .+$", lambda s: s[4:])
    , ("h4", R"^#### .+$", lambda s: s[5:])
    , ("h5", R"^##### .+$", lambda s: s[6:])
    , ("h6", R"^###### .+$", lambda s: s[7:])
    , ("hr", R"^\-\-[\-]+$", lambda s: s)
    , ("strike", R"~~.+~~", lambda s: s[2:-2])
    , ("bold", R"\*\*.+\*\*", lambda s: s[2:-2])
    , ("italic", R"_.+_", lambda s: s[1:-1])
    , ("italic", R"\*.+\*", lambda s: s[1:-1])
    , ("monospace", R"`.+`", lambda s: s[1:-1])
]

crlf_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
whitespace = ' \n\r\t'
inline_whitespace = ' \t'

class Application(tk.Frame):    
    def __init__(self, root=None):
        super().__init__(root)
        self.root = root
        self.fontText = Font(family='Helvetica')
        self.fontH1 = Font(family='Helvetica', size=36, weight='bold')
        self.fontH2 = Font(family='Helvetica', size=21, weight='bold')
        self.fontH3 = Font(family='Helvetica', size=18, weight='bold')
        self.fontH4 = Font(family='Helvetica', size=16, weight='bold')
        self.fontH5 = Font(family='Helvetica', size=14, weight='bold')
        self.fontH6 = Font(family='Helvetica', size=12, weight='bold')
        self.fontStrike = Font(family='Helvetica', overstrike=1)
        self.fontBold = Font(family='Helvetica', weight='bold')
        self.fontItalic = Font(family='Helvetica', slant='italic')
        self.fontMonospace = Font(family='Courier')
        self.fontA = Font(underline=1)
        self.create_widgets()        

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
            while index < len(tokens):
                if (tokens[index][0] == 'text'):
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
                            if tagName == 'a':
                                title = match.group(1)
                                url = match.group(2)
                                newTokens.append((tagName, ''))
                                newTokens.append(('title', title))
                                newTokens.append(('url', url))
                                newTokens.append(('/' + tagName, ''))
                            elif tagName == 'br' or tagName == 'p':
                                newTokens.append((tagName, ''))
                            elif tagName == 'url':
                                url = middle
                                newTokens.append(('a', ''))
                                newTokens.append(('url', middle))
                                newTokens.append(('/a', ''))
                            elif tagName == 'img':
                                alttext = match.group(1)
                                url = match.group(2)
                                if len(match.groups()) >= 3:
                                    title = match.group(3)
                                else:
                                    title = alttext
                                newTokens.append((tagName, ''))
                                newTokens.append(('alttext', alttext))
                                newTokens.append(('url', url))
                                newTokens.append(('title', title))
                                newTokens.append(('/' + tagName, ''))
                            elif tagName == 'hr':
                                newTokens.append(('hr', ''))
                            elif tagName == 'ul' or tagName == 'ol':
                                level = len(match.group(1))
                                item = match.group(2)
                                newTokens.append((tagName, level))
                                newTokens.append(('text', item))
                                newTokens.append(('/' + tagName, ''))
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
                else:
                    index += 1
        print(tokens)
        self.text['state'] = 'normal'
        self.text.delete('1.0', tk.END)
        # self.text.insert(tk.INSERT, fileText)
        tags = []
        self.images = []
        countA = 0
        indent = {}
        for token in tokens:            
            tokenType = token[0]
            tokenText = token[1]

            if tokenType == 'text':
                self.text.insert(tk.INSERT, self.normalize_text(tokenText), tuple(tags))
            elif tokenType == 'img':
                alttext = ''
                url = ''
                title = ''
            elif tokenType == 'a':
                title = ''
                url = ''
            elif tokenType == 'alttext':
                alttext = tokenText
            elif tokenType == 'url':
                url = tokenText
            elif tokenType == 'title':
                title = tokenText
            elif tokenType == '/img':
                if url[0:4] == 'http':
                    u = urllib.request.urlopen(url)
                    raw_data = u.read()
                    u.close()
                    img = tk.PhotoImage(data=base64.encodebytes(raw_data))
                else:
                    img = tk.PhotoImage(file=os.path.join(path, url))
                
                self.images.append(img) # save a reference
                self.text.image_create(tk.INSERT, image=img)
            elif tokenType == 'hr':                
                self.text.insert(tk.INSERT, "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬" ,('hr')) 
            elif tokenType == 'br':
                self.text.insert(tk.INSERT, "\n", tags)                
            elif tokenType == 'p':
                self.text.insert(tk.INSERT, "\n\n", tags)                
            elif tokenType == '/a':
                countA += 1
                tagName = 'a' + str(countA)
                self.text.tag_config(tagName, font=self.fontA)
                self.text.tag_bind(tagName, "<Enter>", lambda event : event.widget.configure(cursor="hand1"))
                self.text.tag_bind(tagName, "<Leave>", lambda event : event.widget.configure(cursor=""))
                self.text.tag_bind(tagName, "<Button-1>", lambda e, url=url, title=title: click(url, title))
                if len(title) == 0:
                    title = url
                self.text.insert(tk.INSERT, title, tuple(tags + [tagName]))
            elif tokenType == 'ul' or tokenType == 'ol':
                if lastToken != '/ul' and lastToken != '/ol': 
                    indent = {}
                level = tokenText # really a number
                if tokenType == 'ol':                    
                    if not level in indent:
                        indent[level] = 1
                    else:
                        indent[level] = indent[level] + 1
                    counter = indent[level]

                tags.append(tokenType)
                self.text.insert(tk.INSERT, "\n", tuple(tags))
                self.text.insert(tk.INSERT, " " * level, tuple(tags))
                if tokenType == 'ul':
                    self.text.insert(tk.INSERT, "● ", tuple(tags))
                else: # ol
                    self.text.insert(tk.INSERT, str(counter) + ". ", tuple(tags))
            else:
                if tokenType[0] == '/':
                    tags.remove(tokenType[1:])
                    if tokenType[1:] in crlf_tags:
                        self.text.insert(tk.INSERT, '\n',)
                else:
                    tags.append(tokenType)
            lastToken = tokenType
        self.text.tag_config('h1', font=self.fontH1)
        self.text.tag_config('h2', font=self.fontH2)
        self.text.tag_config('h3', font=self.fontH3)
        self.text.tag_config('h4', font=self.fontH4)
        self.text.tag_config('h5', font=self.fontH5)
        self.text.tag_config('h6', font=self.fontH6)
        self.text.tag_config('strike', font=self.fontStrike)
        self.text.tag_config('bold', font=self.fontBold)
        self.text.tag_config('italic', font=self.fontItalic)
        self.text.tag_config('monospace', font=self.fontMonospace)
        self.text['state'] = 'disabled'

    def normalize_text(self, text):
        leading = ''
        trailing = ''
        if len(text) >= 1:
            if text[0] in inline_whitespace:
                leading = ' '
        if len(text) >= 2:
            if text[-1] in inline_whitespace:
                trailing = ' '
        # replace carriage return, line feed and tabs with a space.
        temp = text.replace('\n', ' ')
        temp = temp.replace('\r', ' ')
        temp = temp.replace('\t', ' ')
        # get a list of words delimited by space
        # eliminating redundant spaces
        word = [word for word in temp.split(' ') if len(word) > 0]
        return leading + ' '.join(word) + trailing
    
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
        self.root.destroy()

    def command_about(self):
        print('Not yet implemented')

def click(url, title):
    print(f"URL: {url}, TITLE: {title}")

path = os.path.dirname(os.path.realpath(__file__))   
root = tk.Tk()
app = Application(root)
app.mainloop()
