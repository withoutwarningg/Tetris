import sys, random
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor


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



'''КЛАСС ИГРОВОЕ ПОЛЕ'''
class Board(QFrame):

    msg2Statusbar = pyqtSignal(str)
    # параметры игры
    BoardWidth = 10
    BoardHeight = 22
    Speed = 300

    def __init__(self, parent):
        super().__init__(parent)

        self.initBoard()


    def initBoard(self):

        self.timer = QBasicTimer() # Таймер (управление скоростью игры)
        self.isWaitingAfterLine = False

        # Координаты
        self.curX = 0
        self.curY = 0
        # Кол-во удалённых линий
        self.numLinesRemoved = 0
        # Пустое игровое поле
        self.board = []

        self.setFocusPolicy(Qt.StrongFocus)
        self.isStarted = False  # Флаг запущенной игры
        self.isPaused = False   # Пауза
        self.clearBoard()   # Очищение игрового поля

    # возвращаем тип фигурки в заданной позиции в игровом поле
    def shapeAt(self, x, y):
        return self.board[(y * Board.BoardWidth) + x]

    # устанавливаем тип фигурки в заданной позиции в игровом поле
    def setShapeAt(self, x, y, shape):
        self.board[(y * Board.BoardWidth) + x] = shape

    # возвращаем ширину квадрата
    def squareWidth(self):
        return self.contentsRect().width() // Board.BoardWidth

    # возвращаем высоту квадрата
    def squareHeight(self):
        return self.contentsRect().height() // Board.BoardHeight

    # метод запуска игры
    def start(self):
        # если игра была приостановлена, то ничего не делаем
        if self.isPaused:
            return

        self.isStarted = True  # устанавливаем флаги состояния игры
        self.isWaitingAfterLine = False
        self.numLinesRemoved = 0  # сбрасываем флаг ожидания после заполнения линии, очищаем поле
        self.clearBoard()

        self.msg2Statusbar.emit(str(self.numLinesRemoved))  # сообщение в строку состояния о количестве удаленных линий

        self.newPiece()  # создаем новую фигурку
        self.timer.start(Board.Speed, self)

    # метод пауза
    def pause(self):
        # если игра не запущена ничего не делаем
        if not self.isStarted:
            return

        self.isPaused = not self.isPaused

        if self.isPaused:
            self.timer.stop()
            self.msg2Statusbar.emit("paused")

        else:
            self.timer.start(Board.Speed, self)
            self.msg2Statusbar.emit(str(self.numLinesRemoved))

        self.update() # обновляем игровое поле

    # Отрисовываем событие на игровом поле
    def paintEvent(self, event):

        painter = QPainter(self)
        rect = self.contentsRect()  # границы игрового поля

        boardTop = rect.bottom() - Board.BoardHeight * self.squareHeight() # координата y верхней границы игрового поля

        # отрисовываем фигурки (все и текущую в частности)
        for i in range(Board.BoardHeight):
            for j in range(Board.BoardWidth):
                shape = self.shapeAt(j, Board.BoardHeight - i - 1)

                if shape != Tetrominoe.NoShape:
                    self.drawSquare(painter,rect.left() + j * self.squareWidth(), boardTop + i * self.squareHeight(), shape)

        if self.curPiece.shape() != Tetrominoe.NoShape:
            for i in range(4):
                x = self.curX + self.curPiece.x(i)
                y = self.curY - self.curPiece.y(i)
                self.drawSquare(painter, rect.left() + x * self.squareWidth(), boardTop + (Board.BoardHeight - y - 1) * self.squareHeight(),self.curPiece.shape())

    # Обработка нажатия клавиш
    def keyPressEvent(self, event):

        if not self.isStarted or self.curPiece.shape() == Tetrominoe.NoShape:
            super(Board, self).keyPressEvent(event)
            return

        key = event.key()  # получаем код нажатой клавиши

        if key == Qt.Key_P: # если клавиша P - пауза
            self.pause()
            return

        #if self.isPaused:
        #    return
        # Обрабока клавиш движения и вращения
        elif key == Qt.Key_Left:
            self.tryMove(self.curPiece, self.curX - 1, self.curY)

        elif key == Qt.Key_Right:
            self.tryMove(self.curPiece, self.curX + 1, self.curY)

        elif key == Qt.Key_Down:
            self.tryMove(self.curPiece.rotateRight(), self.curX, self.curY)

        elif key == Qt.Key_Up:
            self.tryMove(self.curPiece.rotateLeft(), self.curX, self.curY)

        elif key == Qt.Key_Space:
            self.dropDown()

        elif key == Qt.Key_D:
            self.oneLineDown()

        else:
            super(Board, self).keyPressEvent(event)

    def timerEvent(self, event):

        if event.timerId() == self.timer.timerId(): # если собыьте от таймера получено

            if self.isWaitingAfterLine:  # ожидаем ли мы новую фигурку после заполнения линии
                self.isWaitingAfterLine = False  # меняем флаг
                self.newPiece()  # создаем новую фигурку
            else:
                self.oneLineDown()  # опускаем текущую фигурку на одну строку вниз

        else:
            super(Board, self).timerEvent(event)

    # Очищаем игровое поле
    def clearBoard(self):

        for i in range(Board.BoardHeight * Board.BoardWidth):
            self.board.append(Tetrominoe.NoShape)

    # Быстрое падение фигурки вниз
    def dropDown(self):

        newY = self.curY
        while newY > 0:
            if not self.tryMove(self.curPiece, self.curX, newY - 1):
                break
            newY -= 1
        self.pieceDropped()

    # Опускание фигурки на 1 вниз
    def oneLineDown(self):

        if not self.tryMove(self.curPiece, self.curX, self.curY - 1):
            self.pieceDropped()

    # Метод, выз. когда фигурка упала для обновления поля
    def pieceDropped(self):

        for i in range(4):
            x = self.curX + self.curPiece.x(i)
            y = self.curY - self.curPiece.y(i)
            self.setShapeAt(x, y, self.curPiece.shape())

        self.removeFullLines()

        if not self.isWaitingAfterLine:
            self.newPiece()

    # Удаление заполненных полей
    def removeFullLines(self):

        numFullLines = 0  # количество заполненных полей
        rowsToRemove = []   # их индексы

        for i in range(Board.BoardHeight): # перебор по столбцам

            n = 0
            for j in range(Board.BoardWidth):  # перебор по строкам
                if not self.shapeAt(j, i) == Tetrominoe.NoShape:
                    n = n + 1

            if n == 10: # Если вся линия  заполнена
                rowsToRemove.append(i)

        # Перебираем индексы заполненных строк в обратном порядке и смещаем все ячейки выше них на одну строку вниз.
        rowsToRemove.reverse()
        for m in rowsToRemove:
            for k in range(m, Board.BoardHeight):
                for l in range(Board.BoardWidth):
                    self.setShapeAt(l, k, self.shapeAt(l, k + 1))
        # Увеличиваем количество заполненных линий на количество строк, которые удалили
        numFullLines = numFullLines + len(rowsToRemove)
        if numFullLines > 0:
            self.numLinesRemoved = self.numLinesRemoved + numFullLines  # увеличиваем количество удаленных линий на количество заполненных линий
            self.msg2Statusbar.emit(str(self.numLinesRemoved))  # выводим это число в статусную строку

            # Готовим появление следующей фигуры
            self.isWaitingAfterLine = True
            self.curPiece.setShape(Tetrominoe.NoShape)
            self.update()

    # Метод для создания новой фигуры
    def newPiece(self):

        self.curPiece = Shape()
        self.curPiece.setRandomShape()
        self.curX = Board.BoardWidth // 2 + 1
        self.curY = Board.BoardHeight - 1 + self.curPiece.minY()

        if not self.tryMove(self.curPiece, self.curX, self.curY): # если не получается разместить - игра заканчивается
            self.curPiece.setShape(Tetrominoe.NoShape)
            self.timer.stop()
            self.isStarted = False
            self.msg2Statusbar.emit("Game over")

    # Проверка возможности движения фигурки
    def tryMove(self, newPiece, newX, newY):

        for i in range(4):

            x = newX + newPiece.x(i)
            y = newY - newPiece.y(i)

            if x < 0 or x >= Board.BoardWidth or y < 0 or y >= Board.BoardHeight:  # Если выходит за границы
                return False

            if self.shapeAt(x, y) != Tetrominoe.NoShape:  # если в ячейке есть другая фигура
                return False

        self.curPiece = newPiece
        self.curX = newX
        self.curY = newY
        self.update()

        return True

    def drawSquare(self, painter, x, y, shape):

        colorTable = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
                      0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]

        color = QColor(colorTable[shape])
        painter.fillRect(x + 1, y + 1, self.squareWidth() - 2, self.squareHeight() - 2, color)

        painter.setPen(color.lighter())
        painter.drawLine(x, y + self.squareHeight() - 1, x, y)
        painter.drawLine(x, y, x + self.squareWidth() - 1, y)

        painter.setPen(color.darker())
        painter.drawLine(x + 1, y + self.squareHeight() - 1, x + self.squareWidth() - 1, y + self.squareHeight() - 1)
        painter.drawLine(x + self.squareWidth() - 1, y + self.squareHeight() - 1, x + self.squareWidth() - 1, y + 1)

'''КЛАСС ИМЕНА ВСЕХ ВОЗМОЖНЫХ ФИГУР'''
class Tetrominoe(object):

    NoShape = 0
    ZShape = 1
    SShape = 2
    LineShape = 3
    TShape = 4
    SquareShape = 5
    LShape = 6
    MirroredLShape = 7


'''КЛАСС ИНФОРМАЦИЯ О ЧАСТЯХ ТЕТРИСА'''
class Shape(object):
    # Все возможные значения координат фигурок
    coordsTable = (
        ((0, 0),     (0, 0),     (0, 0),     (0, 0)),
        ((0, -1),    (0, 0),     (-1, 0),    (-1, 1)),
        ((0, -1),    (0, 0),     (1, 0),     (1, 1)),
        ((0, -1),    (0, 0),     (0, 1),     (0, 2)),
        ((-1, 0),    (0, 0),     (1, 0),     (0, 1)),
        ((0, 0),     (1, 0),     (0, 1),     (1, 1)),
        ((-1, -1),   (0, -1),    (0, 0),     (0, 1)),
        ((1, -1),    (0, -1),    (0, 0),     (0, 1))
    )

    def __init__(self):

        self.coords = [[0,0] for i in range(4)]
        self.pieceShape = Tetrominoe.NoShape

        self.setShape(Tetrominoe.NoShape)

    # Возваращем тип фигурки
    def shape(self):
        return self.pieceShape

    # Устанавливаем тип фигурки
    def setShape(self, shape):

        table = Shape.coordsTable[shape]

        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]

        self.pieceShape = shape

    # Устанавливаем случайный тип фигуры
    def setRandomShape(self):
        self.setShape(random.randint(1, 7))

    # Возвращает координату x
    def x(self, index):
        return self.coords[index][0]

    # Возвращает координату у
    def y(self, index):
        return self.coords[index][1]

    # Устанавливает координату x
    def setX(self, index, x):
        self.coords[index][0] = x

    # Устанавливает координату у
    def setY(self, index, y):
        self.coords[index][1] = y

    # Возвращает минимальную координату X для фигуры
    def minX(self):

        m = self.coords[0][0]
        for i in range(4):
            m = min(m, self.coords[i][0])
        return m

    # Возвращает max координату X для фигуры
    def maxX(self):

        m = self.coords[0][0]
        for i in range(4):
            m = max(m, self.coords[i][0])
        return m

    # Возвращает минимальную координату У для фигуры
    def minY(self):

        m = self.coords[0][1]
        for i in range(4):
            m = min(m, self.coords[i][1])

        return m

    # Возвращает максимальную координату У для фигуры
    def maxY(self):

        m = self.coords[0][1]
        for i in range(4):
            m = max(m, self.coords[i][1])

        return m

    def rotateLeft(self):

        if self.pieceShape == Tetrominoe.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):
            result.setX(i, self.y(i))
            result.setY(i, -self.x(i))

        return result

    def rotateRight(self):

        if self.pieceShape == Tetrominoe.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):
            result.setX(i, -self.y(i))
            result.setY(i, self.x(i))

        return result



if __name__ == '__main__':

    app = QApplication([])
    tetris = Tetris()
    sys.exit(app.exec_())
