import sys
from PySide6 import QtCore, QtWidgets, QtGui
from vertex import Vertex

class Edge(QtWidgets.QGraphicsObject):

    deleted = QtCore.Signal(QtWidgets.QGraphicsObject)

    def __init__(self, v1: Vertex, end: QtCore.QPointF):

        super().__init__()
        self.v1 = v1
        self.v1.moved.connect(self.set_start)
        self.v1.deleted.connect(self.delete)
        self.v2: Vertex = None
        self.start = self.v1.pos()
        self.end = end

        self.setZValue(-1)
        self.setAcceptHoverEvents(True)
    

#region Initialization

    def boundingRect(self):

        return QtCore.QRectF(self.start, self.end).normalized().adjusted(-2, -2, 2, 2)


    def shape(self):

        path = QtGui.QPainterPath()
        path.moveTo(self.start)
        path.lineTo(self.end)

        stroker = QtGui.QPainterPathStroker()
        stroker.setWidth(2)
        return stroker.createStroke(path)


    def paint(self, painter, option, /, widget = ...):

        dx = self.end.x() - self.start.x()
        dy = self.end.y() - self.start.y()
        length = (dx**2 + dy**2) ** 0.5

        if length == 0:
            return
        
        offsetStart = QtCore.QPointF(
            self.start.x() + (dx / length) * Vertex.RADIUS,
            self.start.y() + (dy / length) * Vertex.RADIUS
        )

        if self.v2 is None:
            painter.drawLine(offsetStart, self.end)

        else:
            offsetEnd = QtCore.QPointF(
                self.end.x() - (dx / length) * Vertex.RADIUS,
                self.end.y() - (dy / length) * Vertex.RADIUS
            )

            painter.drawLine(offsetStart, offsetEnd)

#endregion


#region Event Handlers

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):

        print("edge pressed")    
        if event.modifiers() & QtCore.Qt.KeyboardModifier.AltModifier:

            self.deleted.emit(self)
            QtWidgets.QApplication.restoreOverrideCursor()


    def hoverEnterEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent):

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.PointingHandCursor)
    

    def hoverLeaveEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent):

        QtWidgets.QApplication.restoreOverrideCursor()

#endregion


    def set_start(self, pos: QtCore.QPointF):

        self.prepareGeometryChange()
        self.start = pos
        self.update()

    def set_end(self, pos: QtCore.QPointF):

        self.prepareGeometryChange()
        self.end = pos
        self.update()

    
    def set_v2(self, v2: Vertex):

        self.v2 = v2
        self.v2.moved.connect(self.set_end)
        self.v2.deleted.connect(self.delete)
        self.set_end(v2.pos())
    
    def delete(self, vertex: QtWidgets.QGraphicsObject):
        
        self.deleted.emit(self)