import datetime
from PyQt5 import QtSql, QtWidgets


def create_model(table='mimatemp'):
    model = QtSql.QSqlTableModel()
    model.setTable(table)
    model.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
    model.select()
    return model


def confirm_deletion(parent, message):
    return QtWidgets.QMessageBox.question(
        parent,
        'Confirm',
        message,
        defaultButton=QtWidgets.QMessageBox.No
    )


def show_not_selected_messagebox(widget):
    QtWidgets.QMessageBox.information(
        widget,
        'Not Selected',
        'Please select an item.'
    )


def delete(widget):
    modelIndex = widget.tableView.currentIndex()
    if not modelIndex.model():
        show_not_selected_messagebox(widget)
        return

    answer = confirm_deletion(widget, widget.confirm_message)
    if answer == QtWidgets.QMessageBox.Yes:
        nonceIndex = modelIndex.sibling(
            modelIndex.row(), widget.COLUMNS['nonce'])
        nonce = nonceIndex.data()

        widget.move_to_trash_or_delete(nonce)


EPOCH = datetime.datetime(1970, 1, 1).isoformat(sep=' ')

MINUTES = 30
TICK = 1000 * 60

MIMA_COLUMNS = dict(
    nonce=0,
    title=1,
    username=2,
    website=3,
    password=4,
    notes=5,
    favorite=6,
    deleted=7
)

HISTORY_COLUMNS = dict(
    nonce=0,
    mimanonce=1,
    title=2,
    username=3,
    website=4,
    password=5,
    notes=6,
    favorite=7,
    deleted=8
)

CREATE_TABLES = """
    CREATE TABLE IF NOT EXISTS mima (
        nonce       varchar(32)    PRIMARY KEY,
        encrypted   blob
    );

    CREATE TABLE IF NOT EXISTS history (
        nonce       varchar(32)    PRIMARY KEY,
        mimanonce   varchar(32)    NOT NULL
                                   REFERENCES mima (nonce) ON DELETE CASCADE,
        encrypted   blob
    );
    """

CREATE_TEMP_TABLES = """
    CREATE TEMPORARY TABLE IF NOT EXISTS mimatemp (
        nonce       varchar(32)     PRIMARY KEY,
        title       varchar(128)    NOT NULL DEFAULT '',
        username    varchar(128)    NOT NULL DEFAULT '',
        website     varchar(128)    NOT NULL DEFAULT '',
        password    varchar(128)    NOT NULL DEFAULT '',
        notes       text            NOT NULL DEFAULT '',
        favorite    integer         DEFAULT 0
                                    CHECK (favorite == 1 or favorite == 0),
        deleted     datetime        NOT NULL
                                    DEFAULT (datetime('1970-01-01 00:00:00')),
        UNIQUE (title, username, deleted)
    );

    CREATE TEMPORARY TABLE IF NOT EXISTS historytemp (
        nonce       varchar(32)     PRIMARY KEY,
        mimanonce   varchar(32)     NOT NULL
                                    REFERENCES mimatemp (nonce)
                                    ON DELETE CASCADE,
        title       varchar(128)    NOT NULL,
        username    varchar(128)    NOT NULL,
        website     varchar(128)    NOT NULL,
        password    varchar(128)    NOT NULL,
        notes       text            NOT NULL,
        favorite    integer         DEFAULT 0
                                    CHECK (favorite == 1 or favorite == 0),
        deleted     datetime        NOT NULL
    );
    """

CHECK_UNIQUENESS = """
    SELECT * FROM mimatemp WHERE title=? and username=? and deleted=datetime(?)
    """

CHECK_UNIQUENESS_EXCEPT_ITSELF = """
    SELECT * FROM mimatemp WHERE
        title=? and username=? and deleted=datetime(?) and nonce<>?
    """

FIND_NONCE_IN_MIMATEMP = 'SELECT nonce FROM mimatemp WHERE nonce=?'

FIND_NONCE_IN_HISTORYTEMP = 'SELECT nonce FROM historytemp WHERE nonce=?'

INSERT_INTO_MIMATEMP = """
    INSERT INTO mimatemp (
        nonce, title, username, website, password, notes, favorite, deleted)
    VALUES (
        :nonce, :title, :username, :website, :password, :notes, :favorite,
        datetime(:deleted))
    """

INSERT_INTO_HISTORYTEMP = """
    INSERT INTO historytemp (
        nonce, mimanonce, title, username, website, password, notes,
        favorite, deleted)
    VALUES (
        :nonce, :mimanonce, :title, :username, :website, :password, :notes,
        :favorite, datetime(:deleted))
    """

INSERT_INTO_MIMA = 'INSERT INTO mima VALUES (:nonce, :encrypted)'

INSERT_INTO_HISTORY = """
    INSERT INTO history (nonce, mimanonce, encrypted)
    VALUES (:nonce, :mimanonce, :encrypted)
    """

UPDATE_FAVORITE = 'UPDATE mimatemp SET favorite=:favorite WHERE nonce=:nonce'

UPDATE_DELETED = """
    UPDATE mimatemp SET favorite=0, deleted=datetime(:deleted)
    WHERE nonce=:nonce
    """

RECOVER = """
    UPDATE mimatemp SET title=:title, deleted=datetime('1970-01-01T00:00:00')
    WHERE nonce=:nonce
    """

SELECT_FROM_MIMATEMP = """
    SELECT nonce, title, username, website, password, notes, favorite, deleted
    FROM mimatemp WHERE nonce=?
    """

SELECT_FROM_HISTORYTEMP = """
    SELECT nonce, mimanonce, title, username, website, password, notes,
           favorite, deleted
    FROM historytemp WHERE nonce=?
    """

UPDATE_MIMA = 'UPDATE mima SET encrypted=:encrypted WHERE nonce=:nonce'

UPDATE_HISTORY = 'UPDATE history SET encrypted=:encrypted WHERE nonce=:nonce'

UPDATE_MIMATEMP = """
    UPDATE mimatemp SET
    title=:title, username=:username, website=:website, password=:password,
    notes=:notes, favorite=:favorite, deleted=datetime(:deleted)
    WHERE nonce=:nonce
    """
