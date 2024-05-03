from PyQt6.QtWidgets import QApplication, QLabel, QMessageBox, QGridLayout,\
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem,\
    QDialog, QVBoxLayout, QComboBox, QToolBar, QAbstractItemView, QStatusBar
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
from sys import argv, exit
import sqlite3 as db


class MainWindow(QMainWindow):
    """
    QMainWindow, which displays a table as the main widget, the table
    displays de data of the student stored in a database. Also contains a menubar,
    a toolbar and a status bar.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.resize(600, 600)
        
        # Set menu bar
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        
        #Add actions to the menu bar
        add_student_action = QAction(QIcon("icons\\add"), "Add student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)
        
        search_student_action = QAction(QIcon("icons\\search"),"Search", self)
        search_student_action.triggered.connect(self.search)
        file_menu_item.addAction(search_student_action)
        
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        help_menu_item.triggered.connect(self.about)
        
        # Set table 
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Phone"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        #Load students data to the table
        self.load_data()
        
        #Set toolbar
        tool_bar = QToolBar()
        tool_bar.setMovable(True)
        self.addToolBar(tool_bar)
        tool_bar.addAction(add_student_action)
        tool_bar.addAction(search_student_action)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("QStatusBar::item {border: none;}")
        
        # Show buttons on toolbar when a cell is clicked
        self.table.cellClicked.connect(self.cell_clicked)
        
        
    def load_data(self):
        """
        Loads the students data stored in the database on the table at main window.
        """
        conn = DataBase().connect()    
        data = conn.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(data):
            self.table.insertRow(row_number)
            for column_number, cell_data in enumerate(row_data):
                self.table.setItem(row_number, column_number,
                                   QTableWidgetItem(str(cell_data)))
        conn.close()

    def cell_clicked(self):
        """
        Show buttons in the status bar when a cell is clicked
        """
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)
        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)
        
        # Remove previous buttons 
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)
        
        #Add new buttons pointing at the cell clicked
        self.status_bar.addWidget(edit_button)
        self.status_bar.addWidget(delete_button)
        
    def insert(self):
        """
        Execute the insert dialog.
        """
        dialog = InsertDialog()
        dialog.exec()
        
    def search(self):
        """
        Execute the search dialog.
        """
        dialog = SearchDialog()
        dialog.exec()
        
    def edit(self):
        """
        Execute the edit dialog.
        """
        dialog = EditDialog()
        dialog.exec()
        
    def delete(self):
        """
        Execute the delete dialog.
        """
        self.dialog = DeleteDialog()
        self.dialog.exec()
        
    def about(self):
        """
        Execute the about dialog.
        """
        self.dialog = AboutDialog()
        self.dialog.exec()
        
class AboutDialog(QMessageBox):
    """
    QMessageBox, which displays the about information of the app.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This app was created during the course "The python Mega Course" by Ardit Sulce.
        Feel free to use or modify this app.
        """
        self.setText(content)

        
class InsertDialog(QDialog):
    """
    QDialog, which serves for the user to add a new student to the database.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert New Student")
        self.setFixedSize(300, 300)
        
        layout = QVBoxLayout()
        
        # Set widgets to the dialog
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
        """
        Add the student data provided by the suer in the insert dialog to 
        the students database.
        """
        name = self.student_name.text()
        course= self.courses_box.itemText(self.courses_box.currentIndex())
        phone = self.student_phone.text()
        
        conn = DataBase().connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO students(name, course, phone) VALUES (?,?,?)",
                    (name, course, phone))
        conn.commit()
        
        cur.close()
        conn.close()
        main_window.load_data()
        
        
class SearchDialog(QDialog):
    """
    QDialog, which let the user search for a specific student by name.
    The result of the search will be selected on the table.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        layout = QVBoxLayout()
        self.setFixedSize(300, 300)
        
        # Set widgets to the dialog
        self.name_line = QLineEdit()
        self.name_line.setPlaceholderText("Name")
        layout.addWidget(self.name_line)
        
        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)
        
        self.setLayout(layout)
        
    def search(self):
        """
        Search for the student(s) which match with the name provided by the user.
        """
        name = self.name_line.text()
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        
        # Selects the student match on the table
        for item in items:
            main_window.table.item(item.row(), item.column()).setSelected(True)


class EditDialog(QDialog):
    """
    QDialog, which allows the user to edit the information of the 
    selected student on the table.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit Student Record")
        layout = QVBoxLayout()
        self.setFixedSize(300, 300)
        
        # Set dialog widgets
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
        
        self.student_id = int(main_window.table.item(main_window.table.currentRow(),
                                                     0).text())
        
        self.load_student()
        
        self.setLayout(layout)
    
    def load_student(self):
        """
        Loads the information of the student on the edit dialog widgets.
        """
        conn = DataBase().connect()
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
        """
        Update the student information in the database with the data provided
        by the user.
        """
        name = self.student_name.text()
        course = self.courses_box.currentText()
        phone = self.student_phone.text()
        
        conn = DataBase().connect()
        cur = conn.cursor()
        cur.execute("UPDATE students SET name = ?, course = ?, phone = ? "\
                    f"WHERE id = {self.student_id}", (name, course, phone))
        conn.commit()
        cur.close()
        conn.close()
        self.close()
        
        main_window.load_data()
    
    
class DeleteDialog(QDialog):
    """
    QDialog, which allows the user to delete a student information 
    from the database.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Record")
        layout = QGridLayout()
        self.setFixedSize(260, 100)
        
        # Set dialog widgets
        label = QLabel("Are you sure you want to delete this record?")
        layout.addWidget(label, 0, 0, 1, 2)
        
        yes_button = QPushButton("YES")
        yes_button.clicked.connect(self.delete_student)
        layout.addWidget(yes_button, 1, 0)
        
        no_button = QPushButton("NO")
        no_button.clicked.connect(self.close)
        layout.addWidget(no_button, 1, 1)
        
        # Get the student id, based on the selected row in the table.
        self.student_id = int(main_window.table.item(main_window.table.currentRow()
                                                     , 0).text())
        
        self.setLayout(layout)
        
    def delete_student(self):
        """
        Delete the user information from the database.
        """
        conn = DataBase().connect()
        cur = conn.cursor()
        cur.execute(f"DELETE FROM students WHERE id == {self.student_id}")
        conn.commit()
        cur.close()
        conn.close()
        self.close()
        main_window.load_data()
        
        # Shows a confirmation message to the user.
        confirmation_box = QMessageBox()
        confirmation_box.setWindowTitle("Success")
        confirmation_box.setText("The record was deleted successfully")
        confirmation_box.exec()


class DataBase:
    def __init__(self, db_file="database.db") -> None:
        self.db_file = db_file
    
    def connect(self):
        connection = db.connect(self.db_file)
        return connection

    def create(self) -> None:
        conn = db.connect(self.db_file)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE name=='students'")
        if cur.fetchone() is None:
            cur.execute("CREATE TABLE students(id INTEGER PRIMARY KEY,"\
                                                "name VARCHAR(256),"\
                                                "course VARCHAR(256),"\
                                                "phone VARCHAR(256))")
        cur.close()
        conn.close()


DataBase().create()

app = QApplication(argv)
main_window = MainWindow()
main_window.show()
exit(app.exec())