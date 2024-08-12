import os
import speech_recognition as sr
from PyQt5.QtCore import QUrl, Qt, QTimer
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTabWidget, 
                             QProgressBar, QMessageBox, QApplication, QComboBox, QLabel)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineSettings, QWebEnginePage
from PyQt5.QtGui import QIcon, QPalette, QColor
from settings_dialog import SettingsDialog
from urllib.parse import quote, urlparse

class SimpleBrowser(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.profile = QWebEngineProfile.defaultProfile()
        self.search_engines = self.config.get('search_engines', {
            "Google": "https://www.google.com/search?q={}",
            "Bing": "https://www.bing.com/search?q={}",
            "DuckDuckGo": "https://duckduckgo.com/?q={}"
        })
        self.current_search_engine = self.config.get('default_search_engine', "Google")
        self.recognizer = sr.Recognizer()
        self.microphones = sr.Microphone.list_microphone_names()
        self.current_microphone = self.config.get('default_microphone', self.microphones[0] if self.microphones else None)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Kir-Browser')
        self.setGeometry(100, 100, 1024, 768)

        self.layout = QVBoxLayout()
        toolbar = QHBoxLayout()

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        self.add_tab_button = QPushButton('+')
        self.add_tab_button.clicked.connect(self.add_tab)
        self.tabs.setCornerWidget(self.add_tab_button, Qt.TopLeftCorner)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText('Введите URL-адрес или поисковый запрос')
        go_btn = QPushButton('Поиск')
        go_btn.clicked.connect(self.navigate)

        back_btn = QPushButton('Назад')
        back_btn.clicked.connect(self.go_back)

        settings_btn = QPushButton('Настройки')
        settings_btn.clicked.connect(self.open_settings)

        voice_btn = QPushButton('🎤')
        voice_btn.clicked.connect(self.start_voice_input)

        self.mic_selector = QComboBox()
        self.mic_selector.addItems(self.microphones)
        if self.current_microphone:
            self.mic_selector.setCurrentText(self.current_microphone)
        self.mic_selector.currentTextChanged.connect(self.change_microphone)

        self.voice_label = QLabel("Готов к голосовому вводу")

        toolbar.addWidget(voice_btn)
        toolbar.addWidget(self.mic_selector)
        toolbar.addWidget(self.voice_label)

        toolbar.addWidget(back_btn)
        toolbar.addWidget(self.url_bar)
        toolbar.addWidget(go_btn)
        toolbar.addWidget(settings_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(10)

        self.layout.addLayout(toolbar)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.tabs)

        self.setLayout(self.layout)

        self.profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        self.profile.setPersistentStoragePath(os.path.join(os.getcwd(), 'browser_data'))

        self.apply_saved_settings()
        self.add_tab()

    def change_microphone(self, mic_name):
        self.current_microphone = mic_name
        self.config.set('default_microphone', mic_name)

    def start_voice_input(self):
        self.voice_label.setText("Говорите...")
        QTimer.singleShot(100, self.voice_input)

    def add_tab(self, url=""):
        new_tab = QWebEngineView()
        new_tab.setPage(QWebEnginePage(self.profile, new_tab))
        new_tab.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        new_tab.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        
        index = self.tabs.addTab(new_tab, "Новая вкладка")
        self.tabs.setCurrentIndex(index)
        new_tab.urlChanged.connect(lambda qurl, browser=new_tab: self.update_url(qurl, browser))
        new_tab.loadProgress.connect(self.update_progress)
        new_tab.loadFinished.connect(lambda _, index=index, browser=new_tab: self.update_tab_title(index, browser))
        if url:
            new_tab.setUrl(QUrl(url))
        else:
            new_tab.setUrl(QUrl("https://www.google.com"))

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()

    def navigate(self):
        query = self.url_bar.text()
        parsed = urlparse(query)
        if parsed.scheme and parsed.netloc:
            url = query
        else:
            if ' ' in query:
                encoded_query = quote(query)
                url = self.search_engines[self.current_search_engine].format(encoded_query)
            else:
                url = 'http://' + quote(query)
        self.tabs.currentWidget().setUrl(QUrl(url))

    def update_url(self, q, browser):
        if browser == self.tabs.currentWidget():
            self.url_bar.setText(q.toString())

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

    def update_tab_title(self, index, browser):
        title = browser.page().title()
        self.tabs.setTabText(index, title)

    def open_settings(self):
        settings = SettingsDialog(self, self.config)
        settings.exec_()

    def set_background_color(self, color):
        palette = self.palette()
        palette.setColor(QPalette.Window, color)
        self.setPalette(palette)
        self.config.set('background_color', color.name())

    def set_icon(self, filename):
        self.setWindowIcon(QIcon(filename))
        self.config.set('icon_path', filename)

    def set_search_engine(self, engine):
        self.current_search_engine = engine
        self.config.set('default_search_engine', engine)

    def add_search_engine(self, name, url):
        self.search_engines[name] = url
        self.config.set('search_engines', self.search_engines)

    def go_back(self):
        if self.tabs.currentWidget().history().canGoBack():
            self.tabs.currentWidget().back()

    def apply_saved_settings(self):
        color = self.config.get('background_color')
        if color:
            self.set_background_color(QColor(color))
        
        icon_path = self.config.get('icon_path')
        if icon_path and os.path.exists(icon_path):
            self.set_icon(icon_path)

    def voice_input(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            QMessageBox.information(self, "Голосовой ввод", "Говорите сейчас...")
            try:
                audio = recognizer.listen(source, timeout=5)
                QMessageBox.information(self, "Голосовой ввод", "Обработка речи...")
                text = recognizer.recognize_google(audio, language="ru-RU")
                self.url_bar.setText(text)
                self.navigate()
            except sr.WaitTimeoutError:
                QMessageBox.warning(self, "Ошибка", "Время ожидания истекло. Попробуйте еще раз.")
            except sr.UnknownValueError:
                QMessageBox.warning(self, "Ошибка", "Не удалось распознать речь")
            except sr.RequestError as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка сервиса распознавания речи: {e}")