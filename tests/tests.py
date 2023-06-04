import sys
sys.path.append("/home/youngpasha/project/tetris/app/Board")
import pytest
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QKeyEvent
from .Board import Board
from .Shape import Tetrominoe, Shape
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal, QTimerEvent

class TestTetris:
    def setup_method(self):
        # Создаем экземпляр класса Board с главным окном в качестве родительского элемента
        self.app = QApplication([])
        self.main_window = QMainWindow()
        self.board = Board(self.main_window)

    def teardown_method(self):
        # Завершаем работу приложения
        self.app.quit()

    def test_setShapeAt(self):
        # Устанавливаем фигуру в координаты (3, 4)
        self.board.setShapeAt(3, 4, Tetrominoe.LineShape)

        # Проверяем, что в этой клетке находится фигурка LineShape
        assert self.board.shapeAt(3, 4) == Tetrominoe.LineShape

        # Проверяем, что в других клетках находится NoShape
        assert self.board.shapeAt(2, 4) == Tetrominoe.NoShape
        assert self.board.shapeAt(3, 5) == Tetrominoe.NoShape

    def test_pause(self):
        # Запускаем игру
        self.board.start()

        # Приостанавливаем игру и проверяем, что она приостановлена
        self.board.pause()
        assert self.board.isPaused == True

        # Запускаем игру снова и проверяем, что она продолжается
        self.board.pause()
        assert self.board.isPaused == False

    # def test_dropDown(self):
    #     # Запускаем игру
    #     self.board.start()
    #
    #     # Сохраняем начальное положение текущей фигурки
    #     startX = self.board.curX
    #     startY = self.board.curY
    #
    #     # Вызываем метод dropDown и проверяем, что текущая фигурка переместилась вниз
    #     self.board.dropDown()
    #     assert self.board.curX == startX
    #     assert self.board.curY == 1

    def test_pieceDropped(self):
        # Запускаем игру
        self.board.start()

        # Сохраняем начальное положение текущей фигурки
        startX = self.board.curX
        startY = self.board.curY

        # Получаем текущую фигурку и ее координаты
        curPiece = self.board.curPiece
        curX = self.board.curX
        curY = self.board.curY

        # Вызываем метод pieceDropped
        self.board.pieceDropped()

        # Проверяем, что клетки, занимаемые текущей фигурой, заполнены в игровом поле
        for i in range(4):
            x = curX + curPiece.x(i)
            y = curY - curPiece.y(i)
            assert self.board.shapeAt(x, y) == curPiece.shape()

    # def test_removeFullLines(self):
    #     # Запускаем игру
    #     self.board.start()
    #
    #     # Заполняем несколько линий в игровом поле
    #     for i in range(5):
    #         for j in range(Board.BoardWidth):
    #             self.board.setShapeAt(j, i, Tetrominoe.LineShape)
    #
    #     # Вызываем метод removeFullLines
    #     self.board.removeFullLines()
    #
    #     # Проверяем, что все заполненные линии удалены, а не заполненные остались на месте
    #     for i in range(5):
    #         for j in range(Board.BoardWidth):
    #             assert self.board.shapeAt(j, i) == Tetrominoe.NoShape
    #     for i in range(5, Board.BoardHeight):
    #         for j in range(Board.BoardWidth):
    #             assert self.board.shapeAt(j, i) == Tetrominoe.LineShape

    def test_timerEvent(self):
        # Запускаем игру
        self.board.start()

        # Запускаем таймер
        self.board.startTimer(self.board.Speed)

        # Сохраняем начальную позицию текущей фигурки
        startCurY = self.board.curY

        # Вызываем метод timerEvent события таймера
        event = QTimerEvent(self.board.timer.timerId())
        self.board.timerEvent(event)

        # Проверяем, что текущая фигура была опущена на одну строку вниз
        assert self.board.curY == startCurY - 1

    def test_dropDown(self):
        # Запускаем игру
        self.board.start()

        # Выбираем текущую фигуру
        self.board.curPiece.setShape(Tetrominoe.TShape)
        self.board.curX = self.board.BoardWidth // 2
        self.board.curY = self.board.BoardHeight - 1

        # Сохраняем начальную позицию текущей фигуры
        startCurY = self.board.curY

        # Вызываем метод dropDown
        self.board.dropDown()

        # Проверяем, что текущая фигура была опущена на максимально возможную позицию
        assert startCurY == 21 or not self.board.tryMove(self.board.curPiece, self.board.curX, self.board.curY + 1)

    def test_newPiece(self):
        # Запускаем игру
        self.board.start()

        # Вызываем метод newPiece
        self.board.newPiece()

        # Проверяем, что текущая фигура была случайно выбрана
        assert self.board.curPiece.shape() != Tetrominoe.NoShape

        # Проверяем, что начальные координаты текущей фигуры находятся в правильной позиции
        assert self.board.curX == self.board.BoardWidth // 2 + 1
        assert self.board.curY == self.board.BoardHeight - 1 + self.board.curPiece.minY()

    def test_newPiece_game_over(self):
        # Запускаем игру
        self.board.start()
        # Делаем невозможным появление фигурки
        for i in range(10):
            # Выбираем текущую фигуру и устанавливаем ее начальную позицию так, чтобы она не могла быть размещена на игровом поле
            self.board.curPiece.setShape(Tetrominoe.SquareShape)
            self.board.curX = self.board.BoardWidth // 2
            self.board.curY = self.board.BoardHeight - 1

            # Сохраняем начальную позицию текущей фигуры
            startCurY = self.board.curY

            # Вызываем метод dropDown
            self.board.dropDown()

        # Проверяем, что текущая фигура была сброшена
        assert self.board.curPiece.shape() == Tetrominoe.NoShape

        # Проверяем, что игра была завершена
        assert not self.board.isStarted


class TestShape:
    def test_rotateLeft(self):
        # Создаем экземпляр класса Shape и устанавливаем тип фигуры
        shape = Shape()
        shape.setShape(Tetrominoe.LShape)

        # Сохраняем начальные координаты фигуры
        startCoords = [(shape.x(i), shape.y(i)) for i in range(4)]

        # Вызываем метод rotateLeft
        shape.rotateLeft()

        # Проверяем, что координаты фигуры изменились в соответствии с ожидаемыми значениями после поворота
        assert shape.x(0) == startCoords[0][0]
        assert shape.y(0) == startCoords[0][1]
        assert shape.x(1) == startCoords[3][0]
        assert shape.y(1) == -startCoords[3][1]
        assert shape.x(2) == startCoords[2][0]
        assert shape.y(2) == -startCoords[2][1]
        assert shape.x(3) == startCoords[3][0]
        assert shape.y(3) == -startCoords[0][1]

    def test_rotateRight(self):
        # Создаем экземпляр класса Shape и устанавливаем тип фигуры
        shape = Shape()
        shape.setShape(Tetrominoe.LShape)

        # Сохраняем начальные координаты фигуры
        startCoords = [(shape.x(i), shape.y(i)) for i in range(4)]

        # Вызываем метод rotateRight
        shape.rotateRight()

        # Проверяем, что координаты фигуры изменились в соответствии с ожидаемыми значениями после поворота
        assert shape.x(0) == startCoords[0][0]
        assert shape.y(0) == startCoords[1][1]
        assert shape.x(1) == startCoords[3][0]
        assert shape.y(1) == startCoords[3][0]
        assert shape.x(2) == startCoords[2][0]
        assert shape.y(2) == startCoords[2][1]
        assert shape.x(3) == startCoords[1][0]
        assert shape.y(3) == startCoords[0][1]


if __name__ == '__name__':
    pytest.main()