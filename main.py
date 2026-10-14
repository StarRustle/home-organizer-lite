"""
Главное окно, кнопки, вкладки, обработка действий пользователя
"""
"""
Создаётся главное окно MainWindow.
Создаются экран входа и основной экран с вкладками.
Загружается каталог рецептов из recipes.json.
Загружаются продукты холодильника и история сеансов, если соответствующие файлы существуют.
Пользователь входит под логином. Программа записывает время входа.
Пользователь работает с холодильником и рецептами.
При выходе из аккаунта или закрытии программы фиксируется время выхода и сохраняются необходимые данные.
"""
import sys # это чтоб получить инфу о запуске закрытии проги
import json

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QMessageBox,
    QGroupBox,
    QFormLayout,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QSplitter
)
from PyQt6.QtCore import Qt
from recipe_loader import RecipeLoader
from models import Product, SessionRecord

from widgets import (
    OrganizerButton,
    UsernameInput,
    ProductNameInput,
    RecipeSearchInput,
    QuantitySpinBox,
    UnitComboBox,
    FridgeTableWidget,
    RecipeListWidget,
    RecipeDetailsTextEdit,
    OrganizerTabWidget,
)

from datetime import datetime
from pathlib import Path

class MainWindow(QMainWindow):
    """тут определяется главное окно приложения"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Домашний органайзер Lite")# название приложение
        self.resize(950, 650)# размер окна приложения

        # Главный контейнер-переключатель окон
        self.stacked_widget = QStackedWidget() # тут типо создается многостроничный контейнер и можно показывать их 
        self.setCentralWidget(self.stacked_widget) # без этого не будет отображаться. содает по центру экрана
        self.fridge_products = [] # список в котором хранятся продукты холодильника

        # Защита от перезаписи повреждённых файлов
        self.fridge_load_failed = False
        self.session_history_load_failed = False

        # Завершённые сеансы текущего запуска
        self.session_records = [] # тут храниться запись текущей сессии

        # Текущий активный сеанс
        self.active_session = None # эта штука None до тех пор пока не залогинишся 
        
        # эта штука нужна чтобы приложение знало правильный путь к папке с программой
        # При обычном запуске это папка проекта,
        # при запуске EXE — папка с исполняемым файлом.
        if getattr(sys, "frozen", False):
            self.app_dir = Path(sys.executable).resolve().parent
        else:
            self.app_dir = Path(__file__).resolve().parent

        # Путь к текстовому отчёту
        self.report_path = self.app_dir / "session_report.txt"

        # создает путь к списку холодильника
        self.fridge_path = (
            self.app_dir / "data" / "fridge.json"
        )

        # Путь к истории сеансов
        self.session_history_path = (
            self.app_dir / "data" / "session_records.json"
        )

        # Создается экран логина и главный экран
        self.init_login_screen()
        self.init_main_screen()

        # Загружаем сохранённые продукты
        self.load_fridge() # он загружает в приложение сохраненные продукты из json файла холодильника
        self.load_session_records() # также из json загружает записи прошлой сессии

        # Показываем первый экран (индекс 0 - логин)
        self.stacked_widget.setCurrentIndex(0) # принудительно запускает экран логина 

    def init_login_screen(self):
        """Создание экрана логина (Страница 0)"""
        login_page = QWidget()
        layout = QVBoxLayout(login_page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Сдвигаем элементы к верху страницы в центр и растягиваем на всю высоту (так и не понял)

        # Верхняя панель авторизации
        auth_box = QHBoxLayout()
        
        self.login_input = UsernameInput() # создается поле логина
        self.login_input.setPlaceholderText("Введите логин...") # пишем в это поле текст подсказку
        self.login_input.setFixedWidth(200) # задается ширина поля логина 

        login_button = OrganizerButton("Войти") # создается кнопка входа
        login_button.clicked.connect(self.handle_login) # говорит что при происходи при нажатии кнопки

        auth_box.addWidget(QLabel("Логин:")) # типо сначала появлятся надпись логин
        auth_box.addWidget(self.login_input) # потом появляется поле
        auth_box.addWidget(login_button) # потом появляется кнопка логина
        auth_box.addStretch() # Сдвигает элементы влево внутри QHBoxLayout

        layout.addLayout(auth_box) # это чтобы не растянулось на всю ширину 

        # Нижняя (пустая пока) часть экрана логина
        welcome_label = QLabel("\n\nПожалуйста, авторизуйтесь для доступа к системе.")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # выравнивае по центру
        layout.addWidget(welcome_label)

        # Добавляем страницу в менеджер окон
        self.stacked_widget.addWidget(login_page) # завершает создание окна и дает ему индекс 0 по которому его можно насильно активировать    
    
    def init_main_screen(self):
        """Создание главного экрана приложения."""

        main_page = QWidget() # создается второй виджет с индексом 1
        layout = QVBoxLayout(main_page) # какая то вертикальная разметка по которой будут размещаться все элементы потом

        # Приветствие пользователя
        self.user_greeting = QLabel("") # создается приветсвие. "" пустое так как заранее не знает он забирает имя из handle_login
        self.user_greeting.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: green;" # делает размер текста 16 шрифт жирным и цвет зеленым 
        )
        layout.addWidget(self.user_greeting) # добавляет на страницу в самый вверх так как создается самой первой

        # Создание вкладок
        self.tabs = OrganizerTabWidget()

        
        # ----------------ВКЛАДКА 1. ХОЛОДИЛЬНИК----------------------
        

        self.tab1 = QWidget()
        tab1_layout = QVBoxLayout(self.tab1)

        # Форма добавления продукта
        add_product_box = QGroupBox("Добавить продукт")
        form_layout = QFormLayout(add_product_box)

        # Название продукта
        self.product_name_input = ProductNameInput()
        self.product_name_input.setPlaceholderText(
            "Например, молоко"
        )

        form_layout.addRow(
            "Название продукта:",
            self.product_name_input
        )

        # Количество продукта
        self.product_quantity_input = QuantitySpinBox()
        self.product_quantity_input.setRange(0.01, 1000000)
        self.product_quantity_input.setDecimals(2)
        self.product_quantity_input.setValue(1.00)

        # Единица измерения
        self.product_unit_input = UnitComboBox()
        self.product_unit_input.addItems([
            "г",
            "кг",
            "мл",
            "л",
            "шт",
            "ст. ложка",
            "ч. ложка",
            "щепотка",
            "зубчик",
            "пучок",
            "пакет",
            "банка",
            "стакан",
            "по вкусу"
        ])

        # Объединяем количество и единицу измерения
        quantity_widget = QWidget()
        quantity_layout = QHBoxLayout(quantity_widget)
        quantity_layout.setContentsMargins(0, 0, 0, 0)

        quantity_layout.addWidget(self.product_quantity_input)
        quantity_layout.addWidget(self.product_unit_input)

        form_layout.addRow("Количество:", quantity_widget)

        # Создаём кнопку ДО подключения её метода
        self.add_product_button = OrganizerButton("Добавить продукт")
        self.add_product_button.clicked.connect(self.add_product)

        form_layout.addRow(self.add_product_button)

        tab1_layout.addWidget(add_product_box)

        # Таблица холодильника
        self.product_table = FridgeTableWidget(0, 3)

        self.product_table.deleteRequested.connect(
            self.delete_product
        )

        self.product_table.setHorizontalHeaderLabels([
            "Продукт",
            "Количество",
            "Единица"
        ])

        header = self.product_table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch
        )
        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents
        )

        self.product_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.product_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.product_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.product_table.setAlternatingRowColors(True)
        self.product_table.verticalHeader().setVisible(False)

        tab1_layout.addWidget(self.product_table)

        # Кнопка удаления продукта
        self.delete_product_button = OrganizerButton(
            "Удалить выбранный продукт"
        )

        self.delete_product_button.clicked.connect(
            self.delete_product
        )

        tab1_layout.addWidget(self.delete_product_button)

        self.tabs.addTab(self.tab1, "Холодильник")

        
        
        # ------------------ВКЛАДКА 2. РЕЦЕПТЫ--------------
        

        self.tab2 = QWidget()
        tab2_layout = QVBoxLayout(self.tab2)

        # Строка поиска
        search_layout = QHBoxLayout()

        self.recipe_search_input = RecipeSearchInput()
        self.recipe_search_input.setPlaceholderText(
            "Введите название рецепта или ингредиент..."
        )

        self.recipe_search_button = OrganizerButton("Найти")
        self.show_all_recipes_button = OrganizerButton("Показать все")
        self.match_fridge_button = OrganizerButton(
            "Подобрать по холодильнику"
        )

        search_layout.addWidget(self.recipe_search_input, 1)
        search_layout.addWidget(self.recipe_search_button)
        search_layout.addWidget(self.show_all_recipes_button)
        search_layout.addWidget(self.match_fridge_button)

        tab2_layout.addLayout(search_layout)

        # Разделение списка и подробного описания
        self.recipe_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Левая часть: список рецептов
        self.recipe_list = RecipeListWidget()
        self.recipe_list.setMinimumWidth(180)

        self.recipe_splitter.addWidget(self.recipe_list)

        # Правая часть: подробное описание рецепта
        recipe_details = QWidget()
        details_layout = QVBoxLayout(recipe_details)

        self.recipe_title_label = QLabel(
            "Выберите рецепт из списка"
        )
        self.recipe_title_label.setStyleSheet(
            "font-size: 16px; font-weight: bold;"
        )
        self.recipe_title_label.setWordWrap(True)

        details_layout.addWidget(self.recipe_title_label)

        # Ингредиенты
        details_layout.addWidget(QLabel("Ингредиенты:"))

        self.recipe_ingredients_text = RecipeDetailsTextEdit()
        self.recipe_ingredients_text.setPlaceholderText(
            "Здесь будут отображаться ингредиенты рецепта."
        )
        self.recipe_ingredients_text.setReadOnly(True)

        details_layout.addWidget(self.recipe_ingredients_text, 1)

        # Способ приготовления
        details_layout.addWidget(QLabel("Приготовление:"))

        self.recipe_instructions_text = RecipeDetailsTextEdit()
        self.recipe_instructions_text.setPlaceholderText(
            "Здесь будет отображаться способ приготовления."
        )
        self.recipe_instructions_text.setReadOnly(True)

        details_layout.addWidget(self.recipe_instructions_text, 2)

        self.recipe_splitter.addWidget(recipe_details)

        # Начальное соотношение ширины областей
        self.recipe_splitter.setStretchFactor(0, 1)
        self.recipe_splitter.setStretchFactor(1, 2)

        tab2_layout.addWidget(self.recipe_splitter, 1)

        # Сообщение о состоянии каталога
        self.recipe_status_label = QLabel(
            "Каталог рецептов пока не загружен."
        )
        tab2_layout.addWidget(self.recipe_status_label)

        # Добавляем вкладку
        self.tabs.addTab(self.tab2, "Рецепты")

        # Подключаем поиск рецептов
        self.recipe_search_button.clicked.connect(
            self.search_recipes
        )

        # Поиск также запускается нажатием Enter
        self.recipe_search_input.returnPressed.connect(
            self.search_recipes
        )

        # Очистка поиска клавишей Escape
        self.recipe_search_input.escapePressed.connect(
            self.show_all_recipes
        )

        # Кнопка показа полного каталога
        self.show_all_recipes_button.clicked.connect(
            self.show_all_recipes
        )

        self.match_fridge_button.clicked.connect(
            self.match_fridge_recipes
        )

        # Выбор рецепта в списке
        self.recipe_list.currentRowChanged.connect(
            self.show_selected_recipe
        )

        self.recipe_list.recipeActivated.connect(
            self.show_selected_recipe
        )

        # Загружаем рецепты
        self.load_recipes()

        # Добавляем вкладки в главное окно
        layout.addWidget(self.tabs)

        # Кнопка выхода из аккаунта
        logout_layout = QHBoxLayout()
        logout_layout.addStretch()

        logout_button = OrganizerButton("Выйти из аккаунта")
        logout_button.setFixedWidth(150)
        logout_button.clicked.connect(self.handle_logout)

        logout_layout.addWidget(logout_button)
        layout.addLayout(logout_layout)

        # Добавляем страницу в переключатель один раз
        self.stacked_widget.addWidget(main_page)

    
    
    def load_recipes(self):
        """Загрузка рецептов из JSON."""

        self.recipe_list.clear()
        self.recipes = []
        self.displayed_recipes = []

        try:
            self.recipes = RecipeLoader().load_recipes()

        except (OSError, ValueError, TypeError) as error:
            self.recipe_title_label.setText(
                "Не удалось загрузить рецепты"
            )

            self.recipe_ingredients_text.clear()
            self.recipe_instructions_text.clear()

            self.recipe_status_label.setText(
                f"Ошибка загрузки рецептов: {error}"
            )
            return

        self._display_recipes(
            self.recipes,
            f"Загружено рецептов: {len(self.recipes)}"
        )

    def _display_recipes(self, recipes, status_text, labels=None):
        """Отображение списка рецептов."""

        self.displayed_recipes = list(recipes)
        self.recipe_list.clear()

        for index, recipe in enumerate(self.displayed_recipes):
            if labels is not None:
                label = labels[index]
            else:
                label = recipe.title

            self.recipe_list.addItem(label)

        self.recipe_status_label.setText(status_text)

        if self.displayed_recipes:
            self.recipe_list.setCurrentRow(0)
        else:
            self.recipe_title_label.setText(
                "Рецепты не найдены"
            )

            self.recipe_ingredients_text.clear()
            self.recipe_instructions_text.clear()

    def search_recipes(self):
        """Поиск по названию рецепта и ингредиентам."""

        query = self.recipe_search_input.text().strip().casefold()

        if not query:
            self.show_all_recipes()
            return

        matching_recipes = []

        for recipe in self.recipes:
            # Проверяем название рецепта
            if query in recipe.title.casefold():
                matching_recipes.append(recipe)
                continue

            # Проверяем названия ингредиентов
            for ingredient in recipe.ingredients:
                if query in ingredient.name.casefold():
                    matching_recipes.append(recipe)
                    break

        self._display_recipes(
            matching_recipes,
            f"Найдено рецептов: {len(matching_recipes)}"
        )

    @staticmethod
    def _normalize_product_name(name):
        """Убирает лишние пробелы и приводит название к нижнему регистру."""

        return " ".join(name.casefold().split())


    def match_fridge_recipes(self):
        """Подбирает рецепты по названиям продуктов холодильника."""

        if not self.fridge_products: # если ничего нет выдает это
            self._display_recipes(
                [],
                "Добавьте продукты в холодильник для подбора рецептов."
            )

            QMessageBox.information(
                self,
                "Подбор рецептов",
                "Сначала добавьте хотя бы один продукт в холодильник."
            )
            return

        # Собираем названия продуктов холодильника
        fridge_names = {
            self._normalize_product_name(product.name)
            for product in self.fridge_products
        }

        results = []

        # Считаем совпадения для каждого рецепта
        for recipe in self.recipes:
            total = len(recipe.ingredients)

            matched = sum(
                1
                for ingredient in recipe.ingredients
                if self._normalize_product_name(ingredient.name)
                in fridge_names
            )

            # Рецепты без совпадений не показываем
            if matched > 0:
                results.append((recipe, matched, total))

            # Сначала рецепты с большей долей совпадений,
            # затем — с большим числом совпавших ингредиентов
            results.sort(
                key=lambda item: (
                    item[1] / item[2],
                    item[1]
                ),
                reverse=True
            )

            matching_recipes = [
                recipe
                for recipe, matched, total in results
            ]

            labels = [
                f"{recipe.title} — совпадений: {matched}/{total}"
                for recipe, matched, total in results
            ]

            if results:
                status_text = (
                    f"Найдено рецептов: {len(results)}. "
                    "Сортировка по доле совпавших ингредиентов. "
                    "Количество продуктов не учитывается."
                )
            else:
                status_text = (
                    "Не найдено рецептов с указанными продуктами."
                )

            self._display_recipes(
                matching_recipes,
                status_text,
                labels
            )

    def show_all_recipes(self):
        """очищает поле поиска возвращает полный каталог рецептов."""

        self.recipe_search_input.clear()

        self._display_recipes(
            self.recipes,
            f"Всего рецептов: {len(self.recipes)}"
        )

    def show_selected_recipe(self, row):
        """получает номер выбранной строки и показывает рецепт в этой строке по очереди название ингрид и инструкция."""

        if row < 0 or row >= len(self.displayed_recipes):
            return

        recipe = self.displayed_recipes[row]

        self.recipe_title_label.setText(recipe.title)

        ingredients_text = "\n".join(
            str(ingredient) # ингридиенты преобразуются в строки
            for ingredient in recipe.ingredients
        )

        self.recipe_ingredients_text.setPlainText(
            ingredients_text
        )

        self.recipe_instructions_text.setPlainText(
            recipe.instructions
        )

    
    def handle_login(self):
        """типо вход. вводим логин проверяем что он не пустой."""

        username = self.login_input.text().strip()

        if not username:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Поле логина не может быть пустым!"
            )
            return

        # Создаём запись об активном сеансе
        self.active_session = SessionRecord(
            username,
            datetime.now() #возвращает время и дату
        )

        self.user_greeting.setText(
            f"Добро пожаловать, {username}!"
        )

        self.statusBar().showMessage(
            f"Авторизован как: {username}"
        )

        self.stacked_widget.setCurrentIndex(1)


    def delete_product(self):
        """Удаляет продукт и сохраняет обновлённый холодильник."""

        if self.fridge_load_failed:
            QMessageBox.warning(
                self,
                "Холодильник недоступен",
                "Сначала исправьте файл data/fridge.json "
                "и перезапустите приложение."
            )
            return

        row = self.product_table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "Удаление продукта",
                "Сначала выберите продукт в таблице."
            )
            return

        product = self.fridge_products.pop(row)
        self._refresh_fridge_table()

        if not self.save_fridge():
            # Возвращаем продукт на прежнее место при ошибке сохранения.
            self.fridge_products.insert(row, product)
            self._refresh_fridge_table()
            return

        self.statusBar().showMessage(
            f"Продукт «{product.name}» удалён.",
            3000
        )

    def load_fridge(self):
        """Загружает продукты из json также проверяет нормалная ли запись если нет говорит об этом ."""

        self.fridge_load_failed = False

        if not self.fridge_path.exists():
            return

        try:
            with self.fridge_path.open(
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            self.fridge_load_failed = True

            QMessageBox.warning(
                self,
                "Ошибка загрузки холодильника",
                "Не удалось прочитать файл холодильника.\n"
                f"Причина: {error}\n\n"
                "Файл не будет перезаписан. "
                "Добавление и удаление продуктов временно заблокированы."
            )
            return

        if not isinstance(data, list):
            self.fridge_load_failed = True

            QMessageBox.warning(
                self,
                "Ошибка загрузки холодильника",
                "Корневой элемент файла должен быть списком.\n"
                "Файл не будет перезаписан. "
                "Исправьте его и перезапустите приложение."
            )
            return

        loaded_products = []
        invalid_count = 0

        for record in data:
            if not isinstance(record, list) or len(record) != 3:
                invalid_count += 1
                continue

            try:
                product = Product(
                    record[0],
                    record[1],
                    record[2]
                )

            except (TypeError, ValueError):
                invalid_count += 1
                continue

            loaded_products.append(product)

        self.fridge_products = loaded_products
        self._refresh_fridge_table()

        if invalid_count:
            self.fridge_load_failed = True

            QMessageBox.warning(
                self,
                "Некорректные данные холодильника",
                f"Пропущено некорректных записей: {invalid_count}.\n\n"
                "Корректные продукты отображены, но добавление и "
                "удаление временно заблокированы, чтобы не потерять "
                "данные. Исправьте файл data/fridge.json."
            )
        else:
            self.statusBar().showMessage(
                f"Загружено продуктов: {len(self.fridge_products)}",
                3000
            )


    def _refresh_fridge_table(self):
        """Обновляет таблицу по текущему списку продуктов."""

        self.product_table.setRowCount(0)

        for product in self.fridge_products:
            row = self.product_table.rowCount()
            self.product_table.insertRow(row)

            self.product_table.setItem(
                row,
                0,
                QTableWidgetItem(product.name)
            )

            self.product_table.setItem(
                row,
                1,
                QTableWidgetItem(f"{product.quantity:g}")
            )

            self.product_table.setItem(
                row,
                2,
                QTableWidgetItem(product.unit)
            )

    def _load_legacy_session_records(self):
        """Восстанавливает историю из прежнего текстового отчёта."""

        if not self.report_path.exists():
            return []

        try:
            lines = self.report_path.read_text(
                encoding="utf-8"
            ).splitlines()

        except (OSError, UnicodeError):
            return []

        records = []
        time_format = "%d.%m.%Y %H:%M:%S"

        for line in lines:
            if not line.strip().startswith("|"):
                continue

            columns = [
                part.strip()
                for part in line.strip().strip("|").split("|")
            ]

            # Пропускаем заголовки и некорректные строки
            if len(columns) != 3:
                continue

            if columns[0].casefold() == "login":
                continue

            if not columns[0] or not columns[1] or not columns[2]:
                continue

            try:
                record = SessionRecord(
                    columns[0],
                    datetime.strptime(columns[1], time_format),
                    datetime.strptime(columns[2], time_format)
                )

            except (TypeError, ValueError):
                continue

            records.append(record)

        return records

    def load_session_records(self):
        """Загружает историю и защищает файл от перезаписи при ошибке."""

        self.session_history_load_failed = False

        if not self.session_history_path.exists():
            self.session_records = self._load_legacy_session_records()
            return

        try:
            with self.session_history_path.open(
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            self.session_history_load_failed = True
            self.session_records = self._load_legacy_session_records()

            QMessageBox.warning(
                self,
                "Ошибка загрузки истории",
                "Не удалось прочитать JSON-файл истории сеансов.\n"
                f"Причина: {error}\n\n"
                "Будет использован текстовый отчёт, если он доступен. "
                "Повреждённый JSON-файл не будет перезаписан."
            )
            return

        if not isinstance(data, list):
            self.session_history_load_failed = True
            self.session_records = self._load_legacy_session_records()

            QMessageBox.warning(
                self,
                "Ошибка загрузки истории",
                "Файл истории должен содержать список записей.\n\n"
                "Будет использован текстовый отчёт, если он доступен. "
                "Исходный JSON-файл не будет перезаписан."
            )
            return

        loaded_records = []
        invalid_count = 0
        time_format = "%d.%m.%Y %H:%M:%S"

        for item in data:
            if not isinstance(item, list) or len(item) != 3:
                invalid_count += 1
                continue

            try:
                time_in = datetime.strptime(
                    item[1],
                    time_format
                )

                if item[2] in (None, ""):
                    time_out = None
                else:
                    time_out = datetime.strptime(
                        item[2],
                        time_format
                    )

                record = SessionRecord(
                    item[0],
                    time_in,
                    time_out
                )

            except (TypeError, ValueError):
                invalid_count += 1
                continue

            loaded_records.append(record)

        if invalid_count:
            self.session_history_load_failed = True

            # Дополняем корректные записи данными из старого отчёта.
            # Одинаковые записи повторно не добавляем.
            legacy_records = self._load_legacy_session_records()

            for legacy_record in legacy_records:
                if legacy_record not in loaded_records:
                    loaded_records.append(legacy_record)

            self.session_records = sorted(loaded_records)

            QMessageBox.warning(
                self,
                "Некорректная история",
                f"Пропущено повреждённых записей: {invalid_count}.\n\n"
                "Доступные записи восстановлены из JSON и текстового "
                "отчёта. Исходный JSON-файл не будет перезаписан, "
                "чтобы избежать потери данных."
            )
        else:
            self.session_records = loaded_records

    def _save_session_history(self):
        """Сохраняет историю сеансов в JSON."""

        data = []
        time_format = "%d.%m.%Y %H:%M:%S"

        for record in self.session_records:
            record.validate()

            time_in_text = record.time_in.strftime(time_format)

            time_out_text = (
                record.time_out.strftime(time_format)
                if record.time_out is not None
                else ""
            )

            # Список из трёх значений вместо словаря
            data.append([
                record.login,
                time_in_text,
                time_out_text
            ])

        self.session_history_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with self.session_history_path.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4
            )
            file.write("\n")

    def _save_session_data(self):
        """Сохраняет историю сеансов и текстовый отчёт."""

        if self.session_history_load_failed:
            self.statusBar().showMessage(
                "JSON-файл истории повреждён. "
                "История сохраняется только в текстовый отчёт.",
                7000
            )
        else:
            try:
                self._save_session_history()

            except (OSError, TypeError, ValueError) as error:
                QMessageBox.warning(
                    self,
                    "Ошибка сохранения истории",
                    f"Не удалось сохранить историю сеансов:\n{error}"
                )

        # Текстовый отчёт сохраняется даже при повреждённом JSON.
        try:
            self._save_session_report()

        except OSError as error:
            QMessageBox.warning(
                self,
                "Ошибка сохранения отчёта",
                f"Не удалось сохранить текстовый отчёт:\n{error}"
            )

    def save_fridge(self):
        """сохраняет продукты переводит их в список списков(dict по задания низя) и кидает в json ."""

        if self.fridge_load_failed:
            return False

        data = [
            [
                product.name,
                product.quantity,
                product.unit
            ]
            for product in self.fridge_products
        ]

        try:
            self.fridge_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            with self.fridge_path.open(
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=4
                )
                file.write("\n")

        except OSError as error:
            QMessageBox.warning(
                self,
                "Ошибка сохранения холодильника",
                f"Не удалось сохранить продукты:\n{error}"
            )
            return False

        return True

    def add_product(self):
        """Добавляет продукт или увеличивает существующее количество также проверяет можно ли его вообще менять."""

        if self.fridge_load_failed:
            QMessageBox.warning(
                self,
                "Холодильник недоступен",
                "Сначала исправьте файл data/fridge.json "
                "и перезапустите приложение."
            )
            return

        name = self.product_name_input.text().strip()

        if not name:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Введите название продукта."
            )
            return

        quantity = self.product_quantity_input.value()
        unit = self.product_unit_input.currentText()

        try:
            product = Product(name, quantity, unit)

        except (TypeError, ValueError) as error:
            QMessageBox.warning(
                self,
                "Ошибка",
                str(error)
            )
            return

        normalized_name = self._normalize_product_name(
            product.name
        )
        normalized_unit = self._normalize_product_name(
            product.unit
        )

        # Ищем продукт с таким же названием и единицей измерения.
        for existing_product in self.fridge_products:
            existing_name = self._normalize_product_name(
                existing_product.name
            )
            existing_unit = self._normalize_product_name(
                existing_product.unit
            )

            if (
                existing_name == normalized_name
                and existing_unit == normalized_unit
            ):
                previous_quantity = existing_product.quantity

                existing_product.quantity = (
                    previous_quantity + product.quantity
                )

                self._refresh_fridge_table()

                if not self.save_fridge():
                    # При ошибке сохранения восстанавливаем прежнее количество.
                    existing_product.quantity = previous_quantity
                    self._refresh_fridge_table()
                    return

                self.product_name_input.clear()
                self.product_quantity_input.setValue(1.0)

                self.statusBar().showMessage(
                    f"Количество продукта «{existing_product.name}» "
                    f"увеличено до {existing_product.quantity:g} "
                    f"{existing_product.unit}.",
                    4000
                )
                return

        # Если такого продукта нет, добавляем новую запись.
        self.fridge_products.append(product)
        self._refresh_fridge_table()

        if not self.save_fridge():
            self.fridge_products.pop()
            self._refresh_fridge_table()
            return

        self.product_name_input.clear()
        self.product_quantity_input.setValue(1.0)

        self.statusBar().showMessage(
            f"Продукт «{product.name}» добавлен.",
            3000
        )

    
    def handle_logout(self):
        """Завершает сеанс сохраняет в json репорт и сохраняет историю."""

        if self.active_session is not None:
            self.active_session.time_out = datetime.now()
            self.active_session.validate()

            self.session_records.append(
                self.active_session
            )

            self.active_session = None

            # Сохраняем завершённый сеанс сразу при выходе
            self._save_session_data()

        self.login_input.clear()

        self.statusBar().showMessage(
            "Вышли из системы"
        )

        self.stacked_widget.setCurrentIndex(0)


    def _save_session_report(self):
        """Сохраняет таблицу сеансов в текстовый файл."""

        columns = (
            "login",
            "time_in",
            "time_out"
        )

        login_width = max(
            [len(columns[0])]
            + [
                len(record.login)
                for record in self.session_records
            ]
        )

        time_in_width = max(len(columns[1]), 19)
        time_out_width = max(len(columns[2]), 19)

        widths = (
            login_width,
            time_in_width,
            time_out_width
        )

        # Верхняя и нижняя границы таблицы
        border = (
            "+"
            + "+".join("-" * (width + 2) for width in widths)
            + "+"
        )

        # Разделитель между заголовками и данными
        separator = (
            "+"
            + "+".join("-" * (width + 2) for width in widths)
            + "+"
        )

        header = (
            f"| {columns[0]:<{login_width}} "
            f"| {columns[1]:<{time_in_width}} "
            f"| {columns[2]:<{time_out_width}} |"
        )

        lines = [
            border,
            header,
            separator
        ]

        for record in self.session_records:
            record.validate()

            time_in_text = record.time_in.strftime(
                "%d.%m.%Y %H:%M:%S"
            )

            time_out_text = (
                record.time_out.strftime("%d.%m.%Y %H:%M:%S")
                if record.time_out is not None
                else ""
            )

            line = (
                f"| {record.login:<{login_width}} "
                f"| {time_in_text:<{time_in_width}} "
                f"| {time_out_text:<{time_out_width}} |"
            )

            lines.append(line)

        lines.append(border)

        self.report_path.write_text(
            "\n".join(lines) + "\n",
            encoding="utf-8"
        )

    def closeEvent(self, event):
        """Завершает сеанс и сохраняет данные приложения. это нужно на случай если закрыли крестиком а не вышли из акка и потом закрыли"""

        if self.active_session is not None:
            self.active_session.time_out = datetime.now()
            self.active_session.validate()

            self.session_records.append(
                self.active_session
            )

            self.active_session = None

        # Не перезаписываем холодильник, если его файл повреждён.
        if not self.fridge_load_failed:
            self.save_fridge()

        self._save_session_data()

        event.accept()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
