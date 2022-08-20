import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QColor, QPainter
from PyQt5.QtWidgets import QLabel, QApplication

class Canvas(QLabel):
    def __init__(self,height, width, background_color=QColor('#FFFFFF')):
        super().__init__()
        self.qpixmap = QPixmap(int(height), int(width))
        self.screen_height = self.qpixmap.height()
        self.screen_width = self.qpixmap.width()
        self.qpixmap.fill(background_color)
        self.setPixmap(self.qpixmap)
        self.pen_color = QColor('#000000')
        self.line_stack=[]
        self.redo_stack=[]
        self.current_move=[]
        self.background_color = background_color
        self.is_fill_clicked=False
        self.bfs_queue = []
        self.have_seen=set()
        self.pixmap_image=self.qpixmap.toImage()

    def set_pen_color(self, color):
        self.pen_color = QtGui.QColor(color)

    def draw_point(self, x, y):
        painter = QPainter(self.pixmap())
        p = painter.pen()
        p.setWidth(4)
        p.setColor(self.pen_color)
        painter.setPen(p)
        painter.drawPoint(x,y)
        self.pixmap_image.setPixelColor(x,y,self.pen_color)
        painter.end()
        self.update()

    def draw_line(self, x0, y0, x1, y1):
        painter = QPainter(self.pixmap())
        p = painter.pen()
        p.setWidth(4)
        p.setColor(self.pen_color)
        painter.setPen(p)
        painter.drawLine(x0, y0, x1, y1)
        self.pixmap_image.setPixelColor(x0,y0,self.pen_color)
        self.pixmap_image.setPixelColor(x1,y1,self.pen_color)
        painter.end()
        self.update()


    def mousePressEvent(self, e: QtGui.QMouseEvent):
        if not self.is_fill_clicked:
            self.draw_point(e.x(), e.y())
            self.prev_point = (e.x(), e.y())
            self.current_move.append((self.prev_point,self.pen_color))
        else:
            self.floodFill(e.x(),e.y(),self.pixmap().toImage().pixelColor(e.x(),e.y()))

    def mouseMoveEvent(self, e):
        if not self.is_fill_clicked:
            self.draw_line(self.prev_point[0], self.prev_point[1], e.x(), e.y())
            self.prev_point = (e.x(), e.y())
            self.current_move.append((self.prev_point,self.pen_color))

    def mouseReleaseEvent(self, e):
        self.prev_point = tuple()
        self.line_stack.append(self.current_move)
        self.current_move=[]
        self.update()

    def draw_stack_line(self):
        temp_color = self.pen_color
        self.qpixmap.fill(self.background_color)
        self.setPixmap(self.qpixmap)
        for line in self.line_stack:
            top_line = line
            for i in range(1,len(top_line)):
                self.pen_color = top_line[i][1]
                self.draw_line(top_line[i-1][0][0],top_line[i-1][0][1],top_line[i][0][0],top_line[i][0][1])
            if len(top_line)==1:
                self.draw_point(top_line[0][0][0],top_line[0][0][1])
        self.pen_color = temp_color

    def floodFill_rec(self,cx,cy,image,pre_color):
        points = []
        for item in [(3, 0), (0, 3), (-3, 0), (0, -3)]:
            xx, yy = cx + item[0], cy + item[1]
            if (xx >= 0 and xx < self.screen_width and
                yy >= 0 and yy < self.screen_height and
                (xx, yy) not in self.have_seen and
                (image.pixelColor(xx,yy))== (pre_color)):

                points.append((xx, yy))
                self.have_seen.add((xx, yy))
        return points
    def floodFill(self,x,y,pre_color):
        image = self.pixmap().toImage()
        self.bfs_queue.append((x, y))
        while self.bfs_queue:
            x, y = self.bfs_queue.pop()
            self.draw_point(x, y)
            self.bfs_queue[0:0] = self.floodFill_rec(x, y,image,pre_color)

        self.update()
        
    def undo(self):
        if len(self.line_stack):
            self.redo_stack.append(self.line_stack.pop())
            self.draw_stack_line()
           
    def redo(self):
        if len(self.redo_stack):
            self.line_stack.append(self.redo_stack.pop())
            self.draw_stack_line()  

    def fill_clicked(self):
        self.is_fill_clicked = not self.is_fill_clicked


class PaletteButton(QtWidgets.QPushButton):

    def __init__(self, color):
        super().__init__()
        self.setFixedSize(QtCore.QSize(32, 32))
        self.color = color
        self.setStyleSheet("background-color: %s;" % color + "border-radius : 15; ")


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.colors = [
            '#000002', '#868687', '#900124', '#ed2832', '#2db153', '#13a5e7', '#4951cf',
            '#fdb0ce', '#fdca0f', '#eee3ab', '#9fdde8', '#7a96c2', '#cbc2ec', '#a42f3b',
            '#f45b7a', '#c24998', '#81588d', '#bcb0c2', '#dbcfc2',
        ]
        app = QApplication.instance()
        screen = app.primaryScreen()
        geometry = screen.availableGeometry()
        self.canvas = Canvas(geometry.width()*0.60, geometry.height()*0.7)
        w = QtWidgets.QWidget()
        w.setStyleSheet("background-color: #313234")
        l = QtWidgets.QVBoxLayout()  # vertical layout
        w.setLayout(l)
        l.addWidget(self.canvas)
        undo_btn = QtWidgets.QPushButton()
        undo_btn.setMaximumWidth(200)
        undo_btn.setText("Undo")
        undo_btn.setStyleSheet("background-color: #FFFFFF;")
        undo_btn.clicked.connect(self.canvas.undo)
        redo_btn = QtWidgets.QPushButton()
        redo_btn.setMaximumWidth(200)
        redo_btn.setText("Redo")
        redo_btn.setStyleSheet("background-color: #FFFFFF;")
        fill_btn = QtWidgets.QPushButton()
        fill_btn.setMaximumWidth(200)
        fill_btn.setText("Fill")
        fill_btn.setStyleSheet("background-color: #FFFFFF;")
        fill_btn.clicked.connect(self.canvas.fill_clicked)
        palette = QtWidgets.QHBoxLayout()  # horizontal layout
        palette.addWidget(undo_btn) # button
        palette.addWidget(redo_btn) # button
        palette.addWidget(fill_btn) # button
        l.addLayout(palette)
        redo_btn.clicked.connect(self.canvas.redo)
        self.quitSc =QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Z'), self)
        self.quitSc.activated.connect(self.canvas.undo)
        self.quitSc =QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Y'), self)
        self.quitSc.activated.connect(self.canvas.redo)
        palette = QtWidgets.QHBoxLayout()  # horizontal layout
        self.add_palette_button(palette)
        l.addLayout(palette)

        self.setCentralWidget(w)


    def add_palette_button(self, palette):
        for c in self.colors:
            item = PaletteButton(c)
            item.pressed.connect(self.set_canvas_color)
            palette.addWidget(item)

    def set_canvas_color(self):
        sender = self.sender()
        self.canvas.set_pen_color(sender.color)


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
window.show()
app.exec_()

# Window dimensions
