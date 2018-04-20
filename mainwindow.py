from PyQt5.QtWidgets import QMainWindow, QWidget, QTabWidget, QVBoxLayout
import connection
from mytabwidget import HomeTab, RecycleBinTab, AutoCloseTab, AboutTab
from mimabox import MimaBox


class MimaWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet(
            'QWidget {font-size: 18px; font-family: Serif;}'
            # 'QLabel {font-size: 18px; font-family: Serif;}'
            # 'QPushButton {font-size: 18px; font-family: Serif;}'
            # 'QLineEdit {font-size: 18px; font-family: Serif;}'
            # 'QPlainTextEdit {font-size: 18px; font-family: Serif;}'
            'QTableView {font-size: 16px; font-family: Serif;}'
        )

        self._init_ui_()

    def _init_ui_(self):
        self.setWindowTitle('Mima (PyQt5)')
        homeTab_homeTableView_width = 80+150+200+200+100
        margin = 60
        self.setGeometry(
            200,
            200,
            homeTab_homeTableView_width + margin,
            600
        )

        # Central Widget
        centralWidget = QWidget()
        vbox = QVBoxLayout()
        tabWidget = QTabWidget()
        vbox.addWidget(tabWidget)
        centralWidget.setLayout(vbox)
        self.setCentralWidget(centralWidget)

        self.homeTab = HomeTab(tabWidget)
        tabWidget.addTab(self.homeTab, 'Home')

        self.recycleBinTab = RecycleBinTab()
        tabWidget.addTab(self.recycleBinTab, 'Recycle Bin')

        self.homeTab.set_recyclebin_model(self.recycleBinTab.model)
        self.recycleBinTab.set_hometable_model(self.homeTab.model)

        autoCloseTab = AutoCloseTab(tabWidget)
        tabWidget.addTab(autoCloseTab, 'Auto Close')
        self.homeTab.set_autoclose_tab(autoCloseTab)

        aboutTab = AboutTab()
        tabWidget.addTab(aboutTab, 'About')

        self.show()
        secretbox = connection.login(self, cancelToQuit=True)
        if secretbox:
            MimaBox.secretbox = secretbox
            connection.populate_temp_tables()
            self.homeTab.model.submitAll()
            self.recycleBinTab.model.submitAll()
            autoCloseTab.start_timer()
            self.homeTab.searchEdit.setFocus()


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    if not connection.create_connection():
        sys.exit(1)
    # connection.populate_temp_table()

    window = MimaWindow()
    # window.show()
    sys.exit(app.exec_())
