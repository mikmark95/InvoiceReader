
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QLabel, QFileDialog, QLineEdit, QMessageBox
)
from utils import estrai_info_da_pdf, genera_nome_file
import os

class FatturaRenamer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rinomina Fatture PDF - Modalità Batch")
        self.resize(500, 250)

        self.layout = QVBoxLayout()

        self.label_info = QLabel("Seleziona uno o più file PDF e inserisci la stagione:")
        self.layout.addWidget(self.label_info)

        self.stagione_input = QLineEdit()
        self.stagione_input.setPlaceholderText("Esempio: PE 25")
        self.layout.addWidget(self.stagione_input)

        self.button_select = QPushButton("Scegli PDF")
        self.button_select.clicked.connect(self.seleziona_pdf_multipli)
        self.layout.addWidget(self.button_select)

        self.label_output = QLabel("")
        self.layout.addWidget(self.label_output)

        self.setLayout(self.layout)

    def seleziona_pdf_multipli(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Seleziona file PDF", "", "PDF Files (*.pdf)")
        if not file_paths:
            return

        stagione = self.stagione_input.text().strip()
        if not stagione:
            QMessageBox.warning(self, "Errore", "Inserisci la stagione prima di procedere.")
            return

        success_count = 0
        fail_count = 0
        for file_path in file_paths:
            denominazione, numero_fattura, data_fattura = estrai_info_da_pdf(file_path)
            if all([denominazione, numero_fattura, data_fattura]):
                nuovo_nome = genera_nome_file(numero_fattura, data_fattura, denominazione, stagione)
                nuovo_percorso = os.path.join(os.path.dirname(file_path), nuovo_nome)
                os.rename(file_path, nuovo_percorso)
                success_count += 1
            else:
                fail_count += 1

        self.label_output.setText(
            f"✅ {success_count} file rinominati correttamente.\n❌ {fail_count} file non elaborati."
        )