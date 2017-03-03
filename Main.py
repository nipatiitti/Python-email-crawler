import re, subprocess, os
from PyQt5 import QtGui, QtWidgets
from UIBase import Ui_MainWindow
from MultiThread import GetThread

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow): #Tuodaan QUI Filen class tähän classiin
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)      # Alustetaan GUI
        self.setWindowIcon(QtGui.QIcon('spiderLogo.png'))
        self.filePath = "Libs\mails.txt"  # Filepath
        self.submit.clicked.connect(self.main)      # Yhdistetään napit oikeisiin slotteihin
        self.open.clicked.connect(self.fileOpen)        #^
        self.clear.clicked.connect(self.clearList)      # Vielä viimeinen

    def main(self):
        self.GetThread = GetThread(self.StartUrl.text(), self.Number.value())   # Haetaan tarvittavat tiedot ja alustetaan
        self.submit.setEnabled(False)    # Estetään käyttäjää aloittamasta kahta threadia peräkkäin
        self.GetThread.start()      # Aloitetaan Thread
        self.GetThread.addNewLine.connect(self.addLine)  # Yhdistetään signaali slottiin
        self.GetThread.progres.connect(self.progress)   # -""-
        self.GetThread.finished.connect(self.activate)  # -""-

    def closeEvent(self, event):    # Ylikirjoitetaan default exit functio omalla sovelluksella
                                    # Joka kysyy halutaanko poistua
        quit_msg = "Are you sure you want to exit the program?"
        reply = QtWidgets.QMessageBox.question(self, 'Message',
                                               quit_msg, QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def activate(self):
        self.submit.setEnabled(True)  # Aktivoidaan submit nappula threadin loputtua

    def fileOpen(self):     # Avataan mails.txt tiedosto default teksti ediorissa
        if sys.platform.startswith('darwin'):      # Darwin pohjaiset
            subprocess.call(('open', self.filePath))
        elif os.name == 'nt':       # Windows
            os.startfile(self.filePath)
        elif os.name == 'posix':    #Linux pohjaiset
            subprocess.call(('xdg-open', self.filePath))

    def clearList(self):        # Luodaan functio jossa tyhjennetään lista
        self.listWidget.clear()     # Tyhjennetään lista

    def addLine(self, string):      # Alustetaan addLine funktio, jota emit signal kutsuu
        item = QtWidgets.QListWidgetItem(string)    # Muutetaan string list itemiksi
        self.listWidget.addItem(item)    # Lisätään item listaan
        if self.autoScroll.isChecked():
            self.listWidget.scrollToBottom()

    def progress(self, number):
        self.progressBar.setValue(number)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
