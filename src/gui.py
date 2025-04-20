from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QLabel, QFileDialog, QLineEdit, QMessageBox,
    QComboBox, QHBoxLayout, QListWidget, QListWidgetItem, QCheckBox, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from utils import estrai_info_da_pdf, genera_nome_file
import os

class FatturaRenamer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rinomina Fatture PDF - Modalità Batch")
        self.resize(700, 520)

        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border-radius: 5px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #005fa1;
            }
            QLineEdit, QComboBox, QListWidget {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
                color: black;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #0078d4;
                selection-color: white;
            }
            QLabel {
                font-weight: bold;
                color: black;
            }
            QCheckBox {
                margin-top: 5px;
                color: black;
            }
        """)

        self.file_paths = []
        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)

        self.layout.addWidget(QLabel("Seleziona uno o più file PDF e compila i campi:"))

        def crea_riga(label_txt, widget):
            riga = QHBoxLayout()
            label = QLabel(label_txt)
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            label.setFixedWidth(90)
            riga.addWidget(label)
            riga.addWidget(widget)
            return riga

        # Campi di input
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Fattura", "Nota di credito"])
        self.layout.addLayout(crea_riga("Tipologia:", self.tipo_combo))

        self.stagione_combo = QComboBox()
        self.stagione_combo.addItems(["PE", "AI", "CONTINUATIVO"])
        self.layout.addLayout(crea_riga("Stagione:", self.stagione_combo))

        self.anno_input = QLineEdit()
        self.anno_input.setPlaceholderText("Es. 2025")
        self.layout.addLayout(crea_riga("Anno:", self.anno_input))

        self.genere_combo = QComboBox()
        self.genere_combo.addItems(["UOMO", "DONNA"])
        self.layout.addLayout(crea_riga("Genere:", self.genere_combo))

        self.cartella_checkbox = QCheckBox("Sposta i file in cartelle con nome del fornitore")
        self.layout.addWidget(self.cartella_checkbox)

        # Pulsanti file management
        self.file_button_layout = QHBoxLayout()

        self.button_select = QPushButton("📂 Scegli PDF")
        self.button_select.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button_select.clicked.connect(self.apri_file_dialog)

        self.button_remove = QPushButton("🗑️ Rimuovi selezionato")
        self.button_remove.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button_remove.clicked.connect(self.rimuovi_file)

        self.button_reset = QPushButton("🔄 Reset")
        self.button_reset.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button_reset.clicked.connect(self.reset_tutto)

        self.file_button_layout.addWidget(self.button_select)
        self.file_button_layout.addWidget(self.button_remove)
        self.file_button_layout.addWidget(self.button_reset)
        self.layout.addLayout(self.file_button_layout)

        # Lista file
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.layout.addWidget(self.file_list)

        # Pulsante di processo
        self.button_process = QPushButton("🚀 Avvia Rinomina")
        self.button_process.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button_process.clicked.connect(self.processa_file)
        self.layout.addWidget(self.button_process)

        # Output
        self.label_output = QLabel("")
        self.label_output.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        self.cartella_checkbox.setChecked(False)
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
        usa_cartelle = self.cartella_checkbox.isChecked()

        success_count = 0
        fail_count = 0
        for file_path in self.file_paths:
            denominazione, numero_fattura, data_fattura = estrai_info_da_pdf(file_path)
            if all([denominazione, numero_fattura, data_fattura]):
                nuovo_nome = genera_nome_file(
                    tipologia, numero_fattura, data_fattura, denominazione, stagione, anno, genere
                )
                base_dir = os.path.dirname(file_path)
                destinazione = base_dir

                if usa_cartelle:
                    destinazione = os.path.join(base_dir, denominazione.replace(" ", "_"))
                    os.makedirs(destinazione, exist_ok=True)

                nuovo_percorso = os.path.join(destinazione, nuovo_nome)
                os.rename(file_path, nuovo_percorso)
                success_count += 1
            else:
                fail_count += 1

        self.label_output.setText(
            f"✅ {success_count} file rinominati correttamente.\n❌ {fail_count} file non elaborati."
        )