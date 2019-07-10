# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'aliPayMainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(487, 218)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.logining_Widget = QtWidgets.QWidget(self.centralwidget)
        self.logining_Widget.setObjectName("logining_Widget")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.logining_Widget)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.token_value_lineEdit = QtWidgets.QLineEdit(self.logining_Widget)
        self.token_value_lineEdit.setObjectName("token_value_lineEdit")
        self.gridLayout_4.addWidget(self.token_value_lineEdit, 0, 1, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.logining_Widget)
        self.label_15.setObjectName("label_15")
        self.gridLayout_4.addWidget(self.label_15, 0, 2, 1, 1)
        self.key_name_lineEdit = QtWidgets.QLineEdit(self.logining_Widget)
        self.key_name_lineEdit.setObjectName("key_name_lineEdit")
        self.gridLayout_4.addWidget(self.key_name_lineEdit, 0, 3, 1, 1)
        self.start_pushButton = QtWidgets.QPushButton(self.logining_Widget)
        self.start_pushButton.setObjectName("start_pushButton")
        self.gridLayout_4.addWidget(self.start_pushButton, 1, 3, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.logining_Widget)
        self.label_14.setObjectName("label_14")
        self.gridLayout_4.addWidget(self.label_14, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.logining_Widget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 487, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "自动操作软件"))
        self.label_15.setText(_translate("MainWindow", "标识备注名"))
        self.start_pushButton.setText(_translate("MainWindow", "开始"))
        self.label_14.setText(_translate("MainWindow", "token值"))


