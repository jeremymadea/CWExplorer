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

from GuiBones import ColorPatch

from colorways import *

class PaletteDisplay(QWidget):
    """PaletteDisplay Class"""
    def __init__(self):
        super().__init__()
        self.colorfg = QColor('#000000')
        self.palette = [[0,0,0], [0, 0,.5], [0,0,1]]
        self.painter = QPainter()
        self.nopen = QPen()
        self.nopen.setStyle(Qt.NoPen)
    
    def setPalette(self, pal):
        self.palette = pal
        self.repaint()

    def paintEvent(self, event):
        self.drawPalette()
        self.painter.begin(self)
        self.painter.setPen(QPen(QColor('#000000')))
        self.painter.end()

    def drawPalette(self, w=None, h=None):
        self.painter.begin(self)
        if w is None:
            w = self.width()
        if h is None:
            h = self.height()
        width = w
        height = h
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        self.painter.setPen(self.nopen)
        n = len(self.palette)
        p = self.palette
        
        if n>0 and isinstance(p[0], list): 
            p = hsl2hex(p)
        for i, s in enumerate(p): 
            brush.setColor(QColor(s))
            self.painter.setBrush(brush)
            self.painter.drawRect(i*width//n, 0, width//n+1, height)
        self.painter.end()


class PaletteSelector(QWidget): 
    paletteSelected = Signal(list)
    def __init__(self):
        super().__init__()
        self.pal = [[0,1,.5], [.333,1,.5], [.666,1,.5]]
        self.initData()
        self.initGui()
        ObjRegistry.add('main-palette-selector', self)

    def initData(self):
        self.pack_mdl = QSqlQueryModel()
        self.pack_mdl.setQuery('''
            SELECT DISTINCT pack 
              FROM palettes ORDER BY pack;''')
        self.pal_mdl = QSqlQueryModel()
        self.pal_mdl.setQuery(f"""
            SELECT pack,name,json 
              FROM palettes 
             WHERE pack='nfl' ORDER BY name ASC;""")
        

    def initGui(self):
        #self.setFrameStyle(QFrame.Plain | QFrame.Raised)
        #self.setLineWidth(2)
        self.main_layout = QVBoxLayout(self)

        self.pack_cbox = QComboBox()
        self.pack_cbox.setModel(self.pack_mdl)
        self.pack_cbox.setModelColumn(0)
        self.pack_cbox.setPlaceholderText('Select Palette Pack')
        self.pack_cbox.setStatusTip('Select Palette Pack')
        self.pack_cbox.activated.connect(self.onPackChange)

        self.pal_cbox = QComboBox()
        self.pal_cbox.setModel(self.pal_mdl)
        self.pal_cbox.setModelColumn(1)
        self.pal_cbox.setPlaceholderText('Select Palette')
        self.pal_cbox.setStatusTip('Select Palette')
        self.pal_cbox.currentIndexChanged.connect(self.onPalChange)

        cb_layout = QHBoxLayout()
        cb_layout.addWidget(self.pack_cbox)
        cb_layout.addWidget(self.pal_cbox)

        btn_layout = QHBoxLayout()
        btn1 = QPushButton("Copy")
        btn1.clicked.connect(self.onCopy)
        btn2 = QPushButton("Select")
        btn2.clicked.connect(self.onSelect)
        btn_layout.addWidget(btn1)
        btn_layout.addWidget(btn2)
        
        #self.main_layout.addWidget(self.pack_cbox,1)
        #self.main_layout.addWidget(self.pal_cbox,1)
        self.main_layout.addLayout(cb_layout)
        self.pd = PaletteDisplay()
        self.pd.setPalette(self.pal)
        self.main_layout.addWidget(self.pd,1)
        self.main_layout.addLayout(btn_layout)
        self.onPackChange()

    def onPackChange(self):
        pack = self.pack_cbox.currentText()
        self.pal_mdl.setQuery(f"""
            SELECT pack, name, json
              FROM palettes
             WHERE pack='{pack}' ORDER BY name;
        """)
        if self.pal_mdl.lastError().isValid():
            print(self.pal_mdl.lastError())

    def onPalChange(self):
        rcd = self.pal_mdl.record(self.pal_cbox.currentIndex())
        pal = json.loads(rcd.value(2))
        self.pd.setPalette(pal)
        #print(pal)

    def onCopy(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(json.dumps(self.pd.palette))

    def onSelect(self):
        rcd = self.pal_mdl.record(self.pal_cbox.currentIndex())
        pal = json.loads(rcd.value(2))
        self.paletteSelected.emit(pal)

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

class RandMixTool(QWidget):
    """RandomPaletteSelector"""
    paletteCreated = Signal(list)
    def __init__(self):
        super().__init__()
        self.baseclr = ColorPatch()
        self.clrmode = QComboBox() 
        self.clrmode.addItem("RGB")
        self.clrmode.addItem("HSL")
        self.clrmode.addItem("HSV")

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(QLabel('Random Mix'),0, Qt.AlignCenter)
        row1_layout = QHBoxLayout()
        label_cm = QLabel('Color Mode:')
        row1_layout.addWidget(label_cm)
        row1_layout.addWidget(self.clrmode)

        row2_layout = QHBoxLayout()
 
        bc_layout = QVBoxLayout()
        bc_layout.addItem(
            QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        label_bc = QLabel('Base')
        label_bc.setAlignment(Qt.AlignCenter)
        bc_layout.addWidget(self.baseclr, 0, Qt.AlignCenter)
        bc_layout.addWidget(label_bc)

        cw_layout = QVBoxLayout()
        label_cw = QLabel('Weight')
        label_cw.setAlignment(Qt.AlignCenter)
        self.cw_dial = QDial()
        self.cw_dial.setMinimum(0)
        self.cw_dial.setMaximum(100)
        self.cw_dial.setSingleStep(1)
        self.cw_dial.setPageStep(25)
        self.cw_dial.setNotchesVisible(True)
        self.cw_dial.setValue(50)
        cw_layout.addWidget(self.cw_dial, Qt.AlignCenter)
        cw_layout.addWidget(label_cw)
        cw_layout.addStretch()

        row3_layout = QHBoxLayout()
        label_ps = QLabel('Size:')
        row3_layout.addWidget(label_ps)
        self.sizesl = QSlider()
        self.sizesl.setOrientation(Qt.Horizontal)
        self.sizesl.setMinimum(1)
        self.sizesl.setMaximum(250)  
        row3_layout.addWidget(self.sizesl)

        row2_layout.addLayout(cw_layout)
        row2_layout.addLayout(bc_layout)
        row2_layout.setStretch(0,1)
        row2_layout.setStretch(1,1)

        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.onCreate)
        main_layout.addLayout(row1_layout)
        main_layout.addLayout(row2_layout)
        main_layout.addLayout(row3_layout)
        main_layout.addWidget(create_btn)
        main_layout.addStretch()
        self.setLayout(main_layout)
        
    def onCreate(self):
        n = self.sizesl.value()
        weight = self.cw_dial.value()/100
        base = self.baseclr.getHex()
        mode = self.clrmode.currentText()
        if mode == 'HSL':
            base = hex2hsl(base)
            palette = hsl2hex(randmix_palette(n, base, weight))
        elif mode == 'HSV':
            base = hex2hsv(base)
            palette = hsv2hex(randmix_palette(n, base, weight))
        elif mode == 'RGB': 
            base = hex2rgb(base)
            palette = rgb2hex(randmix_palette(n, base, weight))
        self.palette = palette
        self.paletteCreated.emit(self.palette)


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
