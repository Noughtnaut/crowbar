from PyQt5.QtCore import QSettings, QSize
from PyQt5.QtGui import QMoveEvent, QResizeEvent
from PyQt5.QtWidgets import *

from src.ui.UiUtils import get_child
from src.widgets.Flow import *
from src.widgets.PanedWidget import PanedWidget
from src.widgets.ToolBar import ToolBar


class WindowMain(QMainWindow):
    canvas: Flow

    def __init__(self):
        super().__init__()
        self.restoreSettings()

        self._create_menu()
        self._create_status_bar()
        self._create_content()

    def close(self):
        self.storeSettings()
        super().close()

    def resizeEvent(self, e: QResizeEvent):
        self.storeSettings()

    def moveEvent(self, e: QMoveEvent):
        self.storeSettings()

    def restoreSettings(self):
        config = QSettings()
        config.beginGroup("WindowMain")
        size = config.value("size")
        pos = config.value("pos")
        if not size:
            size = QSize(1200, 800)  # TODO Set to 80% of display (ask `sys` for dimensions)
        self.resize(size)
        if not pos:
            pos = QPoint(200, 200)
        self.move(pos)
        config.endGroup()

    def storeSettings(self):
        config = QSettings()
        config.beginGroup("WindowMain")
        config.setValue("size", self.size())
        config.setValue("pos", self.pos())
        config.endGroup()

    def _create_menu(self):
        menu_file = self.menuBar().addMenu("&File")
        menu_file.addAction('&New Flow', self._do_new_flow)
        menu_file.addAction('New &Group', self._do_new_group)
        menu_file.addSeparator()
        menu_file.addAction('&Quit', self._do_quit)

        menu_tools = self.menuBar().addMenu("&Tools")
        menu_tools.addAction('&Options', self._do_NYI)

        menu_help = self.menuBar().addMenu("&Help")
        menu_help.addAction('&User Guide', self._do_NYI)
        menu_help.addSeparator()
        menu_help.addAction('&About ' + qApp.applicationName(), self._do_show_about)
        menu_help.addAction('About &Qt', qApp.aboutQt)

    def _create_status_bar(self):
        status = QStatusBar()
        status.showMessage("/!\\ This app is a PROTOTYPE - do not use for anything serious!")
        self.setStatusBar(status)

    def _create_content(self):
        self.setCentralWidget(PanedWidget(
            self.create_pane_left(),
            self.create_pane_right(),
        ))
        splitter = get_child(self.centralWidget(), QSplitter)
        # Don't allow either pane to be shrunk to nothing
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        # Give preference to canvas pane
        splitter.setStretchFactor(1, 10)

    def create_pane_left(self):
        content = QMainWindow()

        toolbar = QToolBar()
        toolbar.addAction('New Category', self._do_new_group)
        toolbar.addAction('New Flow', self._do_new_flow)
        content.addToolBar(toolbar)

        view = QTreeView()
        content.setCentralWidget(view)

        return content

    def create_pane_right(self):
        content = QMainWindow()

        toolbar = ToolBar()
        toolbar.addAction('Run', self._do_NYI)
        toolbar.addSeparator()
        toolbar.addAction('Triggers', self._do_NYI)
        toolbar.addSeparator(True)
        toolbar.addAction('Zoom In', self._do_view_zoom_in)
        toolbar.addAction('Zoom Out', self._do_view_zoom_out)
        toolbar.addAction('Zoom Reset', self._do_view_zoom_reset)
        toolbar.addAction('Zoom to Fit', self._do_view_zoom_to_fit)
        toolbar.addSeparator(True)
        toolbar.addAction('Options', self._do_NYI)
        content.addToolBar(toolbar)

        self.canvas = Flow()
        content.setCentralWidget(self.canvas)

        point1 = QPoint(0, 0)
        point2 = QPoint(0, 100)
        point3 = QPoint(0, 200)
        box_trigger = FlowTrigger(point1)
        box_condition = FlowCondition(point2)
        box_action = FlowAction(point3)
        self.canvas.scene.addItem(box_trigger)
        self.canvas.scene.addItem(box_condition)
        self.canvas.scene.addItem(box_action)
        self._do_view_zoom_reset()
        return content

    def _do_new_flow(self):
        print("Feel the flow, man")

    def _do_new_group(self):
        print("Here's a new group for you.")

    def _do_view_zoom_in(self):
        self.canvas.view.zoom_in()
        print("Zoom in.")

    def _do_view_zoom_out(self):
        self.canvas.view.zoom_out()
        print("Zoom out.")

    def _do_view_zoom_reset(self):
        self.canvas.view.zoom_to_fit()
        self.canvas.view.zoom_reset()
        print("Back to normal.")

    def _do_view_zoom_to_fit(self):
        self.canvas.view.zoom_to_fit()
        self.canvas.view.zoom_out()
        print("Zoing, now it fits.")

    def _do_quit(self):
        self.close()

    def _do_show_about(self):
        qApp.instance().window_about.show()  # TODO Why is `instance()` required here?
        print("Ain't that shiny?")

    def _do_NYI(self):
        print("<Not yet implemented>")
        mb = QMessageBox()
        mb.setIcon(QMessageBox.Warning)
        mb.setText("Watch out for potholes!")
        mb.setInformativeText("That feature is not yet implemented.")
        mb.setWindowTitle("Prototype")
        mb.setDetailedText("It seems the developers have been preoccupied with more important things ..."
                           + " such as writing this incredibly useless dialog ...")
        mb.setStandardButtons(QMessageBox.Ignore | QMessageBox.Ok | QMessageBox.Default | QMessageBox.Retry)
        mb.exec_()
        if 'Retry' == mb.clickedButton().text():
            mb = QMessageBox()
            mb.setIcon(QMessageBox.Information)
            mb.setText("Dream on, man!")
            mb.setInformativeText("Your optimism is admirable. It won't work, though.")
            mb.setWindowTitle("Prototype")
            mb.setStandardButtons(QMessageBox.Ok)
            mb.exec_()
