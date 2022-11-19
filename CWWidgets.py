
import json
from objregistry import ObjRegistry

from PySide6.QtWidgets import (
    QApplication, 
    QColorDialog, 
    QComboBox,
    QDial,
    QHBoxLayout,
    QMainWindow, 
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpacerItem,
    QVBoxLayout,
    QWidget, 
)

from PySide6.QtGui import (
    QBrush, 
    QColor, 
    QIcon, 
    QPainter, 
    QPen, 
)

from PySide6.QtCore import (
    Qt, 
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


