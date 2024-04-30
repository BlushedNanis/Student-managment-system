from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout,\
    QLineEdit, QPushButton, QMainWindow, QMenuBar
from PyQt6.QtGui import QAction
from sys import argv, exit

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        
        add_student_action = QAction("Add student", self)
        file_menu_item.addAction(add_student_action)
        
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)


app = QApplication(argv)
main_window = MainWindow()
main_window.show()
exit(app.exec())