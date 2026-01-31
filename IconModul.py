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

