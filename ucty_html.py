# coding=utf-8
"""
Ucty HTML
"""

class HtmlOutput:
    def __init__(self, db, fname):
        self.db = db
        self.fname = fname
        self.html = None
        self._ebuf = []
        self.cols = [
            ("Datum",     "p=kdy"),
            ("Jak",       "p=jak"),
            ("Celkem",    "c=suma"),
            ("Popis",     "p=popis"),
            ("Jídlo",     "d=Jidlo"),
            ("Domácnost", "d=Domacnost"),
            ("Škola",     "d=Skola"),
            ("Auto",      "d=Auto"),
            ("Dárky",     "d=Darky"),
            ("Služby",    "d=Sluzby"),
            ("Oblečení",  "d=Obleceni"),
            ("Velké",     "d=Velke"),
            ("Ostatní",   "d=Ostatni"),
            ("Zábava",    "-", 4),
                ("Jídlo",     "d=Z-Jidlo"),
                ("Cesta",     "d=Z-Cesta"),
                ("Ostatní",   "d=Z-Ostatni"),
                ("Vstup",     "d=Z-Vstup"),
            ("Výběr",     "d=Vyber"),
            ("Převod CZ", "d=CZ"),
            ("Karta",     "j=K"),
            ("Pure",      "j=P"),
            ("Hotovost",  "j=H")
        ]
# Tvoreni, KAP

        self.open()

    def open(self):
        self.close()
        self.html = open(self.fname, 'w')

    def close(self):
        if self.html is not None:
            self.html.close()
            self.html = None

    def indentLine(self, line):
        self.html.write('  '*len(self._ebuf))
        self.html.write(line)
        self.html.write('\n')
        return self

    def begin(self, tagName, params=None):
        if params is None:
            params = ''
        else:
            params = ' '+params
        self.indentLine('<'+tagName+params+'>')
        self._ebuf.append(tagName)
        return self

    def end(self):
        if len(self._ebuf) == 0:
            raise IndentationError("Trying to end() empty elements buffer.")
        tagName = self._ebuf.pop()
        self.indentLine('</' + tagName + '>')
        return self

    def tag(self, tagName, text, params=None):
        if params is None:
            params = ''
        else:
            params = ' '+params
        if text is None:
            self.indentLine('<'+tagName+params+'/>')
        else:
            self.indentLine('<'+tagName+params+'>'+text+'</'+tagName +'>')
        return self

    def td(self, text, cls, colspan=None, rowspan=None):
        params = "class='%s'" % cls
        if colspan is not None:
            params += " colspan='{}'".format(colspan)
        if rowspan is not None:
            params += " rowspan='{}'".format(rowspan)

        return self.tag('td', text, params)

    def endRest(self):
        while len(self._ebuf) > 0:
            self.end()

    def write(self):
        self\
            .begin('html')\
                .begin('head')\
                    .tag("link", text=None, params='href="style.css" rel="stylesheet" type="text/css"')\
                .end()\
                .begin('body')\
                    .begin('table', "class='tb'")
        self.tableHeader()

        n = 1
        for ll in self.db.get_sorted_db():
            self.tableLine(ll, n)
            n += 1

        self.endRest()

    def tableHeader(self):
        self.begin('tr')
        multi = 0
        for c in self.cols:
            if multi > 0:
                multi -= 1
            else:
                if len(c) == 3:
                    self.td(c[0], 'he', colspan=c[2])
                    multi = c[2]
                else:
                    self.td(c[0], 'he', rowspan=2)
        self.end()
        self.begin('tr')
        for c in self.cols:
            if multi > 0:
                multi -= 1
                self.td(c[0], 'he')
            else:
                if len(c) == 3:
                    multi = c[2]
        self.end()
        pass

    def tableLine(self, line, n):
        self.begin('tr', params="class='r%d'" % (n%2))
        x = ''
        for c in self.cols:
            x = c[1][0]
            if x <> '-':
                what = c[1][2:]
                cls = what
                text = '&nbsp;'
                if x == 'p':
                    text = str(line.__dict__[what])
                elif x == 'c':
                    text = "%.2f" % line.__dict__[what]
                elif x == 'd':
                    cls = 'val'
                    if line.druh == what:
                        text = "%.2f" % line.castka
                    elif line.plus_druh == what:
                        text = "%.2f" % line.plus_castka
                elif x == 'j':
                    cls = 'val'
                    if line.jak == what:
                        text = "%.2f" % line.suma
                else:
                    cls = 'err'
                    text = "? "+c[1]

                self.td(text, cls)
