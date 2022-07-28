from PyQt5 import QtCore, QtWidgets
import parseData

stylesheet = """
    QWidget {
        background-color: black;
    }

    QLabel[accessibleName='title'] {
        color: white;
        font-size: 15px;
        font: Sans Serif Collection;
        font-weight: bold;
        border: 1px solid white;
        padding-left: 6;
        padding-right: 6;
    }

    QLabel[accessibleName='data'] {
        color: white;
        font-size: 60px;
        font-weight: bold;
        padding-bottom: 0;
        margin-top: 7px;
    }

    QLabel[accessibleName='data_label'] {
        color: white;
        font-size: 15px;
    }
"""


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.resize(800, 600)
        self.setStyleSheet(stylesheet)

        self.title = QtWidgets.QLabel("ALL TIME TOTALS")
        self.title.setAccessibleName("title")

        self.plays = QtWidgets.QLabel()
        self.plays.setAccessibleName('data')

        self.hours = QtWidgets.QLabel()
        self.hours.setAccessibleName('data')

        self.collected = QtWidgets.QLabel()
        self.collected.setAccessibleName('data')

        self.ratings = QtWidgets.QLabel()
        self.ratings.setAccessibleName('data')

        self.comments = QtWidgets.QLabel()
        self.comments.setAccessibleName('data')

        self.lists = QtWidgets.QLabel()
        self.lists.setAccessibleName('data')

        self.plays_label = QtWidgets.QLabel("✔PLAYS")
        self.hours_label = QtWidgets.QLabel("⏲HOURS")
        self.collected_label = QtWidgets.QLabel("📑COLLECTED")
        self.ratings_label = QtWidgets.QLabel("❤RATINGS")
        self.comments_label = QtWidgets.QLabel("✍COMMENTS")
        self.lists_label = QtWidgets.QLabel("📄LISTS")

        self.plays_label.setAccessibleName('data_label')
        self.hours_label.setAccessibleName('data_label')
        self.collected_label.setAccessibleName('data_label')
        self.ratings_label.setAccessibleName('data_label')
        self.comments_label.setAccessibleName('data_label')
        self.lists_label.setAccessibleName('data_label')

        spacer_top = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        spacer_bottom = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(30, 0, 0, 0)
        self.gridLayout.setVerticalSpacing(0)

        self.gridLayout.addWidget(self.title, 0, 1, 1, 1, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.gridLayout.addItem(spacer_top, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.plays, 2, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.gridLayout.addWidget(self.hours, 2, 1, 1, 1, QtCore.Qt.AlignHCenter)
        self.gridLayout.addWidget(self.collected, 2, 2, 1, 1, QtCore.Qt.AlignHCenter)
        self.gridLayout.addWidget(self.plays_label, 3, 0, 1, 1, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.gridLayout.addWidget(self.hours_label, 3, 1, 1, 1, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.gridLayout.addWidget(self.collected_label, 3, 2, 1, 1, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.gridLayout.addWidget(self.ratings, 4, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.gridLayout.addWidget(self.comments, 4, 1, 1, 1, QtCore.Qt.AlignHCenter)
        self.gridLayout.addWidget(self.lists, 4, 2, 1, 1, QtCore.Qt.AlignHCenter)
        self.gridLayout.addWidget(self.ratings_label, 5, 0, 1, 1, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.gridLayout.addWidget(self.comments_label, 5, 1, 1, 1, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.gridLayout.addWidget(self.lists_label, 5, 2, 1, 1, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.gridLayout.addItem(spacer_bottom, 6, 1, 1, 1)

        self.setLayout(self.gridLayout)
        self.layout().setAlignment(QtCore.Qt.AlignBaseline | QtCore.Qt.AlignBaseline)
        self.setData()

    def setData(self):
        data = parseData.get_all_time_totals()

        self.plays.setText(data.plays)
        self.hours.setText(data.hours)
        self.collected.setText(data.collected)
        self.ratings.setText(data.number_of_ratings)
        self.comments.setText(data.comments)
        self.lists.setText(data.lists)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
