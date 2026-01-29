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

        # сортировка
        # self.wires_table.setSortingEnabled(True)
        # # Если нужно настроить сортировку по умолчанию:
        # self.wires_table.sortByColumn(0, Qt.AscendingOrder)  # Сортировка по первому столбцу

        # self.wires_table.doubleClicked.connect(self.on_wire_double_clicked)
        


        # Кнопки управления
        buttons_group_main = QGroupBox()
        buttons_group_main.setMaximumSize(1000, 220)
        buttons_layout_main = QGridLayout(buttons_group_main)

        # 1
        buttons_group_1 = QGroupBox()
        buttons_layout_1 = QGridLayout(buttons_group_1)


        self.line_test_file = QLineEdit()
        self.line_test_file.setStyleSheet('background : #ccc; ')
        self.line_test_file.setReadOnly(1)
        self.line_test_file.setPlaceholderText("Выберите файл для тестирования...")

        self.open_button = QPushButton("Открыть")
        self.open_button.setIcon(self.icon.open_folder_icon)
        self.open_button.clicked.connect(self.read_from_csv)
        
        self.check_button = QPushButton("Проверка")
        self.check_button.setIcon(self.icon.search_icon)
        self.check_button.clicked.connect(self.do_check)

        self.save_button = QPushButton("Сохранить результаты проверки")
        self.save_button.setIcon(self.icon.save_icon)
        self.save_button.clicked.connect(self.save_check_result)

        buttons_layout_1.addWidget(self.line_test_file,  1, 0, 1, 1)
        buttons_layout_1.addWidget(self.open_button,     1, 1, 1, 1)
        buttons_layout_1.addWidget(self.check_button,    2, 0, 1, 2)
        buttons_layout_1.addWidget(self.save_button,     3, 0, 1, 2)
        
        # 2
        check_box_group = QGroupBox()
        check_box_layout = QGridLayout(check_box_group)

        self.check_box_num =  QCheckBox('Номер вывода', self)
        self.check_box_num.toggle()
        self.check_box_num.stateChanged.connect(self.update_buttons_text)

        self.check_box_name = QCheckBox('Наименование разъема(вывода)', self)
        self.check_box_name.toggle()
        self.check_box_name.stateChanged.connect(self.update_buttons_text)

        check_box_layout.addWidget(self.check_box_num,  0, 0, 1, 1)
        check_box_layout.addWidget(self.check_box_name,  0, 1, 1, 1)


        buttons_layout_main.addWidget(buttons_group_1)
        buttons_layout_main.addWidget(check_box_group)

        spacerItem = QSpacerItem(20, 40, QSizePolicy.Maximum, QSizePolicy.Expanding)
        buttons_layout_main.addItem(spacerItem)

        wires_layout.addWidget(self.wires_table)
        wires_layout.addWidget(buttons_group_main)
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
            self.line_test_file.setText(os.path.basename(file_path))

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
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

            wb = Workbook()
            ws = wb.active
            ws.title = "Проверка проводов"

            # ---------- Стили ----------
            header_font = Font(bold=True)
            center_alignment = Alignment(horizontal='center', vertical='center')
            thin = Side(style="thin")
            border = Border(left=thin, right=thin, top=thin, bottom=thin)
            
            # Цвета для заливки ячеек
            ok_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")  # Зеленый
            warning_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")  # Желтый
            error_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")  # Красный

            # ---------- Заголовки ----------
            headers = ["№", "Разъём", "Вывод", "OK", "WARNING", "ERROR"]
            ws.append(headers)
            
            # Стилизация заголовков
            for col in range(1, len(headers) + 1):
                cell = ws.cell(row=1, column=col)
                cell.font = header_font
                cell.alignment = center_alignment
                cell.border = border

            # ---------- Данные ----------
            row_num = 2
            total_ok_count = 0
            total_warning_count = 0
            total_error_count = 0
            
            for table_row in range(self.wires_table.rowCount()):
                pin = table_row + 1
                
                # Получаем наименование разъема из таблицы
                socket_item = self.wires_table.item(table_row, 0)
                socket_name = socket_item.text() if socket_item else ""
                
                # ---------- ОЖИДАЕМОЕ ----------
                expected_text = self.wire_data_from_file[table_row][2] if table_row < len(self.wire_data_from_file) else ""
                expected = set()
                for part in expected_text.split(","):
                    part = part.strip()
                    if part.isdigit():
                        expected.add(int(part))

                # ---------- ФАКТИЧЕСКОЕ ----------
                fact = set()
                ok_details = []
                warning_details = []
                error_details = []
                
                cell_widget = self.wires_table.cellWidget(table_row, 2)
                if cell_widget:
                    for i in range(cell_widget.layout().count()):
                        btn = cell_widget.layout().itemAt(i).widget()
                        if btn:
                            pin_num = btn.property("pin_number")
                            socket_name_other = btn.property("socket_name") if btn.property("socket_name") else ""
                            fact.add(pin_num)
                            
                            # Определяем тип соединения по цвету кнопки
                            btn_style = btn.styleSheet()
                            
                            # Формируем строку с информацией о соединении
                            if self.check_box_num.isChecked() and self.check_box_name.isChecked():
                                connection_str = f"{pin_num}: {socket_name_other}"
                            elif self.check_box_num.isChecked():
                                connection_str = f"{pin_num}"
                            elif self.check_box_name.isChecked():
                                connection_str = f"{socket_name_other}"
                            else:
                                connection_str = f"{pin_num}"
                            
                            # Распределяем по соответствующим столбцам
                            if "#28A745" in btn_style:  # OK
                                ok_details.append(connection_str)
                                total_ok_count += 1
                            elif "#DC3545" in btn_style:  # ERROR
                                error_details.append(connection_str)
                                total_error_count += 1
                            else:  # WARNING
                                warning_details.append(connection_str)
                                total_warning_count += 1

                # Также добавляем WARNING для ожидаемых, но не найденных соединений
                for pin_num in expected:
                    if pin_num not in fact:  # Ожидалось, но не найдено
                        if pin_num <= len(self.wire_data_from_file):
                            socket_name_other = self.wire_data_from_file[pin_num - 1][0]
                        else:
                            socket_name_other = f"Неизвестный ({pin_num})"
                        
                        if self.check_box_num.isChecked() and self.check_box_name.isChecked():
                            warning_details.append(f"{pin_num}: {socket_name_other}")
                        elif self.check_box_num.isChecked():
                            warning_details.append(str(pin_num))
                        elif self.check_box_name.isChecked():
                            warning_details.append(socket_name_other)
                        else:
                            warning_details.append(str(pin_num))
                        
                        # Не увеличиваем счетчик здесь, так как это не фактическое соединение

                # Добавляем строку в Excel
                ws.append([
                    table_row + 1,  # Порядковый номер
                    socket_name,  # Наименование разъема
                    pin,  # Номер вывода
                    "\n".join(ok_details),  # OK соединения
                    "\n".join(warning_details),  # WARNING соединения
                    "\n".join(error_details)  # ERROR соединения
                ])
                
                # Применяем стили к ячейкам
                for col in range(1, 7):  # 6 столбцов
                    cell = ws.cell(row=row_num, column=col)
                    cell.border = border
                    cell.alignment = Alignment(wrap_text=True, vertical='top')
                
                # Заливка ячеек в зависимости от наличия данных
                if error_details:
                    ws.cell(row=row_num, column=6).fill = error_fill  # ERROR
                if warning_details:
                    ws.cell(row=row_num, column=5).fill = warning_fill  # WARNING
                if ok_details and not error_details and not warning_details:
                    ws.cell(row=row_num, column=4).fill = ok_fill  # OK
                
                row_num += 1

            # ---------- Автоширина с учетом переноса текста ----------
            for column_cells in ws.columns:
                max_length = 0
                column = column_cells[0].column_letter
                
                for cell in column_cells:
                    try:
                        if cell.value:
                            # Учитываем перенос строк
                            lines = str(cell.value).split('\n')
                            max_line_length = max(len(line) for line in lines)
                            if max_line_length > max_length:
                                max_length = max_line_length
                    except:
                        pass
                
                adjusted_width = min(max_length + 4, 50)  # Максимальная ширина 50 символов
                ws.column_dimensions[column].width = adjusted_width

            # ---------- Замерзшие области для удобства просмотра ----------
            ws.freeze_panes = "B2"

            # ---------- Итоговая статистика ----------
            if row_num > 2:  # Если есть данные
                ws.append([])  # Пустая строка
                
                stats_row = row_num + 1
                ws.append([
                    "", 
                    "ИТОГО:", 
                    "", 
                    f"OK: {total_ok_count}", 
                    f"WARNING: {total_warning_count}", 
                    f"ERROR: {total_error_count}"
                ])
                
                # Стилизация строки с итогами
                for col in range(2, 7):
                    cell = ws.cell(row=stats_row, column=col)
                    cell.font = Font(bold=True)
                    cell.border = border

            wb.save(file_path)

            self.SuccessWindow = SuccessWindow(f"Результаты проверки сохранены в:\n{os.path.basename(file_path)}")
            self.SuccessWindow.Window.show()

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Ошибка при сохранении: {error_details}")
            self.DangerWindow = DangerWindow(f"Ошибка сохранения:\n{str(e)}")
            self.DangerWindow.Window.show()