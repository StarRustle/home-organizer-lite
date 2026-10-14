
import json
from pathlib import Path

from custom_map import CustomMap
from models import Ingredient, Recipe


class RecipeLoader:
    """Загружает рецепты из JSON и создаёт объекты приложения."""

    def __init__(self, file_path=None):
        if file_path is None:
            self._file_path = (
                Path(__file__).resolve().parent
                / "data"
                / "recipes.json"
            )
        else:
            self._file_path = Path(file_path)

    @staticmethod
    def _check_fields(record, required_fields, context):
        """Проверяет наличие обязательных полей."""

        for field in required_fields:
            if field not in record:
                raise ValueError(
                    f"{context}: отсутствует поле '{field}'."
                )

    def load_recipes(self):
        """Читает JSON и возвращает список объектов Recipe."""

        try:
            with self._file_path.open(
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(
                    file,
                    object_pairs_hook=CustomMap
                )

        except FileNotFoundError as error:
            raise FileNotFoundError(
                f"Файл рецептов не найден: {self._file_path}"
            ) from error

        except json.JSONDecodeError as error:
            raise ValueError(
                f"Ошибка JSON в строке {error.lineno}, "
                f"столбце {error.colno}: {error.msg}"
            ) from error

        if not isinstance(data, list):
            raise ValueError(
                "Корневой элемент JSON должен быть списком рецептов."
            )

        recipes = []

        for recipe_number, recipe_data in enumerate(data, start=1):
            context = f"Рецепт №{recipe_number}"

            if not isinstance(recipe_data, CustomMap):
                raise ValueError(
                    f"{context}: данные рецепта должны быть объектом JSON."
                )

            self._check_fields(
                recipe_data,
                ("title", "ingredients", "instructions"),
                context
            )

            raw_ingredients = recipe_data["ingredients"]

            if not isinstance(raw_ingredients, list):
                raise ValueError(
                    f"{context}: поле ingredients должно быть списком."
                )

            ingredients = []

            for ingredient_number, ingredient_data in enumerate(
                raw_ingredients,
                start=1
            ):
                ingredient_context = (
                    f"{context}, ингредиент №{ingredient_number}"
                )

                if not isinstance(ingredient_data, CustomMap):
                    raise ValueError(
                        f"{ingredient_context}: ожидается объект JSON."
                    )

                self._check_fields(
                    ingredient_data,
                    ("name", "quantity", "unit"),
                    ingredient_context
                )

                try:
                    ingredient = Ingredient(
                        ingredient_data["name"],
                        ingredient_data["quantity"],
                        ingredient_data["unit"]
                    )

                except (TypeError, ValueError) as error:
                    raise ValueError(
                        f"{ingredient_context}: {error}"
                    ) from error

                ingredients.append(ingredient)

            try:
                recipe = Recipe(
                    recipe_data["title"],
                    ingredients,
                    recipe_data["instructions"]
                )

            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"{context}: {error}"
                ) from error

            recipes.append(recipe)

        return recipes