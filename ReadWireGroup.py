from PyQt5.QtWidgets import (
    QWidget, QGroupBox, QLabel, 
    QGridLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QHBoxLayout, QSpacerItem, 
    QSizePolicy, QHeaderView, QAbstractItemView,
    QLineEdit
)
from PyQt5.QtGui import QPixmap, QColor, QIcon, QFont
from PyQt5.QtCore import Qt, pyqtSignal

from IconModul import icon


class ReadWireGroup(QWidget):  # QWidget вместо QMainWindow
    """Виджет для отображения результатов прозвонки проводов"""
    
    # Сигналы для связи с другими компонентами
    wire_selected = pyqtSignal(dict)  # Сигнал при выборе провода
    start_test_requested = pyqtSignal(int)  # Запрос теста для конкретного провода
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.icon = icon()

        self.min_size_x = 30 
        self.min_size_y = 30

        self.read_bit_rows = [] # тут наверное немного лишнее

        self.init_ui()
    
    def init_ui(self):
        # Основной layout
        main_layout = QVBoxLayout(self)
        
        # 1. Группа с таблицей проводов (верхняя часть)
        wires_group = QGroupBox("Прозвонка провода")
        wires_layout = QVBoxLayout()
        
        # Таблица для отображения проводов
        self.wires_table = QTableWidget()
        self.wires_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.wires_table.setColumnCount(3)
        self.wires_table.setHorizontalHeaderLabels([
            "Разъем", "Вывод", "Вывод"
        ])
        self.wires_table.setRowCount(1)
        self.wires_table.setSelectionBehavior(QTableWidget.SelectRows)

        self.wires_table.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        self.wires_table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.wires_table.setSelectionBehavior(QTableWidget.SelectRows)
        

        # Кнопки управления
        buttons_group_main = QGroupBox()
        buttons_group_main.setMaximumSize(1000, 220)
        buttons_layout_main = QGridLayout(buttons_group_main)

        # 1
        buttons_group_1 = QGroupBox()
        buttons_layout_1 = QGridLayout(buttons_group_1)

        self.line_accord_file = QLineEdit()
        self.line_accord_file.setStyleSheet('background : #ccc; ')
        self.line_accord_file.setReadOnly(1)
        self.line_accord_file.setPlaceholderText("Выберите таблицу соответствия...")

        self.open_button = QPushButton("Открыть")
        self.open_button.setIcon(self.icon.open_folder_icon)
        self.open_button.clicked.connect(self.read_accord_file)

        self.save_accord_file_button = QPushButton("Сохранить таблицу соответствия как")
        self.save_accord_file_button.setIcon(self.icon.save_icon)
        self.save_accord_file_button.clicked.connect(self.read_accord_file)

        buttons_layout_1.addWidget(self.line_accord_file, 0, 0, 1, 1)
        buttons_layout_1.addWidget(self.open_button, 0, 1, 1, 1)
        buttons_layout_1.addWidget(self.save_accord_file_button, 1, 0, 1, 2)

        # 2
        buttons_group_2 = QGroupBox()
        buttons_layout_2 = QGridLayout(buttons_group_2)

        self.read_button = QPushButton("Прозвонить")
        self.read_button.setIcon(self.icon.tester_icon)
        
        self.edit_button = QPushButton("На редактирование")
        self.edit_button.setIcon(self.icon.send_icon)

        self.test_test_button = QPushButton("test test")
 
        buttons_layout_2.addWidget(self.read_button, 0, 0, 1, 1)
        buttons_layout_2.addWidget(self.edit_button, 1, 0, 1, 1)
        buttons_layout_2.addWidget(self.test_test_button, 2, 0, 1, 1)

        buttons_layout_main.addWidget(buttons_group_1)
        buttons_layout_main.addWidget(buttons_group_2)

        spacerItem = QSpacerItem(20, 40, QSizePolicy.Maximum, QSizePolicy.Expanding)
        buttons_layout_main.addItem(spacerItem)

        wires_layout.addWidget(self.wires_table)
        wires_layout.addWidget(buttons_group_main)
        wires_group.setLayout(wires_layout)
        
        main_layout.addWidget(wires_group)


    def read_accord_file(self):
        print("read_accord_file")