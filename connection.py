import os
import sys
import json
import hashlib
import nacl.secret
from PyQt5 import QtWidgets, QtSql, QtCore

from pymimaconst import CREATE_TABLES, CREATE_TEMP_TABLES
from mimabox import MimaBox, HistoryBox


def create_connection():
    db_path = QtCore.QDir(os.path.dirname(os.path.abspath(__file__)))\
              .filePath('pymima.db')
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName(db_path)

    if not db.open():
        QtWidgets.QMessageBox.critical(None, "Cannot open database",
                                       f"Error: {db.lastError().text()}\n",
                                       QtWidgets.QMessageBox.Close)
        return False

    db.exec_('PRAGMA foreign_keys = ON')
    create_tables(db, CREATE_TABLES)
    create_tables(db, CREATE_TEMP_TABLES)
    return True


def create_tables(db, sql):
    # query = QtSql.QSqlQuery()
    tables = sql.split(';')
    for table in tables:
        # if not query.exec_(table):
        if not db.exec_(table):
            # raise RuntimeError(query.lastError().text())
            raise RuntimeError(db.lastError().text())

# def populate_temp_table(table=None): # table can only be mima or history
#     if not table:
#         sql = 'SELECT nonce, encrypted FROM mima'
#     elif table == 'history':
#         sql = 'SELECT nonce, mimanonce, encrypted FROM history'

#     query = QtSql.QSqlQuery()
#     query.setForwardOnly(True)
#     query.exec_(sql)

#     while query.next():
#         nonce = query.value('nonce')
#         encrypted = query.value('encrypted').data()
#         mima_dict = json.loads(MimaBox.secretbox.decrypt(encrypted).decode())

#         if table == 'history':
#             box = HistoryBox(nonce=nonce, **mima_dict)
#             box.mimanonce = query.value('mimanonce')
#         else:
#             box = MimaBox(nonce=nonce, **mima_dict)

#         box.insert_into_temp()


def populate_temp_tables():
    sql1 = 'SELECT nonce, encrypted FROM mima'
    sql2 = 'SELECT nonce, mimanonce, encrypted FROM history'

    query = QtSql.QSqlQuery()
    query.setForwardOnly(True)

    for sql in (sql1, sql2):
        query.exec_(sql)
        while query.next():
            nonce = query.value('nonce')
            encrypted = query.value('encrypted').data()
            mima_dict = json.loads(
                MimaBox.secretbox.decrypt(encrypted).decode())
            if 'history' in sql:
                box = HistoryBox(nonce=nonce, **mima_dict)
                box.mimanonce = query.value('mimanonce')
            else:
                box = MimaBox(nonce=nonce, **mima_dict)
            box.insert_into_temp()


def login(parent, cancelToQuit=False):
    query = QtSql.QSqlQuery()
    query.setForwardOnly(True)
    query.exec_('SELECT encrypted FROM mima LIMIT 1')
    query.next()
    encrypted = query.value(0).data()

    while True:
        masterpassword = get_password(parent, cancelToQuit)

        if masterpassword is None:
            return None

        key = hashlib.sha256(masterpassword.encode()).digest()
        secretbox = nacl.secret.SecretBox(key)
        try:
            secretbox.decrypt(encrypted)
        except nacl.exceptions.CryptoError:
            QtWidgets.QMessageBox.warning(
                parent,
                'Wrong Password',
                'The password is wrong.'
            )
        else:
            return secretbox


def get_password(parent, cancelToQuit=False):
    password, ok = QtWidgets.QInputDialog.getText(
        parent,
        'Master Password',
        'Password: ',
        QtWidgets.QLineEdit.Password
    )
    if not ok:
        if cancelToQuit:
            parent.close()
            QtWidgets.qApp.quit()
            QtWidgets.QApplication.instance().quit()
            sys.exit(1)
        else:
            return None
    return password


if __name__ == '__main__':
    # from PyQt5.QtCore import QByteArray

    app = QtWidgets.QApplication(sys.argv)

    if not create_connection():
        sys.exit(1)

    masterpassword = 'keep all secrets'
    key = hashlib.sha256(masterpassword.encode()).digest()
    secretbox = nacl.secret.SecretBox(key)
    MimaBox.secretbox = secretbox

    populate_temp_tables()

    box = MimaBox(title='aaa', username='bbb')
    print('UNIQUE: ', box.is_unique())
    box.insert_into_database_and_temp()

    query = QtSql.QSqlQuery()
    query.prepare('select nonce from mimatemp where nonce=?')
    query.addBindValue(box.nonce)
    query.exec_()
    query.next()
    print(query.value(0))         # QByteArray
    print(query.value(0).data())  # bytes

    # ID, NAME, CITY = range(3)

    # query = QtSql.QSqlQuery()
    # query.exec_('SELECT id, name, city FROM employee')
    # print(query.lastError().text())

    # while query.next():
    #     name = query.value(NAME)
    #     print(name)
