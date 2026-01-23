from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QApplication,
    QLineEdit, QMainWindow, QAction, qApp, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTabWidget,
    QTextEdit,
    QAction, QFileDialog, 
    QGroupBox, QSizePolicy, QSpacerItem,
    QScrollArea)
from PyQt5.QtGui import QPixmap, QColor, QIcon, QFont
from PyQt5.QtCore import QCoreApplication, QTimer, QSize, QThread, Qt
import PyQt5

# from setting import color
from IconModul import icon


class color():
    def __init__(self):
        self.primary =  "#1d9ce0" #007bff
        self.success = "#66BB6A" #28a745
        self.secondary = "#9E9E9E" #6c757d

        self.warning = "#FFEB3B"    
        self.danger = "#EE3545"  #DC3545

color = color()



class MessageWindow_class(QMainWindow):
    def __init__(self, msg):
        super().__init__()

        self.msg = msg

        self.min_size_x = 100
        self.min_size_y = 30
        self.border_radius = 15

        self.main_widget = QWidget()
        self.gridLayout = QGridLayout(self.main_widget)
        self.initUI()

        self.setCentralWidget(self.main_widget)


    def initUI(self):

        font = QFont()
        font.setPointSize(9)

        self.groupBox = QGroupBox(self.main_widget)
        self.groupBox.setMaximumSize(QSize(700, 400))

        self.inside_gridLayout = QGridLayout(self.groupBox)
        self.inside_gridLayout.setObjectName("inside_gridLayout")


        self.msg_QLabel = QLabel(self.groupBox)
        self.msg_QLabel.setFont(font)
        self.msg_QLabel.setText(self.msg)

        self.icon_QPushButton = QPushButton(self.groupBox)
        self.icon_QPushButton.setMaximumSize(50, 50)
        self.icon_QPushButton.setMinimumSize(50, 50)
        self.icon_QPushButton.setStyleSheet("background-color:  " + color.warning+ "; border-radius: 25px;")

        addhbox = QHBoxLayout()
        # addhbox.addWidget(self.icon_QPushButton, alignment=Qt.AlignRight)
        # addhbox.addWidget(self.msg_QLabel, alignment=Qt.AlignLeft)
        # self.inside_gridLayout.addLayout(addhbox, 0, 0, 1, 2)

        self.inside_gridLayout.addWidget(self.icon_QPushButton, 0, 0, 1, 2, alignment=Qt.AlignCenter)
        self.inside_gridLayout.addWidget(self.msg_QLabel, 1, 0, 1, 2, alignment=Qt.AlignCenter)


        self.cancel_QPushButton = QPushButton(self.groupBox)
        self.cancel_QPushButton.setText("Закрыть")
        self.cancel_QPushButton.clicked.connect(self.cancel_component)
        self.cancel_QPushButton.setIcon(QIcon('icons/error.png'))
        self.cancel_QPushButton.setMinimumSize(self.min_size_x, self.min_size_y)
        self.cancel_QPushButton.setStyleSheet("background-color:  " + color.secondary+ "; border-radius: " + str(self.border_radius) +"px;")
        self.inside_gridLayout.addWidget(self.cancel_QPushButton, 2, 0, 1, 2)

        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        # self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.setGeometry(200, 200, 500, 200)
        
        # self.resize(700, 200)  # задаем размеры окна
        # self.center()  # центрируем
        
        # Центрируем окно
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)


        self.setWindowTitle(" ")


    def cancel_component(self):
        self.close()




# class QuestionWindow(QMainWindow):
#     def __init__(self, msg):
#         super().__init__()
#         self.Window  = MessageWindow_class(msg)
#         self.Window.setWindowTitle(" ")
#         self.Window.icon_QPushButton.setIcon(QIcon('icons/question.png'))
#         self.Window.icon_QPushButton.setStyleSheet("background-color:  " + color.primary+ "; border-radius: 25px;")

#         self.Window.cancel_QPushButton.setText("Закрыть")
#         self.Window.inside_gridLayout.addWidget(self.Window.cancel_QPushButton, 2, 0, 1, 1)

#         self.Window.submit_QPushButton = QPushButton(self.Window.groupBox)
#         self.Window.submit_QPushButton.setText("ДА, подтвердить")
#         # self.Window.submit_QPushButton.clicked.connect(self.cancel_component)
#         self.Window.submit_QPushButton.setMinimumSize(self.Window.min_size_x, self.Window.min_size_y)
#         self.Window.submit_QPushButton.setIcon(QIcon('icons/check-mark.png'))
#         self.Window.submit_QPushButton.setStyleSheet("background-color:  " + color.success+ "; border-radius: " + str(self.Window.border_radius) +"px;")
#         self.Window.inside_gridLayout.addWidget(self.Window.submit_QPushButton, 2, 1, 1, 1)

class WarningWindow(QMainWindow):
    def __init__(self, msg):
        super().__init__()
        self.icon = icon()
        self.Window  = MessageWindow_class(msg)
        self.Window.setWindowTitle(" ")
        self.Window.icon_QPushButton.setIcon(QIcon(self.icon.alert_icon))
        self.Window.icon_QPushButton.setStyleSheet("background-color:  " + color.warning+ "; border-radius: 25px;")


class DangerWindow(QMainWindow):
    def __init__(self, msg):
        super().__init__()
        self.icon = icon()
        self.Window  = MessageWindow_class(msg)
        self.Window.setWindowTitle(" ")
        self.Window.icon_QPushButton.setIcon(self.icon.error_icon)
        self.Window.icon_QPushButton.setStyleSheet("background-color:  " + color.danger+ "; border-radius: 25px;")


class SuccessWindow(QMainWindow):
    def __init__(self, msg):
        super().__init__()
        self.icon = icon()
        self.Window  = MessageWindow_class(msg)
        self.Window.setWindowTitle(" ")
        self.Window.icon_QPushButton.setIcon(self.icon.check_mark_icon)
        self.Window.icon_QPushButton.setStyleSheet("background-color:  " + color.success+ "; border-radius: 25px;")


class InfoWindow(QMainWindow):
    def __init__(self, msg):
        super().__init__()
        self.icon = icon()
        self.Window  = MessageWindow_class(msg)
        self.Window.setWindowTitle(" ")
        self.Window.icon_QPushButton.setIcon(self.icon.info_icon)
        self.Window.icon_QPushButton.setStyleSheet("background-color:  " + color.primary+ "; border-radius: 25px;")



# class DeleteWindow(QMainWindow):
#     def __init__(self, msg):
#         super().__init__()
#         self.Window  = MessageWindow_class(msg)
#         self.Window.setWindowTitle(" ")
#         self.Window.icon_QPushButton.setIcon(QIcon('icons/bin.png'))
#         self.Window.icon_QPushButton.setStyleSheet("background-color:  " + color.danger+ "; border-radius: 25px;")

#         self.Window.cancel_QPushButton.setText("Закрыть")
#         self.Window.inside_gridLayout.addWidget(self.Window.cancel_QPushButton, 2, 0, 1, 1)

#         self.Window.submit_QPushButton = QPushButton(self.Window.groupBox)
#         self.Window.submit_QPushButton.setText("ДА, Удалить")
#         # self.Window.submit_QPushButton.clicked.connect(self.cancel_component)
#         self.Window.submit_QPushButton.setMinimumSize(self.Window.min_size_x, self.Window.min_size_y)
#         self.Window.submit_QPushButton.setIcon(QIcon('icons/bin.png'))
#         self.Window.submit_QPushButton.setStyleSheet("background-color:  " + color.danger + "; border-radius: " + str(self.Window.border_radius) +"px;")
#         self.Window.inside_gridLayout.addWidget(self.Window.submit_QPushButton, 2, 1, 1, 1)