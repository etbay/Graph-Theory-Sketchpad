import sys
from PySide6 import QtCore, QtWidgets, QtGui

class Vertex(QtWidgets.QGraphicsObject):

    RADIUS = 10
    OFFSET = 0

    drag_started = QtCore.Signal(QtWidgets.QGraphicsObject, QtWidgets.QGraphicsSceneMouseEvent)
    drag_ended = QtCore.Signal(QtWidgets.QGraphicsObject, QtWidgets.QGraphicsSceneMouseEvent)

    moved = QtCore.Signal(QtCore.QPointF)

    deleted = QtCore.Signal(QtWidgets.QGraphicsObject)

    def __init__(self, pos: QtCore.QPointF):

        super().__init__()
        self.position = pos

        self.setPos(self.position)
        self.setAcceptHoverEvents(True)
    

#region Initialization

    # defines the boundary for paint and shape elements
    def boundingRect(self):

        return QtCore.QRectF(-self.RADIUS - self.OFFSET, -self.RADIUS - self.OFFSET, (self.RADIUS + self.OFFSET) * 2, (self.RADIUS + self.OFFSET) * 2)
    

    # defines the collision and hit detection within the boundingRect
    def shape(self):

        path = QtGui.QPainterPath()
        path.addEllipse(-self.RADIUS - self.OFFSET, -self.RADIUS - self.OFFSET, (self.RADIUS + self.OFFSET) * 2, (self.RADIUS + self.OFFSET) * 2)
        return path


    def paint(self, painter, option, /, widget = ...):

        painter.drawEllipse(-self.RADIUS, -self.RADIUS, self.RADIUS * 2, self.RADIUS * 2)

#endregion


#region Event Handlers

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):

        event.accept()
        print("vertex pressed")
        if event.modifiers() & QtCore.Qt.KeyboardModifier.AltModifier:

            self.delete()

        else:

            self.drag_started.emit(self, event)
    

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):

        event.accept()
        print("vertex released")
        self.drag_ended.emit(self, event)


    def hoverEnterEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent):

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.PointingHandCursor)
    

    def hoverLeaveEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent):

        QtWidgets.QApplication.restoreOverrideCursor()

#endregion

    def move_to(self, pos: QtCore.QPointF):

        self.position = pos
        self.setPos(self.position)
        self.moved.emit(self.position)
    
    def delete(self):

        QtWidgets.QApplication.restoreOverrideCursor()
        self.deleted.emit(self)