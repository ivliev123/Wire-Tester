import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QGridLayout, QGroupBox, QPushButton,
    QVBoxLayout, QLabel, QComboBox, QTableWidgetItem, QLineEdit,
    QDialog, QProgressBar
)
from PyQt5.QtGui import QIcon, QPixmap

from PyQt5.QtCore import Qt, QThread, pyqtSignal

import time
import os
import serial
import serial.tools.list_ports
import csv
import configparser

from ReadWireGroup import ReadWireGroup
from TestWireGroup import TestWireGroup
from EditWireGroup import EditWireGroup

from SystemModul import icon

from MessageWindows import WarningWindow
from MessageWindows import DangerWindow
from MessageWindows import SuccessWindow
from MessageWindows import InfoWindow


COMMAND = "t01" 
t_comand = 1


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




class ReadWireWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, serial_manager, command, parent=None):
        super().__init__(parent)
        self.serial_manager = serial_manager
        self.command = command
        self._running = True

    def run(self):
        try:
            ser = self.serial_manager.serial
            if not ser:
                self.error.emit("Нет подключения к устройству")
                return

            # 1. очистка
            time.sleep(0.5)
            ser.read_all()

            # 2. отправка команды
            ser.write((self.command + '\n').encode())
            self.progress.emit(10)

            all_response_bytes = b""
            start = time.time()

            while time.time() - start < 3:
                if not self._running:
                    return

                if ser.in_waiting > 0:
                    all_response_bytes += ser.read(ser.in_waiting)
                    start = time.time()

                self.progress.emit(10 + int((time.time() % 3) / 3 * 80))

            # 3. сохранение
            os.makedirs("arduino_bin_data", exist_ok=True)
            with open("arduino_bin_data/response_.bin", "wb") as f:
                f.write(all_response_bytes)

            self.progress.emit(100)
            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        self._running = False


class ReadProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Прозвонка")
        self.setModal(True)
        self.setFixedSize(300, 120)

        layout = QVBoxLayout(self)
        self.label = QLabel("Идёт прозвонка...")
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)

        layout.addWidget(self.label)
        layout.addWidget(self.bar)

    def set_progress(self, value):
        self.bar.setValue(value)



class SerialManager:
    """Универсальная подсистема работы с COM-портом"""

    def __init__(self):
        self.serial = None

    def list_ports(self):
        """Получить список доступных портов"""
        return [port.device for port in serial.tools.list_ports.comports()]

    # def connect(self, port: str, baudrate: int = 2000000):
    def connect(self, port: str, baudrate: int = 115200):
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

        self.is_device_connected = False

        self.icon = icon()

        self.init_ui()
        self.read_wire_group.read_button.setEnabled(False)

        self.load_command_from_ini()

        self.read_bit_rows = [[] for _ in range(32 * t_comand)] # делаем его не пустым потому как возникают проблемы в edit
        # заглушки чтоб использовать пустышки 
        self.read_wire_group.read_bit_rows =  self.read_bit_rows
        self.test_wire_group.read_bit_rows =  self.read_bit_rows
        self.edit_wire_group.read_bit_rows =  self.read_bit_rows 

        self.load_accord_table()
    

    def init_ui(self):

        self.setWindowTitle("Тестер проводов")
        self.resize(1600, 800)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QGridLayout(central)
        
        # Команда / количество плат
        comand_box = QGroupBox("Команда / количество плат")
        comand_layout = QGridLayout()

        self.comand_setup_line_edit = QLineEdit()
        self.comand_setup_button = QPushButton("Задать")
        self.comand_setup_button.clicked.connect(self.set_command)

        
        comand_layout.addWidget(self.comand_setup_line_edit, 0, 0)
        comand_layout.addWidget(self.comand_setup_button, 0, 1)

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


        comand_box.setLayout(comand_layout)
        main_layout.addWidget(comand_box, 0, 0, 1, 1)
        connection_box.setLayout(conn_layout)
        main_layout.addWidget(connection_box, 0, 1, 1, 3)


        # Создаем и добавляем наш виджет
        self.read_wire_group = ReadWireGroup()
        self.test_wire_group = TestWireGroup()
        self.edit_wire_group = EditWireGroup()

        main_layout.addWidget(self.read_wire_group, 1, 0, 1, 1)  
        main_layout.addWidget(self.test_wire_group, 1, 1, 1, 1)  
        main_layout.addWidget(self.edit_wire_group, 1, 2, 1, 1)  

        # еще сигналы 
        # Подключаем сигнал
        self.read_wire_group.accord_data_ready.connect(self.handle_accord_data) 

        # ===== Сигналы =====
        self.refresh_button.clicked.connect(self.update_ports)
        self.connect_button.clicked.connect(self.connect_device)

        self.update_ports()

        # обработчик событий в других классах
        # обработки нажатия кнопок нужно создавать тут ...
        self.read_wire_group.read_button.clicked.connect(self.do_read_wire)
        self.read_wire_group.edit_button.clicked.connect(self.to_edit_wire)
        self.read_wire_group.test_test_button.clicked.connect(self.test_test)
        

    def handle_accord_data(self, accord_data):
        # Передаем список в EditWireGroup
        self.edit_wire_group.process_accord_data(accord_data)
        self.test_wire_group.process_accord_data(accord_data)

    def update_read_controls(self):
        """Включает / выключает кнопку прозвонки"""
        is_ready = (
            self.is_device_connected
            and self.serial_manager.serial
            and self.serial_manager.serial.is_open
        )
        self.read_wire_group.read_button.setEnabled(is_ready)

    # def do_read_wire(self):
    #     self.read_wire_write_file() # прозваниваем провод // записываем в файл 
    #     self.read_bit_rows = self.read_file() # читаем с файла
    #     self.read_visual(self.read_bit_rows) #отображаем данные в таблице
    #     self.to_test_wire() # отправляем на проверку

    #     self.InfoWindow = InfoWindow(f"Прозвонка завершена")
    #     self.InfoWindow.Window.show()


    # def do_read_wire(self):
    #     self.progress_dialog = ReadProgressDialog(self)
    #     self.progress_dialog.show()

    #     self.worker = ReadWireWorker(
    #         serial_manager=self.serial_manager,
    #         command=COMMAND
    #     )

    #     self.worker.progress.connect(self.progress_dialog.set_progress)
    #     self.worker.finished.connect(self.on_read_finished)
    #     self.worker.error.connect(self.on_read_error)

    #     self.worker.start()

    def is_device_alive(self) -> bool:
        ser = self.serial_manager.serial
        if not ser or not ser.is_open:
            return False

        try:
            ser.write(b'\n')   # любой байт
            return True
        except Exception:
            return False
            
    def do_read_wire(self):
        # if not self.is_device_connected:
        #     WarningWindow("Устройство не подключено").Window.show()
        #     return
        if not self.is_device_alive():
            self.is_device_connected = False
            self.update_read_controls()
            WarningWindow("Устройство не подключено").Window.show()
            return

        self.progress_dialog = ReadProgressDialog(self)
        self.progress_dialog.show()

        self.worker = ReadWireWorker(
            serial_manager=self.serial_manager,
            command=COMMAND
        )

        self.worker.progress.connect(self.progress_dialog.set_progress)
        self.worker.finished.connect(self.on_read_finished)
        self.worker.error.connect(self.on_read_error)

        self.worker.start()

    def on_read_finished(self):
        self.progress_dialog.close()

        self.read_bit_rows = self.read_file()
        self.read_visual(self.read_bit_rows)
        self.to_test_wire()

        InfoWindow("Прозвонка завершена").Window.show()
        
    def on_read_error(self, msg):
        self.progress_dialog.close()
        DangerWindow(msg).Window.show()



    def test_test(self):
        self.read_bit_rows = self.read_file()
        self.read_visual(self.read_bit_rows)
        self.to_test_wire() # отправляем на проверку




    def to_test_wire(self): 
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
        # и тут презаполнять первый столбец
        self.edit_wire_group.accord_data = self.read_wire_group.accord_data
        self.edit_wire_group.fill_table_from_accord_data()

        # self.read_bit_rows = (32 * t_comand) * []
        self.edit_wire_group.read_bit_rows =  self.read_bit_rows
        self.edit_wire_group.edit_visual(self.read_bit_rows)



    def read_visual(self, bit_rows): # в этой функции нужно внести изменения чтобы не затирались accord_data

        intersections_array = []

        self.read_wire_group.wires_table.clearContents()
        self.read_wire_group.wires_table.setRowCount(0)

        # и тут презаполнять первый столбец
        self.read_wire_group.fill_table_from_accord_data()

        # при проходе по строкам нужно строку отзеркалить
        for row_index, row in enumerate(bit_rows):
            # 1. зеркалим строку
            mirrored = row[::-1]
            zero_indexes = [i for i, bit in enumerate(mirrored) if bit == 0]
            intersections = [i for i in zero_indexes if i != row_index]
            # print(intersections)
            intersections_array.append(intersections)
        # print(intersections_array)

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


        # запрет на редактирование.
        for row in range(self.read_wire_group.wires_table.rowCount()):
            item = self.read_wire_group.wires_table.item(row, 1)
            if item:
                # item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Снимаем флаг редактирования
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item = self.read_wire_group.wires_table.item(row, 2)
            if item:
                # item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Снимаем флаг редактирования
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.read_wire_group.wires_table.resizeColumnToContents(2)


    # кривое косое чтение но работает
    def read_wire_write_file(self):
        ser = self.serial_manager.serial 

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
                try:
                    # все биты одной строкой
                    bits = ''.join(f'{b:08b}' for b in all_response_bytes)

                    bits_per_line = 32 * t_comand

                    count_i = 0
                    for i in range(0, len(bits), bits_per_line):
                        count_i = count_i + 1
                        if count_i < 10:
                            count_i_str = "00" + str(count_i)
                        if count_i >= 10 and count_i < 100:
                            count_i_str = "0" + str(count_i)
                        if count_i >= 100 and count_i < 1000:
                            count_i_str = str(count_i)
                        
                        line = bits[i:i + bits_per_line]
                        
                        f.write(count_i_str + ": " +  line + '\n')

                except Exception as e:
                    f.write(f"(ошибка преобразования в биты: {e})")

                    
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

        byte_per_row = t_comand * 4
        print(t_comand)

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

    # def connect_device(self):
    #     port = self.port_combo.currentText()
    #     if not port:
    #         return
    #     try:
    #         self.serial_manager.connect(port)
    #         self.statusBar().showMessage(f"Подключено к {port}")
    #     except Exception as e:
    #         self.statusBar().showMessage(f"Ошибка подключения: {e}")

    #     time.sleep(2)

    def connect_device(self):
        port = self.port_combo.currentText()
        if not port:
            return
        try:
            self.serial_manager.connect(port)
            self.is_device_connected = True
            self.statusBar().showMessage(f"Подключено к {port}")
        except Exception as e:
            self.is_device_connected = False
            self.statusBar().showMessage(f"Ошибка подключения: {e}")

        # time.sleep(2)
        self.update_read_controls()


    def disconnect_device(self):
        self.serial_manager.disconnect()
        self.is_device_connected = False
        self.update_read_controls()

        

    def load_accord_table(self):
        if not self.accord_table_file_name:
            return

        if not os.path.exists(self.accord_table_file_name):
            print("Файл соответствий не найден")
            return

        accord_data = []

        with open(self.accord_table_file_name, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f, delimiter=";")
            for row in reader:
                if len(row) >= 2:
                    accord_data.append([row[0].strip(), row[1].strip()])
                elif len(row) == 1:
                    accord_data.append([row[0].strip(), ""])
                else:
                    accord_data.append(["", ""])

        # 🔥 ПЕРЕДАЁМ В ReadWireGroup
        # self.read_wire_group.set_accord_data(accord_data)

        self.read_wire_group.accord_data = accord_data
        self.read_wire_group.line_accord_file.setText(os.path.basename(self.accord_table_file_name))
        self.read_wire_group.fill_table_from_accord_data()

        # обновляем данные для других блоков 
        self.test_wire_group.accord_data = accord_data
        self.edit_wire_group.accord_data = accord_data


    def load_command_from_ini(self):
        global COMMAND, t_comand

        config = configparser.ConfigParser()

        if not os.path.exists("settings.ini"):
            config["COMMAND"] = {
                "command": COMMAND,
                "t_comand": str(t_comand),
                "accord_table_file_name": ""
            }
            with open("settings.ini", "w", encoding="utf-8") as f:
                config.write(f)
            return

        config.read("settings.ini", encoding="utf-8")

        COMMAND = config.get("COMMAND", "command", fallback="t01")
        t_comand = config.getint("COMMAND", "t_comand", fallback=1)

        self.accord_table_file_name = config.get(
            "COMMAND",
            "accord_table_file_name",
            fallback=""
        )

        self.comand_setup_line_edit.setText(str(t_comand))
        
        # обновляем данные для других блоков 
        self.edit_wire_group.t_comand = t_comand # нужно в сигнал...



    def save_command_to_ini(self):
        global COMMAND, t_comand

        config = configparser.ConfigParser()
        config["COMMAND"] = {
            "command": COMMAND,
            "t_comand": str(t_comand)
        }
        with open("settings.ini", "w") as f:
            config.write(f)


    def set_command(self):
        global COMMAND, t_comand
        text = self.comand_setup_line_edit.text().strip()

        if not text.isdigit() or int(text) <= 0:
            self.statusBar().showMessage("Введите корректное число плат")
            return

        t_comand = int(text)
        COMMAND = f"t{t_comand:02d}"  # t01, t05, t12 ...

        self.save_command_to_ini()
        self.read_wire_group.save_accord_file_to_ini()

        self.statusBar().showMessage(
            f"Установлена команда {COMMAND}, плат: {t_comand}"
        )



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

