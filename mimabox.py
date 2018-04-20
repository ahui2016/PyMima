import json
import base64
import datetime
import nacl.secret
import nacl.utils
from PyQt5.QtCore import QByteArray
from PyQt5.QtSql import QSqlQuery
from pymimaconst import SELECT_FROM_HISTORYTEMP, SELECT_FROM_MIMATEMP, \
    INSERT_INTO_HISTORY, INSERT_INTO_HISTORYTEMP, INSERT_INTO_MIMA, \
    INSERT_INTO_MIMATEMP, EPOCH, FIND_NONCE_IN_HISTORYTEMP, CHECK_UNIQUENESS, \
    FIND_NONCE_IN_MIMATEMP, UPDATE_DELETED, UPDATE_FAVORITE, UPDATE_MIMA, \
    UPDATE_MIMATEMP, MIMA_COLUMNS, CHECK_UNIQUENESS_EXCEPT_ITSELF, RECOVER, \
    HISTORY_COLUMNS, UPDATE_HISTORY


class MimaBox:

    secretbox = None

    def __init__(self, nonce='', title='', username='', website='',
                 password='', notes='', favorite=0, deleted=''):

        self.encrypted = None
        self.COLUMNS = MIMA_COLUMNS
        self.SELECT_FROM_TEMP = SELECT_FROM_MIMATEMP
        self.INSERT_INTO_TEMP = INSERT_INTO_MIMATEMP
        self.INSERT_INTO_DATABASE = INSERT_INTO_MIMA
        self.UPDATE_DATABASE = UPDATE_MIMA

        self.query = QSqlQuery()
        # self.query.setForwardOnly(True)

        if nonce:
            self.nonce = nonce
        else:
            self.nonce = self.new_nonce()

        self.title = title
        self.username = username
        self.website = website
        self.password = password
        self.notes = notes
        self.favorite = favorite

        if deleted:
            self.deleted = deleted
        else:
            self.deleted = EPOCH

    def new_nonce(self):
        while True:
            nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
            nonce = base64.b64encode(nonce).decode()

            self.query.prepare(FIND_NONCE_IN_MIMATEMP)
            self.query.addBindValue(nonce)
            self.query_exec()
            result_1 = self.query.first()

            self.query.prepare(FIND_NONCE_IN_HISTORYTEMP)
            self.query.addBindValue(nonce)
            self.query.exec_()
            result_2 = self.query.first()

            if result_1 is False and result_2 is False:
                return nonce

    def is_unique(self):
        self.query.prepare(CHECK_UNIQUENESS)
        for value in [self.title, self.username, self.deleted]:
            self.query.addBindValue(value)
        self.query_exec()
        return not self.query.first()

    def is_unique_except_itself(self):
        self.query.prepare(CHECK_UNIQUENESS_EXCEPT_ITSELF)
        for value in [self.title, self.username, self.deleted, self.nonce]:
            self.query.addBindValue(value)
        self.query_exec()
        return not self.query.first()

    def to_dict(self):
        return dict(
            title=self.title,
            username=self.username,
            website=self.website,
            password=self.password,
            notes=self.notes,
            favorite=self.favorite,
            deleted=self.deleted
        )

    # def to_list(self):
    #     return [self.title,
    #             self.username,
    #             self.website,
    #             self.password,
    #             self.notes,
    #             self.favorite,
    #             self.deleted]

    def insert_into_temp(self, sql=None):  # also use as update_mimatemp
        if not sql:
            sql = self.INSERT_INTO_TEMP

        self.query.prepare(sql)
        self.query.bindValue(':nonce', self.nonce)

        if sql == INSERT_INTO_HISTORYTEMP:
            self.query.bindValue(':mimanonce', self.mimanonce)

        for k, v in self.to_dict().items():
            self.query.bindValue(':'+k, v)

        self.query_exec()

    def update_temp(self):
        self.insert_into_temp(UPDATE_MIMATEMP)

    def encrypt(self):
        message = json.dumps(self.to_dict()).encode()
        encrypted = self.secretbox.encrypt(
            message, base64.b64decode(self.nonce.encode()))
        self.encrypted = QByteArray(encrypted)

    def insert_into_database(self):
        self.encrypt()
        self.query.prepare(self.INSERT_INTO_DATABASE)
        self.query.bindValue(':nonce', self.nonce)
        self.query.bindValue(':encrypted', self.encrypted)

        if self.INSERT_INTO_DATABASE == INSERT_INTO_HISTORY:
            self.query.bindValue(':mimanonce', self.mimanonce)

        self.query_exec()

    def insert_into_database_and_temp(self):
        self.insert_into_temp()
        self.insert_into_database()

        # self.query.exec_('select * from mimatemp')
        # print('SIZE: ', self.query.size())
        # record = self.query.record()
        # self.query.next()
        # for i in range(record.count()):
        #     print(record.fieldName(i), self.query.value(i))

        # if self.query.lastError().type():
        #     raise RuntimeError(self.query.lastError().text())

        # errorType = self.query.lastError().type()
        # if errorType:
        #     print(self.query.lastError().text())
        # else:
        #     print('No Error.', errorType)

        # print('ACTIVE: ', self.query.isActive())
        # print('VALID: ', self.query.isValid())
        # print('AFFECTED: ', self.query.numRowsAffected())
        # print('COMMIT: ', QSqlDatabase.database().commit())

    def restore_by_nonce(self, nonce='', sql=None):

        COLUMNS = self.COLUMNS
        if sql == SELECT_FROM_MIMATEMP:
            COLUMNS = MIMA_COLUMNS

        if not sql:
            sql = self.SELECT_FROM_TEMP

        self.query.prepare(sql)

        if not nonce:
            nonce = self.nonce

        self.query.addBindValue(nonce)
        self.query_exec()
        self.query.next()

        self.title = self.query.value(COLUMNS['title'])
        self.username = self.query.value(COLUMNS['username'])
        self.website = self.query.value(COLUMNS['website'])
        self.password = self.query.value(COLUMNS['password'])
        self.notes = self.query.value(COLUMNS['notes'])
        self.favorite = self.query.value(COLUMNS['favorite'])
        self.deleted = self.query.value(COLUMNS['deleted'])

        if self.SELECT_FROM_TEMP == SELECT_FROM_HISTORYTEMP \
                and sql == SELECT_FROM_HISTORYTEMP:
            self.mimanonce = self.query.value(HISTORY_COLUMNS['mimanonce'])

    def update_database(self):
        self.encrypt()
        self.query.prepare(self.UPDATE_DATABASE)
        self.query.bindValue(':encrypted', self.encrypted)
        self.query.bindValue(':nonce', self.nonce)
        self.query_exec()

    def toggle_favorite(self):
        self.favorite = not self.favorite
        self.query.prepare(UPDATE_FAVORITE)
        self.query.bindValue(':favorite', self.favorite)
        self.query.bindValue(':nonce', self.nonce)
        self.query_exec()
        self.update_database()

    def move_to_trash(self):
        self.favorite = 0
        self.deleted = datetime.datetime.now().isoformat(sep=' ')
        self.query.prepare(UPDATE_DELETED)
        self.query.bindValue(':deleted', self.deleted)
        self.query.bindValue(':nonce', self.nonce)
        self.query_exec()
        self.update_database()

    def recover(self):
        self.deleted = EPOCH
        self.query.prepare(RECOVER)
        self.query.bindValue(':title', self.title)
        self.query.bindValue(':nonce', self.nonce)
        self.query_exec()
        self.update_database()

    def delete_forever(self, table='mima', temptable='mimatemp'):
        self.query.prepare(f"DELETE FROM {temptable} WHERE nonce=?")
        self.query.addBindValue(self.nonce)
        self.query_exec()

        self.query.prepare(f"DELETE FROM {table} WHERE nonce=?")
        self.query.addBindValue(self.nonce)
        self.query_exec()

    def query_exec(self):
        success = self.query.exec_()
        if not success:
            raise RuntimeError(self.query.lastError().text())


class HistoryBox(MimaBox):

    def __init__(self, nonce='', title='', username='', website='',
                 password='', notes='', favorite=0, deleted=''):

        super().__init__(nonce=nonce, title=title, username=username,
                         website=website, password=password, notes=notes,
                         favorite=favorite, deleted=deleted)

        self.COLUMNS = HISTORY_COLUMNS
        self.SELECT_FROM_TEMP = SELECT_FROM_HISTORYTEMP
        self.INSERT_INTO_TEMP = INSERT_INTO_HISTORYTEMP
        self.INSERT_INTO_DATABASE = INSERT_INTO_HISTORY
        self.UPDATE_DATABASE = UPDATE_HISTORY

    def get_values_from_mimabox(self, mimanonce):
        self.restore_by_nonce(nonce=mimanonce, sql=SELECT_FROM_MIMATEMP)
        self.mimanonce = mimanonce

    def delete_forever(self):
        super().delete_forever(table='history', temptable='historytemp')

    def toggle_favorite(self):
        pass

    def move_to_trash(self):
        pass

    def recover(self):
        pass
