import sys

import socketio
from PyQt5.QtCore import QFile, QTextStream
from PyQt5.QtWidgets import QApplication

from app.UIControl import logger
from app.UIControl.aliPayControl import aliPayControl

from profile import profile

sys._excepthook = sys.excepthook


def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    logger.error(exctype)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook
if __name__ == '__main__':
    def getstylesheetfromQss(qss_path):
        file = QFile(qss_path)
        file.open(QFile.ReadOnly)
        ts = QTextStream(file)

        stylesheet = ts.readAll()
        return stylesheet


    app = QApplication(sys.argv)
    ui = aliPayControl()
    ui.setStyleSheet(getstylesheetfromQss(profile.UI_QSS_URL))
    ui.show()
    sys.exit(app.exec_())



