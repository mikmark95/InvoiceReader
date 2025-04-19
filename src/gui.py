from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QLabel, QFileDialog, QLineEdit, QMessageBox,
    QComboBox, QHBoxLayout
)
from utils import estrai_info_da_pdf, genera_nome_file
import os

class FatturaRenamer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rinomina Fatture PDF - Modalità Batch")
        self.resize(500, 300)

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
        self.button_select.clicked.connect(self.seleziona_pdf_multipli)
        self.layout.addWidget(self.button_select)

        self.label_output = QLabel("")
        self.layout.addWidget(self.label_output)

        self.setLayout(self.layout)

    def seleziona_pdf_multipli(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Seleziona file PDF", "", "PDF Files (*.pdf)")
        if not file_paths:
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
        for file_path in file_paths:
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