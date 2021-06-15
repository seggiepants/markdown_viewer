import os
import tkinter as tk
from tkinter import PhotoImage, scrolledtext
from tkinter.font import Font
import urllib.request
import base64

class MarkdownRenderTk():
    def __init__(self, target):
        self.text = target
        fontName = self.find_font(['Calibri', 'Tahoma', 'Times New Roman', 'FreeSerif', 'Helvetica', 'Liberation Serif', 'Arial'])
        self.fontText = Font(family=fontName)
        self.fontH1 = Font(family=fontName, size=36, weight='bold')
        self.fontH2 = Font(family=fontName, size=21, weight='bold')
        self.fontH3 = Font(family=fontName, size=18, weight='bold')
        self.fontH4 = Font(family=fontName, size=16, weight='bold')
        self.fontH5 = Font(family=fontName, size=14, weight='bold')
        self.fontH6 = Font(family=fontName, size=12, weight='bold')
        self.fontStrike = Font(family=fontName, overstrike=1)
        self.fontBold = Font(family=fontName, weight='bold')
        self.fontItalic = Font(family=fontName, slant='italic')
        fontNameMono = self.find_font(['Tlwg Typewriter', 'Courier', 'Dejavu Sans Mono', 'Liberation Mono', 'FreeSans'])
        self.fontMonospace = Font(family=fontNameMono)
        self.fontA = Font(underline=1)
        self.text.font = self.fontText
        self.crlf_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br']

    def find_font(self, font_list):
        families = [str.lower(font) for font in tk.font.families()]
        for target in font_list:
            if str.lower(target) in families:
                return target
        return families[0]

    def render(self, tokens, img_path, callback):
        self.text['state'] = 'normal'
        self.text.delete('1.0', tk.END)
        tags = []
        self.images = []
        countA = 0
        indent = {}
        for token in tokens:            
            tokenType = token[0]
            tokenText = token[1]

            if tokenType == 'text':
                self.text.insert(tk.INSERT, tokenText, tuple(tags))
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
                    img = tk.PhotoImage(file=os.path.join(img_path, url))
                
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
                self.text.tag_bind(tagName, "<Button-1>", lambda e, url=url, title=title: callback(url, title))
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
                    if tokenType[1:] in self.crlf_tags:
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

