import sys
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QLineEdit, QPushButton, QLabel, QTabWidget,
    QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog,
    QTextEdit
)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator, QDoubleValidator


class UnitConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Конвертер единиц измерения")
        self.setGeometry(300, 200, 600, 500)

        self.units_data = {}
        self.history = []
        self.load_units()

        self.central_widget = QTabWidget()
        self.setCentralWidget(self.central_widget)

        self.converter_tab = QWidget()
        self.setup_converter_tab()
        self.central_widget.addTab(self.converter_tab, "Конвертер")

        self.editor_tab = QWidget()
        self.setup_editor_tab()
        self.central_widget.addTab(self.editor_tab, "Редактор")

        self.history_tab = QWidget()
        self.setup_history_tab()
        self.central_widget.addTab(self.history_tab, "История")

    def load_units(self):
        if os.path.exists("units.json"):
            with open("units.json", "r", encoding="utf-8") as f:
                self.units_data = json.load(f)
        else:
            QMessageBox.critical(self, "Ошибка", "Файл units.json не найден!")
            sys.exit(1)

    def save_units(self):
        with open("units.json", "w", encoding="utf-8") as f:
            json.dump(self.units_data, f, indent=2, ensure_ascii=False)
        QMessageBox.information(self, "Сохранено", "Изменения сохранены в units.json")

    def setup_converter_tab(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Категория:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(self.units_data.keys())
        self.category_combo.currentTextChanged.connect(self.update_units_lists)
        layout.addWidget(self.category_combo)

        units_layout = QHBoxLayout()
        units_layout.addWidget(QLabel("Из:"))
        self.from_combo = QComboBox()
        units_layout.addWidget(self.from_combo)

        units_layout.addWidget(QLabel("В:"))
        self.to_combo = QComboBox()
        units_layout.addWidget(self.to_combo)
        layout.addLayout(units_layout)

        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Значение:"))
        self.value_input = QLineEdit()
        double_validator = QDoubleValidator(0.0, 1e9, 6, self.value_input)
        double_validator.setNotation(QDoubleValidator.StandardNotation)
        self.value_input.setValidator(double_validator)
        input_layout.addWidget(self.value_input)

        self.convert_btn = QPushButton("Конвертировать")
        self.convert_btn.clicked.connect(self.convert)
        input_layout.addWidget(self.convert_btn)
        layout.addLayout(input_layout)

        layout.addWidget(QLabel("Результат:"))
        self.result_label = QLabel("")
        self.result_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.result_label)

        layout.addStretch()
        self.converter_tab.setLayout(layout)

        self.update_units_lists()

    def update_units_lists(self):
        category = self.category_combo.currentText()
        if category in self.units_data:
            units = list(self.units_data[category]["единицы"].keys())
            self.from_combo.clear()
            self.to_combo.clear()
            self.from_combo.addItems(units)
            self.to_combo.addItems(units)

    def convert(self):
        category = self.category_combo.currentText()
        from_unit = self.from_combo.currentText()
        to_unit = self.to_combo.currentText()

        if not from_unit or not to_unit:
            QMessageBox.warning(self, "Ошибка", "Выберите единицы измерения")
            return

        if from_unit == to_unit:
            QMessageBox.warning(self, "Ошибка", "Исходная и целевая единицы должны отличаться!")
            return

        try:
            value = float(self.value_input.text())
            if value <= 0:
                QMessageBox.warning(self, "Ошибка", "Значение должно быть положительным числом!")
                return
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректное число!")
            return

        base_unit = self.units_data[category]["базовая"]
        to_base_factor = self.units_data[category]["единицы"][from_unit]
        from_base_factor = self.units_data[category]["единицы"][to_unit]

        value_in_base = value / to_base_factor
        result = value_in_base * from_base_factor

        self.result_label.setText(f"{value} {from_unit} = {result:.6f} {to_unit}")

        # Сохранение в историю
        self.add_to_history(value, from_unit, result, to_unit)

    def setup_editor_tab(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Редактирование категории:"))
        self.edit_category_combo = QComboBox()
        self.edit_category_combo.addItems(self.units_data.keys())
        self.edit_category_combo.currentTextChanged.connect(self.load_units_table)
        layout.addWidget(self.edit_category_combo)

        self.units_table = QTableWidget()
        self.units_table.setColumnCount(2)
        self.units_table.setHorizontalHeaderLabels(["Единица", "Коэффициент к базовой"])
        self.units_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.units_table)

        btn_layout = QHBoxLayout()
        self.add_unit_btn = QPushButton("Добавить единицу")
        self.add_unit_btn.clicked.connect(self.add_unit)
        self.remove_unit_btn = QPushButton("Удалить выбранную")
        self.remove_unit_btn.clicked.connect(self.remove_unit)
        self.save_units_btn = QPushButton("Сохранить изменения")
        self.save_units_btn.clicked.connect(self.save_units)

        btn_layout.addWidget(self.add_unit_btn)
        btn_layout.addWidget(self.remove_unit_btn)
        btn_layout.addWidget(self.save_units_btn)
        layout.addLayout(btn_layout)

        self.editor_tab.setLayout(layout)
        self.load_units_table()

    def load_units_table(self):
        category = self.edit_category_combo.currentText()
        if category not in self.units_data:
            return

        units = self.units_data[category]["единицы"]
        self.units_table.setRowCount(len(units))
        for row, (unit_name, factor) in enumerate(units.items()):
            self.units_table.setItem(row, 0, QTableWidgetItem(unit_name))
            self.units_table.setItem(row, 1, QTableWidgetItem(str(factor)))

    def add_unit(self):
        category = self.edit_category_combo.currentText()
        name, ok = QInputDialog.getText(self, "Новая единица", "Введите название единицы:")
        if not ok or not name:
            return

        factor, ok = QInputDialog.getDouble(self, "Коэффициент", f"Коэффициент к базовой единице ({self.units_data[category]['базовая']}):",
                                            decimals=6)
        if not ok:
            return

        if name in self.units_data[category]["единицы"]:
            QMessageBox.warning(self, "Ошибка", "Такая единица уже существует!")
            return

        self.units_data[category]["единицы"][name] = factor
        self.load_units_table()
        self.update_units_lists()  # Обновляем списки на вкладке конвертера

    def remove_unit(self):
        category = self.edit_category_combo.currentText()
        current_row = self.units_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите единицу для удаления!")
            return

        unit_name = self.units_table.item(current_row, 0).text()
        if unit_name == self.units_data[category]["базовая"]:
            QMessageBox.warning(self, "Ошибка", "Нельзя удалить базовую единицу!")
            return

        reply = QMessageBox.question(self, "Подтверждение",
                                     f"Удалить единицу '{unit_name}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            del self.units_data[category]["единицы"][unit_name]
            self.load_units_table()
            self.update_units_lists()

    def setup_history_tab(self):
        layout = QVBoxLayout()
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        layout.addWidget(self.history_text)

        btn_layout = QHBoxLayout()
        clear_btn = QPushButton("Очистить историю")
        clear_btn.clicked.connect(self.clear_history)
        btn_layout.addWidget(clear_btn)
        layout.addLayout(btn_layout)

        self.history_tab.setLayout(layout)

    def add_to_history(self, from_val, from_unit, to_val, to_unit):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {from_val} {from_unit} = {to_val:.6f} {to_unit}"
        self.history.append(entry)
        self.history_text.append(entry)

    def clear_history(self):
        self.history.clear()
        self.history_text.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UnitConverterApp()
    window.show()
    sys.exit(app.exec_())