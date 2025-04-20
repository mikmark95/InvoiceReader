"""
Modulo GUI per l'applicazione InvoiceReader.

Questo modulo implementa l'interfaccia grafica dell'applicazione utilizzando PyQt6.
Fornisce una finestra con controlli per selezionare file PDF, specificare parametri
per la rinomina e processare i file.
"""

import os
import logging
import traceback
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QLabel, QFileDialog, QLineEdit, QMessageBox,
    QComboBox, QHBoxLayout, QListWidget, QListWidgetItem, QCheckBox, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from utils import estrai_info_da_pdf, genera_nome_file

class FatturaRenamer(QWidget):
    """
    Classe principale dell'interfaccia grafica per rinominare fatture PDF.

    Questa classe implementa una finestra con controlli per:
    - Selezionare file PDF
    - Specificare parametri per la rinomina (tipologia, stagione, anno, genere)
    - Processare i file per rinominarli in base alle informazioni estratte
    """

    def __init__(self):
        """
        Inizializza la finestra principale e configura l'interfaccia utente.
        """
        super().__init__()
        self.setWindowTitle("Rinomina Fatture PDF - Modalità Batch")
        self.resize(700, 520)

        self.setStyleSheet("""
            QWidget {
                background-color: #E6EAED;
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

        # Checkbox Generico
        self.generico_checkbox = QCheckBox("Generico")
        self.generico_checkbox.stateChanged.connect(self.toggle_tipo_combo)
        self.layout.addLayout(crea_riga("", self.generico_checkbox))

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
        self.layout.addLayout(crea_riga("", self.cartella_checkbox))

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
        """
        Apre un dialogo per selezionare uno o più file PDF.

        I file selezionati vengono aggiunti alla lista dei file da processare,
        evitando duplicati.
        """
        files, _ = QFileDialog.getOpenFileNames(self, "Seleziona file PDF", "", "PDF Files (*.pdf)")
        for path in files:
            if path not in self.file_paths:
                self.file_paths.append(path)
                self.file_list.addItem(QListWidgetItem(os.path.basename(path)))

    def rimuovi_file(self):
        """
        Rimuove il file selezionato dalla lista dei file da processare.
        """
        selected = self.file_list.currentRow()
        if selected >= 0:
            self.file_paths.pop(selected)
            self.file_list.takeItem(selected)

    def toggle_tipo_combo(self, state):
        """
        Abilita o disabilita i campi di input in base allo stato della checkbox 'Generico'.
        Quando la checkbox è selezionata, tutti i campi vengono disabilitati e visualizzati in grigio.

        Args:
            state (int): Stato della checkbox (Qt.Checked o Qt.Unchecked)
        """
        is_disabled = bool(state)

        # Disabilita tutti i campi di input
        self.tipo_combo.setEnabled(not is_disabled)
        self.stagione_combo.setEnabled(not is_disabled)
        self.anno_input.setEnabled(not is_disabled)
        self.genere_combo.setEnabled(not is_disabled)

        # Applica stile per evidenziare i campi disabilitati in grigio
        if is_disabled:
            self.tipo_combo.setStyleSheet("background-color: #e0e0e0; color: #707070;")
            self.stagione_combo.setStyleSheet("background-color: #e0e0e0; color: #707070;")
            self.anno_input.setStyleSheet("background-color: #e0e0e0; color: #707070;")
            self.genere_combo.setStyleSheet("background-color: #e0e0e0; color: #707070;")
        else:
            self.tipo_combo.setStyleSheet("")
            self.stagione_combo.setStyleSheet("")
            self.anno_input.setStyleSheet("")
            self.genere_combo.setStyleSheet("")

    def reset_tutto(self):
        """
        Reimposta tutti i campi dell'interfaccia ai valori predefiniti.

        Cancella la lista dei file, svuota i campi di input e reimposta
        i menu a tendina ai valori iniziali. Ripristina anche lo stile originale
        di tutti i campi.
        """
        self.file_paths.clear()
        self.file_list.clear()
        self.anno_input.clear()
        self.tipo_combo.setCurrentIndex(0)
        self.tipo_combo.setEnabled(True)
        self.stagione_combo.setCurrentIndex(0)
        self.stagione_combo.setEnabled(True)
        self.genere_combo.setCurrentIndex(0)
        self.genere_combo.setEnabled(True)
        self.anno_input.setEnabled(True)

        # Ripristina lo stile originale
        self.tipo_combo.setStyleSheet("")
        self.stagione_combo.setStyleSheet("")
        self.anno_input.setStyleSheet("")
        self.genere_combo.setStyleSheet("")

        self.generico_checkbox.setChecked(False)
        self.cartella_checkbox.setChecked(False)
        self.label_output.setText("")

    def processa_file(self):
        """
        Elabora tutti i file PDF selezionati per rinominarli.

        Estrae le informazioni da ciascun PDF, genera un nuovo nome file
        in base ai parametri specificati dall'utente, e rinomina il file.
        Se l'opzione è selezionata, sposta anche i file in cartelle denominate
        secondo il fornitore.

        Mostra messaggi di errore se non ci sono file selezionati o se mancano
        parametri obbligatori.

        Al termine, visualizza un riepilogo dei file elaborati con successo
        e di quelli non elaborati.
        """
        try:
            if not self.file_paths:
                QMessageBox.warning(self, "Errore", "Nessun file selezionato.")
                return

            anno = self.anno_input.text().strip()
            generico = self.generico_checkbox.isChecked()

            # Se la checkbox "Generico" non è selezionata, verifica che l'anno sia stato inserito
            if not anno and not generico:
                QMessageBox.warning(self, "Errore", "Inserisci l'anno prima di procedere.")
                return

            tipologia = "FATT" if self.tipo_combo.currentText() == "Fattura" else "NC"
            stagione = self.stagione_combo.currentText()
            genere = self.genere_combo.currentText()
            usa_cartelle = self.cartella_checkbox.isChecked()

            # Log dei parametri di elaborazione
            logging.info(f"Avvio elaborazione con parametri: tipologia={tipologia}, stagione={stagione}, "
                        f"anno={anno}, genere={genere}, generico={generico}, usa_cartelle={usa_cartelle}")
            logging.info(f"File da elaborare: {len(self.file_paths)}")

            success_count = 0
            fail_count = 0
            error_files = []

            for file_path in self.file_paths:
                try:
                    logging.info(f"Elaborazione file: {file_path}")

                    # Estrai informazioni dal PDF
                    denominazione, numero_fattura, data_fattura = estrai_info_da_pdf(file_path)

                    if all([denominazione, numero_fattura, data_fattura]):
                        logging.info(f"Informazioni estratte: denominazione={denominazione}, "
                                    f"numero_fattura={numero_fattura}, data_fattura={data_fattura}")

                        # Genera il nuovo nome file
                        nuovo_nome = genera_nome_file(
                            tipologia, numero_fattura, data_fattura, denominazione, stagione, anno, genere, generico
                        )
                        logging.info(f"Nuovo nome generato: {nuovo_nome}")

                        base_dir = os.path.dirname(file_path)
                        destinazione = base_dir

                        # Gestione delle cartelle
                        if usa_cartelle:
                            destinazione = os.path.join(base_dir, denominazione.replace(" ", "_"))
                            try:
                                os.makedirs(destinazione, exist_ok=True)
                                logging.info(f"Cartella creata/verificata: {destinazione}")
                            except Exception as e:
                                logging.error(f"Errore nella creazione della cartella {destinazione}: {str(e)}")
                                raise

                        nuovo_percorso = os.path.join(destinazione, nuovo_nome)

                        # Verifica se il file di destinazione esiste già
                        if os.path.exists(nuovo_percorso):
                            logging.warning(f"Il file di destinazione esiste già: {nuovo_percorso}")
                            # Aggiungi un suffisso al nome file per evitare sovrascritture
                            base, ext = os.path.splitext(nuovo_nome)
                            timestamp = datetime.now().strftime("%H%M%S")
                            nuovo_nome = f"{base}_{timestamp}{ext}"
                            nuovo_percorso = os.path.join(destinazione, nuovo_nome)
                            logging.info(f"Nuovo nome con timestamp: {nuovo_nome}")

                        # Rinomina il file
                        try:
                            os.rename(file_path, nuovo_percorso)
                            logging.info(f"File rinominato con successo: {nuovo_percorso}")
                            success_count += 1
                        except Exception as e:
                            logging.error(f"Errore durante la rinomina del file {file_path}: {str(e)}")
                            error_files.append(os.path.basename(file_path))
                            fail_count += 1
                    else:
                        logging.warning(f"Impossibile estrarre tutte le informazioni dal file: {file_path}")
                        error_files.append(os.path.basename(file_path))
                        fail_count += 1

                except Exception as e:
                    logging.error(f"Errore durante l'elaborazione del file {file_path}: {str(e)}")
                    logging.debug(traceback.format_exc())
                    error_files.append(os.path.basename(file_path))
                    fail_count += 1

            # Aggiorna l'interfaccia con il risultato
            result_text = f"✅ {success_count} file rinominati correttamente.\n❌ {fail_count} file non elaborati."

            # Se ci sono stati errori, aggiungi dettagli
            if error_files:
                error_files_text = "\n\nFile con errori:\n" + "\n".join(error_files[:5])
                if len(error_files) > 5:
                    error_files_text += f"\n... e altri {len(error_files) - 5} file"
                result_text += error_files_text

            self.label_output.setText(result_text)
            logging.info(f"Elaborazione completata: {success_count} successi, {fail_count} fallimenti")

        except Exception as e:
            # Gestione degli errori generali
            logging.error(f"Errore generale durante l'elaborazione dei file: {str(e)}")
            logging.debug(traceback.format_exc())
            QMessageBox.critical(self, "Errore", f"Si è verificato un errore durante l'elaborazione:\n\n{str(e)}")
            self.label_output.setText("❌ Errore durante l'elaborazione. Controlla il file di log per i dettagli.")
