import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QGridLayout, QGroupBox, QPushButton,
    QVBoxLayout, QLabel, QComboBox, QTableWidgetItem
)

from PyQt5.QtCore import Qt


from ReadWireGroup import ReadWireGroup
from TestWireGroup import TestWireGroup
from EditWireGroup import EditWireGroup


import time
import os
import serial
import serial.tools.list_ports

from IconModul import icon




def bytes_to_hex(data, cols=16):
    lines = []
    for i in range(0, len(data), cols):
        chunk = data[i:i+cols]
        hex_part = ' '.join(f'{b:02X}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append(f'{i:08X}  {hex_part:<48}  {ascii_part}')
    return '\n'.join(lines)


def bytes_to_bin(data):
    return ' '.join(f'{b:08b}' for b in data)



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





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.read_bit_rows = []

        self.setWindowTitle("Тестер проводов")
        self.resize(1600, 800)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QGridLayout(central)
        
        self.icon = icon()

        # SERIAL
        self.serial_manager = SerialManager()
        # ===== Панель подключения =====
        connection_box = QGroupBox("Подключение к устройству")
        conn_layout = QGridLayout()

        self.port_combo = QComboBox()
        self.refresh_button = QPushButton("Обновить")
        self.connect_button = QPushButton("Подключиться")
        self.connect_button.setIcon(self.icon.usb_icon)


        conn_layout.addWidget(QLabel("COM порт:"), 0, 0)
        conn_layout.addWidget(self.port_combo, 0, 1)
        conn_layout.addWidget(self.refresh_button, 0, 2)
        conn_layout.addWidget(self.connect_button, 0, 3)


        connection_box.setLayout(conn_layout)
        main_layout.addWidget(connection_box, 0, 0, 1, 3)

        # от разделения выхлопа особо небыло ...



        # Создаем и добавляем наш виджет
        self.read_wire_group = ReadWireGroup()
        self.test_wire_group = TestWireGroup()
        self.edit_wire_group = EditWireGroup()

        main_layout.addWidget(self.read_wire_group, 1, 0, 1, 1)  
        main_layout.addWidget(self.test_wire_group, 1, 1, 1, 1)  
        main_layout.addWidget(self.edit_wire_group, 1, 2, 1, 1)  

        
        # ===== Сигналы =====
        self.refresh_button.clicked.connect(self.update_ports)
        self.connect_button.clicked.connect(self.connect_device)

        self.update_ports()

        # обработки нажатия кнопок нужно создавать тут ...
        self.read_wire_group.read_button.clicked.connect(self.do_read_wire)
        self.read_wire_group.check_button.clicked.connect(self.to_test_wire)
        self.read_wire_group.edit_button.clicked.connect(self.to_edit_wire)

        self.read_wire_group.test_test_button.clicked.connect(self.test_test)

        # обработка событий нажатия ячейки         
        # Изменение текущей ячейки
        # self.edit_wire_group.wires_table.currentItemChanged.connect(self.on_current_item_changed)


    def do_read_wire(self):
        self.read_wire_write_file() # прозваниваем провод // записываем в файл 
        self.read_bit_rows = self.read_file() # читаем с файла
        self.read_visual(self.read_bit_rows) #отображаем данные в таблице

    def test_test(self):
        self.read_bit_rows = self.read_file()
        self.read_visual(self.read_bit_rows)




    def to_test_wire(self):
        # непонятно нужно ли взаимодействовать через отдельные объекты или все вместе городить 
        # будем работать как с отдельными переменными отдельных объектов так как разные задачи у блоков  
        self.test_wire_group.read_bit_rows =  self.read_bit_rows
        # а теперь тут визуализацию в таблиц с editline

        intersections_array = []
        # при проходе по строкам нужно строку отзеркалить
        for row_index, row in enumerate(self.test_wire_group.read_bit_rows):
            # 1. зеркалим строку
            mirrored = row[::-1]
            zero_indexes = [i for i, bit in enumerate(mirrored) if bit == 0]
            intersections = [i for i in zero_indexes if i != row_index]
            intersections_array.append(intersections)
    




    def to_edit_wire(self):
        self.edit_wire_group.read_bit_rows =  self.read_bit_rows
        # self.edit_visual(self.edit_wire_group.read_bit_rows)
        self.edit_wire_group.edit_visual(self.edit_wire_group.read_bit_rows)








    def read_visual(self, bit_rows):

        intersections_array = []

        self.read_wire_group.wires_table.clearContents()
        self.read_wire_group.wires_table.setRowCount(0)

        # при проходе по строкам нужно строку отзеркалить
        for row_index, row in enumerate(bit_rows):
            # 1. зеркалим строку
            mirrored = row[::-1]
            zero_indexes = [i for i, bit in enumerate(mirrored) if bit == 0]

            intersections = [i for i in zero_indexes if i != row_index]
            # print(intersections)
            intersections_array.append(intersections)
        print(intersections_array)

        # далее реализовать таблицу в блоке read

        wire_points = len(intersections_array)
        self.read_wire_group.wires_table.setRowCount(wire_points)

        for point_i, intersections in enumerate(intersections_array):
            
            self.read_wire_group.wires_table.setItem(point_i, 1, QTableWidgetItem(f"{point_i + 1}"))
            if intersections:
                intersections_text = ", ".join(str(i + 1) for i in intersections)
            else:
                intersections_text = ""

            self.read_wire_group.wires_table.setItem(point_i, 2, QTableWidgetItem(intersections_text))





    # кривое косое чтение но работает
    def read_wire_write_file(self):
        ser = self.serial_manager.serial 
        COMMAND = "t01" 

        # Создаем папку для данных
        if not os.path.exists("arduino_bin_data"):
            os.makedirs("arduino_bin_data")
        
        # 1. Читаем информацию о плате (текстовую)
        print("Информация о плате:")
        time.sleep(1)
        if ser.in_waiting > 0:
            info_bytes = ser.read(ser.in_waiting)
            # print(info_bytes.decode('ascii', errors='replace'))
        
        # 2. Отправляем команду
        print(f"\nОтправка: {COMMAND}")
        ser.write((COMMAND + '\n').encode())
        
        time.sleep(0.5)
        
        all_response_bytes = b""  # Байтовый буфер
        
        start = time.time()
        while time.time() - start < 3:
            if ser.in_waiting > 0:
                # Читаем байты
                data_bytes = ser.read(ser.in_waiting)
                all_response_bytes += data_bytes
                
                start = time.time()  # Сбрасываем таймер
        
        # 4. Сохраняем в бинарный файл
        if all_response_bytes:
            bin_filename = f"arduino_bin_data/response_.bin"
            
            # Записываем бинарные данные
            with open(bin_filename, 'wb') as f:  # 'wb' - write binary
                f.write(all_response_bytes)
            
            # Также сохраняем текстовую версию (опционально)
            txt_filename = f"arduino_bin_data/response_.txt"
            with open(txt_filename, 'w', encoding='utf-8') as f:

                # Пробуем декодировать как текст
                try:
                    f.write(bytes_to_bin(all_response_bytes))
                    
                except:
                    f.write("(бинарные данные, не удалось декодировать как текст)")
            
            print(f"Текстовая версия: {txt_filename}")
    


    def read_file(self):
        # Читаем бинарный файл
        filename = "arduino_bin_data/response_.bin"

        if not os.path.exists(filename):
            print(f"Файл {filename} не найден")
            exit()

        # Читаем все байты
        with open(filename, 'rb') as f:
            data = f.read()

        # Преобразуем байты в массив (список чисел)
        byte_array = []
        for byte in data:
            byte_array.append(byte)

        print(f"Всего байт: {len(byte_array)}")

        t_comand = 1
        byte_per_row = t_comand * 4

        # 1. Создаем двухмерный массив с строками по byte_per_row байт
        rows = []
        for i in range(0, len(byte_array), byte_per_row):
            row = byte_array[i:i + byte_per_row]
            if len(row) == byte_per_row:  # Только полные строки
                rows.append(row)

        print(f"\nКоличество строк: {len(rows)}")
        print(f"Байт в строке: {byte_per_row}")

        # 2. Преобразуем каждую строку в массив битов
        bit_rows = []
        for row in rows:
            bit_row = []
            for byte in row:
                # Преобразуем байт в 8 бит
                bits = [(byte >> bit) & 1 for bit in range(7, -1, -1)]
                bit_row.extend(bits)  # Добавляем все 8 бит
            bit_rows.append(bit_row)

        return bit_rows








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

        time.sleep(2)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

