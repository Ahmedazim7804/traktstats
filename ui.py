import sys
import crew_page
import cast_page
import movies_page
import tvshow_page
import all_time_totals_page
from PyQt5 import QtWidgets


basic_stylesheet = '''
    QWidget{
        background-color: transparent;
    }

    QPushButton#nav_button {
        background-color: transparent;
        font-size: 60px;
        color: #2A2929;
    }

    QPushButton#nav_button:hover {
        color: white;
    }
'''


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget)
        self.setStyleSheet(basic_stylesheet)

        self.stackedWidget = QtWidgets.QStackedWidget()
        self.stackedWidget.layout().addWidget(all_time_totals_page.MainWindow())
        self.stackedWidget.layout().addWidget(tvshow_page.MainWindow())
        self.stackedWidget.layout().addWidget(movies_page.MainWindow())
        self.stackedWidget.layout().addWidget(cast_page.MainWindow())
        self.stackedWidget.layout().addWidget(crew_page.MainWindow())

        self.next_bt = QtWidgets.QPushButton(">")
        self.next_bt.setObjectName("nav_button")
        self.next_bt.clicked.connect(self.next_page)

        self.previous_bt = QtWidgets.QPushButton("<")
        self.previous_bt.setObjectName("nav_button")
        self.previous_bt.clicked.connect(self.previous_page)

        self.widget.setLayout(QtWidgets.QHBoxLayout())
        self.widget.layout().setSpacing(0)
        self.widget.layout().addWidget(self.previous_bt)
        self.widget.layout().addWidget(self.stackedWidget)
        self.widget.layout().addWidget(self.next_bt)

    def next_page(self):
        current_page = self.stackedWidget.currentIndex()

        if current_page == 4:
            self.stackedWidget.setCurrentIndex(0)
        else:
            self.stackedWidget.setCurrentIndex(current_page+1)

    def previous_page(self):
        current_page = self.stackedWidget.currentIndex()

        if current_page == 0:
            self.stackedWidget.setCurrentIndex(4)
        else:
            self.stackedWidget.setCurrentIndex(current_page-1)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
