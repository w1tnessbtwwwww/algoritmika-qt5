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
from PyQt5.QtGui import QRegExpValidator, QDoubleValidator, QFont, QPalette, QColor


class UnitConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Конвертер единиц измерения")
        self.setGeometry(300, 200, 650, 550)
        
        self.apply_styles()
        
        self.units_data = {}
        self.history = []
        self.load_units()

        self.central_widget = QTabWidget()
        self.setCentralWidget(self.central_widget)

        self.converter_tab = QWidget()
        self.setup_converter_tab()
        self.central_widget.addTab(self.converter_tab, "📐 Конвертер")

        self.editor_tab = QWidget()
        self.setup_editor_tab()
        self.central_widget.addTab(self.editor_tab, "✏️ Редактор")

        self.history_tab = QWidget()
        self.setup_history_tab()
        self.central_widget.addTab(self.history_tab, "📜 История")

    def apply_styles(self):
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            QTabWidget::pane {
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                background-color: white;
            }
            
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
            }
            
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #c0c0c0;
            }
            
            QLabel {
                color: #333333;
                font-weight: bold;
                margin-top: 5px;
            }
            
            QComboBox {
                padding: 8px;
                border: 2px solid #d0d0d0;
                border-radius: 6px;
                background-color: white;
                font-size: 12px;
                min-width: 150px;
            }
            
            QComboBox:hover {
                border-color: #4CAF50;
            }
            
            QComboBox:focus {
                border-color: #2196F3;
            }
            
            QLineEdit {
                padding: 8px;
                border: 2px solid #d0d0d0;
                border-radius: 6px;
                background-color: white;
                font-size: 12px;
            }
            
            QLineEdit:focus {
                border-color: #2196F3;
            }
            
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
            
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            
            QPushButton:disabled {
                background-color: #cccccc;
            }
            
            QTableWidget {
                border: 2px solid #d0d0d0;
                border-radius: 6px;
                background-color: white;
            }
            
            QTableWidget::item {
                padding: 5px;
            }
            
            QTableWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            
            QTextEdit {
                border: 2px solid #d0d0d0;
                border-radius: 6px;
                background-color: white;
                font-family: monospace;
                font-size: 12px;
            }
            
            QScrollBar:vertical {
                border: none;
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
        """)
        
        # Настройка шрифтов
        font = QFont("Segoe UI", 10)
        QApplication.setFont(font)

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
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("🔄 Конвертер единиц измерения")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; margin-bottom: 10px;")
        layout.addWidget(title_label)

        layout.addWidget(QLabel("📁 Категория:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(self.units_data.keys())
        self.category_combo.currentTextChanged.connect(self.update_units_lists)
        layout.addWidget(self.category_combo)

        units_layout = QHBoxLayout()
        units_layout.setSpacing(20)
        units_layout.addWidget(QLabel("📤 Из:"))
        self.from_combo = QComboBox()
        units_layout.addWidget(self.from_combo)

        units_layout.addWidget(QLabel("📥 В:"))
        self.to_combo = QComboBox()
        units_layout.addWidget(self.to_combo)
        layout.addLayout(units_layout)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        input_layout.addWidget(QLabel("🔢 Значение:"))
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Введите положительное число...")
        double_validator = QDoubleValidator(0.0, 1e9, 6, self.value_input)
        double_validator.setNotation(QDoubleValidator.StandardNotation)
        self.value_input.setValidator(double_validator)
        input_layout.addWidget(self.value_input)

        self.convert_btn = QPushButton("🔄 Конвертировать")
        self.convert_btn.setMinimumWidth(150)
        self.convert_btn.clicked.connect(self.convert)
        input_layout.addWidget(self.convert_btn)
        layout.addLayout(input_layout)

        # Результат в красивой рамке
        result_frame = QWidget()
        result_frame.setStyleSheet("""
            QWidget {
                background-color: #f0f8ff;
                border-radius: 8px;
                border: 2px solid #4CAF50;
                padding: 10px;
            }
        """)
        result_layout = QVBoxLayout(result_frame)
        result_layout.addWidget(QLabel("✨ Результат конвертации:"))
        self.result_label = QLabel("")
        self.result_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #2e7d32; padding: 5px;")
        result_layout.addWidget(self.result_label)
        layout.addWidget(result_frame)

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

        self.result_label.setText(f"{value:.4f} {from_unit} = {result:.6f} {to_unit}")

        self.convert_btn.setStyleSheet("background-color: #45a049; transform: scale(0.95);")
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, lambda: self.convert_btn.setStyleSheet(""))

        self.add_to_history(value, from_unit, result, to_unit)

    def setup_editor_tab(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("✏️ Редактор единиц измерения")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2196F3; margin-bottom: 10px;")
        layout.addWidget(title_label)

        layout.addWidget(QLabel("📁 Выберите категорию:"))
        self.edit_category_combo = QComboBox()
        self.edit_category_combo.addItems(self.units_data.keys())
        self.edit_category_combo.currentTextChanged.connect(self.load_units_table)
        layout.addWidget(self.edit_category_combo)

        self.units_table = QTableWidget()
        self.units_table.setColumnCount(2)
        self.units_table.setHorizontalHeaderLabels(["📏 Единица", "📊 Коэффициент к базовой"])
        self.units_table.horizontalHeader().setStretchLastSection(True)
        self.units_table.setAlternatingRowColors(True)
        layout.addWidget(self.units_table)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.add_unit_btn = QPushButton("➕ Добавить единицу")
        self.add_unit_btn.setStyleSheet("background-color: #2196F3;")
        self.add_unit_btn.clicked.connect(self.add_unit)
        
        self.remove_unit_btn = QPushButton("➖ Удалить выбранную")
        self.remove_unit_btn.setStyleSheet("background-color: #f44336;")
        self.remove_unit_btn.clicked.connect(self.remove_unit)
        
        self.save_units_btn = QPushButton("💾 Сохранить изменения")
        self.save_units_btn.setStyleSheet("background-color: #FF9800;")
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
            
            if unit_name == self.units_data[category]["базовая"]:
                for col in range(2):
                    item = self.units_table.item(row, col)
                    item.setBackground(QColor(200, 230, 200))

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
        self.update_units_lists()
        
        QMessageBox.information(self, "Успех", f"Единица '{name}' добавлена!")

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
            QMessageBox.information(self, "Успех", f"Единица '{unit_name}' удалена!")

    def setup_history_tab(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("📜 История конвертаций")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #9C27B0; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setPlaceholderText("Здесь будет отображаться история ваших конвертаций...")
        layout.addWidget(self.history_text)

        btn_layout = QHBoxLayout()
        clear_btn = QPushButton("🗑️ Очистить историю")
        clear_btn.setStyleSheet("background-color: #f44336;")
        clear_btn.clicked.connect(self.clear_history)
        btn_layout.addWidget(clear_btn)
        layout.addLayout(btn_layout)

        self.history_tab.setLayout(layout)

    def add_to_history(self, from_val, from_unit, to_val, to_unit):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] 📊 {from_val:.4f} {from_unit} → {to_val:.6f} {to_unit}"
        self.history.append(entry)
        
        colored_entry = f"<font color='#333333'>{timestamp}</font> → <font color='#4CAF50'><b>{from_val:.4f} {from_unit}</b></font> = <font color='#2196F3'><b>{to_val:.6f} {to_unit}</b></font><br>"
        self.history_text.insertHtml(colored_entry)

    def clear_history(self):
        self.history.clear()
        self.history_text.clear()
        QMessageBox.information(self, "Готово", "История очищена!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UnitConverterApp()
    window.show()
    sys.exit(app.exec_())