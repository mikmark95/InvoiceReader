
# InvoiceReader - Rinomina Fatture PDF

InvoiceReader è un'applicazione desktop con interfaccia grafica che permette di rinominare automaticamente file PDF di fatture e note di credito. L'applicazione estrae informazioni dai PDF come denominazione del fornitore, numero fattura e data, e genera nomi file standardizzati includendo anche informazioni aggiuntive come stagione, anno e genere.

## Funzionalità

- Selezione multipla di file PDF
- Estrazione automatica di informazioni dai PDF (denominazione fornitore, numero fattura, data)
- Personalizzazione del nome file con parametri aggiuntivi (tipologia, stagione, anno, genere)
- Modalità "Generico" per un formato di nome file semplificato
- Opzione per spostare i file in cartelle denominate secondo il fornitore
- Interfaccia grafica intuitiva realizzata con PyQt6
- Sistema di logging dettagliato per la diagnostica degli errori

## Requisiti di Sistema

- Python 3.8 o superiore
- Dipendenze Python elencate in `requirements.txt`

## Installazione

1. Clona il repository o scarica i file sorgente
2. Installa le dipendenze necessarie:

```bash
pip install -r requirements.txt
```

## Utilizzo

1. Avvia l'applicazione eseguendo:

```bash
python src/main.py
```

2. Utilizza il pulsante "📂 Scegli PDF" per selezionare uno o più file PDF di fatture
3. Scegli la modalità di rinomina:
   - **Modalità Standard**: Compila tutti i campi richiesti:
     - Tipologia: Fattura o Nota di credito
     - Stagione: PE (Primavera/Estate), AI (Autunno/Inverno) o CONTINUATIVO
     - Anno: Anno di riferimento (es. 2025)
     - Genere: UOMO o DONNA
   - **Modalità Generico**: Seleziona la checkbox "Generico" per utilizzare un formato di nome file semplificato che include solo il nome del fornitore, il numero fattura e la data
4. Opzionalmente, seleziona l'opzione "Sposta i file in cartelle con nome del fornitore" per organizzare i file in cartelle
5. Clicca su "🚀 Avvia Rinomina" per processare i file
6. Al termine dell'elaborazione, verrà mostrato un riepilogo dei file elaborati con successo e di quelli non elaborati

## Struttura del Progetto

- `src/main.py`: Punto di ingresso dell'applicazione
- `src/gui.py`: Implementazione dell'interfaccia grafica con PyQt6
- `src/utils.py`: Funzioni di utilità per l'estrazione di informazioni dai PDF e la generazione dei nomi file
- `src/config.py`: File per configurazioni future
- `logs/`: Directory contenente i file di log generati dall'applicazione
- `requirements.txt`: Elenco delle dipendenze Python necessarie

## Come Funziona

L'applicazione utilizza PyMuPDF (fitz) per estrarre il testo dai file PDF. Attraverso espressioni regolari, cerca pattern specifici per identificare la denominazione del fornitore, il numero della fattura e la data. Queste informazioni, insieme ai parametri specificati dall'utente, vengono utilizzate per generare un nuovo nome file standardizzato.

## Sistema di Logging

L'applicazione include un sistema di logging dettagliato che registra informazioni sulle operazioni eseguite e gli eventuali errori riscontrati. I file di log vengono salvati nella cartella `logs` con un nome che include la data e l'ora di esecuzione (es. `error_log_20250421_001523.log`). Questi file sono utili per la diagnostica in caso di problemi.

## Risoluzione dei Problemi

### Errore di Avvio (Exit Code -1073740791)

Se l'applicazione si chiude immediatamente con un errore del tipo:
```
Process finished with exit code -1073740791 (0xC0000409)
```

Questo è spesso causato da uno dei seguenti problemi:

1. **Mancanza di Visual C++ Redistributable**:
   - PyMuPDF e PyQt6 dipendono da librerie C++
   - Scarica e installa l'ultima versione di Microsoft Visual C++ Redistributable dal sito Microsoft

2. **Problemi di Compatibilità con PyMuPDF**:
   - Prova a installare una versione diversa di PyMuPDF:
   ```bash
   pip uninstall PyMuPDF
   pip install PyMuPDF==1.22.0  # Prova una versione stabile precedente
   ```

3. **Ambiente Virtuale Danneggiato**:
   - Crea un nuovo ambiente virtuale:
   ```bash
   python -m venv nuovo_venv
   nuovo_venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Problemi di Estrazione delle Informazioni

Se l'applicazione non riesce a estrarre correttamente le informazioni dai PDF:

1. Verifica che il PDF contenga testo ricercabile e non sia solo un'immagine scansionata
2. Controlla che il formato del documento segua lo standard atteso dall'applicazione
3. Consulta i file di log nella cartella `logs` per dettagli specifici sull'errore

## Autori

- [@mikmark95](https://github.com/mikmark95) - Michele Marchetti

## Licenza

Copyright (c) 2025 Marchetti Michele. Tutti i diritti riservati.

Questo software è concesso in licenza, non venduto. L'uso è consentito esclusivamente per scopi personali o aziendali interni. Qualsiasi uso commerciale, distribuzione, modifica o decompilazione senza esplicita autorizzazione scritta del titolare del copyright è severamente vietata.

Per richieste di autorizzazione o licenze personalizzate, contattare: michele-marchetti@hotmail.it
