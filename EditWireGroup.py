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


class EditWireGroup(QWidget):  # QWidget вместо QMainWindow
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

        self.init_ui()
    
    def init_ui(self):
        # Основной layout
        main_layout = QVBoxLayout(self)
        
        # 1. Группа с таблицей проводов (верхняя часть)
        wires_group = QGroupBox("Редактирование провода")
        wires_layout = QVBoxLayout()
        
        # Таблица для отображения проводов
        self.wires_table = QTableWidget()
        self.wires_table.setColumnCount(3)
        self.wires_table.setHorizontalHeaderLabels([
            "Разъем", "Вывод", "Вывод"
        ])
        self.wires_table.setSelectionBehavior(QTableWidget.SelectRows)
        # self.wires_table.doubleClicked.connect(self.on_wire_double_clicked)
        self.wires_table.itemChanged.connect(self.on_table_item_changed)
        self.wires_table.blockSignals(True) # запрещаем механизм изменения по редактированию...

        
        # Кнопки управления
        buttons_group = QGroupBox()
        buttons_group.setMaximumSize(1000, 150)
        buttons_layout = QGridLayout(buttons_group)


        self.line_file_name = QLineEdit()
        self.line_file_name.setStyleSheet('background : #ccc; ')
        self.line_file_name.setReadOnly(1)

        self.open_button = QPushButton("Открыть")
        self.open_button.setIcon(self.icon.open_folder_icon)
        self.open_button.clicked.connect(self.read_from_csv)

        self.save_button = QPushButton("Сохранить")
        self.save_button.setIcon(self.icon.save_icon)
        self.save_button.clicked.connect(self.save_as_csv)
        
        buttons_layout.addWidget(self.line_file_name, 0, 0, 1, 1)
        buttons_layout.addWidget(self.open_button,    0, 1, 1, 1)
        buttons_layout.addWidget(self.save_button,    1, 0, 1, 2)


        spacerItem = QSpacerItem(20, 40, QSizePolicy.Maximum, QSizePolicy.Expanding)
        buttons_layout.addItem(spacerItem)

        

        wires_layout.addWidget(self.wires_table)
        wires_layout.addWidget(buttons_group)
        wires_group.setLayout(wires_layout)
        
        
        # Добавляем обе группы в основной layout
        main_layout.addWidget(wires_group)
        # main_layout.addWidget(details_group)
        
        # Инициализация состояния
        # self.clear_details()
        # self.update_buttons_state()


    def parse_intersections(self, text):
        """
        '1, 3,5' -> {1, 3, 5}
        """
        result = set()
        for part in text.split(","):
            part = part.strip()
            if part.isdigit():
                result.add(int(part))
        # print(result)
        return result

    def set_intersections(self, row, values):
        text = ", ".join(str(v) for v in sorted(values))
        item = self.wires_table.item(row, 2)
        if not item:
            item = QTableWidgetItem()
            self.wires_table.setItem(row, 2, item)
        item.setText(text) 




    def on_table_item_changed(self, item):
        if item.column() != 2:
            return

        table = self.wires_table
        row = item.row()
        current_pin = row + 1

        table.blockSignals(True)

        try:
            # новые связи из ячейки
            new_links = self.parse_intersections(item.text())

            # старые связи (до изменения)
            old_links = set()
            for r in range(table.rowCount()):
                if r == row:
                    continue
                cell = table.item(r, 2)
                if cell:
                    links = self.parse_intersections(cell.text())
                    if current_pin in links:
                        old_links.add(r + 1)

            # --- УДАЛЕНИЕ ---
            removed = old_links - new_links
            for pin in removed:
                r = pin - 1
                cell = table.item(r, 2)
                if cell:
                    links = self.parse_intersections(cell.text())
                    if current_pin in links:
                        links.remove(current_pin)
                        self.set_intersections(r, links)

            # --- ДОБАВЛЕНИЕ (группы) ---
            group = {current_pin} | new_links
            changed = True
            while changed:
                changed = False
                for r in range(table.rowCount()):
                    pin = r + 1
                    cell = table.item(r, 2)
                    links = self.parse_intersections(cell.text()) if cell else set()
                    if pin in group or links & group:
                        new_group = group | links | {pin}
                        if new_group != group:
                            group = new_group
                            changed = True

            for pin in group:
                self.set_intersections(pin - 1, group - {pin})

        finally:
            table.blockSignals(False)


    # механизм созранения и чтения из файла сделаем тут 
    def save_as_csv(self):

        start_dir = "wire_list/"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить файл",
            os.path.join(start_dir, "wires.csv"),
            "CSV файлы (*.csv);;Все файлы (*.*)"
        )

        if not file_path:
            return  # пользователь нажал «Отмена»

        # если пользователь не указал расширение
        if not file_path.lower().endswith(".csv"):
            file_path += ".csv"

        self.save_to_csv(file_path)



    def save_to_csv(self, file_path):
        if self.wires_table.rowCount() == 0:
            QMessageBox.information(self, "Информация", "Нет данных для сохранения")
            return False

        try:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file, delimiter=";")

                # заголовки
                headers = [
                    self.wires_table.horizontalHeaderItem(i).text()
                    for i in range(self.wires_table.columnCount())
                ]
                writer.writerow(headers)

                # данные
                for row in range(self.wires_table.rowCount()):
                    row_data = []
                    for col in range(self.wires_table.columnCount()):
                        item = self.wires_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)

            # self.line_file_name.setText(os.path.basename(file_path))
            # Information
            QMessageBox.information(self, "Информация", f"Файл {file_path} успешно сохранен")
            return True

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            return False



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

            # Загружаем данные
            self.wires_table.setRowCount(len(data_rows))

            for row_idx, row_data in enumerate(data_rows):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(value)
                    self.wires_table.setItem(row_idx, col_idx, item)

            # Обновляем имя файла
            self.line_file_name.setText(os.path.basename(file_path))

            QMessageBox.information(
                self,
                "Информация",
                f"Файл {os.path.basename(file_path)} успешно загружен"
            )

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
    


    def edit_visual(self, bit_rows):
        intersections_array = []

        self.wires_table.clearContents()
        self.wires_table.setRowCount(0)

        # при проходе по строкам нужно строку отзеркалить
        for row_index, row in enumerate(bit_rows):
            # 1. зеркалим строку
            mirrored = row[::-1]
            zero_indexes = [i for i, bit in enumerate(mirrored) if bit == 0]
            intersections = [i for i in zero_indexes if i != row_index]
            intersections_array.append(intersections)

        # далее реализовать таблицу в блоке edit
        wire_points = len(intersections_array)
        self.wires_table.setRowCount(wire_points)

        for point_i, intersections in enumerate(intersections_array):
            
            self.wires_table.setItem(point_i, 1, QTableWidgetItem(f"{point_i + 1}"))
            if intersections:
                intersections_text = ", ".join(str(i + 1) for i in intersections)
            else:
                intersections_text = ""

            self.wires_table.setItem(point_i, 2, QTableWidgetItem(intersections_text))

        # после добавления данных делаем запрет редактирования второго столбца 
        # Запрет редактирования для всего столбца 2 (второй столбец)
        
        for row in range(self.wires_table.rowCount()):
            item = self.wires_table.item(row, 1)
            if item:
                # item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Снимаем флаг редактирования
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

