import re
import os
import logging
import traceback
import fitz  # PyMuPDF
from pattern_db import PatternDatabase

# Inizializza il database dei pattern
pattern_db = PatternDatabase()

def estrai_info_da_pdf(path, feedback_mode=False):
    """
    Estrae informazioni rilevanti da un file PDF di fattura.

    Utilizza PyMuPDF per estrarre il testo dal PDF e poi cerca pattern specifici
    per identificare la denominazione del fornitore, il numero della fattura e la data.
    Utilizza un database di pattern che migliora nel tempo.

    Args:
        path (str): Percorso completo al file PDF da analizzare
        feedback_mode (bool): Se True, restituisce anche il testo estratto per feedback

    Returns:
        tuple: Una tupla contenente (denominazione, numero_fattura, data_fattura, [testo_estratto])
               Se l'estrazione fallisce, ritorna (None, None, None, [testo_estratto])
    """
    try:
        # Verifica che il file esista
        if not os.path.exists(path):
            logging.error(f"File non trovato: {path}")
            return (None, None, None) if not feedback_mode else (None, None, None, None)

        # Verifica che il file sia un PDF
        if not path.lower().endswith('.pdf'):
            logging.error(f"Il file non è un PDF: {path}")
            return (None, None, None) if not feedback_mode else (None, None, None, None)

        # Estrai il testo dal PDF
        try:
            with fitz.open(path) as pdf:
                testo = ""
                for pagina in pdf:
                    testo += pagina.get_text()
        except fitz.FileDataError:
            logging.error(f"Errore nel formato del file PDF: {path}")
            return (None, None, None) if not feedback_mode else (None, None, None, None)
        except Exception as e:
            logging.error(f"Errore durante l'estrazione del testo dal PDF {path}: {str(e)}")
            logging.debug(traceback.format_exc())
            return (None, None, None) if not feedback_mode else (None, None, None, None)

        # Prima prova a identificare il fornitore usando i pattern globali
        denominazione = None
        for pattern in pattern_db.get_global_patterns("denominazione"):
            match = re.search(pattern, testo)
            if match:
                denominazione = match.group(1).strip()
                break

        # Se abbiamo identificato il fornitore, verifica se abbiamo pattern specifici
        if denominazione:
            fornitore_patterns = pattern_db.get_fornitore_patterns(denominazione)
            if fornitore_patterns and "numero_data" in fornitore_patterns:
                # Usa il pattern specifico del fornitore
                match = re.search(fornitore_patterns["numero_data"], testo)
                if match:
                    numero_fattura = match.group(1).strip().replace("/", "-")
                    data_fattura = match.group(2).strip()
                    logging.info(f"Estrazione riuscita usando pattern specifico per {denominazione}")
                    return (denominazione, numero_fattura, data_fattura) if not feedback_mode else (denominazione, numero_fattura, data_fattura, testo)

        # Se non abbiamo trovato pattern specifici o non hanno funzionato, usa i pattern globali
        for pattern in pattern_db.get_global_patterns("numero_data"):
            match = re.search(pattern, testo)
            if match:
                numero_fattura = match.group(1).strip().replace("/", "-")
                data_fattura = match.group(2).strip()
                logging.info(f"Estrazione riuscita usando pattern globale")
                return (denominazione, numero_fattura, data_fattura) if not feedback_mode else (denominazione, numero_fattura, data_fattura, testo)

        # Se siamo arrivati qui, l'estrazione è fallita
        logging.warning(f"Non è stato possibile estrarre tutte le informazioni dal PDF: {path}")
        logging.debug(f"Testo estratto: {testo[:500]}...")  # Log dei primi 500 caratteri
        return (None, None, None) if not feedback_mode else (None, None, None, testo)

    except Exception as e:
        # Cattura qualsiasi altra eccezione non prevista
        logging.error(f"Errore imprevisto durante l'elaborazione del PDF {path}: {str(e)}")
        logging.debug(traceback.format_exc())
        return (None, None, None) if not feedback_mode else (None, None, None, None)


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
