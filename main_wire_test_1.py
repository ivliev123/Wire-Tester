# requirements:
# pip install pyqt5 pyserial

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QGridLayout, QGroupBox, QPushButton,
    QVBoxLayout, QLabel, QComboBox
)
from PyQt5.QtCore import Qt

# Универсальная работа с COM-портами (Windows / Linux)
import serial
import serial.tools.list_ports

from Icon_modul import icon


class SerialManager:
    """Универсальная подсистема работы с COM-портом"""

    def __init__(self):
        self.serial = None

    def list_ports(self):
        """Получить список доступных портов"""
        return [port.device for port in serial.tools.list_ports.comports()]

    def connect(self, port: str, baudrate: int = 2000000):
        """Подключение к устройству"""
        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=1
        )

    def disconnect(self):
        if self.serial and self.serial.is_open:
            self.serial.close()

    def send(self, data: bytes):
        if self.serial and self.serial.is_open:
            self.serial.write(data)

    def read(self) -> bytes:
        if self.serial and self.serial.is_open:
            return self.serial.read_all()
        return b""


class ReadWireGroup(QGroupBox):
    """пока пустой бокс"""
    def __init__(self):
        super().__init__("Прозвонка провода")
        layout = QVBoxLayout() # тут нужно будет сделать сетку ...

        self.status_label = QLabel("Окно с результатами считывания проводов")

        layout.addWidget(self.status_label)
        
        self.setLayout(layout)

class TestWireGroup(QGroupBox):
    """пока пустой бокс"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout("Проверка провода") # тут нужно будет сделать сетку ...

        self.status_label = QLabel("Окно с ...")

        layout.addWidget(self.status_label)
        
        self.setLayout(layout)

class EditWireGroup(QGroupBox):
    """пока пустой бокс"""
    def __init__(self):
        super().__init__("Редактирование провода")
        layout = QVBoxLayout() # тут нужно будет сделать сетку ...

        self.status_label = QLabel("Окно с ...")

        layout.addWidget(self.status_label)
        
        self.setLayout(layout)


class ReadUnderGroup(QGroupBox):
    """Группа чтения.прозвонки (один логический блок)"""

    def __init__(self):
        super().__init__()
        # layout = QVBoxLayout() # тут нужно будет сделать сетку ...
        layout = QGridLayout()


        self.status_label = QLabel("")
        # self.start_button = QPushButton("Старт теста")
        # self.stop_button = QPushButton("Стоп")

        layout.addWidget(self.status_label, 0, 0, 1, 1)
        # layout.addWidget(self.start_button, 1, 0, 1, 1)
        # layout.addWidget(self.stop_button,  2, 0, 1, 1)

        self.setLayout(layout)


class TestUnderGroup(QGroupBox):
    """Группа тестирования (один логический блок)"""

    def __init__(self):
        super().__init__()
        # layout = QVBoxLayout() # тут нужно будет сделать сетку ...
        layout = QGridLayout()


        self.status_label = QLabel("Статус: ожидание")
        self.start_button = QPushButton("Старт теста")
        self.stop_button = QPushButton("Стоп")

        layout.addWidget(self.status_label, 0, 0, 1, 1)
        layout.addWidget(self.start_button, 1, 0, 1, 1)
        layout.addWidget(self.stop_button,  2, 0, 1, 1)

        self.setLayout(layout)


class EditUnderGroup(QGroupBox):
    """Группа редактирования (один логический блок)"""

    def __init__(self):
        super().__init__()
        # layout = QVBoxLayout() # тут нужно будет сделать сетку ...
        layout = QGridLayout()


        self.status_label = QLabel("")
        # self.start_button = QPushButton("Старт теста")
        # self.stop_button = QPushButton("Стоп")

        layout.addWidget(self.status_label, 0, 0, 1, 1)
        # layout.addWidget(self.start_button, 1, 0, 1, 1)
        # layout.addWidget(self.stop_button,  2, 0, 1, 1)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тестер проводов")
        self.resize(900, 600)

        self.serial_manager = SerialManager()

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout()
        central.setLayout(main_layout)

        # ===== Панель подключения =====
        connection_box = QGroupBox("Подключение к устройству")
        conn_layout = QGridLayout()

        self.port_combo = QComboBox()
        self.refresh_button = QPushButton("Обновить")
        self.connect_button = QPushButton("Подключиться")

        conn_layout.addWidget(QLabel("COM порт:"), 0, 0)
        conn_layout.addWidget(self.port_combo, 0, 1)
        conn_layout.addWidget(self.refresh_button, 0, 2)
        conn_layout.addWidget(self.connect_button, 0, 3)

        connection_box.setLayout(conn_layout)
        main_layout.addWidget(connection_box)

        # ===== Сетка тестовых блоков =====
        grid_widget = QWidget()
        grid_layout = QGridLayout()
        grid_widget.setLayout(grid_layout)

        # Пример 2x2 групп
        self.test_groups = []
        # positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        # for i, pos in enumerate(positions, start=1):
        #     group = TestGroup(f"Тест {i}")
        #     grid_layout.addWidget(group, *pos)
        #     self.test_groups.append(group)


        # тут должен быть бокс с прокручиваемым меню в котором должна быть табличка
        # еще галочки должны быть которые активируют разрешение на редактирование ... возмоно редактирование будет доступно при переносе в правое окно...


        read_wire_group = ReadWireGroup()
        grid_layout.addWidget(read_wire_group, 0, 0)
        test_wire_group = EditWireGroup()
        grid_layout.addWidget(test_wire_group, 0, 1)
        edit_wire_group = EditWireGroup()
        grid_layout.addWidget(edit_wire_group, 0, 2)

        # боксы снизу
        read_under_group = ReadUnderGroup()
        grid_layout.addWidget(read_under_group, 1, 0)

        test_under_group = TestUnderGroup()
        grid_layout.addWidget(test_under_group, 1, 1)

        edit_under_group = EditUnderGroup()
        grid_layout.addWidget(edit_under_group, 1, 2)




        main_layout.addWidget(grid_widget)
        main_layout.addStretch()

        # ===== Сигналы =====
        self.refresh_button.clicked.connect(self.update_ports)
        self.connect_button.clicked.connect(self.connect_device)

        self.update_ports()

    def update_ports(self):
        self.port_combo.clear()
        ports = self.serial_manager.list_ports()
        self.port_combo.addItems(ports)

    def connect_device(self):
        port = self.port_combo.currentText()
        if not port:
            return
        try:
            self.serial_manager.connect(port)
            self.statusBar().showMessage(f"Подключено к {port}")
        except Exception as e:
            self.statusBar().showMessage(f"Ошибка подключения: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
