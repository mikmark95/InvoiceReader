import re
import os
import logging
import traceback
import fitz  # PyMuPDF


def estrai_info_da_pdf(path):
    """
    Estrae informazioni rilevanti da un file PDF di fattura.

    Utilizza PyMuPDF per estrarre il testo dal PDF e poi cerca pattern specifici
    per identificare la denominazione del fornitore, il numero della fattura e la data.

    Args:
        path (str): Percorso completo al file PDF da analizzare

    Returns:
        tuple: Una tupla contenente (denominazione, numero_fattura, data_fattura)
               Se l'estrazione fallisce, ritorna (None, None, None)
    """
    try:
        # Verifica che il file esista
        if not os.path.exists(path):
            logging.error(f"File non trovato: {path}")
            return None, None, None

        # Verifica che il file sia un PDF
        if not path.lower().endswith('.pdf'):
            logging.error(f"Il file non è un PDF: {path}")
            return None, None, None

        # Estrai il testo dal PDF
        try:
            with fitz.open(path) as pdf:
                testo = ""
                for pagina in pdf:
                    testo += pagina.get_text()
        except fitz.FileDataError:
            logging.error(f"Errore nel formato del file PDF: {path}")
            return None, None, None
        except Exception as e:
            logging.error(f"Errore durante l'estrazione del testo dal PDF {path}: {str(e)}")
            logging.debug(traceback.format_exc())
            return None, None, None

        # Cerca i pattern nel testo
        denominazione_match = re.search(r"Denominazione:\s*(.+)", testo)
        numero_data_match = re.search(r"([A-Z0-9/\-]+)\s+(\d{2}-\d{2}-\d{4})", testo)

        if denominazione_match and numero_data_match:
            denominazione = denominazione_match.group(1).strip()
            numero_fattura = numero_data_match.group(1).strip().replace("/", "-")
            data_fattura = numero_data_match.group(2).strip()
            return denominazione, numero_fattura, data_fattura
        else:
            logging.warning(f"Non è stato possibile estrarre tutte le informazioni dal PDF: {path}")
            logging.debug(f"Testo estratto: {testo[:500]}...")  # Log dei primi 500 caratteri
            return None, None, None

    except Exception as e:
        # Cattura qualsiasi altra eccezione non prevista
        logging.error(f"Errore imprevisto durante l'elaborazione del PDF {path}: {str(e)}")
        logging.debug(traceback.format_exc())
        return None, None, None


def genera_nome_file(tipologia, numero_fattura, data_fattura, denominazione, stagione, anno, genere, generico=False):
    """
    Genera un nome file standardizzato per la fattura in base ai parametri forniti.

    Crea un nome file che include tutte le informazioni rilevanti della fattura
    e rimuove eventuali caratteri non validi per i nomi file.

    Args:
        tipologia (str): Tipo di documento (es. "FATT" per fattura, "NC" per nota di credito)
        numero_fattura (str): Numero identificativo della fattura
        data_fattura (str): Data della fattura nel formato "GG-MM-AAAA"
        denominazione (str): Nome del fornitore
        stagione (str): Stagione di riferimento (es. "PE", "AI", "CONTINUATIVO")
        anno (str): Anno di riferimento
        genere (str): Genere di riferimento (es. "UOMO", "DONNA")
        generico (bool, optional): Se True, usa un formato semplificato. Default False.

    Returns:
        str: Nome file standardizzato con estensione .pdf
    """
    if generico:
        nome = f"{denominazione} {numero_fattura} DEL {data_fattura}.pdf"
    else:
        nome = f"{tipologia} {numero_fattura} DEL {data_fattura} {denominazione} {stagione} {anno} {genere}.pdf"

    caratteri_non_validi = r'<>:"/\\|?*'
    for c in caratteri_non_validi:
        nome = nome.replace(c, "")
    return nome
