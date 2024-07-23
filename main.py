import sys
from PyQt5.QtWidgets import QApplication
from browser import SimpleBrowser
from config import Config

def main():
    app = QApplication(sys.argv)
    config = Config()
    window = SimpleBrowser(config)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()