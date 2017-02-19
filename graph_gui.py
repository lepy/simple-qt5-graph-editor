import sys
import math
import operator

from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QAction, qApp, QSizePolicy
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QIcon


from VertexEdge import Vertex, Edge

class MainWindow(QMainWindow):

    MODE_VERTEX = 'V'
    MODE_VERTEX_DEL = 'D'
    MODE_EDGE = 'E'

    MSG_MODE_VERTEX = 'Vertex insert and move mode'
    MSG_MODE_VERTEX_DEL = 'Vertex delete mode'
    MSG_MODE_EDGE = 'Edge insert mode'
    

    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):

        self.mode = self.MODE_VERTEX
        
        exitAction = QAction(QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)

        insertVertexAction = QAction(QIcon('vertex.png'), 'Vertex', self)
        insertVertexAction.setShortcut('Ctrl+V')
        insertVertexAction.triggered.connect(self.vertexMode)

        addEdgeAction = QAction(QIcon('edge.png'), 'Edge', self)
        addEdgeAction.setShortcut('Ctrl+E')
        addEdgeAction.triggered.connect(self.edgeMode)

        deleteVertexAction = QAction(QIcon('delete.png'), 'Delete', self)
        deleteVertexAction.setShortcut('Ctrl+D')
        deleteVertexAction.triggered.connect(self.deleteMode)

        self.statusBar()
        self.statusBar().showMessage(self.MSG_MODE_VERTEX)
        
        self.toolbar = self.addToolBar('Simple graph')
        
        self.toolbar.addAction(insertVertexAction)
        self.toolbar.addAction(addEdgeAction)
        self.toolbar.addAction(deleteVertexAction)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(spacer)

        self.toolbar.addAction(exitAction)
        
        
        self.setGeometry(300, 300, 500, 500)
        self.setWindowTitle('Toolbar')    

        self.canvas = Canvas()
        self.setCentralWidget(self.canvas)

        self.show()


    def vertexMode(self):
        self.canvas.mode = self.MODE_VERTEX
        self.selected_vertex_idx = None
        self.draggin_idx = []
        self.statusBar().showMessage(self.MSG_MODE_VERTEX)


    def deleteMode(self):
        self.canvas.mode = self.MODE_VERTEX_DEL
        self.selected_vertex_idx = None
        self.draggin_idx = []
        self.statusBar().showMessage(self.MSG_MODE_VERTEX_DEL)


    def edgeMode(self):
        self.canvas.mode = self.MODE_EDGE
        self.selected_vertex_idx = None
        self.draggin_idx = []
        self.statusBar().showMessage(self.MSG_MODE_EDGE)


class Canvas(QWidget):

    POINT_RADIUS = 3
    DELTA = 3

    def __init__(self, parent=None):
        super().__init__()
        
        self.setGeometry(0,0,400,400)
        self.vertices = []
        self.edges = {}
        self.draggin_idx = []
        self.selected_vertex_idx = None
        self.mode = MainWindow.MODE_VERTEX
        self.cotrolPressed = False


    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawGraph(qp)
        qp.end()


    def drawGraph(self, qp):
        qp.setPen(Qt.black)
        qp.setBrush(Qt.black)

        for i, vertex in enumerate(self.vertices):

            qpoint = QPoint(vertex.x, vertex.y)

            if i == self.selected_vertex_idx: # TODO: decent context manager (?)
                qp.setBrush(Qt.red)
            elif i in self.draggin_idx:
                qp.setBrush(Qt.blue)

            qp.drawEllipse(qpoint, self.POINT_RADIUS*2, self.POINT_RADIUS*2)

            qp.setBrush(Qt.black)
                
        for _, edges in self.edges.items():
            for edge in edges:
                qp.drawLine(edge.v1.x, edge.v1.y, edge.v2.x, edge.v2.y)


    def _get_point(self, evt):
        return evt.pos().x(), evt.pos().y()


    def _capture_vertex(self, x, y):
        vertex = Vertex([x, y])
        distances = []
        for v in self.vertices:
            distances.append(math.sqrt(sum((i1 - i2)**2 for i1, i2 in zip(v, vertex))))
        if distances and (min(distances) < self.POINT_RADIUS + self.DELTA):
            captured_vertex_idx, _ = min(enumerate(distances), key=operator.itemgetter(1))
            return captured_vertex_idx
        return None


    def addVertex(self, x, y):
        new_vertex = Vertex([x, y])
        self.vertices.append(new_vertex)
        self.edges[id(new_vertex)] = []
        print(self.vertices)
        print(self.edges)
        return


    def deleteVertex(self, vertex_idx):
        vertex = self.vertices[vertex_idx]
        print(vertex)
        for vertex_id, edges in self.edges.items():
            for i, edge in enumerate(edges):
                print("Incoming edges:")
                print(edge)
                if edge.v2 == vertex:
                    print("Deleting {}".format(edge))
                    del edges[i]
        print("Deleting outgoing edges")
        del self.edges[id(vertex)]
        print("Deleting vertex")
        del self.vertices[vertex_idx]


    def addEdge(self, v1_idx, v2_idx, oriented=False):
        v1 = self.vertices[v1_idx]
        v2 = self.vertices[v2_idx]
        new_edge = Edge(v1, v2, oriented)
        new_edge_backwards = Edge(v2, v1, oriented)
        if not new_edge in self.edges[id(v1)] and not new_edge_backwards in self.edges[id(v2)]:
            self.edges[id(v1)].append(new_edge)
        return


    def grabVertex(self, vertex_idx):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:

            print('Control+Click')
            if vertex_idx not in self.draggin_idx:
                self.draggin_idx.append(vertex_idx)
            else:
                self.draggin_idx.remove(vertex_idx)

            self.cotrolPressed = True
            self.update()

        else:
            if self.cotrolPressed == True:
                if vertex_idx not in self.draggin_idx:
                    self.draggin_idx.append(vertex_idx)
                else:
                    self.draggin_idx.remove(vertex_idx)
                    self.draggin_idx.append(vertex_idx) # making sure the pointed vertex is the last in the indices list
                self.cotrolPressed = False
            else:
                self.draggin_idx = [vertex_idx, ]

        print("$"*50)
        print(self.draggin_idx)
        return

    def mousePressEvent(self, evt):

        if self.mode == MainWindow.MODE_VERTEX:

            if evt.button() == Qt.LeftButton:
                x, y = self._get_point(evt)
                captured_vertex_idx = self._capture_vertex(x, y)
                print(captured_vertex_idx)
                if not captured_vertex_idx is None:
                    self.grabVertex(captured_vertex_idx)
                else:                    
                    self.addVertex(x, y)
                    self.update()

        elif self.mode == MainWindow.MODE_EDGE:

            if evt.button() == Qt.LeftButton and self.draggin_idx == []:
                x, y = self._get_point(evt)
                captured_vertex_idx = self._capture_vertex(x, y)
                if not captured_vertex_idx is None:
                    if self.selected_vertex_idx is None:
                        self.selected_vertex_idx = captured_vertex_idx
                        self.update()
                    else:
                        if self.selected_vertex_idx == captured_vertex_idx: # same vertex, deselect
                            self.selected_vertex_idx = None
                            self.update()
                        else:
                            self.addEdge(self.selected_vertex_idx, captured_vertex_idx)
                            self.selected_vertex_idx = None
                            self.update()

        elif self.mode == MainWindow.MODE_VERTEX_DEL:
            if evt.button() == Qt.LeftButton and self.draggin_idx == []:
                x, y = self._get_point(evt)
                captured_vertex_idx = self._capture_vertex(x, y)

                if not captured_vertex_idx is None:

                    self.deleteVertex(captured_vertex_idx)

                self.update()


    def mouseMoveEvent(self, evt):
        if self.draggin_idx != [] and not self.cotrolPressed:

            print(self.vertices)
            print(self.edges)
            print(self.draggin_idx)

            moving_vertices = [self.vertices[i] for i in self.draggin_idx]
            last_vertex = moving_vertices[-1]

            x, y = self._get_point(evt)

            x_delta = x - last_vertex.x
            y_delta = y - last_vertex.y

            for vertex in moving_vertices:
                vertex.x += x_delta
                vertex.y += y_delta

            self.update()


    def mouseReleaseEvent(self, evt):
        if evt.button() == Qt.LeftButton and self.draggin_idx != [] and not self.cotrolPressed:

            print('*'*40)
            print(self.vertices)
            print(self.edges)
            print(self.draggin_idx)
            
            moving_vertices = [self.vertices[i] for i in self.draggin_idx]
            last_vertex = moving_vertices[-1]

            x, y = self._get_point(evt)

            x_delta = x - last_vertex.x
            y_delta = y - last_vertex.y

            for vertex in moving_vertices:
                vertex.x += x_delta
                vertex.y += y_delta

            self.draggin_idx = []
            self.update()


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())

