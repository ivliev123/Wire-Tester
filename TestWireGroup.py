from PyQt5.QtWidgets import (
    QWidget, QGroupBox, QLabel, 
    QGridLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QLineEdit, QMessageBox, QFileDialog
)
from PyQt5.QtGui import QPixmap, QColor, QIcon, QFont
from PyQt5.QtCore import Qt, pyqtSignal

import csv
import os

from IconModul import icon


class TestWireGroup(QWidget):  # QWidget вместо QMainWindow
    """Виджет для тестирования результатов прозвонки проводов"""
    
    # Сигналы для связи с другими компонентами
    wire_selected = pyqtSignal(dict)  # Сигнал при выборе провода
    start_test_requested = pyqtSignal(int)  # Запрос теста для конкретного провода
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.icon = icon()

        self.min_size_x = 30 
        self.min_size_y = 30

        self.read_bit_rows = []

        self.wire_data_from_file = []

        # 
        self.update_data_to_test = 0
        self.update_data_to_test_text = ""

        self.init_ui()

        # тут обновить статус
        self.to_update_data_to_test()

    
    def init_ui(self):
        # Основной layout
        main_layout = QVBoxLayout(self)
        
        # 1. Группа с таблицей проводов (верхняя часть)
        wires_group = QGroupBox("Проверка провода")
        wires_layout = QVBoxLayout()
        
        # Таблица для отображения проводов
        self.wires_table = QTableWidget()
        self.wires_table.setColumnCount(3)
        self.wires_table.setHorizontalHeaderLabels([
            "Разъем", "Вывод", "Вывод"
        ])
        self.wires_table.setSelectionBehavior(QTableWidget.SelectRows)
        # self.wires_table.doubleClicked.connect(self.on_wire_double_clicked)
        
        # Кнопки управления
        buttons_group = QGroupBox()
        buttons_group.setMaximumSize(1000, 150)
        buttons_layout = QGridLayout(buttons_group)



        self.line_edit_file = QLineEdit()
        self.line_edit_file.setStyleSheet('background : #ccc; ')
        self.line_edit_file.setReadOnly(1)


        self.open_button = QPushButton("Открыть")
        self.open_button.setIcon(self.icon.open_folder_icon)
        self.open_button.clicked.connect(self.read_from_csv)
        
        self.check_button = QPushButton("Проверка")
        self.check_button.setIcon(self.icon.search_icon)
        self.check_button.clicked.connect(self.do_check)


        self.test_status_label = QLabel("")
        

        border_radius = 14
        btn_color_secondary = "6C757D"
        btn_color_success = "28A745"
        btn_color_warning = "FFC107"
        btn_color_danger  = "DC3545"

        # тут иконку состояния в виде кнопки 
        self.test_status_button = QPushButton("")
        # self.test_status_button.setMinimumSize(30, 30)
        self.test_status_button.setFixedSize(28, 28)
        # self.test_status_button.setIcon(QIcon())
        self.test_status_button.setStyleSheet(f"background-color: #{btn_color_secondary}; border-radius: {border_radius}px;")        


        buttons_layout.addWidget(self.line_edit_file,  0, 0, 1, 1)
        buttons_layout.addWidget(self.open_button,     0, 1, 1, 1)
        buttons_layout.addWidget(self.check_button,    1, 0, 1, 2)

        buttons_layout.addWidget(self.test_status_label,     2, 0, 1, 1)
        buttons_layout.addWidget(self.test_status_button,    2, 1, 1, 1, alignment=Qt.AlignRight)



        spacerItem = QSpacerItem(20, 40, QSizePolicy.Maximum, QSizePolicy.Expanding)
        buttons_layout.addItem(spacerItem)
        # buttons_layout.setContentsMargins(0, 0, 0, 0)


        wires_layout.addWidget(self.wires_table)
        wires_layout.addWidget(buttons_group)
        wires_group.setLayout(wires_layout)


        main_layout.addWidget(wires_group)

    

    def to_update_data_to_test(self):

        border_radius = 14
        btn_color_secondary = "6C757D"
        btn_color_success = "28A745"
        btn_color_warning = "FFC107"
        btn_color_danger  = "DC3545"

        if self.update_data_to_test == 0:
            self.update_data_to_test_text = "Данные прозвонки не загружены"
            self.test_status_button.setIcon(QIcon(self.icon.error_icon))
            color = btn_color_secondary
        if self.update_data_to_test == 1:
            self.update_data_to_test_text = "Данные прозвонки обновлены"
            self.test_status_button.setIcon(QIcon(self.icon.check_mark_icon))
            color = btn_color_success
        if self.update_data_to_test == 2:
            self.update_data_to_test_text = "Данные прозвонки необходимо обновить"
            self.test_status_button.setIcon(QIcon(self.icon.alert_icon))
            color = btn_color_warning

        self.test_status_label.setText(self.update_data_to_test_text)
        self.test_status_button.setStyleSheet(f"background-color: #{color}; border-radius: {border_radius}px;")        




    def read_from_csv(self):
        start_dir = "wire_list/"

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть файл",
            start_dir,
            "CSV файлы (*.csv);;Все файлы (*.*)"
        )

        if not file_path:
            return  # Отмена

        try:
            with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
                reader = csv.reader(file, delimiter=";")
                rows = list(reader)

            if not rows:
                QMessageBox.warning(self, "Ошибка", "Файл пуст")
                return

            headers = rows[0]
            data_rows = rows[1:]

            self.wire_data_from_file = data_rows
            print(self.wire_data_from_file)

            # Проверяем количество столбцов
            if len(headers) != self.wires_table.columnCount():
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Неверный формат файла (не совпадает количество столбцов)"
                )
                return

            # Очищаем таблицу
            self.wires_table.clearContents()
            self.wires_table.setRowCount(0)

            # Загружаем данные в таблицу
            self.line_edit_file.setText(os.path.basename(file_path))

            QMessageBox.information(
                self,
                "Информация",
                f"Файл {os.path.basename(file_path)} успешно загружен"
            )

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))




    def do_check(self):
        intersections_array = []

        # формируем фактические замыкания
        for row_index, row in enumerate(self.read_bit_rows):
            mirrored = row[::-1]
            zero_indexes = [i for i, bit in enumerate(mirrored) if bit == 0]
            intersections = [i for i in zero_indexes if i != row_index]
            intersections_array.append(intersections)

        table = self.wires_table
        table.setRowCount(len(intersections_array)) #возможно нужно задавать количество строк по количеству строк из CSV

        for i, intersections in enumerate(intersections_array):
            
            pin = i + 1

            # номер вывода
            item = QTableWidgetItem(str(pin))
            item.setTextAlignment(Qt.AlignCenter)
            table.setItem(i, 1, item)

            # ---------- ФАКТ ----------
            fact = {j + 1 for j in intersections} #фактические пересечения
            print(fact)

            # ---------- ОЖИДАЕМОЕ ----------  // это из CSV файла
            text = self.wire_data_from_file[i][2]
            expected = set()
            for part in text.split(","):
                part = part.strip()
                if part.isdigit():
                    expected.add(int(part))
            # print(expected)

            # ---------- ВИДЖЕТ ДЛЯ КНОПОК ----------
            cell_widget = QWidget()
            layout = QHBoxLayout(cell_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(4)
            layout.setAlignment(Qt.AlignCenter)  # вертикальное выравнивание



            btn_color_success = "28A745"
            btn_color_warning = "FFC107"
            btn_color_danger  = "DC3545"

            for other_pin in sorted(fact | expected):

                if other_pin in fact and other_pin in expected:
                    color = btn_color_success     # 🟢 есть и ожидали
                elif other_pin in fact and other_pin not in expected:
                    color = btn_color_danger      # 🔴 есть, но не ожидали
                else:
                    color = btn_color_warning     # 🟡 ожидали, но нет

                btn = QPushButton(str(other_pin))
                btn.setEnabled(False)
                btn.setFixedSize(28, 28)

                btn.setStyleSheet(
                    f"background-color: #{color}; border-radius: 14px; color: white;"
                )

                layout.addWidget(btn)

            table.setCellWidget(i, 2, cell_widget)