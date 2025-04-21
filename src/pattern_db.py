import json
import os
import logging
from datetime import datetime

class PatternDatabase:
    """
    Gestisce un database di pattern di estrazione per migliorare il riconoscimento
    delle informazioni nei PDF nel tempo.
    """
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'patterns.json')
        self.patterns = self._load_patterns()
        
    def _load_patterns(self):
        """Carica i pattern dal file JSON."""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {
                "fornitori": {},
                "regex_patterns": {
                    "denominazione": [r"Denominazione:\s*(.+)"],
                    "numero_data": [r"([A-Z0-9/\-]+)\s+(\d{2}-\d{2}-\d{4})"]
                },
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Errore nel caricamento del database dei pattern: {str(e)}")
            return {
                "fornitori": {},
                "regex_patterns": {
                    "denominazione": [r"Denominazione:\s*(.+)"],
                    "numero_data": [r"([A-Z0-9/\-]+)\s+(\d{2}-\d{2}-\d{4})"]
                },
                "last_updated": datetime.now().isoformat()
            }
    
    def save_patterns(self):
        """Salva i pattern nel file JSON."""
        try:
            self.patterns["last_updated"] = datetime.now().isoformat()
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.patterns, f, indent=4, ensure_ascii=False)
            logging.info(f"Database dei pattern salvato con successo: {self.db_path}")
        except Exception as e:
            logging.error(f"Errore nel salvataggio del database dei pattern: {str(e)}")
    
    def add_fornitore_pattern(self, denominazione, pattern_info):
        """
        Aggiunge o aggiorna un pattern specifico per un fornitore.
        
        Args:
            denominazione (str): Nome del fornitore
            pattern_info (dict): Informazioni sul pattern (regex, posizione, ecc.)
        """
        if denominazione not in self.patterns["fornitori"]:
            self.patterns["fornitori"][denominazione] = {}
        
        self.patterns["fornitori"][denominazione].update(pattern_info)
        self.save_patterns()
    
    def get_fornitore_patterns(self, denominazione):
        """
        Ottiene i pattern specifici per un fornitore.
        
        Args:
            denominazione (str): Nome del fornitore
            
        Returns:
            dict: Pattern specifici per il fornitore o None se non trovati
        """
        return self.patterns["fornitori"].get(denominazione)
    
    def add_global_pattern(self, pattern_type, regex):
        """
        Aggiunge un nuovo pattern regex globale.
        
        Args:
            pattern_type (str): Tipo di pattern (es. "denominazione", "numero_data")
            regex (str): Espressione regolare da aggiungere
        """
        if pattern_type not in self.patterns["regex_patterns"]:
            self.patterns["regex_patterns"][pattern_type] = []
        
        if regex not in self.patterns["regex_patterns"][pattern_type]:
            self.patterns["regex_patterns"][pattern_type].append(regex)
            self.save_patterns()
    
    def get_global_patterns(self, pattern_type):
        """
        Ottiene tutti i pattern regex globali per un tipo specifico.
        
        Args:
            pattern_type (str): Tipo di pattern (es. "denominazione", "numero_data")
            
        Returns:
            list: Lista di pattern regex
        """
        return self.patterns["regex_patterns"].get(pattern_type, [])