from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import QFont, QTextCharFormat, QSyntaxHighlighter
from PyQt5.QtWidgets import QPlainTextEdit


class PasswordEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        # font = QFont()
        # font.setPointSize(18)
        # self.setFont(font)

        self.parent = parent
        self.highlighter = PasswordHighlighter(self.document())

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.parent.accept()
        elif event.key() == Qt.Key_Tab:
            self.parent.notesEdit.setFocus()
        else:
            super(PasswordEdit, self).keyPressEvent(event)


class PasswordHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.numberFormat = QTextCharFormat()
        self.numberFormat.setFontWeight(QFont.Bold)
        self.numberFormat.setForeground(Qt.red)

    def highlightBlock(self, text):
        regExp = QRegularExpression("[0-9]")
        matchIterator = regExp.globalMatch(text)
        while matchIterator.hasNext():
            match = matchIterator.next()
            self.setFormat(
                match.capturedStart(),
                match.capturedLength(),
                self.numberFormat)
