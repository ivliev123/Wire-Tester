from PyQt5.QtWidgets import (
    QWidget, QGroupBox, QLabel, 
    QGridLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
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
        # self.wires_table.doubleClicked.connect(self.on_wire_double_clicked)
        
        # Кнопки управления
        buttons_group = QGroupBox()
        buttons_group.setMaximumSize(1000, 150)
        buttons_layout = QGridLayout(buttons_group)

        self.read_button = QPushButton("Прозвонить")
        # self.read_button.setMinimumSize(self.min_size_x, self.min_size_y)
        self.read_button.setIcon(self.icon.tester_icon)
        # self.read_button.setIcon(QIcon('icons/tester.png'))
        
        self.check_button = QPushButton("На проверку")
        self.check_button.setIcon(self.icon.send_icon)

        self.edit_button = QPushButton("На редактирование")
        self.edit_button.setIcon(self.icon.send_icon)


        self.test_test_button = QPushButton("test test")
        # self.test_test_button.clicked.connect(self.test_test)
        


        buttons_layout.addWidget(self.read_button, 0, 0, 1, 1)
        buttons_layout.addWidget(self.check_button, 1, 0, 1, 1)
        buttons_layout.addWidget(self.edit_button, 2, 0, 1, 1)
        buttons_layout.addWidget(self.test_test_button, 3, 0, 1, 1)

        spacerItem = QSpacerItem(20, 40, QSizePolicy.Maximum, QSizePolicy.Expanding)
        buttons_layout.addItem(spacerItem)

        wires_layout.addWidget(self.wires_table)
        wires_layout.addWidget(buttons_group)
        wires_group.setLayout(wires_layout)
        
        main_layout.addWidget(wires_group)
