from PyQt5.QtCore import QPoint, QSettings, QSize
from PyQt5.QtGui import QMoveEvent, QResizeEvent
from PyQt5.QtWidgets import *

from src.ui.UiUtils import get_child
from src.widgets.PanedWidget import PanedWidget
from src.widgets.ToolBar import ToolBar
from widgets.canvas.core.Canvas import Canvas


class WindowMain(QMainWindow):
    _canvas: Canvas = None

    def __init__(self):
        super().__init__()
        self.restoreSettings()
        self._create_menu()
        self._create_status_bar()
        self._create_content()

    def closeEvent(self, event):
        self.storeSettings()
        super().closeEvent(event)
        qApp.instance().do_quit_cleanup()

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
        menu_file.addAction('New &Group …', self._do_new_group)
        menu_file.addSeparator()
        menu_file.addAction('&Quit', self._do_quit)

        menu_tools = self.menuBar().addMenu("&Tools")
        menu_tools.addAction('&Options …', self._do_NYI)

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
        toolbar.addAction('Triggers …', self._do_NYI)
        toolbar.addSeparator(True)
        toolbar.addAction('Zoom In', self._do_view_zoom_in)
        toolbar.addAction('Zoom Out', self._do_view_zoom_out)
        toolbar.addAction('Zoom Reset', self._do_view_zoom_reset)
        toolbar.addAction('Zoom to Fit', self._do_view_zoom_to_fit)
        toolbar.addSeparator(True)
        toolbar.addAction('Options …', self._do_NYI)
        content.addToolBar(toolbar)

        self.setCanvas(Canvas())
        content.setCentralWidget(self.canvas())
        scene = self.canvas().scene()

        self._do_view_zoom_reset()
        self._do_view_zoom_out()  # TODO Remove this when autorouting works
        self._do_view_zoom_out()
        self._do_view_zoom_out()
        # self._do_view_zoom_to_fit()  # This zooms WAY out ... why? The scene HAS items by now.
        return content

    def canvas(self):
        return self._canvas

    def setCanvas(self, canvas: Canvas):
        self._canvas = canvas
        return self

    def _do_new_flow(self):
        print("Feel the flow, man")

    def _do_new_group(self):
        print("Here's a new group for you.")

    def _do_view_zoom_in(self):
        self.canvas().view().zoom_in()

    def _do_view_zoom_out(self):
        self.canvas().view().zoom_out()

    def _do_view_zoom_reset(self):
        self.canvas().view().zoom_to_fit()
        self.canvas().view().zoom_reset()

    def _do_view_zoom_to_fit(self):
        self.canvas().view().zoom_to_fit()
        self.canvas().view().zoom_out()

    def _do_quit(self):
        self.close()

    def _do_show_about(self):
        qApp.instance().window_about().show()

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
