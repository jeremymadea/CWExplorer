
from PySide6.QtWidgets import ( QColorDialog, QPushButton, QSizePolicy)
from PySide6.QtGui import ( QColor, )
from PySide6.QtCore import ( QSize, )

class ColorPatch(QPushButton):

    def __init__(self):
        super().__init__()
        self.setFlat(True)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        #sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)
        self.setStyleSheet('background-color: #FF00FF; border: none;')
        self.color = '#FF00FF'
        self.clicked.connect(self.onClicked)
   
    def sizeHint(self):
        return QSize(60,40)
 
    def heightForWidth(self, width):
        return width * .5

    def onClicked(self):
        self.clrpick = QColorDialog()
        self.clrpick.setOption(QColorDialog.DontUseNativeDialog)
        self.clrpick.colorSelected.connect(self.onColorSelected)
        self.clrpick.open()

    def onColorSelected(self, color):
        if color.isValid():
            self.color = color.name()
            self.setStyleSheet(f'background-color: {self.color}; border: none;')
        else: 
            pass

    def getHex(self):
        return self.color

    def getQColor(self):
        return QColor(self.color)

