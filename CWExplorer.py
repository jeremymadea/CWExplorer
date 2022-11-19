#!/usr/bin/env python

import sys
import json
from objregistry import ObjRegistry

from PySide6.QtWidgets import (
    QApplication, 
    QCheckBox,
    QColorDialog, 
    QComboBox,
    QDial,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QMainWindow, 
    QLabel,
    QMessageBox, 
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpacerItem,
    QStatusBar,
    QToolBar,
    QTableView,
    QVBoxLayout,
    QWidget, 
)

from PySide6.QtGui import (
    QAction, 
    QBrush, 
    QColor, 
    QFont,
    QIcon, 
    QLinearGradient,
    QPainter, 
    QPainterPath,
    QPen, 
    QPolygon,
)

from PySide6.QtCore import (
    Qt, 
    QPoint, 
    QRect,
    Signal,
    QSize, 
)

from PySide6.QtSql import (
    QSqlDatabase, 
    QSqlTableModel,
    QSqlQuery, 
    QSqlQueryModel,
)

#from GuiBones import ColorPatch
from CWWidgets import *
from colorways import *

class WorkSpace(QWidget): 
    """WorkSpace Class"""
    def __init__(self): 
        super().__init__()
        main_layout = QVBoxLayout(self)
        panel_layout = QHBoxLayout()
        self.randmix = RandMixTool()
        panel_layout.addWidget(self.randmix, 1)
        panel_layout.addWidget(PaletteSelector(), 1)
        self.palettedisplay = PaletteDisplay()
        self.randmix.paletteCreated.connect(self.palettedisplay.setPalette)
        selector = ObjRegistry.get('main-palette-selector')
        selector.paletteSelected.connect(self.palettedisplay.setPalette)
        main_layout.addLayout(panel_layout)
        main_layout.addWidget(self.palettedisplay)
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 1)
        self.setLayout(main_layout)

class MainWindow(QMainWindow):
    """Main Window class"""
    def __init__(self):
        super().__init__()
        self.connectToDB()
        self.initializeUI()

    def connectToDB(self):
        """Connect to color dstabase."""
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('color.db')
        if not db.open():
            print("Unable to open database.")
            print("Connection failed: ", database.lastError().text())
            sys.exit(1)

    def initializeUI(self):
        """Set up the application's GUI."""
        self.setMinimumSize(640, 480)
        self.setGeometry(200,200,840,400)
        self.setWindowTitle("Colorways Explorer")
        self.clrpicker = QColorDialog()
        self.clrpicker.setOption(QColorDialog.DontUseNativeDialog)
        self.clrpicker.colorSelected.connect(self.colorChosen)
        self.setUpMainWindow()
        self.createActions()
        self.createMenu()
        self.createToolBar()
        self.show()

    def setUpMainWindow(self):
        """Create and arrange widgets in the main window."""
        self.work_area = WorkSpace()
        self.work_area.setStatusTip('Work Area')
        self.setCentralWidget(self.work_area)
        self.setStatusBar(QStatusBar())

    def createActions(self):
        """Create the application's menu actions."""

        def create_act(name, shortcut=None, icon=None, **kwargs):
            if icon is not None:
                if isinstance(icon, QIcon):
                    a = QAction(icon, name, **kwargs)
                else:
                    a = QAction(QIcon(icon), name, **kwargs)
            else: 
                a = QAction(name, **kwargs)
            if shortcut is not None:
                a.setShortcut(shortcut)
            return a

        # File Menu Actions
        self.new_act = create_act('New', 'Ctrl+N', 'i/file-new.svg')
        self.open_act = create_act('Open', 'Ctrl+O', 'i/file.svg')
        self.save_act = create_act('Save', 'Ctrl+S', 'i/save.svg')
        self.saveas_act = create_act('Save As', 'Shift+Ctrl+S')
        self.quit_act = create_act('Quit', 'Ctrl+Q', 'i/exit.svg')
       
        self.quit_act.triggered.connect(self.close)

        # Edit Menu Actions
        self.undo_act = create_act('Undo', 'Ctrl+Z')
        self.redo_act = create_act('Redo', 'Shift+Ctrl+Z')
        self.cut_act = create_act('Cut', 'Ctrl+X')
        self.copy_act = create_act('Copy', 'Ctrl+C')
        self.paste_act = create_act('Paste', 'Ctrl+V')

        # Tool Menu Actions
        self.color_act = create_act('Color Picker', None, 'i/palette.svg')
        self.color_act.triggered.connect(self.chooseColor)
        self.togtb_act = create_act('Show Toolbar', checkable=True)
        self.togtb_act.setChecked(True)
        self.togtb_act.triggered.connect(self.togToolbar)
        self.cdb_act = create_act('Color DB', None, 'i/db.svg')
        
        # Help Menu Actions
        self.about_act = create_act('About')
        self.about_act.triggered.connect(self.aboutDialog)

 
    def createMenu(self):
        """Create the application's menu bar."""
        self.menuBar().setNativeMenuBar(False)

        # File menu
        file_menu = self.menuBar().addMenu('File')
        file_menu.addAction(self.new_act)
        file_menu.addAction(self.save_act)
        file_menu.addAction(self.saveas_act)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_act)

        # Edit menu
        edit_menu = self.menuBar().addMenu('Edit')
        edit_menu.addAction(self.undo_act)
        edit_menu.addAction(self.redo_act)
        edit_menu.addAction(self.cut_act)
        edit_menu.addAction(self.copy_act)
        edit_menu.addAction(self.paste_act)

        # Tool menu
        tool_menu = self.menuBar().addMenu('Tools')
        tool_menu.addAction(self.color_act)
        tool_menu.addAction(self.cdb_act)
        tool_menu.addSeparator()
        tool_menu.addAction(self.togtb_act)

        # Help menu
        help_menu = self.menuBar().addMenu('Help')
        help_menu.addAction(self.about_act)

    def createToolBar(self):
        self.tool_bar = QToolBar("Tool Bar")
        self.tool_bar.setIconSize(QSize(24,24))
        self.tool_bar.toggleViewAction().setVisible(False)
        self.addToolBar(Qt.RightToolBarArea, self.tool_bar)
        self.tool_bar.addAction(self.new_act)
        self.tool_bar.addAction(self.open_act)
        self.tool_bar.addAction(self.save_act)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.cdb_act)
        self.tool_bar.addAction(self.color_act)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.quit_act)

    def chooseColor(self):
        self.clrpicker.open()
        #color = QColorDialog().getColor()
        #if color.isValid():
        #    self.work_area.colorfg = color

    def colorChosen(self, color):
        if color.isValid():
            self.work_area.colorfg = color


    def togToolbar(self, state):
        self.tool_bar.setVisible(state)

    def aboutDialog(self):
        QMessageBox.about(self, 
            "About ColorwaysExplorer", 
            """
            <h1 style="text-align:center;">Colorways Explorer</h1>
            <p style="text-align:center;">Pre-Alpha</p>
            <p style="text-align:center; font-weight: bold;">Jeremy Madea</p>
            """) 

    def closeEvent(self, event):
        """Add confirm dialog to app quit."""
        answer = QMessageBox.question(self, "Confirm Quit",
            "Quit?",
            QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
            QMessageBox.StandardButton.Yes)
        if answer == QMessageBox.StandardButton.Yes:
            event.accept()
        if answer == QMessageBox.StandardButton.No:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, True)
    window = MainWindow()
    sys.exit(app.exec())
