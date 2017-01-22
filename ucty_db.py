# coding=utf-8
"""
Ucty DB
"""

from datetime import date
import re
import sys


class Line:
    def __init__(self, kdy, jak, castka, druh, popis, zkratka=None, plus_castka=None, plus_druh=None):
        # datum
        self.kdy = kdy

        # platba v GBP
        self.castka = castka

        # jmeno obchodu nebo popis
        self.popis = popis

        # druh platby
        self.druh = druh

        # zpusob platby
        self.jak = jak.upper()

        self.plus_castka = plus_castka
        self.plus_druh = plus_druh

        self.suma = castka
        if plus_castka is not None:
            self.suma += plus_castka

    def __str__(self):
        return u"{} {} {:.2f} d:{} p:{}".format(self.kdy, self.jak, self.castka, self.druh, self.popis)

    def write(self, file):
        file.write("kdy={} jak={} castka={} druh={} popis={}".format(self.kdy, self.jak, self.castka, self.druh, self.popis))
        if self.plus_castka is not None:
            file.write(" plus_castka={}".format(self.plus_castka))
        if self.plus_druh is not None:
            file.write(" plus_druh={}".format(self.plus_druh))
        file.write("\n")

class DB:
    zkratka = {
        # A 12.45 -> (ASDA,12.45,Pure,Jidlo)
        'A': [('popis', 'ASDA', '!'), ('druh', 'Jidlo', '?'), ('jak', 'P', '?')],
        'VYB': [('popis', 'Vyber', '!'), ('druh', 'Vyber', '!'), ('jak', 'K', '!')],
        'vyber': [('popis', 'Vyber', '!'), ('druh', 'Vyber', '!'), ('jak', 'K', '!')],
        'Nero': [('popis', 'CaffeNerro', '!'), ('druh', 'Z-Jidlo', '!'), ('jak', 'P', '?')],
        'Ovoce': [('popis', 'FreshInABox','!'), ('druh', 'Jidlo', '!'), ('jak', 'H', '?')],
        'bus': [('popis', 'Bus', '!'), ('druh', 'Sluzby', '?')],
        'Posta': [('popis', 'Posta', '?'), ('druh', 'Sluzby', '!')],
        'Vlak': [('popis', 'Vlak', '!'), ('druh', 'Sluzby', '?')],
    }

    druh = ['Jidlo','Domacnost','Skola','Obleceni','Velke','Sluzby','Vyber','Darky','Ostatni','Tvoreni','CZ',
            'KAP',
            'Z-Jidlo','Z-Vstup','Z-Cesta','Z-Ostatni']
    obchod = ['Asda','Charita',("BaM","B&M"), ("Works","TheWorks"),"Tesco","Poundland", "HobbyCraft", "HomeSense", "TkMaxx",
              'M&S']

    def __init__(self):
        self.tokens = []
        self.param = {
            'zkratka' : None,
            'kdy'     : None,
            'castka'  : None,
            'popis'   : None,
            'druh'    : None,
            'jak'     : None,
            'plus_castka': None,
            'plus_druh': None,
        }
        self.is_plus = False
        self.plus = []
        self._db = []
        self._db_sorted = None
        self.error_lines = []

    def __str__(self):
        return "\n".join([unicode(l) for l in self._db])

    def reset(self):
        self.tokens = []
        self.is_plus = False
        self.plus = []
        for k in self.param:
            self.param[k] = None

    def read_user_line(self, line, lineno):
        try:
            l = self._read_user_line_raw(line)
            if l is not None:
                self._db.append(l)
                self._db_sorted = None  # Invalidate sorted database when new item added

        except ValueError as ve:
            print >> sys.stderr, lineno, '"'+line+'"', ve.message
            self.error_lines.append(line)

    def _read_user_line_raw(self, line):
        """
        Precte jednu radku zadanou uzivatelem a vrati instanci Line
        :param: line vstupni radka
        :return: Instance Line pokud je vse v poradku nebo None pokud je chyba
        """

        last_param = self.param.copy()
        self.reset()

        # rozsekame podle mezer a preskocime prazdne tokeny, ktere vzniknou z nasobnych mezer
        self.tokens = [t for t in line.split(' ') if len(t) > 0]

        if len(self.tokens) == 0 or self.tokens[0][0] == '#':
            return None

        ditto = (self.tokens[0] == '"')
        if ditto:
            self.next_token()

        while self.has_token():
            if self.skip():
                pass
            elif self.tokens[0] == '+':
                if self.is_plus:
                    raise ValueError("Pouze jedno + je povoleno")
                else:
                    self.is_plus = True
            elif self.is_plus:
                if self.is_plus_druh():
                    pass
                elif self.is_plus_castka():
                    pass
                else:
                    raise ValueError("Za + pouze castka a druh")
            elif self.is_zkratka():
                pass
            elif self.is_datum():
                pass
            elif self.is_platba():
                pass
            elif self.is_param():
                pass
            elif self.is_druh():
                pass
            elif self.is_castka():
                pass
            elif self.is_popis():
                pass
            else:
                raise ValueError("Tak tohle neznam ("+self.tokens[0]+")")
            self.next_token()

        if self.param['zkratka'] is not None:
            self.expand_zkratka()

        if ditto:
            last_param['plus_druh'] = None
            last_param['plus_castka'] = None
            for k,v in self.param.iteritems():
                if v is None:
                    self.param[k] = last_param[k]

        # mame vsechno prectene bez chyby
        if self.param['kdy'] is None:
            self.param['kdy'] = date.today()

        notpresent = [p for p in ['castka', 'popis', 'druh', 'jak'] if self.param[p] is None]
        if len(notpresent) > 0:
            raise ValueError("Chybi parametr ("+','.join(notpresent)+")")

        if self.is_plus:
            if self.param['plus_druh'] is None or self.param['plus_castka'] is None:
                raise ValueError("Za + musi byt castka a druh")

        return Line(**self.param)

    def has_token(self):
        return len(self.tokens) > 0

    def next_token(self):
        self.tokens = self.tokens[1:]

    def skip(self):
        inp = self.tokens[0]
        if inp == ',':
            return True
        else:
            return False

    def is_zkratka(self):
        """
        Najde zkratku v seznamu a ulozi ji do parametru.
        :return: False pokud token neni zkratka nebo pokud jiz byla zkratka nalezena. Jinak True.
        """
        t = self.tokens[0].lower()
        for k in DB.zkratka.iterkeys():
            if k.lower() == t:
                if self.param['zkratka'] is not None:
                    return False
                self.param['zkratka'] = k
                return True
        return False

    def is_platba(self):
        p = self.tokens[0].upper()
        if p == 'K' or p == 'H' or p == 'P' or p == 'U':
            if self.param['jak'] is not None:
                return False
            self.param['jak'] = p
            return True

        return False

    def is_datum(self, inp=None):
        """
        Najde datum v seznamu a ulozi ho do parametru.
        Chybny datum (napr. 37/8) zpusobi vyjimku ValueError, ktera musi byt odchycena vyse jako chyba celeho radku.
        Znamena to, ze retezec vypada jako datum, ale hodnoty jsou chybne -> chyba.
        :param: inp pokud je zadany, bere se jako vstup. Jinak je vstupem token.
        :return: False pokud token neni datum nebo pokud jiz byl datum nalezeny. Jinak True.
        """
        if inp == None:
            inp = self.tokens[0]

        mo_uk = re.match('^(?P<day>[0123]?\d)/(?P<month>[01]?\d)(/(?P<year>\d{2}(\d{2})?))?$', inp)
        mo_cz = re.match('^(?P<day>[0123]?\d)\.(?P<month>[01]?\d)\.(?P<year>\d{2}(\d{2})?)?$', inp)
        if mo_uk is None and mo_cz is None:
            return False

        y = 0
        m = 0
        d = 0
        for mo in [mo_uk, mo_cz]:
            if mo is not None:
                d = int(mo.group('day'))
                m = int(mo.group('month'))
                if mo.group('year'):
                    y = int(mo.group('year'))
                    if y < 100:
                        y += 2000
                else:
                    # if the year is not specified,
                    # any date later than March added physically before March will be considered as last year's
                    if m > 3 and date.today().month < 3:
                        y = date.today().year-1
                    else:
                        y = date.today().year

        if self.param['kdy'] is not None:
            return False
        self.param['kdy'] = date(y,m,d)
        return True

    def is_param(self):
        """
        Parametr je ve tvaru <jmeno>=<hodnota>. Jmeno nemusi byt cele, staci zacatek.
        :return: False pokud token neni parametr nebo pokud jiz byl zadany (jakym koliv zpusobem). Jinak True.
        """
        p = self.tokens[0].split('=')
        if len(p) != 2:
            return False

        for k, v in self.param.iteritems():
            if k.startswith(p[0]):
                # nasli jsme neco, co zacina jmenem
                if v is not None:
                    # ... ale uz to bylo zadane
                    return False
                if k == 'kdy': # TODO: tohle by slo udelat lip
                    if self.is_datum(p[1]):
                        return True
                    else:
                        raise ValueError("Chybny datum "+p[1])
                elif k == 'zkratka':
                    raise ValueError("Zkratka neni povolena v parametrech")
                else:
                    self.param[k] = p[1]
                return True

        raise ValueError("Parametr '"+p[0]+"' neexistuje")  # je to zapis parametru, ale zadny takovy neni

    def is_druh(self):
        return self._is_druh('druh')

    def is_plus_druh(self):
        return self._is_druh('plus_druh')

    def _is_druh(self, pname):
        d = self.tokens[0].lower()
        found = []
        for x in DB.druh:
            if x.lower().startswith(d):
                found.append(x)
        if len(found) == 0:
            return False
        elif len(found) == 1:
            if self.param[pname] is not None:
                return False
            else:
                self.param[pname] = found[0]
                return True
        return False

    def is_popis(self):
        inp = self.tokens[0]
        for p in DB.obchod:
            if type(p) is tuple:
                if p[0].lower() == inp.lower() or p[1].lower() == inp.lower():
                    self.param['popis'] = p[1]
                    return True
            else:
                if p.lower() == inp.lower():
                    self.param['popis'] = p
                    return True
        if (len(self.tokens) == 1 or self.tokens[1]=='+') and self.param['popis'] is None:
            self.param['popis'] = inp
            return True
        else:
            return False

    def is_castka(self):
        return self._is_castka('castka')

    def is_plus_castka(self):
        return self._is_castka('plus_castka')

    def _is_castka(self, pname):
        num = self.tokens[0]

        # dovolime i desetinnou carku misto tecky
        if num.count(',') == 1:
            num = num.replace(',', '.')

        try:
            c = float(num)
            if self.param[pname] is not None:
                return False
            self.param[pname] = c
            return True
        except ValueError:
            return False

    def expand_zkratka(self):
        z = DB.zkratka[self.param['zkratka']]
        for cmd in z:
            if cmd[2] == '!':
                if self.param[cmd[0]] is not None and self.param[cmd[0]] != cmd[1]:
                    raise ValueError("Zkratka "+self.param['zkratka']+" nesmi prepsat '"+cmd[0]+"' ("+cmd[1]+"->"+self.param[cmd[0]]+")")
                else:
                    self.param[cmd[0]] = cmd[1]
            if cmd[2] == '?' and self.param[cmd[0]] is None:
                self.param[cmd[0]] = cmd[1]

    def log(self):
        for k, v in self.param.iteritems():
            if v is not None:
                print "%s : %s" % (k, v)

    def get_sorted_db(self):
        if self._db_sorted is None:
            def date_cmp(d1,d2):
                if (d1 < d2):
                    return -1
                elif d1 > d2:
                    return 1
                else:
                    return 0

            self._db_sorted = sorted(self._db, cmp=lambda x, y: date_cmp(x.kdy, y.kdy))

        return self._db_sorted

    def write(self, file):
        for ll in self.get_sorted_db():
            ll.write(file)
