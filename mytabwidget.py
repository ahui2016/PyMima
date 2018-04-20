from PyQt5 import QtWidgets, QtCore
from mydialogs import AddDialog, EditDialog
from mytableview import HomeTableView, RecycleBinTableView
from pymimaconst import MIMA_COLUMNS, EPOCH, MINUTES, TICK, create_model, \
    confirm_deletion

import connection
from mimabox import MimaBox


class MyTabWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_widgets_()

    def _init_widgets_(self):
        self.vBox = QtWidgets.QVBoxLayout()
        self.setLayout(self.vBox)
        self.model = create_model()

    def delete(self):

        modelIndex = self.tableView.currentIndex()
        if not modelIndex.model():
            self.show_not_selected_messagebox()
            return

        answer = confirm_deletion(self, self.confirm_message)
        if answer == QtWidgets.QMessageBox.Yes:
            nonceIndex = modelIndex.sibling(
                modelIndex.row(), MIMA_COLUMNS['nonce'])
            nonce = nonceIndex.data()
            box = MimaBox(nonce)

            self.move_to_trash_or_delete(box)

    def show_not_selected_messagebox(self):
        QtWidgets.QMessageBox.information(
            self,
            'Not Selected',
            'Please select an item.'
        )

    def resizeEvent(self, event):
        self.tableView.resizeColumns()
        super().resizeEvent(event)


class HomeTab(MyTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.confirm_message = 'Remove the seleted record to recycle bin?'

        self._init_ui_()

    def _init_ui_(self):
        self.model.setFilter(f"deleted <= '{EPOCH}' AND "
                             f"title   <> ''")
        self.model.setSort(MIMA_COLUMNS['favorite'], QtCore.Qt.DescendingOrder)

        self.searchHBox = QtWidgets.QHBoxLayout()
        self.searchEdit = QtWidgets.QLineEdit()
        self.searchEdit.returnPressed.connect(self.search)
        self.searchButton = QtWidgets.QPushButton('Search')
        self.searchButton.clicked.connect(self.search)
        self.searchHBox.addWidget(self.searchEdit)
        self.searchHBox.addWidget(self.searchButton)

        self.tableView = HomeTableView(self)
        self.tableView.setModel(self.model)
        self.tableView.customize_columns()

        # self.bottomHBox = Add + stretch + Edit + Delete
        self.bottomHBox = QtWidgets.QHBoxLayout()
        addButton = QtWidgets.QPushButton('Add')
        editButton = QtWidgets.QPushButton('Edit')
        deleteButton = QtWidgets.QPushButton('Delete')
        self.bottomHBox.addWidget(addButton)
        self.bottomHBox.addStretch(1)
        self.bottomHBox.addWidget(editButton)
        self.bottomHBox.addWidget(deleteButton)

        addButton.clicked.connect(self.show_add_dialog)
        editButton.clicked.connect(self.show_edit_dialog)
        deleteButton.clicked.connect(self.delete)

        self.vBox.addLayout(self.searchHBox)
        self.vBox.addWidget(self.tableView)
        self.vBox.addLayout(self.bottomHBox)

    def set_autoclose_tab(self, autoCloseTab):
        self.autoCloseTab = autoCloseTab

    def search(self):
        text = self.searchEdit.text()
        self.model.setFilter(f"title     <>  ''        AND "
                             f"deleted   <=  '{EPOCH}' AND ("
                             f"title     LIKE '%{text}%' OR "
                             f"username  LIKE '%{text}%' OR "
                             f"website   LIKE '%{text}%' )")

    def show_add_dialog(self):
        self.autoCloseTab.reset_timer()
        self.addDialog = AddDialog(self.model, self)
        self.addDialog.exec_()

    def show_edit_dialog(self):
        self.autoCloseTab.reset_timer()
        modelIndex = self.tableView.currentIndex()

        if not modelIndex.model():
            self.show_not_selected_messagebox()
            return

        nonceIndex = modelIndex.sibling(
            modelIndex.row(), MIMA_COLUMNS['nonce'])
        nonce = nonceIndex.data()
        box = MimaBox(nonce)
        box.restore_by_nonce()

        editDialog = EditDialog(box, self.model, self)
        editDialog.exec_()

    def move_to_trash_or_delete(self, box):
        box.restore_by_nonce()
        box.move_to_trash()
        self.model.submitAll()
        self.recycleBinModel.submitAll()

    def set_recyclebin_model(self, recycleBinModel):
        self.recycleBinModel = recycleBinModel


class RecycleBinTab(MyTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.confirm_message = "Delete the seleted record?\n" \
                               "(Can not recover)"
        self._init_ui_()

    def _init_ui_(self):
        self.model.setFilter(f"deleted > '{EPOCH}'")
        self.model.setSort(MIMA_COLUMNS['deleted'], QtCore.Qt.DescendingOrder)

        self.tableView = RecycleBinTableView(self)
        self.tableView.setModel(self.model)
        self.tableView.customize_columns()

        self.bottomHBox = QtWidgets.QHBoxLayout()
        recoverButton = QtWidgets.QPushButton('Recover')
        deleteForeverButton = QtWidgets.QPushButton('Delete Forever')
        self.bottomHBox.addWidget(recoverButton)
        self.bottomHBox.addStretch(1)
        self.bottomHBox.addWidget(deleteForeverButton)

        recoverButton.clicked.connect(self.recover)
        deleteForeverButton.clicked.connect(self.delete)

        self.vBox.addWidget(self.tableView)
        self.vBox.addLayout(self.bottomHBox)

    def recover(self):
        modelIndex = self.tableView.currentIndex()

        if not modelIndex.model():
            self.show_not_selected_messagebox()
            return

        answer = confirm_deletion(self, 'Recover the selected record?')

        if answer == QtWidgets.QMessageBox.Yes:
            nonceIndex = modelIndex.sibling(modelIndex.row(),
                                            MIMA_COLUMNS['nonce'])
            nonce = nonceIndex.data()
            box = MimaBox(nonce)
            box.restore_by_nonce()
            box.deleted = EPOCH
            while True:
                if box.is_unique():
                    box.recover()
                    modelIndex.model().submitAll()
                    self.homeTableModel.submitAll()
                    return
                else:
                    title, ok = QtWidgets.QInputDialog.getText(
                        self,
                        'Not Unique',
                        'The (title, username) pair already exists.\n'
                        'Please input a new title.',
                        text=box.title
                    )
                    if not ok:
                        return
                    box.title = title

    def move_to_trash_or_delete(self, box):
        box.delete_forever()
        self.model.submitAll()
        self.homeTableModel.submitAll()

    def set_hometable_model(self, homeTableModel):
        self.homeTableModel = homeTableModel


class AutoCloseTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent

        self.timer = QtCore.QBasicTimer()
        self.step = MINUTES

        self._init_ui_()

    def _init_ui_(self):

        self.vBox = QtWidgets.QVBoxLayout()
        self.setLayout(self.vBox)

        description = QtWidgets.QLabel(
            "PyMima will lock automatically in 30 minutes.\n\n"
            "( When PyMima is locked, if any window popped up,\n"
            "  close it as it prevents to click the Unlock button. )\n\n"
        )
        self.vBox.addWidget(description)

        self.counterHBox = QtWidgets.QHBoxLayout()

        self.counterHBox.addStretch(1)
        self.lcd = QtWidgets.QLCDNumber(self)
        self.lcd.display(MINUTES)
        self.lcd.setDigitCount(3)
        self.lcd.setMinimumHeight(72)
        self.lcd.setMinimumWidth(100)
        self.counterHBox.addWidget(self.lcd)

        self.resetButton = QtWidgets.QPushButton('Reset')
        self.resetButton.clicked.connect(self.reset_timer)
        self.counterHBox.addWidget(self.resetButton)

        self.lockNowButton = QtWidgets.QPushButton('Lock Now')
        self.lockNowButton.clicked.connect(self.lock_now)
        self.counterHBox.addWidget(self.lockNowButton)

        self.unlockButton = QtWidgets.QPushButton('Unlock')
        self.unlockButton.clicked.connect(self.unlock)
        self.unlockButton.setEnabled(False)
        self.counterHBox.addWidget(self.unlockButton)

        self.counterHBox.addStretch(1)
        self.vBox.addLayout(self.counterHBox)
        self.vBox.addStretch(1)

    def toggle_buttons_enabled(self):
        self.resetButton.setEnabled(not self.resetButton.isEnabled())
        self.lockNowButton.setEnabled(not self.lockNowButton.isEnabled())
        self.unlockButton.setEnabled(not self.unlockButton.isEnabled())

    def timerEvent(self, event):
        if self.step <= 0:
            self.stop_and_lock()
            return
        self.step -= 1
        self.lcd.display(self.step)

    def stop_and_lock(self):
        self.timer.stop()
        self.toggle_buttons_enabled()

        homeTab = self.parent.widget(0)
        if hasattr(homeTab, 'addDialog'):
            homeTab.addDialog.reject()
        if hasattr(homeTab, 'editDialog'):
            homeTab.editDialog.reject()
        self.parent.setTabEnabled(0, False)
        self.parent.setTabEnabled(1, False)

    def start_timer(self):
        if not self.timer.isActive():
            self.timer.start(TICK, self)

    def reset_timer(self):
        self.timer.stop()
        self.step = MINUTES
        self.lcd.display(MINUTES)
        self.timer.start(TICK, self)

    def unlock(self):
        if connection.login(self):
            self.reset_timer()
            self.toggle_buttons_enabled()
            self.parent.setTabEnabled(0, True)
            self.parent.setTabEnabled(1, True)

    def lock_now(self):
        self.stop_and_lock()
        self.lcd.display(0)
        self.step = 0
