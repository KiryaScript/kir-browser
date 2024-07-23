import sys
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTabWidget, 
                             QProgressBar, QMenu, QAction, QColorDialog, QFileDialog, QComboBox, QLabel, QDialog)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon, QPalette, QColor

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.layout = QVBoxLayout()

        # Color picker
        self.color_btn = QPushButton("Choose background color")
        self.color_btn.clicked.connect(self.choose_color)
        self.layout.addWidget(self.color_btn)

        # Icon picker
        self.icon_btn = QPushButton("Choose icon")
        self.icon_btn.clicked.connect(self.choose_icon)
        self.layout.addWidget(self.icon_btn)

        # Search engine selector
        self.search_label = QLabel("Default search engine:")
        self.search_combo = QComboBox()
        self.search_combo.addItems(["Google", "Bing", "DuckDuckGo"])
        self.search_combo.currentTextChanged.connect(self.parent().set_search_engine)
        self.layout.addWidget(self.search_label)
        self.layout.addWidget(self.search_combo)

        self.setLayout(self.layout)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.parent().set_background_color(color)

    def choose_icon(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Icon", "", "Image Files (*.png *.jpg *.bmp)")
        if filename:
            self.parent().set_icon(filename)

class SimpleBrowser(QWidget):
    def __init__(self):
        super().__init__()
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

        settings_btn = QPushButton('Settings')
        settings_btn.clicked.connect(self.open_settings)

        toolbar.addWidget(self.url_bar)
        toolbar.addWidget(go_btn)
        toolbar.addWidget(settings_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(10)

        self.layout.addLayout(toolbar)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.tabs)

        self.setLayout(self.layout)

        self.search_engines = {
            "Google": "https://www.google.com/search?q=",
            "Bing": "https://www.bing.com/search?q=",
            "DuckDuckGo": "https://duckduckgo.com/?q="
        }
        self.current_search_engine = "Google"

        self.add_tab()

    def add_tab(self, url=""):
        new_tab = QWebEngineView()
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
            url = self.search_engines[self.current_search_engine] + query
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
        settings = SettingsDialog(self)
        settings.exec_()

    def set_background_color(self, color):
        palette = self.palette()
        palette.setColor(QPalette.Window, color)
        self.setPalette(palette)

    def set_icon(self, filename):
        self.setWindowIcon(QIcon(filename))

    def set_search_engine(self, engine):
        self.current_search_engine = engine

def main():
    app = QApplication(sys.argv)
    window = SimpleBrowser()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()