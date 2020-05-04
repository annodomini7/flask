import sqlite3
import re


def sqlite_like(template_, value_):
    return sqlite_like_escape(template_, value_, None)


def sqlite_like_escape(template_, value_, escape_):
    re_ = re.compile(template_.lower().
                     replace(".", "\\.").replace("^", "\\^").replace("$", "\\$").
                     replace("*", "\\*").replace("+", "\\+").replace("?", "\\?").
                     replace("{", "\\{").replace("}", "\\}").replace("(", "\\(").
                     replace(")", "\\)").replace("[", "\\[").replace("]", "\\]").
                     replace("_", ".").replace("%", ".*?"))
    return re_.match(value_.lower()) is not None


def sqlite_lower(value_):
    return value_.lower()


def sqlite_upper(value_):
    return value_.upper()


def sqlite_nocase_collation(value1_, value2_):
    return (value1_.encode('utf-8').lower() < value2_.encode('utf-8').lower()) - (
            value1_.encode('utf-8').lower() > value2_.encode('utf-8').lower())


con = sqlite3.connect("db/pharmacy.db")
con.create_collation("BINARY", sqlite_nocase_collation)
con.create_collation("NOCASE", sqlite_nocase_collation)
con.create_function("LIKE", 2, sqlite_like)
con.create_function("LOWER", 1, sqlite_lower)
con.create_function("UPPER", 1, sqlite_upper)
cur = con.cursor()
result = cur.execute(
    """select *
    from medicine
    where UPPER(medicine.name) LIKE UPPER('%БрОнхикУм%')""").fetchall()
print(result)


# http://victor-k-development.blogspot.com/2010/10/sqlite.html
