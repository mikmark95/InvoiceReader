from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QLabel, QFileDialog, QLineEdit, QMessageBox,
    QComboBox, QHBoxLayout, QListWidget, QListWidgetItem
)
from utils import estrai_info_da_pdf, genera_nome_file
import os

class FatturaRenamer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rinomina Fatture PDF - Modalità Batch")
        self.resize(600, 450)

        self.file_paths = []

        self.layout = QVBoxLayout()

        self.layout.addWidget(QLabel("Seleziona uno o più file PDF e compila i campi:")
)

        self.tipo_layout = QHBoxLayout()
        self.tipo_layout.addWidget(QLabel("Tipologia:"))
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Fattura", "Nota di credito"])
        self.tipo_layout.addWidget(self.tipo_combo)
        self.layout.addLayout(self.tipo_layout)

        self.stagione_layout = QHBoxLayout()
        self.stagione_layout.addWidget(QLabel("Stagione:"))
        self.stagione_combo = QComboBox()
        self.stagione_combo.addItems(["PE", "AI", "CONTINUATIVO"])
        self.stagione_layout.addWidget(self.stagione_combo)
        self.layout.addLayout(self.stagione_layout)

        self.anno_layout = QHBoxLayout()
        self.anno_layout.addWidget(QLabel("Anno:"))
        self.anno_input = QLineEdit()
        self.anno_input.setPlaceholderText("Es. 2025")
        self.anno_layout.addWidget(self.anno_input)
        self.layout.addLayout(self.anno_layout)

        self.genere_layout = QHBoxLayout()
        self.genere_layout.addWidget(QLabel("Genere:"))
        self.genere_combo = QComboBox()
        self.genere_combo.addItems(["UOMO", "DONNA"])
        self.genere_layout.addWidget(self.genere_combo)
        self.layout.addLayout(self.genere_layout)

        self.button_select = QPushButton("Scegli PDF")
        self.button_select.clicked.connect(self.apri_file_dialog)
        self.layout.addWidget(self.button_select)

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.layout.addWidget(self.file_list)

        self.button_remove = QPushButton("Rimuovi selezionato")
        self.button_remove.clicked.connect(self.rimuovi_file)
        self.layout.addWidget(self.button_remove)

        self.button_reset = QPushButton("Reset campi e lista")
        self.button_reset.clicked.connect(self.reset_tutto)
        self.layout.addWidget(self.button_reset)

        self.button_process = QPushButton("Avvia Rinomina")
        self.button_process.clicked.connect(self.processa_file)
        self.layout.addWidget(self.button_process)

        self.label_output = QLabel("")
        self.layout.addWidget(self.label_output)

        self.setLayout(self.layout)

    def apri_file_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Seleziona file PDF", "", "PDF Files (*.pdf)")
        for path in files:
            if path not in self.file_paths:
                self.file_paths.append(path)
                self.file_list.addItem(QListWidgetItem(os.path.basename(path)))

    def rimuovi_file(self):
        selected = self.file_list.currentRow()
        if selected >= 0:
            self.file_paths.pop(selected)
            self.file_list.takeItem(selected)

    def reset_tutto(self):
        self.file_paths.clear()
        self.file_list.clear()
        self.anno_input.clear()
        self.tipo_combo.setCurrentIndex(0)
        self.stagione_combo.setCurrentIndex(0)
        self.genere_combo.setCurrentIndex(0)
        self.label_output.setText("")

    def processa_file(self):
        if not self.file_paths:
            QMessageBox.warning(self, "Errore", "Nessun file selezionato.")
            return

        anno = self.anno_input.text().strip()
        if not anno:
            QMessageBox.warning(self, "Errore", "Inserisci l'anno prima di procedere.")
            return

        tipologia = "FATT" if self.tipo_combo.currentText() == "Fattura" else "NC"
        stagione = self.stagione_combo.currentText()
        genere = self.genere_combo.currentText()

        success_count = 0
        fail_count = 0
        for file_path in self.file_paths:
            denominazione, numero_fattura, data_fattura = estrai_info_da_pdf(file_path)
            if all([denominazione, numero_fattura, data_fattura]):
                nuovo_nome = genera_nome_file(
                    tipologia, numero_fattura, data_fattura, denominazione, stagione, anno, genere
                )
                nuovo_percorso = os.path.join(os.path.dirname(file_path), nuovo_nome)
                os.rename(file_path, nuovo_percorso)
                success_count += 1
            else:
                fail_count += 1

        self.label_output.setText(
            f"✅ {success_count} file rinominati correttamente.\n❌ {fail_count} file non elaborati."
        )
