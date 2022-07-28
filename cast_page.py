import parseData
from PyQt5 import QtCore, QtGui, QtWidgets
from PIL import Image, ImageDraw, ImageOps


stylesheet = """
    QWidget {
        background-color: black;
    }

    QScrollBar:horizontal
    {
        height: 15px;
        margin: 3px 15px 3px 15px;
        border: 1px transparent #2A2929;
        border-radius: 4px;
        background-color: #2A2929;
    }

    QScrollBar::handle:horizontal
    {
        background-color: gray;
        min-width: 5px;
        border-radius: 4px;
    }

    QScrollBar::add-line:horizontal
    {
        margin: 0px 3px 0px 3px;
        border-image: url(:/qss_icons/rc/right_arrow_disabled.png);
        width: 10px;
        height: 10px;
        subcontrol-position: right;
        subcontrol-origin: margin;
    }

    QScrollBar::sub-line:horizontal
    {
        margin: 0px 3px 0px 3px;
        border-image: url(:/qss_icons/rc/left_arrow_disabled.png);
        height: 10px;
        width: 10px;
        subcontrol-position: left;
        subcontrol-origin: margin;
    }

    QScrollBar::add-line:horizontal:hover,QScrollBar::add-line:horizontal:on
    {
        border-image: url(:/qss_icons/rc/right_arrow.png);
        height: 10px;
        width: 10px;
        subcontrol-position: right;
        subcontrol-origin: margin;
    }


    QScrollBar::sub-line:horizontal:hover, QScrollBar::sub-line:horizontal:on
    {
        border-image: url(:/qss_icons/rc/left_arrow.png);
        height: 10px;
        width: 10px;
        subcontrol-position: left;
        subcontrol-origin: margin;
    }

    QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal
    {
        background: none;
    }


    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal
    {
        background: none;
    }

    QScrollBar:vertical
    {
        background-color: #2A2929;
        width: 15px;
        margin: 15px 3px 15px 3px;
        border: 1px transparent #2A2929;
        border-radius: 4px;
    }

    QScrollBar::handle:vertical
    {
        background-color: gray;
        min-height: 5px;
        border-radius: 4px;
    }

    QScrollBar::sub-line:vertical
    {
        margin: 3px 0px 3px 0px;
        border-image: url(:/qss_icons/rc/up_arrow_disabled.png);
        height: 10px;
        width: 10px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }

    QScrollBar::add-line:vertical
    {
        margin: 3px 0px 3px 0px;
        border-image: url(:/qss_icons/rc/down_arrow_disabled.png);
        height: 10px;
        width: 10px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }

    QScrollBar::sub-line:vertical:hover,QScrollBar::sub-line:vertical:on
    {
        border-image: url(:/qss_icons/rc/up_arrow.png);
        height: 10px;
        width: 10px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }

    QScrollBar::add-line:vertical:hover, QScrollBar::add-line:vertical:on
    {
        border-image: url(:/qss_icons/rc/down_arrow.png);
        height: 10px;
        width: 10px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }

    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical
    {
        background: none;
    }

    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical
    {
        background: none;
    }
"""


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.actresses, self.actors, self.nb = parseData.most_watched_cast()

        self.setLayout(QtWidgets.QVBoxLayout())
        self.setStyleSheet(stylesheet)

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
        self.scrollWidget = QtWidgets.QWidget()
        self.scrollWidget.setLayout(QtWidgets.QVBoxLayout())

        actorsUi = Ui('ACTORS', self.actors)
        actressesUi = Ui('ACTRESSES', self.actresses)
        nbUi = Ui('NON-BINARY', self.nb)

        self.scrollWidget.layout().addWidget(actorsUi)
        self.scrollWidget.layout().addWidget(actressesUi)

        self.scrollArea.setWidget(self.scrollWidget)
        self.layout().addWidget(self.scrollArea)


class Ui(QtWidgets.QWidget):
    def __init__(self, titlename, actors):
        super(Ui, self).__init__()
        QtGui.QFontDatabase.addApplicationFont("resources\\ProximaNova-Reg.ttf")
        QtGui.QFontDatabase.addApplicationFont("resources\\Roboto-Medium.ttf")

        self.titlename = titlename
        self.actors = actors

        #self.resize(539, 433)
        self.setStyleSheet("""
            QWidget {
                background-color: black;
            }
                
            QLabel[accessibleName='title'] {
                color: white;
                font-size: 15px;
                font: Sans Serif Collection;
                font-weight: bold;
                border: 1px solid white;
                margin-bottom: 15px;
            }

            QPushButton {
                color: #B2B2B2;
            }
            
            QPushButton:hover {
                color: white;
            }
""")

        self.setLayout(QtWidgets.QVBoxLayout())

        self.label = QtWidgets.QLabel()
        self.label.setAccessibleName('title')
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)

        self.gridWidget = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gridWidget.sizePolicy().hasHeightForWidth())
        self.gridWidget.setSizePolicy(sizePolicy)
        self.gridWidget.setLayout(QtWidgets.QGridLayout())
        self.gridWidget.layout().setSpacing(0)

        self.previous_bt = QtWidgets.QPushButton()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.previous_bt.sizePolicy().hasHeightForWidth())
        self.previous_bt.setSizePolicy(sizePolicy)
        self.previous_bt.setObjectName("previous")

        self.next_bt = QtWidgets.QPushButton()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.next_bt.sizePolicy().hasHeightForWidth())
        self.next_bt.setSizePolicy(sizePolicy)

        self.cast_widget = CastWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cast_widget.sizePolicy().hasHeightForWidth())
        self.cast_widget.setSizePolicy(sizePolicy)

        self.retranslateUi()

        self.gridWidget.layout().addWidget(self.previous_bt, 0, 0, 1, 1, alignment=QtCore.Qt.AlignHCenter)
        self.gridWidget.layout().addWidget(self.cast_widget, 1, 0, 1, 1)
        self.gridWidget.layout().addWidget(self.next_bt, 2, 0, 1, 1, alignment=QtCore.Qt.AlignHCenter)

        self.layout().addWidget(self.label, alignment=QtCore.Qt.AlignHCenter)
        self.layout().addWidget(self.gridWidget)

        self.setupLogic()

    def setupLogic(self):
        self.page_number = -1

        self.next_bt.clicked.connect(self.next_page)
        self.previous_bt.clicked.connect(self.previous_page)

        self.next_page()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "Form"))
        self.label.setAccessibleName(_translate("Form", "title"))
        self.label.setText(_translate("Form", "MOST WATCHED ACTORS"))
        self.next_bt.setText(_translate("Form", "🡇     SEE MORE     🡇"))
        self.previous_bt.setText(_translate("Form", "🡅     PREVIOUS     🡅"))

    def next_page(self):
        self.page_number += 1
        actors = self.actors[self.page_number * 10: (self.page_number + 1) * 10]

        next_page_actors = self.actors[(self.page_number+1) * 10: (self.page_number + 2) * 10]
        if not next_page_actors:
            self.next_bt.setDisabled(True)
        if not self.previous_bt.isEnabled():
            self.previous_bt.setEnabled(True)

        page = CastPage(actors, startIndex=self.page_number * 10)

        self.cast_widget.addWidget(page)
        self.cast_widget.setCurrentIndex(self.page_number)

    def previous_page(self):
        self.page_number -= 1
        actors = self.actors[self.page_number * 10: (self.page_number + 1) * 10]

        previous_page_actors = self.actors[(self.page_number - 1) * 10: self.page_number * 10]
        if not previous_page_actors:
            self.previous_bt.setDisabled(True)
        if not self.next_bt.isEnabled():
            self.next_bt.setEnabled(True)

        page = CastPage(actors, startIndex=self.page_number * 10)

        self.cast_widget.addWidget(page)
        self.cast_widget.setCurrentIndex(self.page_number)


class CastWidget(QtWidgets.QStackedWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.page_number = -1
        self.setLayout(QtWidgets.QGridLayout())


class CastPage(QtWidgets.QWidget):
    def __init__(self, actors, startIndex=0, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.setLayout(QtWidgets.QGridLayout())

        count = 0
        startIndex += 1
        for id, actor in actors:
            item = CastItem(actor, startIndex)

            row = count // 5
            column = count % 5

            self.layout().addWidget(item, row, column)

            count += 1
            startIndex += 1


class CastItem(QtWidgets.QWidget):
    def __init__(self, actor, index, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.setStyleSheet("""QToolTip { 
                           background-color: black; 
                           color: white; 
                           border: black solid 1px;
                           font: 8pt Roboto;
                           }""")

        self.name = QtWidgets.QLabel(actor['name'].title())
        self.name.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self.name.setStyleSheet('color: white; font: 11pt "Proxima Nova";')

        self.image_path = actor['image']

        self.movies = actor.get('movies', {})
        self.shows = actor.get('shows', {})

        self.index_lbl = QtWidgets.QLabel(str(index))
        self.index_lbl.setStyleSheet('color: white; font-weight: bold;')
        self.index_lbl.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        self.setLayout(QtWidgets.QGridLayout())

        self.image = QtWidgets.QLabel()
        self.image.setPixmap(roundImage(image_path=self.image_path))
        self.image.setContentsMargins(0, 0, 0, 16)

        self.layout().addWidget(self.index_lbl, 0, 0)
        self.layout().addWidget(self.image, 0, 1, 1, 1)
        self.layout().addWidget(self.name, 1, 1)


        movies_names = []
        show_names = []
        for movie in self.movies.values():
            title, year = movie.values()
            movies_names.append(f"{title} - {year}")
        for show in self.shows.values():
            title, episode = show.values()
            if episode != 1:
                show_names.append(f"{title} - {episode} episodes")
            else:
                show_names.append(f"{title} - {episode} episode")

        self.movie_tv_names = '\n'.join([*movies_names, *show_names])

        self.image.setToolTip(self.movie_tv_names)

        txt = ""
        if movies_names:
            txt = f"{len(self.movies)} MOVIES\n"
        if show_names:
            if movies_names:
                txt = txt + f"{len(self.shows)} SHOWS"
            else:
                txt = txt + f"{len(self.shows)} SHOWS\n"

        total_lbl = QtWidgets.QLabel()
        total_lbl.setStyleSheet('color: #B2B2B2; font: 8pt Roboto;')
        total_lbl.setText(txt)
        total_lbl.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)

        self.layout().addWidget(total_lbl, 2, 1)




def roundImage(image_path):
    im = Image.open(image_path)
    bigsize = (164 * 2, 164 * 2)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)

    if not hasattr(Image, 'Resampling'):  # Pillow<9.0
        Image.Resampling.LANCZOS = Image.ANTIALIAS

    mask = mask.resize((164, 164), Image.Resampling.LANCZOS)
    output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)

    image = pil2pixmap(output)
    return image


def pil2pixmap(im):

    if im.mode == "RGB":
        r, g, b = im.split()
        im = Image.merge("RGB", (b, g, r))
    elif im.mode == "RGBA":
        r, g, b, a = im.split()
        im = Image.merge("RGBA", (b, g, r, a))
    elif im.mode == "L":
        im = im.convert("RGBA")

    # Convert image to RGBA if not already done
    im2 = im.convert("RGBA")
    data = im2.tobytes("raw", "RGBA")
    qim = QtGui.QImage(data, im.size[0], im.size[1], QtGui.QImage.Format_ARGB32)
    pixmap = QtGui.QPixmap.fromImage(qim)
    return pixmap


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
