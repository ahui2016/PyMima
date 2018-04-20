import string
import secrets
import datetime
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QLineEdit, QLabel, QPushButton, QPlainTextEdit, \
    QDialogButtonBox, QDialog, QMessageBox, QHBoxLayout, QFrame, \
    QApplication, QVBoxLayout, QGridLayout

from mytableview import HistoryTableView
from mimabox import MimaBox, HistoryBox
from passwordedit import PasswordEdit
import pymimaconst
from pymimaconst import HISTORY_COLUMNS, create_model


class MyDialog(QDialog):
    def __init__(self, mimatemp_model, parent=None):
        super().__init__(parent)

        self.PASSWORD_LENGTH = 15
        self.alphabet = string.ascii_letters + string.digits

        # self.setStyleSheet(
        #     'QLabel {font-size: 18px;}'
        #     'QPushButton {font-size: 18px;}'
        #     'QLineEdit {font-size: 18px;}'
        #     'QPlainTextEdit {font-size: 18px;}')

        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.mimatemp_model = mimatemp_model

    def _init_ui_(self):
        self.vBox = QVBoxLayout()
        self.setLayout(self.vBox)

        grid = QGridLayout()
        self.vBox.addLayout(grid)

        titleLabel = QLabel('Title')
        self.titleEdit = QLineEdit()
        titleLabel.setBuddy(self.titleEdit)
        grid.addWidget(titleLabel, 0, 0)
        grid.addWidget(self.titleEdit, 0, 1)

        websiteLabel = QLabel('Website')
        self.websiteEdit = QLineEdit()
        websiteLabel.setBuddy(self.websiteEdit)
        grid.addWidget(websiteLabel, 1, 0)
        grid.addWidget(self.websiteEdit, 1, 1)

        usernameLabel = QLabel('Username')
        self.usernameEdit = QLineEdit()
        usernameLabel.setBuddy(self.usernameEdit)
        grid.addWidget(usernameLabel, 2, 0)
        grid.addWidget(self.usernameEdit, 2, 1)

        passwordLabel = QLabel('Password')
        self.passwordEdit = PasswordEdit(self)
        self.passwordEdit.setFixedHeight(30)
        self.passwordEdit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        passwordLabel.setBuddy(self.passwordEdit)
        grid.addWidget(passwordLabel, 3, 0)
        grid.addWidget(self.passwordEdit, 3, 1)

        # self.passwordEdit.highlighter = PasswordHighlighter(
        #     self.passwordEdit.document())

        self.generateButton = QPushButton('generate')
        self.generateButton.setFixedHeight(30)
        grid.addWidget(self.generateButton, 3, 1, Qt.AlignRight)
        # font = self.generateButton.font()
        # font.setPixelSize(14)
        # self.generateButton.setFont(font)
        self.generateButton.setStyleSheet(
            'QPushButton {font-size: 14px; font-family: Sans;}')
        self.generateButton.clicked.connect(self.generate)

        notesLabel = QLabel('Notes')
        # notesLabel.setAlignment(Qt.AlignTop)
        self.notesEdit = QPlainTextEdit()
        self.notesEdit.setFixedHeight(100)
        notesLabel.setBuddy(self.notesEdit)
        grid.addWidget(notesLabel, 4, 0, Qt.AlignTop)
        grid.addWidget(self.notesEdit, 4, 1)

        # self.notesEdit.highlighter = PasswordHighlighter(
        #     self.notesEdit.document())

        # submitButton = QPushButton('Submit')
        # submitButton.setAutoDefault(False)
        # submitButton.clicked.connect(self.addToDatabase)

        # cancelButton = QPushButton('Cancel')
        # cancelButton.setAutoDefault(False)
        # cancelButton.clicked.connect(self.close)

        # buttonBox = QDialogButtonBox(Qt.Horizontal)
        # buttonBox.addButton(cancelButton, QDialogButtonBox.ActionRole)
        # cancelButton.clicked.connect(self.close)

        # cancelButton = buttonBox.addButton(QDialogButtonBox.Cancel)
        # buttonBox.rejected.connect(self.reject)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel, Qt.Horizontal)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.accepted.connect(self.accept)

        grid.addWidget(self.buttonBox, 5, 1, 2, 1)

        self.resize(QSize(400, self.sizeHint().height()))

    def generate(self):
        password = self.new_password()
        self.passwordEdit.setPlainText(password)

    def new_password(self):
        while True:
            password = ''.join(secrets.choice(self.alphabet) for i in range(
                self.PASSWORD_LENGTH))
            if (any(c.islower() for c in password) and
                    any(c.isupper() for c in password) and
                    any(c.isdigit() for c in password)):
                return password

    def accept(self):
        if self.titleEdit.text().strip():
            self.really_accept()
        else:
            QMessageBox.warning(self,
                                'Need a title.',
                                'The title cannot be blank.\n'
                                'Please input a title.')
            self.titleEdit.setFocus()

    def show_not_unique_message(self):
        QMessageBox.warning(
            self,
            'Not Unique',
            'The (title, username) pair already exists.')
        self.titleEdit.setFocus()


class AddDialog(MyDialog):
    def __init__(self, mimatemp_model, parent=None):
        super().__init__(mimatemp_model, parent)

        self.setMinimumWidth(425)
        self.setWindowTitle('Add')
        self.box = MimaBox()

        super()._init_ui_()

    def really_accept(self):
        self.box.title = self.titleEdit.text().strip()
        self.box.username = self.usernameEdit.text().strip()
        self.box.website = self.websiteEdit.text().strip()
        self.box.password = self.passwordEdit.toPlainText().strip()
        self.box.notes = self.notesEdit.toPlainText().strip()

        if self.box.is_unique():
            self.box.insert_into_database_and_temp()
            self.mimatemp_model.submitAll()
            QDialog.accept(self)
        else:
            self.show_not_unique_message()


class EditDialog(MyDialog):
    def __init__(self, box, mimatemp_model, parent=None):
        super().__init__(mimatemp_model, parent)

        self.setMinimumWidth(500)
        self.setWindowTitle('Edit')
        self.box = box

        super()._init_ui_()
        self.resetButton = self.buttonBox.addButton(
            'Reset', QDialogButtonBox.ResetRole)
        self.resetButton.clicked.connect(self.update_form)

        self.update_form()
        self._init_table_()

        if self.tableView.rowAt(0) == -1:
            self.tableView.hide()
        else:
            self.tableView.show()
            self.show_history_table()
            self.setMinimumHeight(600)

    def show_history_table(self):
        self.vBox.addSpacing(20)
        self.vBox.addWidget(self.make_hLine())
        self.vBox.addWidget(QLabel('History'))
        self.vBox.addSpacing(20)
        self.vBox.addWidget(self.tableView)

        hBox = QHBoxLayout()
        self.deleteButton = QPushButton('Delete')
        self.deleteButton.clicked.connect(self.delete_history)
        hBox.addStretch(1)
        hBox.addWidget(self.deleteButton)
        self.vBox.addLayout(hBox)

    def make_hLine(self):
        hLine = QFrame(self)
        hLine.setLineWidth(1)
        hLine.setMidLineWidth(1)
        hLine.setFrameStyle(QFrame.HLine | QFrame.Sunken)
        return hLine

    def update_form(self, box=None):
        if not box:
            box = self.box

        self.titleEdit.setText(box.title)
        self.usernameEdit.setText(box.username)
        self.websiteEdit.setText(box.website)
        self.passwordEdit.setPlainText(box.password)
        self.notesEdit.setPlainText(box.notes)

    def _init_table_(self):
        self.model = create_model('historytemp')
        self.model.setFilter(f"mimanonce = '{self.box.nonce}'")
        self.model.setSort(HISTORY_COLUMNS['deleted'], Qt.DescendingOrder)

        self.tableView = HistoryTableView(self)
        self.tableView.setModel(self.model)
        self.tableView.customize_columns()

    def really_accept(self):
        has_changed = False

        old_values = [
            self.box.title,
            self.box.username,
            self.box.website,
            self.box.password,
            self.box.notes
        ]
        new_values = [
            self.titleEdit.text().strip(),
            self.usernameEdit.text().strip(),
            self.websiteEdit.text().strip(),
            self.passwordEdit.toPlainText().strip(),
            self.notesEdit.toPlainText().strip()
        ]
        for i in range(len(old_values)):
            if old_values[i] != new_values[i]:
                has_changed = True
                break

        if not has_changed:
            QDialog.reject(self)
            return
        has_changed = False

        new_box_dict = dict(
            title=self.titleEdit.text().strip(),
            username=self.usernameEdit.text().strip(),
            website=self.websiteEdit.text().strip(),
            password=self.passwordEdit.toPlainText().strip(),
            notes=self.notesEdit.toPlainText().strip(),
            favorite=self.box.favorite
        )
        new_box = MimaBox(nonce=self.box.nonce, **new_box_dict)

        if new_box.is_unique_except_itself():
            historyBox = HistoryBox()
            historyBox.get_values_from_mimabox(self.box.nonce)
            historyBox.deleted = datetime.datetime.now().isoformat(sep=' ')
            historyBox.insert_into_database_and_temp()
            self.model.submitAll()

            new_box.update_temp()
            new_box.update_database()
            self.mimatemp_model.submitAll()

            QDialog.accept(self)
        else:
            self.show_not_unique_message()

    def delete_history(self):
        self.COLUMNS = HISTORY_COLUMNS
        self.confirm_message = "Delete the seleted record?\n" \
                               "(Can not recover)"
        pymimaconst.delete(self)

    def move_to_trash_or_delete(self, nonce):
        box = HistoryBox(nonce)
        box.delete_forever()
        self.model.submitAll()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = AddDialog()
    window.show()
    sys.exit(app.exec_())
