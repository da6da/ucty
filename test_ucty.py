import unittest

from ucty import DB
from datetime import date

class UctyTestValue(unittest.TestCase):
    def test_datum_bad_date(self):
        db = DB()
        with self.assertRaisesRegexp(ValueError, "day is out of range for month"):
            db._read_user_line_raw("37/9")

    def test_datum_bad_moth(self):
        db = DB()
        with self.assertRaisesRegexp(ValueError, "month must be in 1..12"):
            db._read_user_line_raw("27/19")

    def test_datum(self):
        db = DB()

        db._read_user_line_raw("K 1.1. 0 Jidlo ObchodNaRohu")
        d = db.param['kdy']
        self.assertEquals(d.day, 1)
        self.assertEquals(d.month, 1)

        db._read_user_line_raw("K 1.1.1900 0 Jidlo ObchodNaRohu")
        d = db.param['kdy']
        self.assertEquals(d.day, 1)
        self.assertEquals(d.month, 1)
        self.assertEquals(d.year, 1900)

        db._read_user_line_raw("K 1/1 0 Jidlo ObchodNaRohu")
        d = db.param['kdy']
        self.assertEquals(d.day, 1)
        self.assertEquals(d.month, 1)

        db._read_user_line_raw("K 1/1/1900 0 Jidlo ObchodNaRohu")
        d = db.param['kdy']
        self.assertEquals(d.day, 1)
        self.assertEquals(d.month, 1)
        self.assertEquals(d.year, 1900)


    def test_param_kdy_err(self):
        db = DB()
        with self.assertRaisesRegexp(ValueError, "Chybny datum.*"):
            db._read_user_line_raw("kdy=2719")

    def test_param_zkratka_err(self):
        db = DB()
        with self.assertRaisesRegexp(ValueError, "Zkratka neni povolena v parametrech"):
            db._read_user_line_raw("zkratka=X")

    def test_param_noexist(self):
        db = DB()
        with self.assertRaisesRegexp(ValueError, "Parametr '.*' neexistuje"):
            db._read_user_line_raw("bla=X")

    def test_neznam(self):
        db = DB()
        with self.assertRaisesRegexp(ValueError, "Tak tohle neznam (.*)"):
            db._read_user_line_raw("Obchod K")

    def test_neuplne_zadani(self):
        db = DB()

        with self.assertRaisesRegexp(ValueError, "Chybi parametr \(jak\)"):
            db._read_user_line_raw("1/1 12 Jidlo ObchodNaRohu")

        with self.assertRaisesRegexp(ValueError, "Chybi parametr \(castka\)"):
            db._read_user_line_raw("1/1 K Jidlo ObchodNaRohu")

        with self.assertRaisesRegexp(ValueError, "Chybi parametr \(druh\)"):
            db._read_user_line_raw("1/1 K 12 ObchodNaRohu")

        with self.assertRaisesRegexp(ValueError, "Chybi parametr \(popis\)"):
            db._read_user_line_raw("1/1 K 12 Jidlo")

    def test_today(self):
        db = DB()
        db._read_user_line_raw("K 12 Jidlo ObchodNaRohu")
        self.assertEquals(db.param['kdy'], date.today())

    def test_datum_vs_castka(self):
        db = DB()

        db._read_user_line_raw("K 1.1. 2.2 Jidlo ObchodNaRohu")
        c = db.param['castka']
        d = db.param['kdy']
        self.assertEquals(c, 2.2)
        self.assertEquals(d.day, 1)
        self.assertEquals(d.month, 1)

        db._read_user_line_raw("K 3.4 Jidlo ObchodNaRohu")
        c = db.param['castka']
        self.assertEquals(c, 3.4)

    def test_castka(self):
        db = DB()
        db._read_user_line_raw("K 12 Jidlo ObchodNaRohu")
        self.assertEquals(db.param['castka'], 12)

        db._read_user_line_raw("K 12.1 Jidlo ObchodNaRohu")
        self.assertEquals(db.param['castka'], 12.1)

        db._read_user_line_raw("K 12,1 Jidlo ObchodNaRohu")
        self.assertEquals(db.param['castka'], 12.1)

        db._read_user_line_raw("K -5.30 Jidlo ObchodNaRohu")
        self.assertEquals(db.param['castka'], -5.30)

    def test_zadani(self):
        db = DB()
        db._read_user_line_raw("8/4/1974 K 12,3 Jidlo ObchodNaRohu")
        self.assertEquals(db.param['kdy'], date(1974,4,8))


    def test_comment(self):
        db = DB()
        rslt = db._read_user_line_raw("# whatever")
        self.assertEquals(rslt, None)


    def test_plus(self):
        db = DB()
        db._read_user_line_raw("10/10 K jidlo 15 Obchod + dom 4")
        self.assertEquals(db.param['castka'], 15)
        self.assertEquals(db.param['plus_castka'], 4)
        self.assertEquals(db.param['druh'],"Jidlo")
        self.assertEquals(db.param['plus_druh'], "Domacnost")

        with self.assertRaisesRegexp(ValueError, "Za \+ musi byt castka a druh"):
            db._read_user_line_raw("10/10 K jidlo 15 Obchod + dom")

        with self.assertRaisesRegexp(ValueError, "Pouze jedno \+ je povoleno"):
            db._read_user_line_raw("10/10 K jidlo 15 Obchod + + dom 4")

        with self.assertRaisesRegexp(ValueError, "Za \+ pouze castka a druh"):
            db._read_user_line_raw("10/10 K jidlo 15 Obchod + dom 4 Asda")

    def test_ditto(self):
        db = DB()
        db._read_user_line_raw("8/10 K jidlo 15 Obchod")
        db._read_user_line_raw('" A 20')
        self.assertEquals(db.param['castka'], 20)
        d = db.param['kdy']
        self.assertEquals(d.day, 8)
        self.assertEquals(d.month, 10)

        db._read_user_line_raw('" A 20 + dom 4')
        self.assertEquals(db.param['plus_castka'], 4)
        db._read_user_line_raw('" A 20')
        self.assertEquals(db.param['plus_castka'], None)

if __name__ == '__main__':
    unittest.main(verbosity=2)
    # suite = unittest.TestLoader().loadTestsFromTestCase(MyTestCase)
    # unittest.TextTestRunner(verbosity=2).run(suite)