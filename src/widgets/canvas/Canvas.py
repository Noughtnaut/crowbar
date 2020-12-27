import enum
import typing
from typing import Any

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QLineF, QPointF, QRect, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QCursor, QMouseEvent, QPainter, QPen, QPolygonF, QStaticText, \
    QWheelEvent
from PyQt5.QtWidgets import QFrame, QGraphicsItem, QGraphicsPolygonItem, QGraphicsRectItem, QGraphicsScene, \
    QGraphicsView, QGridLayout, QStyleOptionGraphicsItem, QWidget

from ui.UiUtils import click_descriptor, with_control_key

_DEFAULT_SIZE_W = 80
_DEFAULT_SIZE_H = 80


class Socket(enum.Enum):
    """ This defines, in an abstract fashion, where on a Component a Wire is attached.
        Calling `Component.socketPoint(s: Socket)` will return the concrete point, in scene coordinates.
    """
    NONE = 0
    TOP = 1
    BOTTOM = 2
    LEFT = 4
    RIGHT = 8


class Mode(enum.Enum):
    """ This defines the usage and appearance of a Wire:
        - NORMAL: This is the default exit path after completing the Component operation.
        - TRUE: Applicable to Conditions, yields the exit path if the condition was TRUE.
        - FALSE: Applicable to Conditions, yields the exit path if the condition was FALSE.
        - ERROR: In case the Component operation caused an error, *only* paths of this mode will be followed.
        Note:
        - IF not specified, NORMAL is assumed.
        - Components may have any number of exit paths of any types. Duplicate mode paths will fork the flow process,
          while a Component with no exit paths will end the flow process.
    """
    NORMAL = 0
    TRUE = 1
    FALSE = 2
    ERROR = 4


class Component(QGraphicsRectItem):
    _title: str

    def __init__(self, pos: QPointF = None, title: str = None, *__args):
        r = QRectF(
            pos.x() - _DEFAULT_SIZE_W / 2,
            pos.y() - _DEFAULT_SIZE_H / 2,
            _DEFAULT_SIZE_W,
            _DEFAULT_SIZE_H
        )
        super().__init__(r)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
        self.setVisible(True)
        self._title = title
        pen_component_edge = QPen()
        pen_component_edge.setWidth(2)
        pen_component_edge.setJoinStyle(Qt.RoundJoin)
        pen_component_edge.setCosmetic(True)
        pen_component_edge.setColor(QColor(192, 192, 192))
        brush_component_fill = QBrush()
        brush_component_fill.setColor(QColor(0, 0, 64))
        brush_component_fill.setStyle(Qt.SolidPattern)
        self.setPen(pen_component_edge)
        self.setBrush(brush_component_fill)

    # TODO Make Component deletable -- unless it's a Trigger

    def pos(self):
        return self.rect().center()  # TODO: Fully implement centre-based locations

    def width(self):
        return self.rect().width()

    def height(self):
        return self.rect().height()

    def title(self):
        return self._title

    def setTitle(self, title: str):
        self._title = '' if title is None else title
        return self

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, new_pos: Any) -> Any:
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            scene_rect = self.scene().sceneRect()
            # Keep the item inside the scene rect
            if not scene_rect.contains(new_pos):
                new_pos.setX(min(scene_rect.right(), max(new_pos.x(), scene_rect.left())))
                new_pos.setY(min(scene_rect.bottom(), max(new_pos.y(), scene_rect.top())))
            # Snap item to grid
            grid_snap_increment = self.scene().grid_snap_increment()
            x = round(new_pos.x() / grid_snap_increment) * grid_snap_increment
            y = round(new_pos.y() / grid_snap_increment) * grid_snap_increment
            return QPointF(x, y)
        else:
            return QGraphicsItem.itemChange(self, change, new_pos)

    def paint(self, painter: QtGui.QPainter, option: QStyleOptionGraphicsItem,
              widget: typing.Optional[QWidget] = ...) -> None:
        painter.setRenderHint(QPainter.Antialiasing)
        self.paintShape(painter)
        self.paintTitle(painter)

    def paintShape(self, painter: QPainter):
        r = self.boundingRect()
        painter.drawRect(r)
        painter.drawLine(r.topLeft(), r.bottomRight())
        painter.drawLine(r.bottomLeft(), r.topRight())
        raise Exception('Override the paintShape() method in your subclass')

    def paintTitle(self, painter: QPainter):
        text = QStaticText(self.title())
        text.setTextWidth(20)
        half_size = QPointF(
            text.size().width() / 2,
            text.size().height() / 2
        )
        painter.drawStaticText(self.pos() - half_size, text)
        # FIXME Use drawText() instead of drawStaticText() to have multi-line text centered

    def socketPoint(self, side: Socket):
        if side == Socket.TOP:
            return QPointF(self.pos().x(), self.rect().top())
        if side == Socket.BOTTOM:
            return QPointF(self.pos().x(), self.rect().bottom())
        if side == Socket.LEFT:
            return QPointF(self.rect().left(), self.pos().y())
        if side == Socket.RIGHT:
            return QPointF(self.rect().right(), self.pos().y())


class Wire(QGraphicsPolygonItem):
    _mode: Mode
    _title: str

    _color = {
        Mode.NORMAL: QColor(192, 192, 192),  # white
        Mode.TRUE: QColor(0, 192, 0),  # green
        Mode.FALSE: QColor(192, 0, 0),  # red
        Mode.ERROR: QColor(192, 192, 0),  # yellow
    }

    def __init__(self,
                 from_component: Component, from_socket: Socket,
                 to_component: Component, to_socket: Socket,
                 mode: Mode = Mode.NORMAL,
                 title: str = None):
        super().__init__()
        pen = QPen()
        pen.setWidth(2)
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setCapStyle(Qt.RoundCap)
        pen.setCosmetic(True)
        self.setPen(pen)
        self.autoRoute(from_component, from_socket, to_component, to_socket)
        self.setMode(mode)
        self.setTitle(title)

    def autoRoute(self,
                  from_component: Component, from_socket: Socket,
                  to_component: Component, to_socket: Socket):
        new_path = QPolygonF()
        new_path.append(from_component.socketPoint(from_socket))
        # TODO Write label near source socket
        # TODO Create I-, L-, or Z-shaped path, depending on socket directions
        # TODO When routing, take into account other components, wires, labels, etc.
        new_path.append(to_component.socketPoint(to_socket))
        # TODO Add an arrow head
        self.setPolygon(new_path)

    def mode(self):
        return self._mode

    def setMode(self, mode):
        self._mode = mode
        p = self.pen()
        p.setColor(self._color[self.mode()])
        self.setPen(p)

    def title(self):
        return self._title

    def setTitle(self, title: str):
        self._title = '' if title is None else title
        return self

    def paint(self, painter: QtGui.QPainter, option: QStyleOptionGraphicsItem,
              widget: typing.Optional[QWidget] = ...) -> None:
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(self.pen())
        painter.drawPolyline(self.polygon())
        # FIXME Paint wires *behind* components


class CanvasScene(QGraphicsScene):
    _grid_line_increment = 20
    _grid_snap_increment = 10

    def __init__(self):
        super().__init__()
        self.setSceneRect(-5000, -500, 10000, 10000)  # TODO This should be set outside of Canvas
        self._prepare_background_grid()

    def grid_snap_increment(self):
        return self._grid_snap_increment

    def grid_minor(self):
        return self._grid_line_increment

    def grid_medium(self):
        return self.grid_minor() * 5

    def grid_major(self):
        return self.grid_medium() * 5

    def _prepare_background_grid(self):
        self._brush_background = QBrush(QColor(0, 24, 0))

        self._pen_grid_minor = QPen()
        self._pen_grid_minor.setWidth(1)
        self._pen_grid_minor.setCosmetic(True)
        self._pen_grid_minor.setColor(QColor(0, 40, 0))

        self._pen_grid_medium = QPen()
        self._pen_grid_medium.setWidth(2)
        self._pen_grid_medium.setCosmetic(True)
        self._pen_grid_medium.setColor(QColor(0, 48, 0))

        self._pen_grid_major = QPen()
        self._pen_grid_major.setWidth(3)
        self._pen_grid_major.setCosmetic(True)
        self._pen_grid_major.setColor(QColor(0, 56, 0))

        self._pen_grid_axis = QPen()
        self._pen_grid_axis.setWidth(3)
        self._pen_grid_axis.setCosmetic(True)
        self._pen_grid_axis.setColor(QColor(0, 80, 0))

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        super().drawBackground(painter, rect)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate necessary grid with a bit of overshoot
        # - this avoids edge glitches of background fill
        # - this ensures all necessary grid lines are included
        r = QRect(
            rect.left() - self.grid_minor() - rect.left() % self.grid_minor(),
            rect.top() - self.grid_minor() - rect.top() % self.grid_minor(),
            rect.width() + 2 * (self.grid_minor() + rect.width() % self.grid_minor()),
            rect.height() + 2 * (self.grid_minor() + rect.height() % self.grid_minor())
        )

        # Fill the background
        painter.setBrush(self._brush_background)
        painter.drawRect(r)

        # Calculate necessary grid lines and sort them into bins
        lines_minor = []
        lines_medium = []
        lines_major = []
        lines_axis = []
        for x in range(r.left(), r.right(), self.grid_minor()):
            line = QLineF(x, r.top(), x, r.bottom())
            if not x % self.grid_major():
                lines_major.append(line)
            elif not x % self.grid_medium():
                lines_medium.append(line)
            else:
                lines_minor.append(line)
        for y in range(r.top(), r.bottom(), self.grid_minor()):
            line = QLineF(r.left(), y, r.right(), y)
            if not y % self.grid_major():
                lines_major.append(line)
            elif not y % self.grid_medium():
                lines_medium.append(line)
            else:
                lines_minor.append(line)
        # Axis lines are simpler
        lines_axis.append(QLineF(0, r.top(), 0, r.bottom()))
        lines_axis.append(QLineF(r.left(), 0, r.right(), 0))
        # Draw in order from minor to axis, so bright lines aren't chopped up by darker ones
        pens_and_lines = [
            (self._pen_grid_minor, lines_minor),
            (self._pen_grid_medium, lines_medium),
            (self._pen_grid_major, lines_major),
            (self._pen_grid_axis, lines_axis)
        ]
        # TODO Might it be faster to pre-calculate all of the above (even if lines need to be longer)?
        for (pen, lines) in pens_and_lines:
            painter.setPen(pen)
            for line in lines:
                painter.drawLine(line)


class CanvasView(QGraphicsView):
    _zoom = 1.0
    _zoom_factor = 1.25
    _zoom_min = 0.125
    _zoom_max = 8

    def __init__(self, scene: CanvasScene, parent: QWidget):
        super().__init__(scene, parent)
        self.setFrameStyle(QFrame.Panel)
        self.setMouseTracking(True)
        self._cursor_normal = QCursor(Qt.ArrowCursor)
        self._cursor_crosshair = QCursor(Qt.CrossCursor)
        self._cursor_closed_hand = QCursor(Qt.ClosedHandCursor)
        self.setCursor(self._cursor_normal)

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        print(click_descriptor(event, 'drag¤'))
        super().dragMoveEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        # print(click_descriptor(event, 'move'))
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        print(click_descriptor(event, 'click'))
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseDoubleClickEvent(event)
        print(click_descriptor(event, 'double-click'))

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        print(click_descriptor(event, 'release'))
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        # print(click_descriptor(event, 'scroll'))
        # Zoom on Ctrl-scroll
        if with_control_key(event) and event.angleDelta().y():
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        else:
            super().wheelEvent(event)

    def zoom_out(self):
        factor = 1 / self._zoom_factor
        self.zoom_by_factor(factor)

    def zoom_in(self):
        factor = self._zoom_factor
        self.zoom_by_factor(factor)

    def zoom_by_factor(self, factor):
        new_zoom = self._zoom * factor
        if self._zoom_min < new_zoom < self._zoom_max:
            self.scale(factor, factor)
            self._zoom = self.transform().m11()  # m11 and m22 are the applied x and y scaling factors
        # TODO Keep the point at the cursor position in place while zooming (when possible)

    def zoom_reset(self):
        # Note: This works, but does nothing to bring the contents into view
        self.scale(1 / self._zoom, 1 / self._zoom)
        self._zoom = self.transform().m11()

    def zoom_to_fit(self):
        self.fitInView(self.scene().itemsBoundingRect(), Qt.KeepAspectRatio)
        self._zoom = self.transform().m11()


class Canvas(QWidget):
    _scene: CanvasScene
    _view: CanvasView

    def __init__(self):
        super().__init__()
        self._scene = CanvasScene()
        self._view = CanvasView(self._scene, self)
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view())
        self.setLayout(layout)

    def scene(self):
        return self._scene

    def view(self):
        return self._view
