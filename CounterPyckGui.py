import sys
from PyQt4 import QtGui, QtCore


class CounterPyckGui(QtGui.QWidget):

    def __init__(self):
        super(CounterPyckGui, self).__init__()

        self.initUI()

    def initUI(self):

        qbtn = QtGui.QPushButton('Quit', self)
        qbtn.clicked.connect(QtCore.QCoreApplication.instance().quit)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(50, 50)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Quit button')
        self.show()

def main():

    app = QtGui.QApplication(sys.argv)
    ex = CounterPyckGui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
