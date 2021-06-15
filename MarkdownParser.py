import re

class MarkdownParser():
    def __init__(self):
        self.patterns = [
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
        self.inline_whitespace = ' \t'

    def parse(self, buffer):
        tokens = [('text', buffer)]
        for patternRow in self.patterns:
            tagName = patternRow[0]
            pattern = patternRow[1]
            fnFormat = patternRow[2]            
            index = 0
            while index < len(tokens):
                if (tokens[index][0] == 'text'):
                    textBuffer = tokens[index][1]
                    match = re.search(pattern, textBuffer, re.MULTILINE)            
                    if match != None:
                        indexStart = match.start()
                        indexEnd = match.end()
                        
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
        return [('text', self.normalize_text(token[1])) if token[0] == 'text' else token for token in tokens]

    def normalize_text(self, text):
        leading = ''
        trailing = ''
        if len(text) >= 1:
            if text[0] in self.inline_whitespace:
                leading = ' '
        if len(text) >= 2:
            if text[-1] in self.inline_whitespace:
                trailing = ' '
        # replace carriage return, line feed and tabs with a space.
        temp = text.replace('\n', ' ')
        temp = temp.replace('\r', ' ')
        temp = temp.replace('\t', ' ')
        # get a list of words delimited by space
        # eliminating redundant spaces
        word = [word for word in temp.split(' ') if len(word) > 0]
        return leading + ' '.join(word) + trailing

