"""
Собственный класс для работы с ключами и значениями
"""
from collections.abc import MutableMapping


class CustomMap(MutableMapping):
    """Собственный класс маппинга на основе списка пар."""

    def __init__(self, pairs=None):
        self._items = []

        if pairs is not None:
            for key, value in pairs:
                self[key] = value

    def __getitem__(self, key):
        """Получает значение по ключу."""

        for existing_key, value in self._items:
            if existing_key == key:
                return value

        raise KeyError(key)

    def __setitem__(self, key, value):
        """Добавляет пару или изменяет существующее значение."""

        for index, (existing_key, _) in enumerate(self._items):
            if existing_key == key:
                self._items[index] = (key, value)
                return

        self._items.append((key, value))

    def __delitem__(self, key):
        """Удаляет пару по ключу."""

        for index, (existing_key, _) in enumerate(self._items):
            if existing_key == key:
                del self._items[index]
                return

        raise KeyError(key)

    def __iter__(self):
        """Позволяет перебирать ключи."""

        for key, _ in self._items:
            yield key

    def __len__(self):
        """Возвращает количество пар."""

        return len(self._items)

    def __repr__(self):
        return f"CustomMap({self._items!r})"

    def __str__(self):
        pairs = ", ".join(
            f"{key!r}: {value!r}"
            for key, value in self._items
        )
        return "{" + pairs + "}"