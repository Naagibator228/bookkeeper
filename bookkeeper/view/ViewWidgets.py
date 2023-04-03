from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout,\
    QWidget, QLineEdit, QPushButton, QHBoxLayout, QComboBox

from bookkeeper.models.category import Category
from bookkeeper.models.budget import Budget
from bookkeeper.models.expense import Expense

from _datetime import datetime
class ExpensesListWidget(QListWidget):
    def __init__(self, repo_expense=None, repo_category=None):
        super().__init__()

        self.repo_expense = repo_expense
        self.repo_cat = repo_category
        # Заполняем список расходов из базы данных
        expenses = self.repo_expense.get_all()
        categories = self.repo_cat.get_all()
        cat_ids = {}
        for category in categories:
            cat_ids[category.pk] = category.name
        for expense in expenses:
            cat = cat_ids[expense.category]
            if expense.comment == None:
                comment = ''
            else:
                comment = expense.comment
            item = QListWidgetItem(f'{expense.expense_date}    {cat}    {expense.amount}    {comment}')
            self.addItem(item)



class BudgetWidget(QWidget):
    def __init__(self, repo=None):
        super().__init__()

        self.repo = repo

        # Создаем таблицу
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setRowCount(3)
        self.table.setHorizontalHeaderLabels(['Период', 'Сумма', 'Бюджет'])

        # Заполняем таблицу данными
        self.table.setItem(0, 0, QTableWidgetItem('День'))
        self.table.setItem(1, 0, QTableWidgetItem('Неделя'))
        self.table.setItem(2, 0, QTableWidgetItem('Месяц'))

        for row in range(3):
            period = self.table.item(row, 0).text()
            #spent = self.repo.get_spent_for_period(period)
            spent = 3.422*(row+1)
            # budget = self.repo.get_budget_for_period(period)
            budget = 5000*(row+1)

            self.table.setItem(row, 1, QTableWidgetItem(str(spent)))
            self.table.setItem(row, 2, QTableWidgetItem(str(budget)))

        # Создаем метку для отображения общей суммы бюджета
        # self.total_label = QLabel()
        # self.update_total_label()

        # Создаем вертикальный лэйаут и добавляем в него таблицу и метку
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        # layout.addWidget(self.total_label)
        self.setLayout(layout)

    def update_total_label(self):
        total_budget = self.repository.get_total_budget()
        self.total_label.setText(f'Общий бюджет: {total_budget}')

class AddExpenseLineEdit(QWidget):
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
        hlayout2.addWidget(addButton_)

        self.layout.addLayout(hlayout1)
        self.layout.addLayout(hlayout2)
        self.setLayout(self.layout)
        # Добавляем кнопку для добавления нового расхода
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
        obj = Expense(amount=amount, category = cat_ids[name])
        obj.expense_date = datetime.now()
        self.repo_expenses.add(obj)

class CategoriesListWidget(QListWidget):
    def __init__(self, repo=None):
        super().__init__()
        self.repo = repo
        # Заполняем список категорий из базы данных
        # categories = repo.get_all()
        categories = ['Еда', 'Хозтовары']
        for category in categories:
            item = QListWidgetItem(f'{category}')
            self.addItem(item)