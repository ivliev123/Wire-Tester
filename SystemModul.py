from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QIcon



class icon(QWidget):
    def __init__(self):

        self.tester_icon = QIcon('icons/tester.png')
        self.right_arrow_icon = QIcon('icons/right-arrow.png')
        self.send_icon = QIcon('icons/send.png')
        self.search_icon = QIcon('icons/search.png')

        self.open_folder_icon = QIcon('icons/open-folder.png')
        self.save_icon = QIcon('icons/save.png')
        self.usb_icon = QIcon('icons/usb.png')

        self.alert_icon = QIcon('icons/alert.png')
        self.check_mark_icon = QIcon('icons/check-mark.png')
        self.error_icon = QIcon('icons/error.png')
        self.info_icon = QIcon('icons/info.png')
        self.write_icon = QIcon('icons/write.png')



class Constants:
        
    """Класс для хранения констант и названий элементов интерфейса"""
    
    # Названия таблиц и групп
    READ_TABLE_GROUP_TITLE = "Прозвонка провода"
    TEST_TABLE_GROUP_TITLE = "Проверка провода"
    EDIT_TABLE_GROUP_TITLE = "Редактирование провода"

    # Заголовки таблиц
    TABLE_HEADERS = {
        "wire_test": ["Разъем", "Вывод", "Вывод"]
    }
    
    # Тексты для кнопок
    BUTTON_TEXTS = {
        "open": "Открыть",
        "save_accord_table": "Сохранить таблицу соответствия как",
        
        "read": "Прозвонка",
        "to_edit": "На редактирование",

        "check": "Проверка",
        "save_check_result": "Сохранить результаты проверки",

        "save": "Сохранить",
        
        "num_pin": "Номер вывода",
        "socket_name": "Наименование разъема(вывода)"
    }
    
    # Тексты для полей ввода
    PLACEHOLDER_TEXTS = {
        "read_file_select": "Выберите таблицу соответствия...",
        "test_file_select": "Выберите файл для тестирования...",
        "edit_file_select": "Выберите файл для просмотра и редактирования..."
    }
    
    # # Тексты для диалоговых окон
    # DIALOG_TITLES = {
    #     "open_file": "Открыть файл",
    #     "save_file": "Сохранить результаты проверки"
    # }
    
    # # Фильтры файлов
    # FILE_FILTERS = {
    #     "csv": "CSV файлы (*.csv);;Все файлы (*.*)",
    #     "excel": "Excel файлы (*.xlsx)"
    # }
    
    # Начальные директории
    DIRECTORIES = {
        "wire_dataset": "_База данных проводов/",
        "accod_table_dataset": "_База данных таблиц соответствий/",

        "default_save": "check_result.xlsx"
    }
    
    OK_translate        = "Корректные соединения"
    WARNING_translate   = "Отсутствующие соединения"
    ERROR_translate     = "Некорректные соединения"

    # ok = 0
    # warning = 0
    # error = 0
    # Сообщения об ошибках и уведомления
    MESSAGES = {
        "empty_file": "Ошибка. Файл пуст",
        "wrong_format": "Ошибка. Неверный формат файла (не совпадает количество столбцов)",
        "file_loaded": "Файл {filename} успешно загружен",
        "no_data": "Нет данных для сохранения",
        "save_success": "Результаты проверки сохранены в:\n{filename}",
        "save_error": "Ошибка сохранения:\n{error}",
        # "critical_errors": "Обнаружены критические ошибки!\nOK: {ok}, WARNING: {warning}, ERROR: {error}",
        # "deviations": "Есть отклонения.\nOK: {ok}, WARNING: {warning}",
        # "success_check": "Проверка успешна.\nВсе соединения корректны ({ok})",
    
        
        "error_check_result"    : "Обнаружены ошибки соединений!\n"+
                                OK_translate        + ": {ok},\n" +
                                WARNING_translate   + ": {warning},\n" +
                                ERROR_translate     + ": {error}",
        "warning_check_result"  : "Обнаружены ошибки соединений!\n"+
                                OK_translate        + ": {ok},\n" +
                                WARNING_translate   + ": {warning},\n",
        "success_check_result"  : "Проверка успешна.\nВсе соединения корректны ({ok})"
    }
    
    # Названия листов Excel
    EXCEL_SHEETS = {
        "main": "Проверка проводов"
    }
    
    # Заголовки Excel
    EXCEL_HEADERS = ["№", "Разъём", "Вывод", OK_translate, WARNING_translate, ERROR_translate]
    
    # Цвета для кнопок
    COLORS = {
        "success": "28A745",
        "warning": "FFC107",
        "danger": "DC3545"
    }
    
    # Стили CSS
    STYLES = {
        "readonly_line": "background : #ccc;",
        "success_button": """
            background-color: #28A745;
            border-radius: 12px;
            color: white;
            padding: 6px 12px;
        """,
        "warning_button": """
            background-color: #FFC107;
            border-radius: 12px;
            color: white;
            padding: 6px 12px;
        """,
        "danger_button": """
            background-color: #DC3545;
            border-radius: 12px;
            color: white;
            padding: 6px 12px;
        """
    }
    
    # Константы размеров
    SIZES = {
        "min_x": 30,
        "min_y": 30,
        "button_size": 28,
        "button_spacing": 4,
        "button_margins": 8,
        "max_button_width": 1000,
        "max_button_height": 220
    }
    
    # Excel стили
    EXCEL_STYLES = {
        "ok_fill": {"start_color": "C6EFCE", "end_color": "C6EFCE", "fill_type": "solid"},
        "warning_fill": {"start_color": "FFEB9C", "end_color": "FFEB9C", "fill_type": "solid"},
        "error_fill": {"start_color": "FFC7CE", "end_color": "FFC7CE", "fill_type": "solid"}
    }