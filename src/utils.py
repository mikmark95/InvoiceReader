import re
import fitz  # PyMuPDF


def estrai_info_da_pdf(path):
    with fitz.open(path) as pdf:
        testo = ""
        for pagina in pdf:
            testo += pagina.get_text()

    denominazione_match = re.search(r"Denominazione:\s*(.+)", testo)
    numero_data_match = re.search(r"([A-Z0-9/\-]+)\s+(\d{2}-\d{2}-\d{4})", testo)

    if denominazione_match and numero_data_match:
        denominazione = denominazione_match.group(1).strip().replace(" ", "_")
        numero_fattura = numero_data_match.group(1).strip().replace("/", "-")
        data_fattura = numero_data_match.group(2).strip()
        return denominazione, numero_fattura, data_fattura

    return None, None, None


def genera_nome_file(numero_fattura, data_fattura, denominazione, stagione):
    nome = f"FATT {numero_fattura} DEL {data_fattura} {denominazione} STAGIONE {stagione}.pdf"
    caratteri_non_validi = r'<>:"/\\|?*'
    for c in caratteri_non_validi:
        nome = nome.replace(c, "")
    nome = nome.replace(" ", "_")
    return nome
