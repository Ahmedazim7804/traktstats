from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class MplCanvas(FigureCanvas):
    def __init__(self, figure):
        self.fig = figure
        FigureCanvas.__init__(self, figure=self.fig)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        FigureCanvas.updateGeometry(self)
        #self.fig.tight_layout()


class MplWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

    def setupUi(self, figure):
        canvas = MplCanvas(figure)
        vbl = QtWidgets.QVBoxLayout()
        vbl.addWidget(canvas)
        self.setLayout(vbl)