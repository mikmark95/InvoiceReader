"""
Modulo GUI per l'applicazione InvoiceReader.

Questo modulo implementa l'interfaccia grafica dell'applicazione utilizzando PyQt6.
Fornisce una finestra con controlli per selezionare file PDF, specificare parametri
per la rinomina e processare i file.
"""

import os
import logging
import re
import traceback
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QLabel, QFileDialog, QLineEdit, QMessageBox,
    QComboBox, QHBoxLayout, QListWidget, QListWidgetItem, QCheckBox, QSizePolicy, QSpacerItem,
    QGraphicsView, QGraphicsScene, QFrame, QMenuBar, QMenu, QMainWindow
)
from PyQt6.QtCore import Qt, QRectF, QUrl
from PyQt6.QtGui import QFont, QImage, QPixmap, QDesktopServices
import fitz  # PyMuPDF
from utils import estrai_info_da_pdf, genera_nome_file
from pattern_db import PatternDatabase

class FatturaRenamer(QMainWindow):
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
        self.resize(1000, 600)  # Aumentato per accomodare il preview

        # Crea il widget centrale
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Inizializza il database dei pattern
        self.pattern_db = PatternDatabase()
        self.current_extraction_text = None  # Per memorizzare il testo estratto dall'ultimo PDF
        self.current_pdf_path = None  # Per memorizzare il percorso del PDF attualmente selezionato
        self.zoom_factor = 1.0  # Fattore di zoom iniziale
        self.current_page = 0  # Pagina corrente del PDF
        self.total_pages = 0  # Numero totale di pagine nel PDF

        # Crea il menu bar
        self.create_menu_bar()

        # Inizializza l'interfaccia utente
        self.setup_ui()

    def create_menu_bar(self):
        """
        Crea la barra dei menu con le opzioni Info e Guida.
        """
        menubar = self.menuBar()

        # Menu Info
        info_menu = menubar.addMenu("Info")
        about_action = info_menu.addAction("Informazioni")
        about_action.triggered.connect(self.show_about_dialog)

        # Menu Guida
        help_menu = menubar.addMenu("Guida")
        readme_action = help_menu.addAction("Apri README")
        readme_action.triggered.connect(self.open_readme)

    def show_about_dialog(self):
        """
        Mostra un dialog con informazioni sull'autore e la versione dell'applicazione.
        """
        QMessageBox.about(
            self,
            "Informazioni su InvoiceReader",
            "<h3>InvoiceReader - Rinomina Fatture PDF</h3>"
            "<p><b>Versione:</b> 1.2.0 (Maggio 2025)</p>"
            "<p><b>Autore:</b> Michele Marchetti (@mikmark95)</p>"
            "<p><b>Copyright:</b> © 2025 Marchetti Michele. Tutti i diritti riservati.</p>"
            "<p>Applicazione per rinominare automaticamente file PDF di fatture e note di credito.</p>"
        )

    def open_readme(self):
        """
        Apre il file README.md nel browser predefinito.
        """
        readme_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "README.md")
        if os.path.exists(readme_path):
            # Usa un URL con schema 'https' per forzare l'apertura nel browser predefinito
            url = QUrl.fromLocalFile(readme_path)
            url.setScheme("https")
            QDesktopServices.openUrl(url)
        else:
            QMessageBox.warning(self, "File non trovato", "Il file README.md non è stato trovato.")

    def setup_ui(self):
        """
        Inizializza tutti i componenti dell'interfaccia utente.
        """
        self.setStyleSheet("""
            QWidget {
                background-color: #9DB4C4;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QPushButton {
                background-color: #61707B;
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
            QGraphicsView {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)

        self.file_paths = []

        # Layout principale orizzontale per dividere form e preview
        self.main_layout = QHBoxLayout()

        # Layout per il form a sinistra
        self.form_layout = QVBoxLayout()
        self.form_layout.setSpacing(10)

        self.form_layout.addWidget(QLabel("Seleziona uno o più file PDF e compila i campi:"))

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
        self.form_layout.addLayout(crea_riga("Tipologia:", self.tipo_combo))

        # Checkbox Generico
        self.generico_checkbox = QCheckBox("Generico")
        self.generico_checkbox.stateChanged.connect(self.toggle_tipo_combo)
        self.form_layout.addLayout(crea_riga("", self.generico_checkbox))

        self.stagione_combo = QComboBox()
        self.stagione_combo.addItems(["PE", "AI", "CONTINUATIVO"])
        self.form_layout.addLayout(crea_riga("Stagione:", self.stagione_combo))

        self.anno_input = QLineEdit()
        self.anno_input.setPlaceholderText("Es. 2025")
        self.form_layout.addLayout(crea_riga("Anno:", self.anno_input))

        self.genere_combo = QComboBox()
        self.genere_combo.addItems(["UOMO", "DONNA"])
        self.form_layout.addLayout(crea_riga("Genere:", self.genere_combo))

        self.cartella_checkbox = QCheckBox("Sposta i file in cartelle con nome del fornitore")
        self.form_layout.addLayout(crea_riga("", self.cartella_checkbox))

        # Checkbox per l'apprendimento automatico
        self.ml_checkbox = QCheckBox("Abilita apprendimento automatico")
        self.ml_checkbox.setChecked(False)  # Non abilitato di default
        self.ml_checkbox.setToolTip("Quando abilitato, il sistema impara dai documenti elaborati creando nuovi pattern di estrazione per migliorare il riconoscimento futuro")
        self.form_layout.addLayout(crea_riga("", self.ml_checkbox))

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

        self.button_patterns = QPushButton("🔍 Gestisci Pattern")
        self.button_patterns.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button_patterns.clicked.connect(self.apri_gestore_pattern)

        self.file_button_layout.addWidget(self.button_select)
        self.file_button_layout.addWidget(self.button_remove)
        self.file_button_layout.addWidget(self.button_reset)
        self.file_button_layout.addWidget(self.button_patterns)
        self.form_layout.addLayout(self.file_button_layout)

        # Lista file
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.file_list.currentRowChanged.connect(self.aggiorna_anteprima_pdf)  # Connetti il segnale di cambio selezione
        self.form_layout.addWidget(self.file_list)

        # Pulsante di processo
        self.button_process = QPushButton("🚀 Avvia Rinomina")
        self.button_process.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button_process.clicked.connect(self.processa_file)
        self.form_layout.addWidget(self.button_process)

        # Output
        self.label_output = QLabel("")
        self.label_output.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.form_layout.addWidget(self.label_output)

        # Aggiungi il form layout al layout principale
        self.main_layout.addLayout(self.form_layout, 1)  # Proporzione 1

        # Crea il widget per l'anteprima PDF
        self.pdf_preview_widget = QWidget()
        self.pdf_preview_container = QVBoxLayout(self.pdf_preview_widget)

        # Titolo per l'anteprima
        self.preview_title = QLabel("Anteprima PDF")
        self.preview_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pdf_preview_container.addWidget(self.preview_title)

        # Crea la vista grafica per l'anteprima PDF
        self.pdf_scene = QGraphicsScene()
        self.pdf_view = QGraphicsView(self.pdf_scene)
        self.pdf_view.setFrameShape(QFrame.Shape.StyledPanel)
        self.pdf_view.setMinimumWidth(400)
        self.pdf_preview_container.addWidget(self.pdf_view)

        # Aggiungi controlli di navigazione pagine
        page_nav_layout = QHBoxLayout()
        self.prev_page_button = QPushButton("◀️ Pagina precedente")
        self.next_page_button = QPushButton("Pagina successiva ▶️")
        self.page_label = QLabel("Pagina 1 di 1")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.prev_page_button.clicked.connect(self.prev_page)
        self.next_page_button.clicked.connect(self.next_page)

        page_nav_layout.addWidget(self.prev_page_button)
        page_nav_layout.addWidget(self.page_label)
        page_nav_layout.addWidget(self.next_page_button)

        # Nascondi i controlli di navigazione inizialmente
        self.prev_page_button.setVisible(False)
        self.next_page_button.setVisible(False)
        self.page_label.setVisible(False)

        self.pdf_preview_container.addLayout(page_nav_layout)

        # Aggiungi controlli di zoom
        zoom_layout = QHBoxLayout()
        self.zoom_in_button = QPushButton("🔍+")
        self.zoom_out_button = QPushButton("🔍-")
        self.zoom_reset_button = QPushButton("Reset Zoom")
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.zoom_reset_button.clicked.connect(self.zoom_reset)
        zoom_layout.addWidget(self.zoom_in_button)
        zoom_layout.addWidget(self.zoom_out_button)
        zoom_layout.addWidget(self.zoom_reset_button)
        self.pdf_preview_container.addLayout(zoom_layout)

        # Nascondi l'intero widget di anteprima inizialmente
        self.pdf_preview_widget.setVisible(False)

        # Aggiungi il widget dell'anteprima al layout principale
        self.main_layout.addWidget(self.pdf_preview_widget, 1)  # Proporzione 1

        self.central_widget.setLayout(self.main_layout)

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

        # Se è stato aggiunto almeno un file, seleziona il primo
        if len(self.file_paths) > 0 and self.file_list.currentRow() == -1:
            self.file_list.setCurrentRow(0)

    def rimuovi_file(self):
        """
        Rimuove il file selezionato dalla lista dei file da processare.
        """
        selected = self.file_list.currentRow()
        if selected >= 0:
            self.file_paths.pop(selected)
            self.file_list.takeItem(selected)

            # Se non ci sono più file, nascondi l'anteprima
            if len(self.file_paths) == 0:
                self.pdf_preview_widget.setVisible(False)
                self.preview_title.setText("Anteprima PDF")
                self.current_pdf_path = None

                # Resetta le variabili di navigazione pagine
                self.current_page = 0
                self.total_pages = 0

                # Nascondi i controlli di navigazione
                self.prev_page_button.setVisible(False)
                self.next_page_button.setVisible(False)
                self.page_label.setVisible(False)

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
        self.ml_checkbox.setChecked(False)  # Ripristina l'apprendimento automatico a disabilitato
        self.label_output.setText("")

        # Nascondi l'anteprima PDF
        self.pdf_preview_widget.setVisible(False)
        self.preview_title.setText("Anteprima PDF")
        self.current_pdf_path = None

        # Resetta le variabili di navigazione pagine
        self.current_page = 0
        self.total_pages = 0

        # Nascondi i controlli di navigazione
        self.prev_page_button.setVisible(False)
        self.next_page_button.setVisible(False)
        self.page_label.setVisible(False)

    def resizeEvent(self, event):
        """
        Gestisce il ridimensionamento della finestra.

        Quando la finestra viene ridimensionata, adatta l'anteprima PDF
        per mantenere le proporzioni corrette.

        Args:
            event: L'evento di ridimensionamento
        """
        super().resizeEvent(event)

        # Se c'è un PDF attualmente visualizzato, adattalo alla nuova dimensione
        if self.current_pdf_path and self.pdf_preview_widget.isVisible():
            # Ottieni gli elementi nella scena
            items = self.pdf_scene.items()
            if items:
                # Prendi il primo elemento (il pixmap del PDF)
                pixmap_item = items[0]
                # Adatta la vista all'elemento, tenendo conto del fattore di zoom
                if self.zoom_factor == 1.0:
                    self.pdf_view.fitInView(pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
                else:
                    # Mantieni lo zoom corrente
                    self.pdf_view.resetTransform()
                    self.pdf_view.scale(self.zoom_factor, self.zoom_factor)

    def zoom_in(self):
        """
        Aumenta il livello di zoom dell'anteprima PDF.
        """
        if not self.current_pdf_path or not self.pdf_preview_widget.isVisible():
            return

        # Aumenta il fattore di zoom del 20%
        self.zoom_factor *= 1.2

        # Applica il nuovo zoom
        self.pdf_view.resetTransform()
        self.pdf_view.scale(self.zoom_factor, self.zoom_factor)

    def zoom_out(self):
        """
        Diminuisce il livello di zoom dell'anteprima PDF.
        """
        if not self.current_pdf_path or not self.pdf_preview_widget.isVisible():
            return

        # Diminuisce il fattore di zoom del 20%
        self.zoom_factor *= 0.8

        # Applica il nuovo zoom
        self.pdf_view.resetTransform()
        self.pdf_view.scale(self.zoom_factor, self.zoom_factor)

    def zoom_reset(self):
        """
        Reimposta il livello di zoom dell'anteprima PDF al valore predefinito.
        """
        if not self.current_pdf_path or not self.pdf_preview_widget.isVisible():
            return

        # Reimposta il fattore di zoom
        self.zoom_factor = 1.0

        # Ottieni gli elementi nella scena
        items = self.pdf_scene.items()
        if items:
            # Prendi il primo elemento (il pixmap del PDF)
            pixmap_item = items[0]
            # Adatta la vista all'elemento
            self.pdf_view.fitInView(pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)

    def aggiorna_anteprima_pdf(self, current_row):
        """
        Aggiorna l'anteprima del PDF quando viene selezionato un file dalla lista.

        Args:
            current_row (int): L'indice del file selezionato nella lista
        """
        # Pulisci la scena grafica
        self.pdf_scene.clear()

        # Se non c'è nessun file selezionato, nascondi l'anteprima
        if current_row < 0 or current_row >= len(self.file_paths):
            self.pdf_preview_widget.setVisible(False)
            self.preview_title.setText("Anteprima PDF")
            self.current_pdf_path = None
            self.current_page = 0
            self.total_pages = 0
            self.prev_page_button.setVisible(False)
            self.next_page_button.setVisible(False)
            self.page_label.setVisible(False)
            return

        # Ottieni il percorso del file selezionato
        file_path = self.file_paths[current_row]
        self.current_pdf_path = file_path

        # Resetta il fattore di zoom quando si cambia documento
        self.zoom_factor = 1.0

        # Resetta la pagina corrente
        self.current_page = 0

        try:
            # Apri il PDF con PyMuPDF
            doc = fitz.open(file_path)

            # Salva il numero totale di pagine
            self.total_pages = len(doc)

            # Aggiorna i controlli di navigazione
            self.aggiorna_controlli_navigazione()

            # Mostra la pagina corrente
            self.mostra_pagina_corrente(doc)

            # Mostra l'anteprima
            self.pdf_preview_widget.setVisible(True)

            # Aggiorna il titolo con il nome del file
            self.preview_title.setText(f"Anteprima: {os.path.basename(file_path)}")

            # Chiudi il documento
            doc.close()

        except Exception as e:
            # In caso di errore, nascondi l'anteprima e mostra un messaggio
            self.pdf_preview_widget.setVisible(False)
            self.preview_title.setText(f"Errore nell'anteprima: {str(e)}")
            logging.error(f"Errore durante la generazione dell'anteprima PDF: {str(e)}")
            logging.debug(traceback.format_exc())

    def mostra_pagina_corrente(self, doc=None):
        """
        Mostra la pagina corrente del PDF nell'anteprima.

        Args:
            doc (fitz.Document, optional): Documento PDF già aperto. Se None, apre il documento corrente.
        """
        if not self.current_pdf_path:
            return

        close_doc = False
        try:
            if doc is None:
                doc = fitz.open(self.current_pdf_path)
                close_doc = True

            if self.current_page < 0:
                self.current_page = 0
            elif self.current_page >= self.total_pages:
                self.current_page = self.total_pages - 1

            # Prendi la pagina corrente
            page = doc[self.current_page]

            # Renderizza la pagina come immagine
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))  # Scala 1.5 per una migliore qualità

            # Converti l'immagine in QImage
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)

            # Crea un QPixmap dall'immagine
            pixmap = QPixmap.fromImage(img)

            # Pulisci la scena e aggiungi l'immagine
            self.pdf_scene.clear()
            self.pdf_scene.addPixmap(pixmap)

            # Adatta la vista alla scena
            self.pdf_view.setScene(self.pdf_scene)
            self.pdf_view.fitInView(QRectF(0, 0, pixmap.width(), pixmap.height()), Qt.AspectRatioMode.KeepAspectRatio)

            # Aggiorna l'etichetta della pagina
            self.page_label.setText(f"Pagina {self.current_page + 1} di {self.total_pages}")

        except Exception as e:
            logging.error(f"Errore durante la visualizzazione della pagina {self.current_page}: {str(e)}")
            logging.debug(traceback.format_exc())
        finally:
            if close_doc and doc:
                doc.close()

    def aggiorna_controlli_navigazione(self):
        """
        Aggiorna la visibilità e lo stato dei controlli di navigazione in base al numero di pagine.
        """
        # Mostra i controlli di navigazione solo se ci sono più pagine
        has_multiple_pages = self.total_pages > 1

        self.prev_page_button.setVisible(has_multiple_pages)
        self.next_page_button.setVisible(has_multiple_pages)
        self.page_label.setVisible(has_multiple_pages)

        # Aggiorna lo stato dei pulsanti
        self.prev_page_button.setEnabled(self.current_page > 0)
        self.next_page_button.setEnabled(self.current_page < self.total_pages - 1)

    def prev_page(self):
        """
        Visualizza la pagina precedente del PDF.
        """
        if self.current_page > 0:
            self.current_page -= 1
            self.mostra_pagina_corrente()
            self.aggiorna_controlli_navigazione()

    def next_page(self):
        """
        Visualizza la pagina successiva del PDF.
        """
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.mostra_pagina_corrente()
            self.aggiorna_controlli_navigazione()

    def mostra_dialog_feedback(self, file_path, denominazione, numero_fattura, data_fattura, testo_estratto):
        """
        Mostra un dialog per confermare o correggere l'estrazione e migliorare i pattern.

        Args:
            file_path (str): Percorso del file PDF
            denominazione (str): Denominazione estratta
            numero_fattura (str): Numero fattura estratto
            data_fattura (str): Data fattura estratta
            testo_estratto (str): Testo completo estratto dal PDF

        Returns:
            tuple: Denominazione, numero fattura e data fattura confermati o corretti
        """
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit

        dialog = QDialog(self)
        dialog.setWindowTitle("Conferma Estrazione")
        dialog.resize(600, 500)

        layout = QVBoxLayout()

        # Informazioni estratte
        layout.addWidget(QLabel("<b>Informazioni estratte:</b>"))

        # Denominazione
        denom_layout = QHBoxLayout()
        denom_layout.addWidget(QLabel("Denominazione:"))
        denom_input = QLineEdit(denominazione if denominazione else "")
        denom_layout.addWidget(denom_input)
        layout.addLayout(denom_layout)

        # Numero fattura
        num_layout = QHBoxLayout()
        num_layout.addWidget(QLabel("Numero fattura:"))
        num_input = QLineEdit(numero_fattura if numero_fattura else "")
        num_layout.addWidget(num_input)
        layout.addLayout(num_layout)

        # Data fattura
        data_layout = QHBoxLayout()
        data_layout.addWidget(QLabel("Data fattura:"))
        data_input = QLineEdit(data_fattura if data_fattura else "")
        data_layout.addWidget(data_input)
        layout.addLayout(data_layout)

        # Testo estratto
        layout.addWidget(QLabel("<b>Testo estratto dal PDF:</b>"))
        text_view = QTextEdit()
        text_view.setPlainText(testo_estratto if testo_estratto else "Nessun testo estratto")
        text_view.setReadOnly(True)
        layout.addWidget(text_view)

        # Pulsanti
        buttons_layout = QHBoxLayout()

        btn_cancel = QPushButton("Annulla")
        btn_cancel.clicked.connect(dialog.reject)

        # Cambia il testo del pulsante in base allo stato dell'apprendimento automatico
        btn_text = "Conferma e Migliora" if self.ml_checkbox.isChecked() else "Conferma"
        btn_confirm = QPushButton(btn_text)
        btn_confirm.clicked.connect(dialog.accept)

        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(btn_confirm)
        layout.addLayout(buttons_layout)

        dialog.setLayout(layout)

        # Esegui il dialog
        if dialog.exec():
            # L'utente ha confermato, salva le correzioni
            new_denom = denom_input.text().strip()
            new_num = num_input.text().strip()
            new_data = data_input.text().strip()

            # Se i valori sono stati corretti e l'apprendimento automatico è abilitato, crea nuovi pattern
            if self.ml_checkbox.isChecked():
                if new_denom and new_denom != denominazione:
                    # Crea un nuovo pattern per la denominazione
                    pattern = self.crea_pattern_da_testo(testo_estratto, new_denom, "denominazione")
                    if pattern:
                        self.pattern_db.add_global_pattern("denominazione", pattern)

                if new_denom and new_num and new_data:
                    # Crea un pattern specifico per questo fornitore
                    pattern = self.crea_pattern_da_testo(testo_estratto, f"{new_num}\\s+{new_data}", "numero_data")
                    if pattern:
                        self.pattern_db.add_fornitore_pattern(new_denom, {
                            "numero_data": pattern
                        })

            return new_denom, new_num, new_data

        return denominazione, numero_fattura, data_fattura

    def crea_pattern_da_testo(self, testo, valore, tipo):
        """
        Crea un pattern regex basato sul testo e sul valore estratto.

        Args:
            testo (str): Testo completo
            valore (str): Valore da cercare nel testo
            tipo (str): Tipo di pattern (denominazione, numero_data)

        Returns:
            str: Pattern regex creato o None se non è possibile crearlo
        """
        try:
            # Escape dei caratteri speciali nel valore
            escaped_value = re.escape(valore)

            if tipo == "denominazione":
                # Cerca il valore nel testo e crea un pattern con il contesto
                index = testo.find(valore)
                if index >= 0:
                    # Prendi fino a 20 caratteri prima del valore
                    prefix = testo[max(0, index-20):index]
                    # Trova l'ultimo separatore nel prefisso (spazio, newline, :)
                    separators = [prefix.rfind(" "), prefix.rfind("\n"), prefix.rfind(":")]
                    sep_index = max(separators)
                    if sep_index >= 0:
                        prefix = prefix[sep_index:]

                    # Crea il pattern
                    return f"{re.escape(prefix)}(.+)"

            elif tipo == "numero_data":
                # Per numero e data, crea un pattern che cattura entrambi
                parts = escaped_value.split("\\s+")
                if len(parts) == 2:
                    return f"({parts[0]})\\s+({parts[1]})"

            return None
        except Exception as e:
            logging.error(f"Errore nella creazione del pattern: {str(e)}")
            return None

    def apri_gestore_pattern(self):
        """
        Apre una finestra per gestire i pattern di estrazione salvati.
        """
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle("Gestione Pattern di Estrazione")
        dialog.resize(800, 600)
        layout = QVBoxLayout()

        # Crea un widget con schede
        tab_widget = QTabWidget()

        # Scheda per i pattern globali
        global_tab = QWidget()
        global_layout = QVBoxLayout()

        # Tabella per i pattern di denominazione
        global_layout.addWidget(QLabel("<b>Pattern per Denominazione:</b>"))
        denom_table = QTableWidget(0, 2)
        denom_table.setHorizontalHeaderLabels(["ID", "Pattern Regex"])
        denom_table.horizontalHeader().setStretchLastSection(True)

        # Popola la tabella
        denom_patterns = self.pattern_db.get_global_patterns("denominazione")
        denom_table.setRowCount(len(denom_patterns))
        for i, pattern in enumerate(denom_patterns):
            denom_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            denom_table.setItem(i, 1, QTableWidgetItem(pattern))

        global_layout.addWidget(denom_table)

        # Tabella per i pattern di numero/data
        global_layout.addWidget(QLabel("<b>Pattern per Numero/Data:</b>"))
        numdata_table = QTableWidget(0, 2)
        numdata_table.setHorizontalHeaderLabels(["ID", "Pattern Regex"])
        numdata_table.horizontalHeader().setStretchLastSection(True)

        # Popola la tabella
        numdata_patterns = self.pattern_db.get_global_patterns("numero_data")
        numdata_table.setRowCount(len(numdata_patterns))
        for i, pattern in enumerate(numdata_patterns):
            numdata_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            numdata_table.setItem(i, 1, QTableWidgetItem(pattern))

        global_layout.addWidget(numdata_table)

        global_tab.setLayout(global_layout)
        tab_widget.addTab(global_tab, "Pattern Globali")

        # Scheda per i pattern specifici dei fornitori
        fornitori_tab = QWidget()
        fornitori_layout = QVBoxLayout()

        fornitori_table = QTableWidget(0, 3)
        fornitori_table.setHorizontalHeaderLabels(["Fornitore", "Tipo Pattern", "Pattern Regex"])
        fornitori_table.horizontalHeader().setStretchLastSection(True)

        # Popola la tabella
        row = 0
        for fornitore, patterns in self.pattern_db.patterns["fornitori"].items():
            for tipo, pattern in patterns.items():
                fornitori_table.insertRow(row)
                fornitori_table.setItem(row, 0, QTableWidgetItem(fornitore))
                fornitori_table.setItem(row, 1, QTableWidgetItem(tipo))
                fornitori_table.setItem(row, 2, QTableWidgetItem(pattern))
                row += 1

        fornitori_layout.addWidget(fornitori_table)
        fornitori_tab.setLayout(fornitori_layout)
        tab_widget.addTab(fornitori_tab, "Pattern Fornitori")

        layout.addWidget(tab_widget)

        # Pulsanti
        buttons_layout = QHBoxLayout()
        btn_close = QPushButton("Chiudi")
        btn_close.clicked.connect(dialog.accept)
        buttons_layout.addWidget(btn_close)
        layout.addLayout(buttons_layout)

        dialog.setLayout(layout)
        dialog.exec()

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

                    # Estrai informazioni dal PDF con feedback mode
                    denominazione, numero_fattura, data_fattura, testo_estratto = estrai_info_da_pdf(file_path, feedback_mode=True)

                    if all([denominazione, numero_fattura, data_fattura]):
                        logging.info(f"Informazioni estratte: denominazione={denominazione}, "
                                    f"numero_fattura={numero_fattura}, data_fattura={data_fattura}")

                        # Chiedi conferma e migliora i pattern solo se l'apprendimento automatico è abilitato
                        if self.ml_checkbox.isChecked():
                            denominazione, numero_fattura, data_fattura = self.mostra_dialog_feedback(
                                file_path, denominazione, numero_fattura, data_fattura, testo_estratto
                            )

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
                        # Se l'estrazione è fallita ma abbiamo il testo, chiedi all'utente di inserire manualmente
                        if testo_estratto:
                            logging.info(f"Estrazione fallita ma testo disponibile")
                            # Mostra il dialog solo se l'apprendimento automatico è abilitato
                            if self.ml_checkbox.isChecked():
                                logging.info(f"Richiedo input manuale per miglioramento")
                                denominazione, numero_fattura, data_fattura = self.mostra_dialog_feedback(
                                    file_path, None, None, None, testo_estratto
                                )
                            else:
                                # Se l'apprendimento automatico è disabilitato, non mostrare il dialog
                                denominazione, numero_fattura, data_fattura = None, None, None

                            # Se l'utente ha inserito i dati manualmente, procedi con la rinomina
                            if all([denominazione, numero_fattura, data_fattura]):
                                # Genera il nuovo nome file
                                nuovo_nome = genera_nome_file(
                                    tipologia, numero_fattura, data_fattura, denominazione, stagione, anno, genere, generico
                                )
                                logging.info(f"Nuovo nome generato manualmente: {nuovo_nome}")

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
                                logging.warning(f"L'utente non ha fornito dati sufficienti per la rinomina")
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
