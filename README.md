
# InvoiceReader - Rinomina Fatture PDF

InvoiceReader è un'applicazione desktop con interfaccia grafica che permette di rinominare automaticamente file PDF di fatture e note di credito. L'applicazione estrae informazioni dai PDF come denominazione del fornitore, numero fattura e data, e genera nomi file standardizzati includendo anche informazioni aggiuntive come stagione, anno e genere.

## Funzionalità

- Selezione multipla di file PDF
- Estrazione automatica di informazioni dai PDF (denominazione fornitore, numero fattura, data)
- Personalizzazione del nome file con parametri aggiuntivi (tipologia, stagione, anno, genere)
- Opzione per spostare i file in cartelle denominate secondo il fornitore
- Interfaccia grafica intuitiva realizzata con PyQt6

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

2. Utilizza il pulsante "Scegli PDF" per selezionare uno o più file PDF di fatture
3. Compila i campi richiesti:
   - Tipologia: Fattura o Nota di credito
   - Stagione: PE (Primavera/Estate), AI (Autunno/Inverno) o CONTINUATIVO
   - Anno: Anno di riferimento (es. 2025)
   - Genere: UOMO o DONNA
4. Opzionalmente, seleziona l'opzione per spostare i file in cartelle con il nome del fornitore
5. Clicca su "Avvia Rinomina" per processare i file

## Struttura del Progetto

- `src/main.py`: Punto di ingresso dell'applicazione
- `src/gui.py`: Implementazione dell'interfaccia grafica con PyQt6
- `src/utils.py`: Funzioni di utilità per l'estrazione di informazioni dai PDF e la generazione dei nomi file
- `src/config.py`: File per configurazioni future

## Come Funziona

L'applicazione utilizza PyMuPDF (fitz) per estrarre il testo dai file PDF. Attraverso espressioni regolari, cerca pattern specifici per identificare la denominazione del fornitore, il numero della fattura e la data. Queste informazioni, insieme ai parametri specificati dall'utente, vengono utilizzate per generare un nuovo nome file standardizzato.

## Autori

- [@mikmark95](https://github.com/mikmark95) - Michele Marchetti

## Licenza

Copyright (c) 2025 Marchetti Michele. Tutti i diritti riservati.

Questo software è concesso in licenza, non venduto. L'uso è consentito esclusivamente per scopi personali o aziendali interni. Qualsiasi uso commerciale, distribuzione, modifica o decompilazione senza esplicita autorizzazione scritta del titolare del copyright è severamente vietata.

Per richieste di autorizzazione o licenze personalizzate, contattare: michele-marchetti@hotmail.it
