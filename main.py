from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout,\
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem,\
    QDialog, QVBoxLayout, QComboBox
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
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)
        
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Phone"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)
        
        self.load_data()
        
    def load_data(self):
        conn = db.connect("database.db")
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE name=='students'")
        if cur.fetchone() is None:
            cur.execute("CREATE TABLE students(id INTEGER PRIMARY KEY,"\
                                                "name, course, phone)")
            
        data = cur.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(data):
            self.table.insertRow(row_number)
            for column_number, cell_data in enumerate(row_data):
                self.table.setItem(row_number, column_number,
                                   QTableWidgetItem(str(cell_data)))
        cur.close()
        conn.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()
        
        
class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert New Student")
        self.setFixedSize(300, 300)
        
        layout = QVBoxLayout()
        
        # Dialog widgets
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)
        self.courses_box = QComboBox()
        self.courses_box.addItems(("Biology", "Math", "Astronomy", "Physics"))
        layout.addWidget(self.courses_box)
        self.student_phone = QLineEdit()
        self.student_phone.setPlaceholderText("Phone number")
        layout.addWidget(self.student_phone)
        button = QPushButton("Submit")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)
        
        self.setLayout(layout)
        
        
    def add_student(self):
        name = self.student_name.text()
        course= self.courses_box.itemText(self.courses_box.currentIndex())
        phone = self.student_phone.text()
        conn = db.connect("database.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO students(name, course, phone) VALUES (?,?,?)",
                    (name, course, phone))
        conn.commit()
        cur.close()
        conn.close()
        main_window.load_data()
        
    
app = QApplication(argv)
main_window = MainWindow()
main_window.show()
exit(app.exec())