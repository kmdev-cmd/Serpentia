# CONEXÃO GERAL ENTRE TODOS OS CÓDIGOS + INTERFACE

import sys
import json
import datetime
import os
import traceback
import subprocess
import venv
import re
import random
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPlainTextEdit, QPushButton, QMessageBox, QHBoxLayout, QProgressBar, QLineEdit, QDialog, QTextEdit
)
from PySide6.QtCore import Qt, QThread, Signal, QObject, QProcess
from PySide6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor
from ai_review import ai_review 

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

VENV_DIR = os.path.join(os.path.abspath("."), "venv_app")

def setup_venv():
    """Cria a venv se ela não existir e retorna o caminho do executável python"""
    if not os.path.exists(VENV_DIR):
        print("Criando ambiente virtual (venv)... Isso pode levar alguns segundos.")
        venv.create(VENV_DIR, with_pip=True)
    
    if sys.platform == "win32":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")

PYTHON_EXE = setup_venv()

try:
    from progress_manager import update_streak, check_current_streak
except ImportError:
    def check_current_streak(): return 0
    def update_streak(): return 0, False

DATA_FILE = resource_path("daily_challenge.json")
CHALLENGE_FILE = resource_path("challenges.json")

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []
        def fmt(color, bold=False):
            f = QTextCharFormat()
            f.setForeground(QColor(color))
            if bold: f.setFontWeight(QFont.Bold)
            return f
        keywords = ["def", "return", "if", "else", "elif", "for", "while", "import", "from", "as", "class", "try", "except", "True", "False", "None"]
        for kw in keywords:
            self.rules.append((re.compile(rf"\b{kw}\b"), fmt("#c084fc", True)))
        self.rules.append((re.compile(r"#.*"), fmt("#94a3b8")))
        self.rules.append((re.compile(r"'.*?'|\".*?\""), fmt("#f472b6")))
        self.rules.append((re.compile(r"\b\d+\b"), fmt("#60a5fa")))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)

def load_all_challenges():
    try:
        with open(CHALLENGE_FILE, "r") as f: return json.load(f)
    except: return []

def load_daily_challenge():
    today = str(datetime.date.today())
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            if data["date"] == today: return data["challenge"]
    except: pass
    challenges = load_all_challenges()
    challenge = random.choice(challenges) if challenges else None
    if challenge:
        with open(DATA_FILE, "w") as f: json.dump({"date": today, "challenge": challenge}, f)
    return challenge

class Worker(QObject):
    finished = Signal(bool, str)
    def __init__(self, code, challenge):
        super().__init__()
        self.code = code
        self.challenge = challenge

    def run(self):
        try:

            feedback = ai_review(self.code, self.challenge)
            ok = "✅" in feedback 
            self.finished.emit(ok, feedback)
        except Exception as e:
            self.finished.emit(False, traceback.format_exc())

class FeedbackDialog(QDialog):
    def __init__(self, ok, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Review do Professor")
        self.setMinimumSize(450, 300)
        self.setStyleSheet("""
            QDialog { 
                background-color: #fff8f5; 
                border: 3px solid #f9a8d4; 
                border-radius: 15px; 
            }
            QLabel#status_icon { font-size: 50px; margin: 10px; }
            QTextEdit { 
                background-color: #fff1f8; 
                border: 2px solid #fbcfe8; 
                border-radius: 12px; 
                padding: 15px; 
                font-size: 14px; 
                color: #333;
            }
            QPushButton#close_btn { 
                background-color: #f9c6e0; 
                border-radius: 12px; 
                padding: 10px; 
                font-weight: bold; 
                border: 2px solid #f472b6; 
                min-width: 100px;
            }
        """)

        layout = QVBoxLayout()
        
        self.icon_lbl = QLabel("✅" if ok else "❌")
        self.icon_lbl.setObjectName("status_icon")
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setText(message)
        
        close_btn = QPushButton("Entendido!")
        close_btn.setObjectName("close_btn")
        close_btn.clicked.connect(self.accept)
        
        layout.addWidget(self.icon_lbl)
        layout.addWidget(self.text_area)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        self.setLayout(layout)


class DailyChallengeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.challenges = load_all_challenges()
        self.challenge = load_daily_challenge()
        
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.init_ui()

    def closeEvent(self, event):
        """Exclui arquivos temporários ao fechar a janela"""
        temp_files = ["temp_run.py"]
        for f in temp_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass
        event.accept()

    def init_ui(self):
        self.setWindowTitle("Serpentia - Daily Challenges")
        self.resize(850, 850)
        self.setStyleSheet("""
            QWidget { background-color: #fff8f5; color: #333; }
            QLabel#title { font-size: 20px; font-weight: bold; color: #f472b6; background-color: #ffe4f0; border: 3px solid #f9a8d4; border-radius: 12px; padding: 8px; }
            QLabel#desc { font-size: 14px; color: #7c3aed; background-color: #fdf0fb; border: 2px solid #fbcfe8; border-radius: 12px; padding: 8px; }
            QLabel#streak_label { font-size: 16px; font-weight: bold; color: #ff69b4; background-color: #fff0f5; border: 2px solid #fbcfe8; border-radius: 15px; padding: 6px 10px; }
            QPlainTextEdit#editor, QPlainTextEdit#console { background-color: #fff1f8; color: #333; border: 2px solid #f9a8d4; border-radius: 16px; padding: 12px; font-size: 13px; }
            QPlainTextEdit#console { font-family: 'Consolas', monospace; border-color: #7c3aed; }
            QLineEdit#console_input { background-color: #fff1f8; color: #7c3aed; border: 2px solid #f472b6; border-radius: 12px; padding: 8px; font-family: 'Consolas', monospace; }
            QPushButton { background-color: #f9c6e0; border-radius: 14px; padding: 10px; font-weight: bold; border: 2px solid #f472b6; }
            QPushButton:hover { background-color: #f472b6; color: white; }
            QProgressBar { border: 2px solid #f472b6; border-radius: 12px; text-align: center; background-color: #fff0f5; }
            QProgressBar::chunk { background-color: #fbcfe8; border-radius: 12px; }
        """)

        layout = QVBoxLayout()
        header_layout = QHBoxLayout()
        
        self.title_lbl = QLabel(self.challenge["title"] if self.challenge else "Sem desafio")
        self.title_lbl.setObjectName("title")
        
        self.streak_label = QLabel(f"🔥 {check_current_streak()}")
        self.streak_label.setObjectName("streak_label")
        
        header_layout.addStretch(); header_layout.addWidget(self.title_lbl); header_layout.addStretch(); header_layout.addWidget(self.streak_label)

        self.desc = QLabel(self.challenge["description"] if self.challenge else "")
        self.desc.setObjectName("desc")
        self.desc.setWordWrap(True)

        self.editor = QPlainTextEdit()
        self.editor.setObjectName("editor")
        self.highlighter = PythonHighlighter(self.editor.document())

        self.console = QPlainTextEdit()
        self.console.setObjectName("console")
        self.console.setReadOnly(True)
        
        self.console_input = QLineEdit()
        self.console_input.setPlaceholderText("Comando rápido...")
        self.console_input.returnPressed.connect(self.run_console_command)

        self.loading = QProgressBar()
        self.loading.setVisible(False)

        btn_layout = QHBoxLayout()
        self.run_btn = QPushButton("▶ Run Code")
        self.run_btn.clicked.connect(self.run_code)
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.clicked.connect(self.submit_code)
        self.next_btn = QPushButton("🔄 Próximo")
        self.next_btn.clicked.connect(self.next_challenge)
        btn_layout.addWidget(self.run_btn); btn_layout.addWidget(self.submit_btn); btn_layout.addWidget(self.next_btn)

        layout.addLayout(header_layout)
        layout.addWidget(self.desc)
        layout.addWidget(self.editor, stretch=4)
        layout.addWidget(QLabel("💻 Console (venv):"))
        layout.addWidget(self.console, stretch=2)
        layout.addWidget(self.console_input)
        layout.addWidget(self.loading)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.console.appendPlainText(data)

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode()
        self.console.appendPlainText(f"ERROR: {data}")

    def run_code(self):
        self.console.clear()
        code = self.editor.toPlainText()
        with open("temp_run.py", "w", encoding="utf-8") as f: 
            f.write(code)
        self.process.start(PYTHON_EXE, ["temp_run.py"])

    def run_console_command(self):
        cmd = self.console_input.text()
        if not cmd: return
        self.console.appendPlainText(f">>> {cmd}")
        self.process.start(PYTHON_EXE, ["-c", cmd])
        self.console_input.clear()

    def submit_code(self):
        """Envia para a IA o desafio que está ATUALMENTE na tela"""
        if not self.challenge:
            QMessageBox.warning(self, "Erro", "Não há desafio carregado.")
            return

        self.loading.setRange(0, 0)
        self.loading.setVisible(True)
        
        self.thread = QThread()
        self.worker = Worker(self.editor.toPlainText(), self.challenge)
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.on_submit_finished)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def on_submit_finished(self, ok, result):
            self.loading.setVisible(False)
            
            if ok:
                new_streak, updated = update_streak() 
                self.streak_label.setText(f"🔥 {new_streak}") 
            
            dialog = FeedbackDialog(ok, result, self)
            dialog.exec()
                
            self.thread.quit()
            self.thread.wait()

    def next_challenge(self):
        """Atualiza o obje to challenge para que a IA enxergue o novo desafio"""
        if not self.challenges: 
            return
            
        self.challenge = random.choice(self.challenges)
        
        self.editor.clear()
        self.console.clear()
        
        self.title_lbl.setText(self.challenge["title"])
        self.desc.setText(self.challenge["description"])
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DailyChallengeApp()
    window.show()
    sys.exit(app.exec())
