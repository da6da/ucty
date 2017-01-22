# coding=utf-8
"""
Ucty
"""

from ucty_db import DB
from ucty_html import HtmlOutput

if __name__ == "__main__":
    db = DB()
    lineno=1
    for l in open("u-2016-11-03.txt").read().splitlines():
        db.read_user_line(l, lineno)
        lineno += 1

    db.write(open("o.txt", mode='w'))
    if len(db.error_lines) > 0:
        open("o_err.txt", mode='w').writelines(db.error_lines)

    #_db.log()
    #print "---- Prevedeno:"
    #print _db
    o = HtmlOutput(db, "out.html")
    o.write()
    o.close()
