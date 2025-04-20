"""
InvoiceReader - Applicazione per rinominare automaticamente file PDF di fatture

Questo modulo è il punto di ingresso dell'applicazione. Inizializza l'interfaccia
grafica PyQt6 e avvia l'applicazione.
"""

import sys
import os
import logging
import traceback
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMessageBox
from gui import FatturaRenamer

# Configurazione del sistema di logging
def setup_logging():
    """
    Configura il sistema di logging per salvare i dettagli degli errori in un file.

    Crea una directory 'logs' se non esiste e configura il logger per scrivere
    in un file con timestamp nel nome.
    """
    # Crea la directory dei log se non esiste
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Crea un nome file con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"error_log_{timestamp}.log")

    # Configura il logger
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    return log_file

# Gestore delle eccezioni non gestite
def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Gestisce le eccezioni non catturate registrandole nel file di log.

    Args:
        exc_type: Tipo dell'eccezione
        exc_value: Valore dell'eccezione
        exc_traceback: Traceback dell'eccezione
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # Non gestiamo l'interruzione da tastiera
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # Log dell'eccezione
    logging.error("Eccezione non gestita:", exc_info=(exc_type, exc_value, exc_traceback))

    # Formatta il traceback come stringa
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_text = ''.join(tb_lines)

    # Log dettagliato
    logging.error(f"Dettagli dell'errore:\n{tb_text}")

    # Mostra un messaggio all'utente
    error_msg = f"Si è verificato un errore imprevisto.\n\nDettagli: {str(exc_value)}\n\nL'errore è stato registrato nel file di log."
    try:
        if QApplication.instance():
            QMessageBox.critical(None, "Errore", error_msg)
    except:
        # Se non possiamo mostrare una finestra di dialogo, stampiamo sulla console
        print(error_msg)

if __name__ == "__main__":
    # Configura il logging
    log_file = setup_logging()

    # Imposta il gestore delle eccezioni non gestite
    sys.excepthook = handle_exception

    try:
        # Inizializza l'applicazione PyQt6
        app = QApplication(sys.argv)

        # Crea e mostra la finestra principale
        window = FatturaRenamer()
        window.show()

        # Avvia il loop di eventi dell'applicazione
        sys.exit(app.exec())
    except Exception as e:
        # Cattura qualsiasi eccezione durante l'avvio dell'applicazione
        logging.error(f"Errore durante l'avvio dell'applicazione: {str(e)}", exc_info=True)

        # Mostra un messaggio all'utente
        error_msg = f"Si è verificato un errore durante l'avvio dell'applicazione.\n\nDettagli: {str(e)}\n\nL'errore è stato registrato nel file: {log_file}"
        try:
            if QApplication.instance():
                QMessageBox.critical(None, "Errore di avvio", error_msg)
            else:
                print(error_msg)
        except:
            print(f"Errore fatale: {str(e)}")
