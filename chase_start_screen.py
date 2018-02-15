# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'chase_start_screen.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(700, 200)
        MainWindow.setMinimumSize(QtCore.QSize(700, 200))
        MainWindow.setMaximumSize(QtCore.QSize(700, 200))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.Team_Name_label = QtGui.QLabel(self.centralwidget)
        self.Team_Name_label.setGeometry(QtCore.QRect(10, 20, 141, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.Team_Name_label.setFont(font)
        self.Team_Name_label.setObjectName(_fromUtf8("Team_Name_label"))
        self.Car_Type = QtGui.QComboBox(self.centralwidget)
        self.Car_Type.setGeometry(QtCore.QRect(470, 15, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.Car_Type.setFont(font)
        self.Car_Type.setMaxVisibleItems(5)
        self.Car_Type.setObjectName(_fromUtf8("Car_Type"))
        self.Car_Type.addItem(_fromUtf8(""))
        self.Car_Type.addItem(_fromUtf8(""))
        self.Car_Type.addItem(_fromUtf8(""))
        self.Car_Type.addItem(_fromUtf8(""))
        self.Car_Type.addItem(_fromUtf8(""))
        self.Vehicle_Label = QtGui.QLabel(self.centralwidget)
        self.Vehicle_Label.setGeometry(QtCore.QRect(370, 20, 91, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.Vehicle_Label.setFont(font)
        self.Vehicle_Label.setObjectName(_fromUtf8("Vehicle_Label"))
        self.lat_label = QtGui.QLabel(self.centralwidget)
        self.lat_label.setGeometry(QtCore.QRect(10, 80, 221, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lat_label.setFont(font)
        self.lat_label.setObjectName(_fromUtf8("lat_label"))
        self.lon_label = QtGui.QLabel(self.centralwidget)
        self.lon_label.setGeometry(QtCore.QRect(10, 120, 231, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lon_label.setFont(font)
        self.lon_label.setObjectName(_fromUtf8("lon_label"))
        self.Chase_Start = QtGui.QPushButton(self.centralwidget)
        self.Chase_Start.setGeometry(QtCore.QRect(560, 130, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.Chase_Start.setFont(font)
        self.Chase_Start.setObjectName(_fromUtf8("Chase_Start"))
        self.Team_Name = QtGui.QLineEdit(self.centralwidget)
        self.Team_Name.setGeometry(QtCore.QRect(150, 20, 131, 20))
        self.Team_Name.setObjectName(_fromUtf8("Team_Name"))
        self.lat = QtGui.QLineEdit(self.centralwidget)
        self.lat.setGeometry(QtCore.QRect(230, 80, 113, 20))
        self.lat.setObjectName(_fromUtf8("lat"))
        self.lon = QtGui.QLineEdit(self.centralwidget)
        self.lon.setGeometry(QtCore.QRect(250, 120, 113, 20))
        self.lon.setObjectName(_fromUtf8("lon"))
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "ISU AMS Storm Chase Simulation", None))
        self.Team_Name_label.setText(_translate("MainWindow", "Enter a team name:", None))
        self.Car_Type.setItemText(0, _translate("MainWindow", "Compact", None))
        self.Car_Type.setItemText(1, _translate("MainWindow", "Sedan", None))
        self.Car_Type.setItemText(2, _translate("MainWindow", "Hybrid", None))
        self.Car_Type.setItemText(3, _translate("MainWindow", "Pickup", None))
        self.Car_Type.setItemText(4, _translate("MainWindow", "SUV", None))
        self.Vehicle_Label.setText(_translate("MainWindow", "Vehicle Type:", None))
        self.lat_label.setText(_translate("MainWindow", "Enter latitude of starting point:", None))
        self.lon_label.setText(_translate("MainWindow", "Enter longitude of starting point:", None))
        self.Chase_Start.setText(_translate("MainWindow", "Begin Chase", None))
        self.Team_Name.setPlaceholderText(_translate("MainWindow", "team name", None))
        self.lat.setPlaceholderText(_translate("MainWindow", "(i.e. 42.167505)", None))
        self.lon.setPlaceholderText(_translate("MainWindow", "(i.e. -93.962312)", None))

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

