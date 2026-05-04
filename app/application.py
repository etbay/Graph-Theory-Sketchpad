import sys
from PySide6 import QtCore, QtWidgets, QtGui
from graph import GraphView
import traceback

class App(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.graph = GraphView()

        self.appLayout = QtWidgets.QVBoxLayout(self)
        self.appLayout.addWidget(self.graph)
        self.setLayout(self.appLayout)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = App()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())