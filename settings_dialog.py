from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, 
                             QListWidget, QInputDialog, QColorDialog, QFileDialog, QTabWidget, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
import subprocess

class SettingsDialog(QDialog):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.parent = parent
        self.config = config
        self.setWindowTitle("Настройки")
        self.setWindowFlags(self.windowFlags() | Qt.WindowSystemMenuHint | Qt.WindowMinMaxButtonsHint)
        
        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()

        self.init_general_tab()
        self.init_extensions_tab()

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def init_general_tab(self):
        general_tab = QWidget()
        general_layout = QVBoxLayout()

        # Добавляем новую кнопку для запуска игры
        self.game_btn = QPushButton("Запустить игру")
        self.game_btn.clicked.connect(self.launch_game)
        general_layout.addWidget(self.game_btn)

        general_tab.setLayout(general_layout)
        self.tabs.addTab(general_tab, "General")

        # Color picker
        self.color_btn = QPushButton("Изменить цвет окна")
        self.color_btn.clicked.connect(self.choose_color)
        general_layout.addWidget(self.color_btn)

        # Icon picker
        self.icon_btn = QPushButton("Изменить иконку")
        self.icon_btn.clicked.connect(self.choose_icon)
        general_layout.addWidget(self.icon_btn)

        # Search engine selector
        self.search_label = QLabel("ЛУЧШЕ НЕ ЖМИ:")
        self.search_combo = QComboBox()
        
        if hasattr(self.parent, 'search_engines') and self.parent.search_engines is not None:
            self.search_combo.addItems(list(self.parent.search_engines.keys()))
        else:
            default_engines = ["Google", "Bing", "DuckDuckGo"]
            self.search_combo.addItems(default_engines)
        
        self.search_combo.currentTextChanged.connect(self.parent.set_search_engine)
        general_layout.addWidget(self.search_label)
        general_layout.addWidget(self.search_combo)

        # Add new search engine
        self.add_search_btn = QPushButton("Добавить поисковую систему(НЕ НАЖИМАЙ)")
        self.add_search_btn.clicked.connect(self.add_search_engine)
        general_layout.addWidget(self.add_search_btn)

        general_tab.setLayout(general_layout)
        self.tabs.addTab(general_tab, "General")

    def launch_game(self):
        try:
            subprocess.Popen(["python", "game.py"])
        except Exception as e:
            print(f"Ошибка при запуске игры: {e}")

    def init_extensions_tab(self):
        extensions_tab = QWidget()
        extensions_layout = QVBoxLayout()
        self.extensions_list = QListWidget()
        extensions_layout.addWidget(self.extensions_list)
        
        add_extension_btn = QPushButton("Добавить расширение")
        add_extension_btn.clicked.connect(self.add_extension)
        extensions_layout.addWidget(add_extension_btn)

        extensions_tab.setLayout(extensions_layout)
        self.tabs.addTab(extensions_tab, "Расширения")

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.parent.set_background_color(color)

    def choose_icon(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Выбор иконки", "", "Image Files (*.png *.jpg *.bmp)")
        if filename:
            self.parent.set_icon(filename)

    def add_search_engine(self):
        name, ok = QInputDialog.getText(self, "Добавить поисковую систему", "Введите поисковую систему:")
        if ok and name:
            url, ok = QInputDialog.getText(self, "Добавить поисковую систему", "Введите URL адрес системы (use {} for query):")
            if ok and url:
                self.parent.add_search_engine(name, url)
                self.search_combo.addItem(name)

    def add_extension(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Выбрать расширение", "", "CRX Files (*.crx)")
        if filename:
            # Здесь я бы реализовал логику для добавления и включения расширения
            # Это заглушка, так как реализация поддержки расширений браузера - пиздец сложная задача
            # Here I would implement the logic for adding and enabling extensions.
            # This is a stub, because implementing browser extension support is a fucking difficult task.
            self.extensions_list.addItem(filename)