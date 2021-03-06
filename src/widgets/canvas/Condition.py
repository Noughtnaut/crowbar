from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPainter, QPainterPath, QPolygonF

from widgets.canvas.core.Component import Component


class Condition(Component):
    """ In a task (flow) that requires several steps to complete, each step is a Component.
        A Condition contains some user-defined script snippet that will result in a True/False decision. If the
        decision is True, the Condition will create a flow process for only those Wires connected to it that are of
        mode True. Similarly, if the decision is False, the Condition will create a flow process for only those Wires
        connected to it that are of mode False.
    """
    _polygon: QPolygonF
    _shape: QPainterPath

    def __init__(self, *__args):
        super().__init__(*__args)
        self.initShape()

    def initShape(self):
        self._polygon = QPolygonF()
        # Calculate by axis
        top = QPoint(self.pos().x(), self.pos().y() - self.height() / 2)
        bot = QPoint(self.pos().x(), self.pos().y() + self.height() / 2)
        lef = QPoint(self.pos().x() - self.width() / 2, self.pos().y())
        rig = QPoint(self.pos().x() + self.width() / 2, self.pos().y())
        # Add points by clockwise order
        self._polygon.append(top)
        self._polygon.append(rig)
        self._polygon.append(bot)
        self._polygon.append(lef)
        self._shape = QPainterPath()
        self._shape.addPolygon(self._polygon)

    def shape(self) -> QPainterPath:
        # This defines the outline when it comes to resolving click targets
        return self._shape

    def paintShape(self, painter: QPainter):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawConvexPolygon(self._polygon)
