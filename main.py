from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout,\
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem
from PyQt6.QtGui import QAction
from sys import argv, exit
import sqlite3 as db

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
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Phone"))
        self.setCentralWidget(self.table)
        
        self.load_data()
        
    def load_data(self):
        conn = db.connect("database.db")
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE name=='students'")
        if cur.fetchone() is None:
            cur.execute("CREATE TABLE students(id, name, course, phone)")
            
        data = cur.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(data):
            self.table.insertRow(row_number)
            for column_number, cell_data in enumerate(row_data):
                self.table.setItem(row_number, column_number,
                                   QTableWidgetItem(str(cell_data)))
        conn.close()

    
app = QApplication(argv)
main_window = MainWindow()
main_window.show()
exit(app.exec())