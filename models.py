from abc import ABC, abstractmethod
from datetime import datetime


class BaseEntity(ABC):
    """Абстрактный базовый класс для сущностей приложения."""

    @abstractmethod
    def validate(self):
        """Проверяет корректность данных сущности."""
        raise NotImplementedError(
            "Каждая сущность должна реализовать validate()."
        )


class Product(BaseEntity):
    """Продукт, который хранится в холодильнике."""

    def __init__(self, name, quantity, unit):
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.validate()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError("Название продукта должно быть строкой.")

        value = value.strip()

        if not value:
            raise ValueError("Название продукта не может быть пустым.")

        self._name = value

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError) as error:
            raise ValueError(
                "Количество должно быть числом."
            ) from error

        if value <= 0:
            raise ValueError("Количество должно быть больше нуля.")

        self._quantity = value

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, value):
        if not isinstance(value, str):
            raise TypeError("Единица измерения должна быть строкой.")

        value = value.strip()

        if not value:
            raise ValueError("Единица измерения не может быть пустой.")

        self._unit = value

    def validate(self):
        if not self.name or not self.unit or self.quantity <= 0:
            raise ValueError("Данные продукта некорректны.")

    def __str__(self):
        return f"{self.name}: {self.quantity:g} {self.unit}"

    def __repr__(self):
        return (
            f"Product(name={self.name!r}, "
            f"quantity={self.quantity!r}, unit={self.unit!r})"
        )

    def __eq__(self, other):
        if not isinstance(other, Product):
            return NotImplemented

        return (
            self.name.casefold() == other.name.casefold()
            and self.quantity == other.quantity
            and self.unit.casefold() == other.unit.casefold()
        )

    def __lt__(self, other):
        if not isinstance(other, Product):
            return NotImplemented

        return (
            self.name.casefold(),
            self.unit.casefold(),
            self.quantity
        ) < (
            other.name.casefold(),
            other.unit.casefold(),
            other.quantity
        )

    def __format__(self, format_spec):
        if format_spec == "short":
            return self.name

        if format_spec == "quantity":
            return f"{self.quantity:g} {self.unit}"

        return format(str(self), format_spec)

    def __add__(self, other):
        if not isinstance(other, Product):
            return NotImplemented

        if (
            self.name.casefold() != other.name.casefold()
            or self.unit.casefold() != other.unit.casefold()
        ):
            raise ValueError(
                "Можно складывать количество только одинаковых "
                "продуктов с одинаковыми единицами измерения."
            )

        return Product(
            self.name,
            self.quantity + other.quantity,
            self.unit
        )


class Ingredient(BaseEntity):
    """Ингредиент, используемый в рецепте."""

    def __init__(self, name, quantity, unit):
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.validate()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError("Название ингредиента должно быть строкой.")

        value = value.strip()

        if not value:
            raise ValueError("Название ингредиента не может быть пустым.")

        self._name = value

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError) as error:
            raise ValueError(
                "Количество ингредиента должно быть числом."
            ) from error

        if value <= 0:
            raise ValueError(
                "Количество ингредиента должно быть больше нуля."
            )

        self._quantity = value

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, value):
        if not isinstance(value, str):
            raise TypeError("Единица измерения должна быть строкой.")

        value = value.strip()

        if not value:
            raise ValueError("Единица измерения не может быть пустой.")

        self._unit = value

    def validate(self):
        if not self.name or not self.unit or self.quantity <= 0:
            raise ValueError("Данные ингредиента некорректны.")

    def __str__(self):
        return f"{self.name}: {self.quantity:g} {self.unit}"

    def __repr__(self):
        return (
            f"Ingredient(name={self.name!r}, "
            f"quantity={self.quantity!r}, unit={self.unit!r})"
        )

    def __eq__(self, other):
        if not isinstance(other, Ingredient):
            return NotImplemented

        return (
            self.name.casefold() == other.name.casefold()
            and self.quantity == other.quantity
            and self.unit.casefold() == other.unit.casefold()
        )

    def __lt__(self, other):
        if not isinstance(other, Ingredient):
            return NotImplemented

        return (
            self.name.casefold(),
            self.unit.casefold(),
            self.quantity
        ) < (
            other.name.casefold(),
            other.unit.casefold(),
            other.quantity
        )

    def __format__(self, format_spec):
        if format_spec == "short":
            return self.name

        if format_spec == "quantity":
            return f"{self.quantity:g} {self.unit}"

        return format(str(self), format_spec)

    def __add__(self, other):
        if not isinstance(other, Ingredient):
            return NotImplemented

        if (
            self.name.casefold() != other.name.casefold()
            or self.unit.casefold() != other.unit.casefold()
        ):
            raise ValueError(
                "Можно складывать только одинаковые ингредиенты "
                "с одинаковыми единицами измерения."
            )

        return Ingredient(
            self.name,
            self.quantity + other.quantity,
            self.unit
        )


class Recipe(BaseEntity):
    """Рецепт с ингредиентами и инструкцией приготовления."""

    def __init__(self, title, ingredients, instructions):
        self.title = title
        self.ingredients = ingredients
        self.instructions = instructions
        self.validate()

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if not isinstance(value, str):
            raise TypeError("Название рецепта должно быть строкой.")

        value = value.strip()

        if not value:
            raise ValueError("Название рецепта не может быть пустым.")

        self._title = value

    @property
    def ingredients(self):
        # Возвращаем неизменяемый набор ингредиентов.
        return tuple(self._ingredients)

    @ingredients.setter
    def ingredients(self, value):
        if not isinstance(value, (list, tuple)):
            raise TypeError(
                "Ингредиенты должны передаваться списком или кортежем."
            )

        items = list(value)

        if not items:
            raise ValueError(
                "Рецепт должен содержать хотя бы один ингредиент."
            )

        for item in items:
            if not isinstance(item, Ingredient):
                raise TypeError(
                    "Каждый ингредиент должен быть объектом Ingredient."
                )

        self._ingredients = items

    @property
    def instructions(self):
        return self._instructions

    @instructions.setter
    def instructions(self, value):
        if not isinstance(value, str):
            raise TypeError(
                "Инструкция приготовления должна быть строкой."
            )

        value = value.strip()

        if not value:
            raise ValueError(
                "Инструкция приготовления не может быть пустой."
            )

        self._instructions = value

    def validate(self):
        if not self.title or not self.instructions:
            raise ValueError("Данные рецепта некорректны.")

        if not self._ingredients:
            raise ValueError("У рецепта отсутствуют ингредиенты.")

        for ingredient in self._ingredients:
            ingredient.validate()

    def __str__(self):
        return self.title

    def __repr__(self):
        return (
            f"Recipe(title={self.title!r}, "
            f"ingredients={self.ingredients!r}, "
            f"instructions={self.instructions!r})"
        )

    def __eq__(self, other):
        if not isinstance(other, Recipe):
            return NotImplemented

        return (
            self.title.casefold() == other.title.casefold()
            and self.ingredients == other.ingredients
            and self.instructions == other.instructions
        )

    def __lt__(self, other):
        if not isinstance(other, Recipe):
            return NotImplemented

        return self.title.casefold() < other.title.casefold()

    def __format__(self, format_spec):
        if format_spec == "title":
            return self.title

        if format_spec == "summary":
            return (
                f"{self.title} — "
                f"ингредиентов: {len(self)}"
            )

        return format(str(self), format_spec)

    def __add__(self, other):
        if not isinstance(other, Ingredient):
            return NotImplemented

        new_ingredients = list(self.ingredients)
        new_ingredients.append(other)

        return Recipe(
            self.title,
            new_ingredients,
            self.instructions
        )

    def __len__(self):
        return len(self._ingredients)

    def __iter__(self):
        return iter(self._ingredients)

    def __contains__(self, item):
        if isinstance(item, Ingredient):
            search_name = item.name
        elif isinstance(item, str):
            search_name = item
        else:
            return False

        search_name = search_name.strip().casefold()

        return any(
            ingredient.name.casefold() == search_name
            for ingredient in self._ingredients
        )


class SessionRecord(BaseEntity):
    """Хранит данные об одном сеансе работы пользователя."""

    def __init__(self, login, time_in, time_out=None):
        self.login = login
        self.time_in = time_in
        self.time_out = time_out
        self.validate()

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, value):
        if not isinstance(value, str):
            raise TypeError("Логин должен быть строкой.")

        value = value.strip()

        if not value:
            raise ValueError("Логин не может быть пустым.")

        self._login = value

    @property
    def time_in(self):
        return self._time_in

    @time_in.setter
    def time_in(self, value):
        if not isinstance(value, datetime):
            raise TypeError(
                "Время входа должно иметь тип datetime."
            )

        self._time_in = value

    @property
    def time_out(self):
        return self._time_out

    @time_out.setter
    def time_out(self, value):
        if value is not None and not isinstance(value, datetime):
            raise TypeError(
                "Время выхода должно иметь тип datetime или быть None."
            )

        self._time_out = value

    def validate(self):
        if not self.login:
            raise ValueError("Логин не может быть пустым.")

        if (
            self.time_out is not None
            and self.time_out < self.time_in
        ):
            raise ValueError(
                "Время выхода не может быть раньше времени входа."
            )

    def __str__(self):
        """Возвращает читаемое описание сеанса."""

        time_in_text = self.time_in.strftime(
            "%d.%m.%Y %H:%M:%S"
        )

        if self.time_out is None:
            time_out_text = "Сеанс активен"
        else:
            time_out_text = self.time_out.strftime(
                "%d.%m.%Y %H:%M:%S"
            )

        return (
            f"{self.login} | "
            f"{time_in_text} | "
            f"{time_out_text}"
        )

    def __repr__(self):
        """Возвращает техническое представление объекта."""

        return (
            f"SessionRecord(login={self.login!r}, "
            f"time_in={self.time_in!r}, "
            f"time_out={self.time_out!r})"
        )

    def __eq__(self, other):
        """Проверяет равенство двух записей о сеансах."""

        if not isinstance(other, SessionRecord):
            return NotImplemented

        return (
            self.login == other.login
            and self.time_in == other.time_in
            and self.time_out == other.time_out
        )

    def __lt__(self, other):
        """Сравнивает сеансы по времени входа."""

        if not isinstance(other, SessionRecord):
            return NotImplemented

        return self.time_in < other.time_in

    def __format__(self, format_spec):
        """Поддерживает специальные варианты отображения сеанса."""

        if format_spec == "login":
            return self.login

        if format_spec == "status":
            if self.time_out is None:
                return "Активен"

            return "Завершён"

        return format(str(self), format_spec)

    def __bool__(self):
        """Возвращает True, если сеанс ещё активен."""

        return self.time_out is None
