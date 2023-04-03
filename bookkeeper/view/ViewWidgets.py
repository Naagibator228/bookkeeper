from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout,\
    QWidget, QLineEdit, QPushButton, QHBoxLayout, QComboBox, QDialog

from PyQt5.QtCore import pyqtSignal

from bookkeeper.models.category import Category
from bookkeeper.models.budget import Budget
from bookkeeper.models.expense import Expense

from _datetime import datetime


class ExpensesListWidget(QWidget):
    def __init__(self, repo_expense=None, repo_category=None):
        super().__init__()
        self.repo_expense = repo_expense
        self.repo_cat = repo_category
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Дата покупки', 'Сумма', 'Категория', 'Комментарий'])
        self.display_list()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
    def refresh_list(self):
        self.table.setRowCount(0)
        self.display_list()


    def display_list(self):
        expenses = self.repo_expense.get_all()
        categories = self.repo_cat.get_all()
        cat_ids = {}
        for category in categories:
            cat_ids[category.pk] = category.name
        for expense in expenses:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            cat = cat_ids[expense.category]
            if expense.comment == None:
                comment = ''
            else:
                comment = expense.comment
            self.table.setItem(row_position, 0, QTableWidgetItem(expense.expense_date))
            self.table.setItem(row_position, 1, QTableWidgetItem(str(expense.amount)))
            self.table.setItem(row_position, 2, QTableWidgetItem(cat))
            self.table.setItem(row_position, 3, QTableWidgetItem(comment))




class BudgetWidget(QWidget):
    def __init__(self, repo_expenses = None, repo_budget=None):
        super().__init__()
        self.repo_expenses = repo_expenses
        self.repo_budget = repo_budget
        self.table = QTableWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.display_budget()


    def display_budget(self):
        self.table.setColumnCount(3)
        self.table.setRowCount(3)
        self.table.setHorizontalHeaderLabels(['Период', 'Сумма', 'Бюджет'])
        self.table.setItem(0, 0, QTableWidgetItem('День'))
        self.table.setItem(1, 0, QTableWidgetItem('Неделя'))
        self.table.setItem(2, 0, QTableWidgetItem('Месяц'))
        budgets = self.repo_budget.get_all()

        d = {0:1, 1:7, 2:30}
        for row in range(3):
            period = self.table.item(row, 0).text()
            term_amount = 0
            for expense in self.repo_expenses.get_all():
                if (datetime.now() - datetime.strptime(expense.expense_date, '%Y-%m-%d %H:%M:%S.%f')).days < d[row]:
                    term_amount += float(expense.amount)

            self.table.setItem(row, 1, QTableWidgetItem(str(term_amount)))
            self.table.setItem(row, 2, QTableWidgetItem(str(budgets[row].amount)))

    def refresh_budget(self):
        self.table.setRowCount(0)
        self.display_budget()

class AddExpenseLineEdit(QWidget):
    expense_added = pyqtSignal()
    budget_changed = pyqtSignal()
    def __init__(self, repo_cat=None, repo_expenses=None):
        super().__init__()
        self.repo_expenses = repo_expenses
        self.repo_cat = repo_cat
        hlayout1 = QHBoxLayout()
        hlayout2 = QHBoxLayout()
        self.layout = QVBoxLayout()
        label1 = QLabel('Сумма')
        hlayout1.addWidget(label1)
        self.input1 = QLineEdit()
        hlayout1.addWidget(self.input1)
        label2 = QLabel('Категория')
        hlayout2.addWidget(label2)
        self.input2 = QComboBox()
        results = self.repo_cat.get_all()
        for result in results:
            self.input2.addItem(result.name)
        hlayout2.addWidget(self.input2)

        addButton_ = QPushButton('Редактировать')
        addButton_.clicked.connect(self.show_edit_window)
        hlayout2.addWidget(addButton_)

        self.layout.addLayout(hlayout1)
        self.layout.addLayout(hlayout2)
        self.setLayout(self.layout)
        self.addButton = QPushButton('Добавить')
        self.addButton.clicked.connect(self.add_expense)
        self.layout.addWidget(self.addButton)

    def add_expense(self):

        # Получаем данные из QLineEdit и добавляем их в базу данных
        name = self.input2.currentText()
        amount = self.input1.text()
        categories = self.repo_cat.get_all()
        cat_ids = {}
        for category in categories:
            cat_ids[category.name] = category.pk
        obj = Expense(amount=amount, category=cat_ids[name])
        obj.expense_date = datetime.now()
        self.repo_expenses.add(obj)
        self.expense_added.emit()
        self.budget_changed.emit()


    def show_edit_window(self):
        window = CategoriesWidget(self.repo_cat)
        window.exec()

class CategoriesWidget(QDialog):
    def __init__(self, repo_cat=None):
        super().__init__()
        self.repo_cat = repo_cat
        # Заполняем список категорий из базы данных
        self.setWindowTitle('Категории')
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        widgetlist = CategoriesListWidget(self.repo_cat)
        widgetedit = CategoriesEditWidget(self.repo_cat)
        self.layout.addWidget(widgetlist)
        self.layout.addWidget(widgetedit)
        widgetedit.category_added.connect(widgetlist.refresh_list)


class CategoriesListWidget(QListWidget):
    def __init__(self, repo_cat=None):
        super().__init__()
        self.repo_cat = repo_cat

        self.display_cats()

    def display_cats(self):
        categories = self.repo_cat.get_all()
        for category in categories:
            if category.get_parent(self.repo_cat) != None:
                basic_str = f'{category.name}'
                parents = category.get_all_parents(self.repo_cat)
                for p in parents:
                    basic_str += f' -> {p.name}'
                item = QListWidgetItem(basic_str)
            else:
                item = QListWidgetItem(f'{category.name}')
            self.addItem(item)
    def refresh_list(self):
        self.clear()
        self.display_cats()
class CategoriesEditWidget(QWidget):
    category_added = pyqtSignal()
    def __init__(self, repo_cat=None):
        super().__init__()
        self.repo_cat = repo_cat
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        vlayout1 = QVBoxLayout()
        label1 = QLabel('Категория')
        vlayout1.addWidget(label1)
        self.input1 = QLineEdit()
        vlayout1.addWidget(self.input1)
        vlayout2 = QVBoxLayout()
        label2 = QLabel('Категория родителя')
        vlayout2.addWidget(label2)
        self.input2 = QComboBox()
        results = self.repo_cat.get_all()
        self.input2.addItem(None)
        for result in results:
            self.input2.addItem(result.name)
        vlayout2.addWidget(self.input2)
        vlayout = QVBoxLayout()
        vlayout.addLayout(vlayout1)
        vlayout.addLayout(vlayout2)
        self.layout.addLayout(vlayout)
        self.addButton = QPushButton('Добавить')
        self.addButton.clicked.connect(self.add_category)
        self.layout.addWidget(self.addButton)

    def add_category(self):
        name = self.input1.text()
        if name == None:
            raise ValueError('Недопустимое значение')
        parent = self.input2.currentText()
        categories = self.repo_cat.get_all()
        cat_ids = {}
        for category in categories:
            cat_ids[category.name] = category.pk
        if parent in cat_ids:
            obj = Category(name=name, parent=cat_ids[parent])
        else:
            obj = Category(name=name)
        self.repo_cat.add(obj)
        self.category_added.emit()
