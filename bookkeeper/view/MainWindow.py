from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout,\
    QWidget, QLineEdit, QPushButton, QMainWindow,QApplication, QSizePolicy, QMessageBox

from bookkeeper.view.ViewWidgets import ExpensesListWidget, AddExpenseLineEdit, CategoriesListWidget, BudgetWidget
from bookkeeper.repository.sqlite_repository import SQLiteRepository


from bookkeeper.models.category import Category
from bookkeeper.models.budget import Budget
from bookkeeper.models.expense import Expense

import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Budget Tracker")
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # создаем экземпляры виджетов и добавляем их в главное окно
        def repo_category():
            return SQLiteRepository("C:/Users/User/PycharmProjects/bookkeeper/customs", Category)
        def repo_expenses():
            return SQLiteRepository("C:/Users/User/PycharmProjects/bookkeeper/customs", Expense)
        def repo_budget():
            return SQLiteRepository("C:/Users/User/PycharmProjects/bookkeeper/customs", Budget)

        expenses_widget = ExpensesListWidget(repo_expenses(), repo_category())
        expenses_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(expenses_widget)

        budget_widget = BudgetWidget(repo_expenses(), repo_budget())
        budget_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(budget_widget)

        add_expense_widget = AddExpenseLineEdit(repo_category(), repo_expenses())
        add_expense_widget.expense_added.connect(expenses_widget.refresh_list)
        add_expense_widget.budget_changed.connect(budget_widget.refresh_budget)
        add_expense_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(add_expense_widget)

        # categories_widget = CategoriesEditWidget()
        # categories_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # layout.addWidget(categories_widget)

        self.setCentralWidget(central_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())