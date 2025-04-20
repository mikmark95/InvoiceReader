"""
InvoiceReader - Applicazione per rinominare automaticamente file PDF di fatture

Questo modulo è il punto di ingresso dell'applicazione. Inizializza l'interfaccia
grafica PyQt6 e avvia l'applicazione.
"""

import sys
from PyQt6.QtWidgets import QApplication
from gui import FatturaRenamer

if __name__ == "__main__":
    # Inizializza l'applicazione PyQt6
    app = QApplication(sys.argv)

    # Crea e mostra la finestra principale
    window = FatturaRenamer()
    window.show()

    # Avvia il loop di eventi dell'applicazione
    sys.exit(app.exec())
