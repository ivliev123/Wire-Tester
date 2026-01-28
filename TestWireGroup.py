from PyQt5.QtWidgets import (
    QWidget, QGroupBox, QLabel, 
    QGridLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QHBoxLayout, QSpacerItem, 
    QSizePolicy, QLineEdit, QMessageBox, QFileDialog,
    QAbstractItemView, QCheckBox
)
from PyQt5.QtGui import QPixmap, QColor, QIcon, QFont
from PyQt5.QtCore import Qt, pyqtSignal

import csv
import os

from IconModul import icon

from MessageWindows import WarningWindow
from MessageWindows import DangerWindow
from MessageWindows import SuccessWindow
from MessageWindows import InfoWindow



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
        # self.to_update_data_to_test()

    
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

        self.wires_table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.wires_table.setSelectionBehavior(QTableWidget.SelectRows)

        # self.wires_table.doubleClicked.connect(self.on_wire_double_clicked)
        
        # Кнопки управления
        buttons_group = QGroupBox()
        buttons_group.setMaximumSize(1000, 200)
        buttons_layout = QGridLayout(buttons_group)

        check_box_group = QGroupBox()
        check_box_layout = QGridLayout(check_box_group)

        self.check_box_num =  QCheckBox('Номер вывода', self)
        self.check_box_num.toggle()
        self.check_box_num.stateChanged.connect(self.update_buttons_text)

        self.check_box_name = QCheckBox('Наименование разъема(вывода)', self)
        self.check_box_name.toggle()
        self.check_box_name.stateChanged.connect(self.update_buttons_text)


        self.line_edit_file = QLineEdit()
        self.line_edit_file.setStyleSheet('background : #ccc; ')
        self.line_edit_file.setReadOnly(1)

        self.open_button = QPushButton("Открыть")
        self.open_button.setIcon(self.icon.open_folder_icon)
        self.open_button.clicked.connect(self.read_from_csv)
        
        self.check_button = QPushButton("Проверка")
        self.check_button.setIcon(self.icon.search_icon)
        self.check_button.clicked.connect(self.do_check)

        self.save_button = QPushButton("Сохранить результаты проверки")
        self.save_button.setIcon(self.icon.save_icon)
        self.save_button.clicked.connect(self.save_check_result)


        # self.test_status_label = QLabel("")
        # border_radius = 14
        # btn_color_secondary = "6C757D"
        # btn_color_success = "28A745"
        # btn_color_warning = "FFC107"
        # btn_color_danger  = "DC3545"

        # # тут иконку состояния в виде кнопки 
        # self.test_status_button = QPushButton("")
        # # self.test_status_button.setMinimumSize(30, 30)
        # self.test_status_button.setFixedSize(28, 28)
        # # self.test_status_button.setIcon(QIcon())
        # self.test_status_button.setStyleSheet(f"background-color: #{btn_color_secondary}; border-radius: {border_radius}px;")        


        check_box_layout.addWidget(self.check_box_num,  0, 0, 1, 1)
        check_box_layout.addWidget(self.check_box_name,  0, 1, 1, 1)

        buttons_layout.addWidget(check_box_group,  0, 0, 1, 2)

        buttons_layout.addWidget(self.line_edit_file,  1, 0, 1, 1)
        buttons_layout.addWidget(self.open_button,     1, 1, 1, 1)
        buttons_layout.addWidget(self.check_button,    2, 0, 1, 2)
        buttons_layout.addWidget(self.save_button,     3, 0, 1, 2)
        

        # buttons_layout.addWidget(self.test_status_label,     4, 0, 1, 1)
        # buttons_layout.addWidget(self.test_status_button,    4, 1, 1, 1, alignment=Qt.AlignRight)



        spacerItem = QSpacerItem(20, 40, QSizePolicy.Maximum, QSizePolicy.Expanding)
        buttons_layout.addItem(spacerItem)
        # buttons_layout.setContentsMargins(0, 0, 0, 0)


        wires_layout.addWidget(self.wires_table)
        wires_layout.addWidget(buttons_group)
        wires_group.setLayout(wires_layout)


        main_layout.addWidget(wires_group)

    

    # def to_update_data_to_test(self):

    #     border_radius = 14
    #     btn_color_secondary = "6C757D"
    #     btn_color_success = "28A745"
    #     btn_color_warning = "FFC107"
    #     btn_color_danger  = "DC3545"

    #     if self.update_data_to_test == 0:
    #         self.update_data_to_test_text = "Данные прозвонки отсутствуют"
    #         self.test_status_button.setIcon(QIcon(self.icon.error_icon))
    #         color = btn_color_secondary
    #     if self.update_data_to_test == 1:
    #         self.update_data_to_test_text = "Данные прозвонки обновлены"
    #         self.test_status_button.setIcon(QIcon(self.icon.check_mark_icon))
    #         color = btn_color_success

    #     self.test_status_label.setText(self.update_data_to_test_text)
    #     self.test_status_button.setStyleSheet(f"background-color: #{color}; border-radius: {border_radius}px;")        




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
                # QMessageBox.warning(self, "Ошибка", "Файл пуст")
                self.WarningWindow  = WarningWindow("Ошибка. Файл пуст")
                self.WarningWindow.Window.show()
                return

            headers = rows[0]
            data_rows = rows[1:]

            self.wire_data_from_file = data_rows
            print(self.wire_data_from_file)

            # Проверяем количество столбцов
            if len(headers) != self.wires_table.columnCount():
                # QMessageBox.warning(
                #     self,
                #     "Ошибка",
                #     "Неверный формат файла (не совпадает количество столбцов)"
                # )
                self.DangerWindow = DangerWindow("Ошибка. Неверный формат файла (не совпадает количество столбцов)")
                self.DangerWindow.Window.show()
                return

            # Очищаем таблицу
            self.wires_table.clearContents()
            self.wires_table.setRowCount(0)

            # Загружаем данные в таблицу
            self.line_edit_file.setText(os.path.basename(file_path))

            # QMessageBox.information(
            #     self,
            #     "Информация",
            #     f"Файл {os.path.basename(file_path)} успешно загружен"
            # )
            self.InfoWindow = InfoWindow(f"Файл {os.path.basename(file_path)} успешно загружен")
            self.InfoWindow.Window.show()

        except Exception as e:
            # QMessageBox.critical(self, "Ошибка", str(e))
            print(str(e))


    def make_btn_text(self, pin_number, socket_name):
        if self.check_box_num.isChecked() and self.check_box_name.isChecked():
            return f"{pin_number}: {socket_name}"
        elif self.check_box_num.isChecked():
            return f"{pin_number}"
        elif self.check_box_name.isChecked():
            return f"{socket_name}"
        else:
            return ""


    def update_buttons_text(self):
        table = self.wires_table

        for row in range(table.rowCount()):
            cell_widget = table.cellWidget(row, 2)
            if not cell_widget:
                continue

            layout = cell_widget.layout()
            for i in range(layout.count()):
                btn = layout.itemAt(i).widget()
                if not btn:
                    continue

                pin = btn.property("pin_number")
                socket = btn.property("socket_name")

                btn.setText(self.make_btn_text(pin, socket))
                btn.adjustSize()

        table.resizeColumnToContents(2)

            

    def do_check(self):

        total_ok = 0
        total_warning = 0
        total_error = 0

        table = self.wires_table
        table.clearContents()

        # ---------- формируем фактические замыкания ----------
        intersections_array = []
        for row_index, row in enumerate(self.read_bit_rows):
            mirrored = row[::-1]
            zero_indexes = [i for i, bit in enumerate(mirrored) if bit == 0]
            intersections = [i for i in zero_indexes if i != row_index]
            intersections_array.append(intersections)

        table.setRowCount(len(intersections_array))

        BTN_SIZE = 28
        SPACING = 4
        MARGINS = 8

        btn_color_success = "28A745"
        btn_color_warning = "FFC107"
        btn_color_danger  = "DC3545"

        max_column_width = 0  # запомним максимальную ширину для столбца

        # ---------- обработка строк ----------
        for i, intersections in enumerate(intersections_array):

            
            item_soket = QTableWidgetItem(str(self.wire_data_from_file[i][0]))
            item_soket.setTextAlignment(Qt.AlignLeft)
            table.setItem(i, 0, item_soket)

            pin = i + 1

            # --- номер вывода ---
            item = QTableWidgetItem(str(pin))
            # item.setTextAlignment(Qt.AlignCenter)
            item.setTextAlignment(Qt.AlignLeft)
            table.setItem(i, 1, item)

            # ---------- ФАКТ ----------
            fact = {j + 1 for j in intersections}

            # ---------- ОЖИДАЕМОЕ (из CSV) ----------
            expected = set()
            if i < len(self.wire_data_from_file):
                text = self.wire_data_from_file[i][2]
                for part in text.split(","):
                    part = part.strip()
                    if part.isdigit():
                        expected.add(int(part))

            # ---------- анализ ----------
            ok = fact & expected
            warning = expected - fact
            error = fact - expected

            total_ok += len(ok)
            total_warning += len(warning)
            total_error += len(error)

            # ---------- виджет с кнопками ----------
            cell_widget = QWidget()
            layout = QHBoxLayout(cell_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(SPACING)
            # layout.setAlignment(Qt.AlignCenter)
            layout.setAlignment(Qt.AlignLeft)

            all_pins = sorted(fact | expected)
            btn_count = len(all_pins)

            for other_pin in all_pins:

                if other_pin in fact and other_pin in expected:
                    color = btn_color_success     # 🟢 есть и ожидали
                elif other_pin in fact and other_pin not in expected:
                    color = btn_color_danger      # 🔴 есть, но не ожидали
                else:
                    color = btn_color_warning     # 🟡 ожидали, но нет

                # вот здесь менять текст в зависимости от check_box

                soket_pin_name = self.wire_data_from_file[other_pin - 1][0]
                btn_text = self.make_btn_text(other_pin, soket_pin_name)

                # if (self.check_box_num.isChecked() and self.check_box_name.isChecked()):
                #     btn_text = f"{other_pin}: {soket_pin_name}"
                # elif (self.check_box_num.isChecked() and not self.check_box_name.isChecked()):
                #     btn_text = f"{other_pin}"
                # elif (not self.check_box_num.isChecked() and self.check_box_name.isChecked()):
                #     btn_text = f"{soket_pin_name}"
                # else:
                #     btn_text = f""

                btn = QPushButton(btn_text)
                btn.setEnabled(False)

                btn.setProperty("pin_number", other_pin)
                btn.setProperty("socket_name", soket_pin_name)

                btn.setStyleSheet(
                    f"""
                    background-color: #{color};
                    border-radius: 12px;
                    color: white;
                    padding: 6px 12px;
                    """
                )

                btn.adjustSize()

                layout.addWidget(btn)

            table.setCellWidget(i, 2, cell_widget)


        # ---------- применяем ширину ----------
        table.resizeColumnToContents(2)

        # ---------- итоговая оценка ----------
        if total_error > 0:
            self.DangerWindow = DangerWindow(
                f"Обнаружены критические ошибки!\n"
                f"OK: {total_ok}, WARNING: {total_warning}, ERROR: {total_error}"
            )
            self.DangerWindow.Window.show()

        elif total_warning > 0:
            self.WarningWindow = WarningWindow(
                f"Есть отклонения.\n"
                f"OK: {total_ok}, WARNING: {total_warning}"
            )
            self.WarningWindow.Window.show()

        else:
            self.SuccessWindow = SuccessWindow(
                f"Проверка успешна.\n"
                f"Все соединения корректны ({total_ok})"
            )
            self.SuccessWindow.Window.show()





    def save_check_result(self):
        if not self.wire_data_from_file or self.wires_table.rowCount() == 0:
            self.WarningWindow = WarningWindow("Нет данных для сохранения")
            self.WarningWindow.Window.show()
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить результаты проверки",
            "check_result.xlsx",
            "Excel файлы (*.xlsx)"
        )

        if not file_path:
            return

        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font
            from openpyxl.styles import Border, Side

            wb = Workbook()
            ws = wb.active
            ws.title = "Проверка проводов"

            # ---------- Заголовки ----------
            headers = ["Разъём", "Вывод", "OK", "WARNING", "ERROR"]
            ws.append(headers)

            for col in range(1, len(headers) + 1):
                ws.cell(row=1, column=col).font = Font(bold=True)

            # ---------- Данные ----------
            for row in range(self.wires_table.rowCount()):
                pin = row + 1

                # ---------- ОЖИДАЕМОЕ ----------
                expected_text = self.wire_data_from_file[row][2]
                expected = set()
                for part in expected_text.split(","):
                    part = part.strip()
                    if part.isdigit():
                        expected.add(int(part))

                # ---------- ФАКТИЧЕСКОЕ ----------
                fact = set()
                cell_widget = self.wires_table.cellWidget(row, 2)
                if cell_widget:
                    for i in range(cell_widget.layout().count()):
                        btn = cell_widget.layout().itemAt(i).widget()
                        if btn:
                            fact.add(int(btn.text()))

                ok = sorted(fact & expected)
                warning = sorted(expected - fact)
                error = sorted(fact - expected)

                ws.append([
                    "",                       # Разъём (можно позже заполнить)
                    pin,
                    ", ".join(map(str, ok)),
                    ", ".join(map(str, warning)),
                    ", ".join(map(str, error))
                ])

            # ---------- Автоширина ----------
            for column_cells in ws.columns:
                length = max(len(str(cell.value)) if cell.value else 0 for cell in column_cells)
                ws.column_dimensions[column_cells[0].column_letter].width = length + 4


            thin = Side(style="thin")
            border = Border(left=thin, right=thin, top=thin, bottom=thin)

            for row in ws.iter_rows(
                min_row=1,
                max_row=ws.max_row,
                min_col=1,
                max_col=ws.max_column
            ):
                for cell in row:
                    cell.border = border


            wb.save(file_path)

            self.SuccessWindow = SuccessWindow("Результаты проверки сохранены")
            self.SuccessWindow.Window.show()

        except Exception as e:
            self.DangerWindow = DangerWindow(f"Ошибка сохранения:\n{e}")
            self.DangerWindow.Window.show()