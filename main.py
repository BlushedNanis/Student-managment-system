from PyQt6.QtWidgets import QApplication, QLabel, QMessageBox, QGridLayout,\
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem,\
    QDialog, QVBoxLayout, QComboBox, QToolBar, QAbstractItemView, QStatusBar
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
from sys import argv, exit
import sqlite3 as db


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.resize(600, 600)
        
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")
        
        add_student_action = QAction(QIcon("icons\\add"), "Add student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)
        
        search_student_action = QAction(QIcon("icons\\search"),"Search", self)
        search_student_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_student_action)
        
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Phone"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        self.load_data()
        
        tool_bar = QToolBar()
        tool_bar.setMovable(True)
        self.addToolBar(tool_bar)
        tool_bar.addAction(add_student_action)
        tool_bar.addAction(search_student_action)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("QStatusBar::item {border: none;}")
        self.table.cellClicked.connect(self.cell_clicked)
        
        
    def load_data(self):
        conn = db.connect("database.db")    
        data = conn.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(data):
            self.table.insertRow(row_number)
            for column_number, cell_data in enumerate(row_data):
                self.table.setItem(row_number, column_number,
                                   QTableWidgetItem(str(cell_data)))
        conn.close()

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)
        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)
        
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)
        
        self.status_bar.addWidget(edit_button)
        self.status_bar.addWidget(delete_button)
        
    def insert(self):
        dialog = InsertDialog()
        dialog.exec()
        
    def search(self):
        dialog = SearchDialog()
        dialog.exec()
        
    def edit(self):
        dialog = EditDialog()
        dialog.exec()
        
    def delete(self):
        self.dialog = DeleteDialog()
        self.dialog.exec()
        
        
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
        
        
class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        layout = QVBoxLayout()
        self.setFixedSize(300, 300)
        
        self.name_line = QLineEdit()
        self.name_line.setPlaceholderText("Name")
        layout.addWidget(self.name_line)
        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)
        
        self.setLayout(layout)
        
    def search(self):
        name = self.name_line.text()
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            main_window.table.item(item.row(), item.column()).setSelected(True)


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit Student Record")
        layout = QVBoxLayout()
        self.setFixedSize(300, 300)
        
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
        button.clicked.connect(self.edit_student)
        layout.addWidget(button)
        
        self.student_id = int(main_window.table.item(main_window.table.currentRow()
                                                     , 0).text())
        
        self.load_student()
        
        self.setLayout(layout)
    
    def load_student(self):
        conn = db.connect("database.db")
        cur = conn.cursor()
        cur.execute("SELECT name, course, phone FROM students "\
                    f"WHERE id = {self.student_id}")
        result = cur.fetchall()
        name, course, phone = result[0]
        cur.close()
        conn.close()
        
        self.student_name.setText(name)
        self.courses_box.setCurrentText(course)
        self.student_phone.setText(phone)
        
        
    def edit_student(self):
        name = self.student_name.text()
        course = self.courses_box.currentText()
        phone = self.student_phone.text()
        conn = db.connect("database.db")
        cur = conn.cursor()
        cur.execute("UPDATE students SET name = ?, course = ?, phone = ? "\
                    f"WHERE id = {self.student_id}", (name, course, phone))
        conn.commit()
        cur.close()
        conn.close()
        self.close()
        main_window.load_data()
    
    
class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Record")
        layout = QGridLayout()
        self.setFixedSize(260, 100)
        
        #Dialog widgets
        label = QLabel("Are you sure you want to delete this record?")
        layout.addWidget(label, 0, 0, 1, 2)
        yes_button = QPushButton("YES")
        yes_button.clicked.connect(self.delete_student)
        layout.addWidget(yes_button, 1, 0)
        no_button = QPushButton("NO")
        no_button.clicked.connect(self.close)
        layout.addWidget(no_button, 1, 1)
        
        self.student_id = int(main_window.table.item(main_window.table.currentRow()
                                                     , 0).text())
        
        self.setLayout(layout)
        
    def delete_student(self):
        conn = db.connect("database.db")
        cur = conn.cursor()
        cur.execute(f"DELETE FROM students WHERE id == {self.student_id}")
        conn.commit()
        cur.close()
        conn.close()
        self.close()
        main_window.load_data()
        
        confirmation_box = QMessageBox()
        confirmation_box.setWindowTitle("Success")
        confirmation_box.setText("The record was deleted successfully")
        confirmation_box.exec()
        

conn = db.connect("database.db")
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE name=='students'")
if cur.fetchone() is None:
    cur.execute("CREATE TABLE students(id INTEGER PRIMARY KEY,"\
                                        "name VARCHAR(256),"\
                                        "course VARCHAR(256),"\
                                        "phone VARCHAR(256))")
cur.close()
conn.close()

app = QApplication(argv)
main_window = MainWindow()
main_window.show()
exit(app.exec())