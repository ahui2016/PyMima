from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox, QTableView, QApplication, \
    QAbstractItemView, QStyledItemDelegate, QHeaderView
from pymimaconst import MIMA_COLUMNS, HISTORY_COLUMNS
from mimabox import MimaBox, HistoryBox


class HomeTableView(QTableView):

    def __init__(self, parent=None):
        super(HomeTableView, self).__init__(parent)

        self.parent = parent
        self.FAVORITE_WIDTH = 100
        self.PASSWORD_WIDTH = 100
        self.MARGIN = 46

        self.clipboard = QApplication.clipboard()
        self.headerView = self.horizontalHeader()

        self._init_ui_()

    def _init_ui_(self):
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setItemDelegateForColumn(
            MIMA_COLUMNS['password'], PasswordDelegate(self))
        self.setItemDelegateForColumn(
            MIMA_COLUMNS['favorite'], FavoriteDelegate(self))

        self.doubleClicked[QtCore.QModelIndex].connect(self.copy_or_favorite)

    def customize_columns(self):
        # self.setColumnWidth(MIMA_COLUMNS['favorite'], 80)
        # self.setColumnWidth(MIMA_COLUMNS['website'], 150)
        # self.setColumnWidth(MIMA_COLUMNS['title'], 200)
        # self.setColumnWidth(MIMA_COLUMNS['username'], 200)
        # self.setColumnWidth(MIMA_COLUMNS['password'], 100)

        self.setColumnHidden(MIMA_COLUMNS['nonce'], True)
        self.setColumnHidden(MIMA_COLUMNS['notes'], True)
        self.setColumnHidden(MIMA_COLUMNS['deleted'], True)

        # self.headerView.setSortIndicatorShown(True)
        self.headerView.moveSection(MIMA_COLUMNS['website'], 2)
        self.headerView.moveSection(MIMA_COLUMNS['favorite'], 0)
        # self.headerView.setSectionResizeMode(QHeaderView.Stretch)
        self.headerView.resizeSection(
            MIMA_COLUMNS['favorite'],
            self.FAVORITE_WIDTH
        )
        self.headerView.resizeSection(
            MIMA_COLUMNS['password'],
            self.PASSWORD_WIDTH
        )

    def resizeColumns(self):
        column_favorite_width = self.headerView.sectionSize(
            MIMA_COLUMNS['favorite'])
        column_password_width = self.headerView.sectionSize(
            MIMA_COLUMNS['password'])
        remain_length = self.parent.width() - column_favorite_width - \
            column_password_width - self.MARGIN

        for i in (MIMA_COLUMNS['website'],
                  MIMA_COLUMNS['title'],
                  MIMA_COLUMNS['username']):
            self.headerView.resizeSection(i, remain_length / 3)

    def copy_or_favorite(self, modelIndex):
        if modelIndex.column() == MIMA_COLUMNS['favorite']:
            nonceIndex = modelIndex.sibling(modelIndex.row(),
                                            MIMA_COLUMNS['nonce'])
            nonce = nonceIndex.data()
            box = MimaBox(nonce)
            box.restore_by_nonce()
            box.toggle_favorite()
            modelIndex.model().submitAll()
        elif modelIndex.data():
            # if modelIndex.column() == self.PASSWORD:
            #     self.clipboard.setText(modelIndex.data(QtCore.Qt.UserRole))
            self.clipboard.setText(modelIndex.data())
            TimerMessageBox(
                QMessageBox.Information, 'Copied', 'Copied', parent=self
            ).exec_()
            # self.setSelectionBehavior(QAbstractItemView.SelectItems)


class PasswordDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        if index.data():
            painter.drawText(option.rect, QtCore.Qt.AlignCenter, '******')

    # def createEditor(self, parent, option, index):
    #     super().createEditor(parent, option, index)

    # def setEditorData(self, editor, index):
    #     super().setEditorData(editor, index)

    # def updateEditorGeometry(self, editor, option, index):
    #     super().updateEditorGeometry(editor, option, index)

    # def setModelData(self, editor, model, index):
    #     super().setModelData(editor, model, index)
    # def setModelData(self, editor, model, index):
    #     model.setData(QtCore.Qt.UserRole, index.data())


class FavoriteDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.data():
            font = painter.font()
            font.setPixelSize(18)
            painter.setFont(font)
            painter.drawText(option.rect, QtCore.Qt.AlignCenter, '★')

    # def setModelData(self, editor, model, index):
    #     super().setModelData(editor, model, index)


class TimerMessageBox(QMessageBox):
    def __init__(self, icon, title, text, parent=None):
        super().__init__(icon, title, text, parent=parent)
        self.setStandardButtons(QMessageBox.NoButton)
        QtCore.QTimer.singleShot(2000, self.close)

    def closeEvent(self, event):
        event.accept()


class RecycleBinTableView(QTableView):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.COLUMNS = MIMA_COLUMNS
        self.headerView = self.horizontalHeader()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.set_width()

    def set_width(self):
        self.DELETED_WIDTH = 170
        self.MARGIN = 46

    def customize_columns(self):
        self.setColumnHidden(self.COLUMNS['nonce'], True)
        self.setColumnHidden(self.COLUMNS['favorite'], True)
        self.setColumnHidden(self.COLUMNS['notes'], True)
        self.setColumnHidden(self.COLUMNS['password'], True)

        self.headerView.moveSection(self.COLUMNS['website'], 2)
        self.headerView.moveSection(self.COLUMNS['deleted'], 0)
        # self.headerView.setSectionResizeMode(QHeaderView.Stretch)
        # self.headerView.setDefaultSectionSize(self.DELETED_WIDTH)
        self.headerView.resizeSection(self.COLUMNS['deleted'],
                                      self.DELETED_WIDTH)

    def update_remain_width(self):
        deletedColumn_width = \
            self.headerView.sectionSize(self.COLUMNS['deleted'])
        self.remain_length = \
            self.parent.width() - deletedColumn_width - self.MARGIN

    def resizeColumns(self):
        self.update_remain_width()
        for i in (self.COLUMNS['website'],
                  self.COLUMNS['title'],
                  self.COLUMNS['username']):
            self.headerView.resizeSection(i, self.remain_length / 3)


class HistoryTableView(RecycleBinTableView):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.COLUMNS = HISTORY_COLUMNS
        self.doubleClicked[QtCore.QModelIndex].connect(self.update_form)

    def customize_columns(self):
        super().customize_columns()
        self.setColumnHidden(self.COLUMNS['mimanonce'], True)
        self.setColumnHidden(self.COLUMNS['website'], True)
        self.headerView.setSectionResizeMode(QHeaderView.Stretch)
        # self.headerView.setDefaultSectionSize(self.DELETED_WIDTH)

    def update_form(self, modelIndex):
        nonceIndex = modelIndex.sibling(modelIndex.row(),
                                        self.COLUMNS['nonce'])
        historyBox = HistoryBox(nonceIndex.data())
        historyBox.restore_by_nonce()
        self.parent.update_form(historyBox)
