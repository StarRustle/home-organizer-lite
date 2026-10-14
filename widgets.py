from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QPushButton,
    QLineEdit,
    QDoubleSpinBox,
    QComboBox,
    QTableWidget,
    QListWidget,
    QTextEdit,
    QTabWidget
)


class OrganizerButton(QPushButton):
    """Кнопка с изменением курсора при наведении."""

    def enterEvent(self, event):
        super().enterEvent(event)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.unsetCursor()


class UsernameInput(QLineEdit):
    """Поле логина, очищающее пробелы по краям."""

    def focusOutEvent(self, event):
        self.setText(self.text().strip())
        super().focusOutEvent(event)


class ProductNameInput(QLineEdit):
    """Поле названия продукта, нормализующее пробелы."""

    def focusOutEvent(self, event):
        self.setText(" ".join(self.text().split()))
        super().focusOutEvent(event)


class RecipeSearchInput(QLineEdit):
    """Поле поиска с очисткой по клавише Escape."""

    escapePressed = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.clear()
            self.escapePressed.emit()
            event.accept()
            return

        super().keyPressEvent(event)


class QuantitySpinBox(QDoubleSpinBox):
    """Поле количества без лишних нулей после запятой."""

    def textFromValue(self, value):
        return f"{value:.2f}".rstrip("0").rstrip(".")


class UnitComboBox(QComboBox):
    """Выбор единицы измерения без изменения колёсиком мыши."""

    def wheelEvent(self, event):
        event.accept()


class FridgeTableWidget(QTableWidget):
    """Таблица холодильника с удалением по клавише Delete."""

    deleteRequested = pyqtSignal()

    def keyPressEvent(self, event):
        if (
            event.key() == Qt.Key.Key_Delete
            and self.currentRow() >= 0
        ):
            self.deleteRequested.emit()
            event.accept()
            return

        super().keyPressEvent(event)


class RecipeListWidget(QListWidget):
    """Список рецептов с активацией выбранной записи по Enter."""

    recipeActivated = pyqtSignal(int)

    def keyPressEvent(self, event):
        if event.key() in (
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter
        ):
            row = self.currentRow()

            if row >= 0:
                self.recipeActivated.emit(row)
                event.accept()
                return

        super().keyPressEvent(event)


class RecipeDetailsTextEdit(QTextEdit):
    """Поле рецепта с дополнительной командой копирования."""

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        menu.addSeparator()

        copy_all_action = menu.addAction(
            "Копировать весь текст"
        )
        copy_all_action.triggered.connect(
            self._copy_all_text
        )

        menu.exec(event.globalPos())

    def _copy_all_text(self):
        self.selectAll()
        self.copy()


class OrganizerTabWidget(QTabWidget):
    """Вкладки с подсказками при отображении."""

    def showEvent(self, event):
        super().showEvent(event)

        for index in range(self.count()):
            self.setTabToolTip(
                index,
                f"Перейти на вкладку «{self.tabText(index)}»"
            )
