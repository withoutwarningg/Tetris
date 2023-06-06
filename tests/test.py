import sys
sys.path.append('/home/youngpasha/project/tetris/app')
from app.Board import Board
from app.Shape import Shape, Tetrominoe

import pytest
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimerEvent



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
        # Устанавливаем квадратик в координаты (3, 4)
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

    def test_dropDown(self):
        # Запускаем игру
        self.board.start()

        self.curPiece = Shape()
        self.curPiece.setShape(5)
        self.curX = Board.BoardWidth // 2 + 1
        self.curY = Board.BoardHeight - 1 + self.curPiece.minY()
        # Сохраняем начальное положение текущей фигурки
        startX = self.board.curX

        # Вызываем метод dropDown и проверяем, что текущая фигурка переместилась вниз
        self.board.dropDown()
        assert self.board.curX == startX
        assert self.board.curY == 21


    def test_removeFullLines_oneline(self):
        # Запускаем игру
        self.board.start()

        # Заполняем 1 линию в игровом поле
        for i in range(10):
            self.board.setShapeAt(i, 21, Tetrominoe.LineShape)

        # Вызываем метод removeFullLines
        self.board.removeFullLines()

        # Проверяем, что все заполненные линии удалены, а не заполненные остались на месте
        for i in range(10):
            assert self.board.shapeAt(i, 21) == Tetrominoe.NoShape
        assert self.board.numLinesRemoved == 1


    def test_removeFullLines_2lines(self):
        # Запускаем игру
        self.board.start()

        # Заполняем 2 линии в игровом поле
        for i in range(10):
            for j in range(20,22):
                self.board.setShapeAt(i, j, Tetrominoe.LineShape)

        # Вызываем метод removeFullLines
        self.board.removeFullLines()

        # Проверяем, что все заполненные линии удалены, а не заполненные остались на месте
        for i in range(10):
            for j in range(20, 22):
                assert self.board.shapeAt(i, j) == Tetrominoe.NoShape
        assert self.board.numLinesRemoved == 2


    def test_removeFullLines_noline(self):
        # Запускаем игру
        self.board.start()

        # Вызываем метод removeFullLines
        self.board.removeFullLines()

        # Проверяем, что ни одна линия не удалена
        assert self.board.numLinesRemoved == 0

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

    def test_tryMove_success(self):
        self.board.start()

        # Выбираем текущую фигуру
        self.board.curPiece.setShape(Tetrominoe.TShape)
        self.board.curX = self.board.BoardWidth // 2
        self.board.curY = self.board.BoardHeight - 1

        # сдвигаем фигуру на 1 по сторонам
        assert True == self.board.tryMove(self.board.curPiece, self.board.curX - 1, self.board.curY)
        assert True == self.board.tryMove(self.board.curPiece, self.board.curX + 1, self.board.curY)
        assert True == self.board.tryMove(self.board.curPiece, self.board.curX, self.board.curY - 1)

    def test_tryMove_outOfBounds(self):
        self.board.start()

        # Выбираем текущую фигуру
        self.board.curPiece.setShape(Tetrominoe.TShape)
        self.board.curX = 0
        self.board.curY = 0

        # сдвигаем фигуру на 1 влево
        assert self.board.tryMove(self.board.curPiece, self.board.curX - 1, self.board.curY) == False
        # сдвигаем фигуру на 11 влево
        assert self.board.tryMove(self.board.curPiece, self.board.curX + 11, self.board.curY) == False

    def test_tryMove_othFigs(self):

        self.board.start()

        # Выбираем текущую фигуру
        self.board.curPiece.setShape(Tetrominoe.TShape)
        self.board.curX = 0
        self.board.curY = 0

        self.board.setShapeAt(1, 0, Tetrominoe.LineShape)

        # сдвигаем фигуру на 1 вправо
        assert self.board.tryMove(self.board.curPiece, self.board.curX + 1, self.board.curY) == False


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
        for i in range(11):
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


    def test_rotate_right(self):
        shape = Shape()
        shape.setShape(Tetrominoe.ZShape)
        shape.setX(0, 1)
        shape.setY(0, 1)
        shape.setX(1, 1)
        shape.setY(1, 2)
        shape.setX(2, 2)
        shape.setY(2, 2)
        shape.setX(3, 2)
        shape.setY(3, 3)

        rotated_shape = shape.rotateRight()

        assert rotated_shape.x(0) == -1
        assert rotated_shape.y(0) == 1
        assert rotated_shape.x(1) == -2
        assert rotated_shape.y(1) == 1
        assert rotated_shape.x(2) == -2
        assert rotated_shape.y(2) == 2
        assert rotated_shape.x(3) == -3
        assert rotated_shape.y(3) == 2


if __name__ == '__name__':
    pytest.main()