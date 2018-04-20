from PyQt5.QtSql import QSqlDatabase, QSqlQuery


db = QSqlDatabase.addDatabase('QSQLITE')
db.setDatabaseName(':memory:')
db.open()
query = QSqlQuery()

# query.exec_("SELECT datetime('now')")
# query.exec_("SELECT datetime('')")


def query_exec(query, sql):
    success = query.exec_(sql)
    if not success:
        raise RuntimeError(query.lastError().text())


sql = """
    CREATE TABLE testtable (
        name text,
        timestamp datetime DEFAULT (datetime('1970-01-01 00:00:00'))
                           check (timestamp <> (datetime('')))
    );
    """
query_exec(query, sql)
# query_exec(query, "INSERT INTO testtable VALUES ("
#                   "'aaa', datetime('1970-01-01T00:00:00'))")
# query_exec(query, "INSERT INTO testtable (name) VALUES ('aaa')")
query.prepare("INSERT INTO testtable VALUES (?, datetime(?))")
query.addBindValue('aaa')
query.addBindValue('')
query.exec_()
query_exec(query, "SELECT * FROM testtable")

query.next()
print(type(query.value(0)), query.value(0))
print(type(query.value(1)), query.value(1))
