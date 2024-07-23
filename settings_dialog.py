import pyaudio
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, 
                             QListWidget, QInputDialog, QColorDialog, QFileDialog, QTabWidget, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineSettings

class SettingsDialog(QDialog):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.parent = parent
        self.config = config
        self.setWindowTitle("Settings")
        self.setWindowFlags(self.windowFlags() | Qt.WindowSystemMenuHint | Qt.WindowMinMaxButtonsHint)
        
        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()

        self.init_general_tab()
        self.init_audio_tab()
        self.init_extensions_tab()

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def init_audio_tab(self):
        audio_tab = QWidget()
        audio_layout = QVBoxLayout()

        # Output devices
        self.output_label = QLabel("Output Device:")
        self.output_combo = QComboBox()
        self.fill_audio_devices(self.output_combo, 'output')
        self.output_combo.currentIndexChanged.connect(self.change_output_device)
        audio_layout.addWidget(self.output_label)
        audio_layout.addWidget(self.output_combo)

        # Input devices
        self.input_label = QLabel("Input Device:")
        self.input_combo = QComboBox()
        self.fill_audio_devices(self.input_combo, 'input')
        self.input_combo.currentIndexChanged.connect(self.change_input_device)
        audio_layout.addWidget(self.input_label)
        audio_layout.addWidget(self.input_combo)

        audio_tab.setLayout(audio_layout)
        self.tabs.addTab(audio_tab, "Audio")

    def fill_audio_devices(self, combo, device_type):
        p = pyaudio.PyAudio()
        default_device = p.get_default_host_api_info()['defaultOutputDevice' if device_type == 'output' else 'defaultInputDevice']
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if (device_type == 'output' and dev['maxOutputChannels'] > 0) or \
               (device_type == 'input' and dev['maxInputChannels'] > 0):
                combo.addItem(dev['name'], dev['index'])
                if dev['index'] == default_device:
                    combo.setCurrentIndex(combo.count() - 1)
        p.terminate()

    def change_output_device(self, index):
        device_index = self.output_combo.currentData()
        self.config.set('audio_output_device', device_index)
        QWebEngineSettings.globalSettings().setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)
        # Note: Setting the actual audio device requires lower-level audio API integration

    def change_input_device(self, index):
        device_index = self.input_combo.currentData()
        self.config.set('audio_input_device', device_index)
        # Note: Setting the actual audio device requires lower-level audio API integration

    def init_general_tab(self):
        general_tab = QWidget()
        general_layout = QVBoxLayout()

        # Color picker
        self.color_btn = QPushButton("Choose background color")
        self.color_btn.clicked.connect(self.choose_color)
        general_layout.addWidget(self.color_btn)

        # Icon picker
        self.icon_btn = QPushButton("Choose icon")
        self.icon_btn.clicked.connect(self.choose_icon)
        general_layout.addWidget(self.icon_btn)

        # Search engine selector
        self.search_label = QLabel("Default search engine:")
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
        self.add_search_btn = QPushButton("Add new search engine")
        self.add_search_btn.clicked.connect(self.add_search_engine)
        general_layout.addWidget(self.add_search_btn)

        general_tab.setLayout(general_layout)
        self.tabs.addTab(general_tab, "General")

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
            self.extensions_list.addItem(filename)