import sys
import json
import hashlib
import nacl.secret
from PyQt5 import QtSql
import connection
from mimabox import MimaBox, HistoryBox


OLD_PASSWORD = 'keep all secrets'
NEW_PASSWORD = 'all secrets kept'


def main():
    key = hashlib.sha256(OLD_PASSWORD.encode()).digest()
    old_secretbox = nacl.secret.SecretBox(key)

    key = hashlib.sha256(NEW_PASSWORD.encode()).digest()
    new_secretbox = nacl.secret.SecretBox(key)

    MimaBox.secretbox = new_secretbox

    # Similar to connection.populate_temp_tables
    sql1 = 'SELECT nonce, encrypted FROM mima'
    sql2 = 'SELECT nonce, encrypted FROM history'

    query = QtSql.QSqlQuery()
    query.setForwardOnly(True)

    for sql in (sql1, sql2):
        query.exec_(sql)
        while query.next():
            nonce = query.value('nonce')
            encrypted = query.value('encrypted').data()
            mima_dict = json.loads(old_secretbox.decrypt(encrypted).decode())
            if 'history' in sql:
                box = HistoryBox(nonce=nonce, **mima_dict)
            else:
                box = MimaBox(nonce=nonce, **mima_dict)
            box.update_database()


if __name__ == '__main__':
    if not connection.create_connection():
        sys.exit(1)
    main()
