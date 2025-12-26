import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

class IconTest(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест иконки")
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        # 1. Проверяем пути
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Текущая директория файла: {current_dir}")
        
        # 2. Пробуем несколько путей
        possible_paths = [
            'icons/tester.png',
            os.path.join(current_dir, 'icons', 'tester.png'),
            os.path.join(current_dir, '..', 'icons', 'tester.png'),
            os.path.join(current_dir, '../icons/tester.png'),
            'tester.png'
        ]
        
        found_icon = None
        for path in possible_paths:
            print(f"Проверяю: {path}")
            print(f"  Существует: {os.path.exists(path)}")
            if os.path.exists(path):
                found_icon = path
                print(f"  ✓ Найден: {os.path.abspath(path)}")
                break
        
        # 3. Создаем кнопку
        if found_icon:
            self.button = QPushButton("Прозвонить")
            icon = QIcon(found_icon)
            
            # Проверяем загрузилась ли иконка
            if icon.isNull():
                self.button.setText("❌ Иконка не загрузилась")
                print("Иконка не загрузилась - файл поврежден или не поддерживаемый формат")
            else:
                self.button.setIcon(icon)
                self.button.setIconSize(QSize(32, 32))
                print("✅ Иконка загружена")
        else:
            self.button = QPushButton("❌ Файл иконки не найден")
            print("❌ Файл иконки не найден ни по одному из путей")
            
            # Выводим список файлов в папках
            print("\nСодержимое текущей директории:")
            try:
                for item in os.listdir(current_dir):
                    print(f"  {item}")
            except:
                pass
                
            print("\nПроверьте что файл tester.png находится в папке icons/ рядом с этим файлом")
        
        layout.addWidget(self.button)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IconTest()
    window.show()
    sys.exit(app.exec_())