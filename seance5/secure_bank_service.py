import Pyro5.api
import logging
import re

# Configuration de la journalisation de sécurité
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("SecureBankLogger")

# Paramètres globaux de sécurité
AUTH_TOKEN = "BankToken_Production_2026!"
ID_REGEX = re.compile(r"^[a-zA-Z0-9_-]+$")

@Pyro5.api.expose
class DurcementDocumentService:
    def __init__(self):
        # Utilisation de variables privées pour bloquer l'inspection distante
        self.__secret_key = "sk-1234567890abcdef"
        self.__allowed_docs = {
            "doc_a": "Rapport Financier Q1.txt",
            "doc_b": "Audits Infrastructures.txt"
        }

    def get_secure_document(self, token: str, key: str) -> str:
        """Méthode d'accès sécurisée et validée"""
        
        # 1. Contrôle de l'authentification
        if token != AUTH_TOKEN:
            logger.warning("[SECURITY AUDIT] Échec d'authentification : Jeton invalide.")
            raise PermissionError("Accès non autorisé.")

        # 2. Validation de type
        if not isinstance(key, str):
            logger.error("[SECURITY AUDIT] Type de paramètre invalide reçu.")
            raise TypeError("Requête malformée.")

        # 3. Validation de format par Regex (Anti-Path Traversal)
        if not ID_REGEX.match(key):
            logger.warning(f"[SECURITY AUDIT] Format d'ID invalide détecté : {key!r}")
            raise ValueError("Requête malformée.")

        # 4. Résolution de la clé
        if key not in self.__allowed_docs:
            logger.info(f"Ressource demandée non répertoriée : {key}")
            raise KeyError("Document introuvable.")

        filename = self.__allowed_docs[key]
        logger.info(f"[SUCCESS] Extraction sécurisée du document : {key}")
        return f"[Contenu sécurisé du document {filename}]"


def main():
    # On configure le Daemon pour écouter localement sur 127.0.0.1
    with Pyro5.api.Daemon(host="127.0.0.1") as daemon:
        try:
            # INTERVENTION ICI : On force Pyro5 à chercher l'annuaire sur 127.0.0.1
            ns = Pyro5.api.locate_ns(host="127.0.0.1")
            
            uri = daemon.register(DurcementDocumentService)
            ns.register("securebank.hardened.documents", uri)
            
            print(" [+] Serveur DURCI prêt à fonctionner.")
            print(" [!] En attente de requêtes du client...")
            daemon.requestLoop()
        except Exception as e:
            print(f"[-] Erreur d'initialisation : {e}")

if __name__ == "__main__":
    main()