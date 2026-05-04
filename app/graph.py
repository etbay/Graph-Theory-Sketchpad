from PySide6 import QtCore, QtWidgets, QtGui
from vertex import Vertex
from edge import Edge
from enum import Enum

class GraphView(QtWidgets.QGraphicsView):

    class GraphState(Enum):

        IDLE = 0
        MOVING_VERTEX = 1
        PANNING = 2
        ADDING_EDGE = 3


    def __init__(self):

        super().__init__()
        self.vertices = []
        self.edges = []
        self.mousePos = QtCore.QPointF(0, 0)
        self.state = self.GraphState.IDLE

        #region MOVING_VERTEX
        self.selectedVertex: Vertex = None
        #endregion

        #region PANNING
        self.previousPoint = QtCore.QPointF(0, 0)
        #endregion

        #region ADDING_EDGE
        self.newEdge: Edge = None
        self.hoveredVertex: Vertex = None
        #endregion

        self.setScene(QtWidgets.QGraphicsScene())
        self.show()
        self.setSceneRect(0, 0, 10, 10)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.ViewportUpdateMode.FullViewportUpdate)


    def mousePressEvent(self, event: QtGui.QMouseEvent):

        if self.state == self.GraphState.IDLE:

            # process mouse event elsewhere
            super().mousePressEvent(event)

            item = self.itemAt(event.position().toPoint())

            # if we don't hit a vertex or edge, process input
            if item is None:

                if event.button() == QtCore.Qt.MouseButton.LeftButton:
                    
                    if event.modifiers() & QtCore.Qt.KeyboardModifier.AltModifier:

                        return
                    
                    self.add_vertex(event.position())
                    print(f"created vertex")

                elif event.button() == QtCore.Qt.MouseButton.RightButton:

                    # begin panning handled in mouseMoveEvent
                    QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
                    self.previousPoint = event.position()
                    self.state = self.GraphState.PANNING


#region MousePress Util

    def add_vertex(self, pos: QtCore.QPointF):

        # convert global pos to scene pos
        point = self.mapToScene(pos.toPoint())
        vertex = Vertex(point)

        # subscribe to events for vertex moving and edge connecting
        vertex.drag_started.connect(self.on_vertex_drag_start)
        vertex.drag_ended.connect(self.on_vertex_drag_end)
        vertex.deleted.connect(self.on_vertex_delete)

        # add vertices to graph and scene
        self.vertices.append(vertex)
        self.scene().addItem(vertex)

#endregion


    def mouseMoveEvent(self, event: QtGui.QMouseEvent):

        super().mouseMoveEvent(event)

        point = self.mapToScene(event.position().toPoint())

        if self.state == self.GraphState.MOVING_VERTEX and self.selectedVertex != None:

            self.selectedVertex.move_to(point)

        elif self.state == self.GraphState.PANNING:

            self.pan_screen(event.position())
        
        elif self.state == self.GraphState.ADDING_EDGE:

            # detect if a vertex is hovered while adding an edge
            items = self.scene().items(point)
            hovered = False

            for item in items:

                if isinstance(item, Vertex):
                    
                    hovered = True
                    self.hoveredVertex = item
            
            if not hovered:

                self.hoveredVertex = None

            # update edge drawing
            if self.newEdge is not None:

                self.newEdge.set_end(point)
            
        self.mousePos = event.pos()


#region MouseMove Util

    def pan_screen(self, pos: QtCore.QPointF):

        delta = self.previousPoint - pos
        transform = self.transform()

        # calculate movement relative to current scale
        deltaX = delta.x() / transform.m11()
        deltaY = delta.y() / transform.m22()

        self.setSceneRect(self.sceneRect().translated(deltaX, deltaY))

        self.previousPoint = pos

#endregion

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):

        super().mouseReleaseEvent(event)

        if self.state == self.GraphState.PANNING and event.button() == QtCore.Qt.MouseButton.RightButton:

            print("resetting to idle")
            self.state = self.GraphState.IDLE
            QtWidgets.QApplication.restoreOverrideCursor()


    def wheelEvent(self, event: QtGui.QWheelEvent):

        if (event.angleDelta().y() > 0):

            self.scale(1.1, 1.1)

        elif (event.angleDelta().y() < 0):

            self.scale(0.9, 0.9)


#region SUBSCRIPTIONS

    # Defines behavior while holding a mouse button on a vertex
    def on_vertex_drag_start(self, obj: QtWidgets.QGraphicsObject, event: QtWidgets.QGraphicsSceneMouseEvent):

        print("started dragging vertex")
        self.selectedVertex = obj

        if event.button() == QtCore.Qt.MouseButton.RightButton:

            print("started moving vertex")
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
            self.state = self.GraphState.MOVING_VERTEX

        elif event.button() == QtCore.Qt.MouseButton.LeftButton:

            print("started creating edge")

            end = self.mapToScene(self.mousePos)
            self.newEdge = Edge(obj, end)
            self.scene().addItem(self.newEdge)
            self.state = self.GraphState.ADDING_EDGE
    

    # Defines reset behavior after vertex is released
    def on_vertex_drag_end(self, obj: QtWidgets.QGraphicsObject, event: QtWidgets.QGraphicsSceneMouseEvent):

        print("ended dragging vertex")
        self.selectedVertex = None

        if self.state == self.GraphState.MOVING_VERTEX and event.button() == QtCore.Qt.MouseButton.RightButton:

            self.state = self.GraphState.IDLE
            QtWidgets.QApplication.restoreOverrideCursor()

        if self.state == self.GraphState.ADDING_EDGE and event.button() == QtCore.Qt.MouseButton.LeftButton:

            self.state = self.GraphState.IDLE
            print("done adding edge")

            if self.hoveredVertex is None:

                print("deleting edge")
                self.scene().removeItem(self.newEdge)
                self.newEdge = None

            else:

                self.newEdge.deleted.connect(self.on_edge_delete)
                self.newEdge.set_v2(self.hoveredVertex)
                self.edges.append(self.newEdge)
                self.newEdge = None


    def on_vertex_delete(self, vertex: QtWidgets.QGraphicsObject):

        print("deleted vertex")
        self.vertices.remove(vertex)
        self.scene().removeItem(vertex)


    def on_edge_delete(self, edge: QtWidgets.QGraphicsObject):

        print("deleted edge")
        self.edges.remove(edge)
        self.scene().removeItem(edge)

#endregion