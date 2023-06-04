import sys
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QApplication
from Board import Board


'''КЛАСС Основное окно игры'''
class Tetris(QMainWindow):
    def __init__(self):
        super().__init__()  # Конструктор класса
        self.initUI()  # Инициализация


    def initUI(self):
        # Инициализация
        self.tboard = Board(self)
        # Устанавливаем игровое поле в качестве центрального виджета в окне
        self.setCentralWidget(self.tboard)
        self.statusbar = self.statusBar()   # объект строки состояния
        self.tboard.msg2Statusbar[str].connect(self.statusbar.showMessage)  # связь сигнал из объекта игрового полясо слотом строки состояния
        # запуск игры
        self.tboard.start()
        self.resize(180, 380)
        self.center()
        self.setWindowTitle('Tetris')
        self.show()

    '''центрируем окно игры относительно экрана'''
    def center(self):

        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width()-size.width())/2),int((screen.height()-size.height())/2))




if __name__ == '__main__':

    app = QApplication([])
    tetris = Tetris()
    sys.exit(app.exec_())
