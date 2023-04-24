import sys
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QTextEdit, QLineEdit, QScrollArea, QWidget, QFrame, QMessageBox, QSizePolicy)
from PyQt5.QtCore import Qt

class QueryBindingApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Query Binding")
        self.setFixedSize(700, 500)

        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout)

        self.query_label = QLabel("Log Text:")
        left_layout.addWidget(self.query_label)

        self.query_text = QTextEdit()
        left_layout.addWidget(self.query_text)

        self.params_label = QLabel("Parameters (0):")
        left_layout.addWidget(self.params_label)
        self.params_label.hide()

        self.result_label = QLabel("Result:")
        left_layout.addWidget(self.result_label)

        self.result_text = QTextEdit()
        left_layout.addWidget(self.result_text)

        button_layout = QHBoxLayout()
        left_layout.addLayout(button_layout)

        self.bind_button = QPushButton("Bind")
        button_layout.addWidget(self.bind_button)
        self.bind_button.clicked.connect(lambda: self.submit())

        self.clear_button = QPushButton("Clear")
        button_layout.addWidget(self.clear_button)
        self.clear_button.clicked.connect(self.clear)

        self.update_button = QPushButton("Update Parameters")
        button_layout.addWidget(self.update_button)
        self.update_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.update_button.clicked.connect(self.update_param_entries)
        self.update_button.hide()

        self.clipboard_button = QPushButton("Copy to Clipboard")
        button_layout.addWidget(self.clipboard_button)
        self.clipboard_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.clipboard_button.clicked.connect(self.copy_to_clipboard)
        self.clipboard_button.hide()

        self.scroll_area = QScrollArea()
        main_layout.addWidget(self.scroll_area)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.entries_frame = QFrame()
        self.scroll_area.setWidget(self.entries_frame)

        self.entries_layout = QVBoxLayout()
        self.entries_frame.setLayout(self.entries_layout)

        self.param_entries = [QLineEdit() for _ in range(100)]
        self.param_name_labels = [QLabel(f"Var {i + 1}:") for i in range(100)]

        for i in range(100):
            entry_label_layout = QHBoxLayout()
            self.entries_layout.addLayout(entry_label_layout)

            entry_label_layout.addWidget(self.param_name_labels[i])
            entry_label_layout.addWidget(self.param_entries[i])

            self.param_entries[i].hide()
            self.param_name_labels[i].hide()

            self.entries_layout.addStretch(1)  # 이 줄을 추가하여 파라미터 영역이 더 넓어지도록 합니다.

        main_layout.setStretch(0, 7)  # 왼쪽 레이아웃의 비율을 줄입니다.
        main_layout.setStretch(1, 3)  # 오른쪽 레이아웃의 비율을 늘립니다.
    def bind_query(self, query_template, params):
        query_template = re.sub(r'\?', r"'{}'", query_template)
        return query_template.format(*params)

    def extract_query_params(self, log_text):
        param_pattern = r'Parameters: \[(.*?)\]'
        param_match = re.search(param_pattern, log_text)

        params = param_match.group(1).split(',') if param_match else []
        return params

    def extract_binding_vars(self, query_template):
        matches = re.findall(r"(\w+)\s*=\s*\?", query_template)
        question_marks = query_template.count("?")

        while len(matches) < question_marks:
            matches.append("temp")

        return matches

    def submit(self):
        log_text = self.query_text.toPlainText().strip()
        query_template = log_text.split("DEBUG")[0].strip()

        params = self.extract_query_params(log_text)
        binding_vars = self.extract_binding_vars(query_template)

        for i, (param, binding_var) in enumerate(zip(params, binding_vars)):
            self.param_name_labels[i].setText(f"{binding_var}:")
            self.param_entries[i].setText(param.strip())

            self.params_label.setText(f"Parameters ({len(params)}): {', '.join(params)}")
            self.params_label.hide()

            result = self.bind_query(query_template, params)
            self.result_text.clear()
            self.result_text.insertPlainText(result)

            self.update_button.show()
            self.clipboard_button.show()
            self.update_params()


    def clear(self):
        self.query_text.clear()
        self.result_text.clear()
        self.params_label.setText("Parameters (0):")
        self.params_label.hide()
        for entry, var_name_label in zip(self.param_entries, self.param_name_labels):
            entry.hide()
            var_name_label.hide()

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.clear()
        clipboard.setText(self.result_text.toPlainText().strip())
        QMessageBox.information(self, "복사 완료", "클립보드로 복사되었습니다.")

    def update_params(self):
        log_text = self.query_text.toPlainText().strip()
        query_template = log_text.split("DEBUG")[0].strip()
        binding_vars = self.extract_binding_vars(log_text)

        params = []
        for i, binding_var in enumerate(binding_vars):
            self.param_name_labels[i].setText(f"{binding_var}:")
            self.param_entries[i].show()
            self.param_name_labels[i].show()
            params.append(self.param_entries[i].text().strip())

        for i in range(len(binding_vars), 100):
            self.param_entries[i].hide()
            self.param_name_labels[i].hide()

        for i, (param, binding_var) in enumerate(zip(params, binding_vars)):
            self.param_name_labels[i].setText(f"{binding_var}:")
            self.param_entries[i].setText(param.strip())

        self.params_label.setText(f"Parameters ({len(params)}): {', '.join(params)}")

        result = self.bind_query(query_template, params)
        self.result_text.clear()
        self.result_text.insertPlainText(result)

    def update_param_entries(self):
        self.update_params()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    query_binding_app = QueryBindingApp()
    query_binding_app.show()
    sys.exit(app.exec_())

