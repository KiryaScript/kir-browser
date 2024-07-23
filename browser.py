from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTabWidget, 
                             QProgressBar)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineSettings
from PyQt5.QtGui import QIcon, QPalette, QColor
from settings_dialog import SettingsDialog
import os

class SimpleBrowser(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Simple Browser')
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
        self.url_bar.setPlaceholderText('Enter URL or search query')
        go_btn = QPushButton('Go')
        go_btn.clicked.connect(self.navigate)

        back_btn = QPushButton('Back')
        back_btn.clicked.connect(self.go_back)

        settings_btn = QPushButton('Settings')
        settings_btn.clicked.connect(self.open_settings)

        toolbar.addWidget(back_btn)
        toolbar.addWidget(self.url_bar)
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

        self.search_engines = self.config.get('search_engines')
        self.current_search_engine = self.config.get('default_search_engine')

        # Set custom user agent for better YouTube compatibility
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        # Set persistent storage path for cookies, cache, etc.
        self.profile.setPersistentStoragePath('./browser_data')

        self.apply_saved_settings()
        self.add_tab()

    def apply_saved_settings(self):
        color = self.config.get('background_color')
        if color:
            self.set_background_color(QColor(color))
        
        icon_path = self.config.get('icon_path')
        if icon_path and os.path.exists(icon_path):
            self.set_icon(icon_path)

    def add_tab(self, url=""):
        new_tab = QWebEngineView()
        new_tab.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        new_tab.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        
        index = self.tabs.addTab(new_tab, "New Tab")
        self.tabs.setCurrentIndex(index)
        new_tab.urlChanged.connect(lambda qurl, browser=new_tab: self.update_url(qurl, browser))
        new_tab.loadProgress.connect(self.update_progress)
        new_tab.loadFinished.connect(lambda _, index=index, browser=new_tab: self.update_tab_title(index, browser))
        if url:
            new_tab.setUrl(QUrl(url))

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()

    def navigate(self):
        query = self.url_bar.text()
        if query.startswith(('http://', 'https://')):
            url = query
        else:
            url = self.search_engines[self.current_search_engine].format(query)
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