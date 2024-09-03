import os
import speech_recognition as sr
from PyQt5.QtCore import QUrl, Qt, QTimer, QFileInfo
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTabWidget, 
                             QProgressBar, QMessageBox, QApplication, QComboBox, QLabel, QFileDialog, QMenu, QTextEdit)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineSettings, QWebEnginePage, QWebEngineDownloadItem
from PyQt5.QtGui import QIcon, QPalette, QColor
from settings_dialog import SettingsDialog
from urllib.parse import quote, urlparse
import time
from bs4 import BeautifulSoup
import requests

class DownloadManager:
    def __init__(self, parent=None):
        self.parent = parent

    def handle_download(self, download):
        old_path = download.path()
        suffix = QFileInfo(old_path).suffix()
        path, _ = QFileDialog.getSaveFileName(self.parent, "Save File", old_path, f"*.{suffix}")
        if path:
            download.setPath(path)
            download.accept()
            download.finished.connect(self.download_finished)
        else:
            download.cancel()

    def download_finished(self):
        QMessageBox.information(self.parent, "Загрузка завершена", "Файл загружен успешно.")

class SimpleBrowser(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.profile = QWebEngineProfile.defaultProfile()
        self.download_manager = DownloadManager(self)
        self.profile.downloadRequested.connect(self.download_manager.handle_download)
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

        dev_tools_btn = QPushButton('Dev Tools')
        dev_tools_btn.clicked.connect(self.toggle_dev_tools)
        toolbar.addWidget(dev_tools_btn)

        self.add_tab_button = QPushButton('+')
        self.add_tab_button.clicked.connect(self.add_tab)
        self.tabs.setCornerWidget(self.add_tab_button, Qt.TopLeftCorner)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText('Введите URL-адрес или поисковый запрос')
        go_btn = QPushButton('Поиск')
        go_btn.clicked.connect(self.navigate)

        downloads_btn = QPushButton('Загрузки')
        downloads_btn.clicked.connect(self.show_downloads)
        toolbar.addWidget(downloads_btn)

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

    def toggle_dev_tools(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            dev_tools_page = QWebEnginePage(self.profile, self)
            current_tab.page().setDevToolsPage(dev_tools_page)
        
            dev_tools_view = QWebEngineView()
            dev_tools_view.setPage(dev_tools_page)
            dev_tools_view.setWindowTitle("Developer Tools")
            dev_tools_view.resize(800, 600)
            dev_tools_view.show()

    def view_source(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            url = current_tab.url().toString()
            response = requests.get(url)
            source_code = response.text
            self.show_source_code(source_code)

    def show_source_code(self, source_code):
        source_window = QWidget()
        source_window.setWindowTitle("Source Code")
        source_layout = QVBoxLayout()
        source_text = QTextEdit()
        source_text.setPlainText(source_code)
        source_layout.addWidget(source_text)
        source_window.setLayout(source_layout)
        source_window.resize(800, 600)
        source_window.show()

    def inspect_element(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.page().runJavaScript("""
                function getElementInfo(element) {
                    return {
                        tagName: element.tagName,
                        id: element.id,
                        className: element.className,
                        innerText: element.innerText
                    };
                }
                
                document.addEventListener('click', function(e) {
                    e.preventDefault();
                    console.log(JSON.stringify(getElementInfo(e.target)));
                }, true);
            """)

    def start_performance_analysis(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.page().loadStarted.connect(self.performance_load_started)
            current_tab.page().loadFinished.connect(self.performance_load_finished)

    def performance_load_started(self):
        self.load_start_time = time.time()

    def performance_load_finished(self):
        load_time = time.time() - self.load_start_time
        print(f"Page loaded in {load_time:.2f} seconds")

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
        new_tab.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        new_tab.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        new_tab.settings().setAttribute(QWebEngineSettings.AutoLoadImages, True)
        new_tab.settings().setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        new_tab.settings().setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        new_tab.settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, True)

        # Добавьте контекстное меню
        new_tab.setContextMenuPolicy(Qt.CustomContextMenu)
        new_tab.customContextMenuRequested.connect(self.show_context_menu)

        index = self.tabs.addTab(new_tab, "Новая вкладка")
        self.tabs.setCurrentIndex(index)
        new_tab.urlChanged.connect(lambda qurl, browser=new_tab: self.update_url(qurl, browser))
        new_tab.loadProgress.connect(self.update_progress)
        new_tab.loadFinished.connect(lambda _, index=index, browser=new_tab: self.update_tab_title(index, browser))
        if url:
            new_tab.setUrl(QUrl(url))
        else:
            new_tab.setUrl(QUrl("https://www.google.com"))

    def show_context_menu(self, pos):
        context_menu = QMenu(self)
        view_source_action = context_menu.addAction("View Source")
        inspect_element_action = context_menu.addAction("Inspect Element")
        performance_analysis_action = context_menu.addAction("Start Performance Analysis")

        action = context_menu.exec_(self.mapToGlobal(pos))
        if action == view_source_action:
            self.view_source()
        elif action == inspect_element_action:
            self.inspect_element()
        elif action == performance_analysis_action:
            self.start_performance_analysis()

    def show_downloads(self):
    # Здесь вы можете добавить логику для отображения списка загрузок
        QMessageBox.information(self, "Загрузки", "Downloads feature is not yet implemented.")

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
        
        default_mic = self.config.get('default_microphone')
        if default_mic and default_mic in self.microphones:
            self.mic_selector.setCurrentText(default_mic)

    def voice_input(self):
        try:
            with sr.Microphone(device_index=self.microphones.index(self.current_microphone)) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                self.voice_label.setText("Обработка речи...")
                text = self.recognizer.recognize_google(audio, language="ru-RU")
                self.url_bar.setText(text)
                self.navigate()
                self.voice_label.setText("Готов к голосовому вводу")
        except sr.WaitTimeoutError:
            self.voice_label.setText("Время ожидания истекло. Попробуйте еще раз.")
        except sr.UnknownValueError:
            self.voice_label.setText("Не удалось распознать речь")
        except sr.RequestError as e:
            self.voice_label.setText(f"Ошибка сервиса распознавания речи: {e}")
        finally:
            QTimer.singleShot(3000, lambda: self.voice_label.setText("Готов к голосовому вводу"))