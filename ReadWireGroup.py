from PyQt5.QtWidgets import (
    QWidget, QGroupBox, QLabel, 
    QGridLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QHBoxLayout, QSpacerItem, 
    QSizePolicy, QHeaderView, QAbstractItemView,
    QLineEdit, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QPixmap, QColor, QIcon, QFont
from PyQt5.QtCore import Qt, pyqtSignal

import os
import csv
import configparser

from IconModul import icon


class ReadWireGroup(QWidget):  # QWidget вместо QMainWindow
    """Виджет для отображения результатов прозвонки проводов"""
    
    # Сигналы для связи с другими компонентами
    accord_data_ready = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.icon = icon()

        self.min_size_x = 30 
        self.min_size_y = 30

        self.read_bit_rows = [] # тут наверное немного лишнее
        self.is_editing_mode = True
        self.accord_table_file_name = ""

        self.init_ui()
    
    def init_ui(self):
        # Основной layout
        main_layout = QVBoxLayout(self)
        
        # 1. Группа с таблицей проводов (верхняя часть)
        wires_group = QGroupBox("Прозвонка провода")
        wires_layout = QVBoxLayout()
        
        # Таблица для отображения проводов
        self.wires_table = QTableWidget()
        # self.wires_table.setEditTriggers(QTableWidget.NoEditTriggers) 
        self.wires_table.setColumnCount(3)
        self.wires_table.setHorizontalHeaderLabels([
            "Разъем", "Вывод", "Вывод"
        ])
        header = self.wires_table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignLeft)

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
        self.save_accord_file_button.clicked.connect(self.save_accord_file_as)

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


    # def save_accord_file_to_ini(self):
    #     config = configparser.ConfigParser()
    #     config.read("settings.ini", encoding="utf-8")

    #     if "COMMAND" not in config:
    #         config["COMMAND"] = {}

    #     config["COMMAND"]["accord_table_file_name"] = self.accord_table_file_name

    #     with open("settings.ini", "w", encoding="utf-8") as f:
    #         config.write(f)
    
    def save_accord_file_to_ini(self):
        config = configparser.ConfigParser()
        config.read("settings.ini", encoding="utf-8")

        if "COMMAND" not in config:
            config["COMMAND"] = {}

        # делаем путь относительным к текущему проекту
        base_dir = os.getcwd()
        relative_path = os.path.relpath(self.accord_table_file_name, base_dir)

        config["COMMAND"]["accord_table_file_name"] = relative_path

        with open("settings.ini", "w", encoding="utf-8") as f:
            config.write(f)


    def read_accord_file(self):
        """Чтение файла соответствий из CSV (только первые 2 столбца)"""
        start_dir = "accord_tables/"
        
        # Создаем директорию если ее нет
        if not os.path.exists(start_dir):
            os.makedirs(start_dir)
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть файл соответствий",
            start_dir,
            "CSV файлы (*.csv);;Все файлы (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
                reader = csv.reader(file, delimiter=";")
                rows = list(reader)
            
            if not rows:
                QMessageBox.warning(self, "Ошибка", "Файл пуст")
                return
            
            # Проверяем минимальное количество столбцов
            if len(rows[0]) < 2:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Неверный формат файла. Должно быть минимум 2 столбца: Разъем и Вывод"
                )
                return
            
            # Сохраняем только первые 2 столбца каждой строки
            self.accord_data = []
            for row in rows:
                # Берем только первые 2 элемента или заполняем пустыми строками
                if len(row) >= 2:
                    self.accord_data.append([row[0].strip(), row[1].strip()])
                elif len(row) == 1:
                    self.accord_data.append([row[0].strip(), ""])
                else:
                    self.accord_data.append(["", ""])
            
            self.accord_file_path = file_path
            self.accord_table_file_name = file_path # плодим сущности ...
            print(file_path)
            self.save_accord_file_to_ini()
            self.line_accord_file.setText(os.path.basename(file_path))
            
            # Заполняем таблицу
            self.fill_table_from_accord_data()
            # 
            self.accord_data_ready.emit(self.accord_data)
            
            # Включаем кнопки
            self.edit_button.setEnabled(True)
            self.save_accord_file_button.setEnabled(True)
            
            QMessageBox.information(
                self,
                "Успех",
                f"Файл {os.path.basename(file_path)} успешно загружен\n"
                f"Загружено строк: {len(self.accord_data)-1 if len(self.accord_data) > 1 else 0}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка чтения файла", str(e))



    def fill_table_from_accord_data(self):
        """Заполнение таблицы данными из файла соответствий (только 2 столбца)"""
        # Очищаем таблицу
        self.wires_table.setRowCount(0)
        
        if not self.accord_data:
            return
        
        # Если первая строка - заголовки
        has_headers = True
        # Проверяем, является ли первая строка заголовками (содержит текст, а не числа)
        if self.accord_data and len(self.accord_data[0]) > 0:
            first_cell = self.accord_data[0][0]
            if first_cell and first_cell.lower() in ["разъем", "socket", "connector", "вывод", "pin"]:
                has_headers = True
                headers = self.accord_data[0]
                data_rows = self.accord_data[1:]
            else:
                has_headers = False
                data_rows = self.accord_data
        else:
            has_headers = False
            data_rows = self.accord_data
        
        # Устанавливаем количество строк
        self.wires_table.setRowCount(len(data_rows))
        
        # Устанавливаем заголовки таблицы
        if has_headers and len(headers) >= 2:
            # self.wires_table.setHorizontalHeaderLabels([headers[0], headers[1], "Выводы"])
            self.wires_table.setHorizontalHeaderLabels([
                "Разъем", "Вывод", "Вывод"
            ])
        
        header = self.wires_table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignLeft)

        # Заполняем данные
        for row_idx, row_data in enumerate(data_rows):
            # Разъем (столбец 0)
            if len(row_data) > 0:
                item_socket = QTableWidgetItem(row_data[0])
                item_socket.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.wires_table.setItem(row_idx, 0, item_socket)
            
            # Вывод (столбец 1)
            if len(row_data) > 1:
                item_pin = QTableWidgetItem(row_data[1])
                item_pin.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.wires_table.setItem(row_idx, 1, item_pin)
            
            # Столбец "Соответствующие выводы" оставляем пустым
            # Пользователь может заполнить его вручную при редактировании
        
        # Автоматически подгоняем ширину столбцов
        self.wires_table.resizeColumnsToContents()
        
        # Делаем третий столбец шире
        header = self.wires_table.horizontalHeader()
        header.setStretchLastSection(True)


    def update_accord_data_from_table(self):
        """Обновление данных accord_data из таблицы (только первые 2 столбца)"""
        new_data = []
        
        # Добавляем заголовки
        new_data.append(["Разъем", "Вывод"])
        
        # Собираем данные из таблицы (только первые 2 столбца)
        for row in range(self.wires_table.rowCount()):
            socket_item = self.wires_table.item(row, 0)
            pin_item = self.wires_table.item(row, 1)
            
            socket = socket_item.text().strip() if socket_item else ""
            pin = pin_item.text().strip() if pin_item else ""
            
            # Добавляем только непустые строки
            if socket or pin:
                new_data.append([socket, pin])
        
        self.accord_data = new_data



    def save_accord_file(self):
        """Сохранение таблицы соответствий в файл (только 2 столбца)"""
        if not self.accord_data:
            QMessageBox.warning(self, "Предупреждение", "Нет данных для сохранения")
            return
        
        # Определяем путь для сохранения
        if self.accord_file_path:
            default_dir = os.path.dirname(self.accord_file_path)
            default_name = os.path.basename(self.accord_file_path)
        else:
            default_dir = "accord_tables/"
            default_name = "table_accord.csv"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить таблицу соответствий",
            os.path.join(default_dir, default_name),
            "CSV файлы (*.csv);;Все файлы (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            # Обновляем данные из таблицы перед сохранением
            if self.is_editing_mode:
                self.update_accord_data_from_table()
            
            # Сохраняем в CSV только 2 столбца
            with open(file_path, "w", encoding="utf-8-sig", newline="") as file:
                writer = csv.writer(file, delimiter=";")
                
                # Если есть данные, сохраняем их
                if len(self.accord_data) > 0:
                    # Записываем все строки
                    for row in self.accord_data:
                        # Берем только первые 2 элемента из каждой строки
                        row_to_write = row[:2] if len(row) >= 2 else ["", ""]
                        writer.writerow(row_to_write)
                else:
                    # Если нет данных, сохраняем только заголовки
                    writer.writerow(["Разъем", "Вывод"])
            
            # Обновляем информацию о файле
            self.accord_file_path = file_path
            self.line_accord_file.setText(os.path.basename(file_path))
            
            QMessageBox.information(
                self,
                "Успех",
                f"Файл успешно сохранен:\n{os.path.basename(file_path)}\n"
                f"Сохранено строк: {len(self.accord_data)-1 if len(self.accord_data) > 1 else 0}"
            )
            
        except Exception as e:
            print(e)
            QMessageBox.critical(self, "Ошибка сохранения", str(e))


    def save_accord_file_as(self):
        """Сохранение таблицы соответствий как нового файла"""
        self.save_accord_file()

