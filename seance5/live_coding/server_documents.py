import Pyro5.api
import logging
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Données simulées côté serveur
_DOCUMENTS = {
    "doc_001": "Rapport annuel 2024 — données confidentielles",
    "doc_002": "Politique de sécurité — version 3.2",
    "doc_003": "Guide d'utilisation — accès public",
}

@Pyro5.api.expose
class DocumentService:
    """Service de gestion de documents — équivalent RMI Python."""

    def list_documents(self) -> list:
        """Retourne la liste des IDs de documents disponibles."""
        logger.info("Appel list_documents()")
        return list(_DOCUMENTS.keys())

    def get_document_content(self, doc_id: str) -> str:
        """Retourne le contenu d'un document après validation stricte."""
        # 1. Validation du type
        if not isinstance(doc_id, str):
            logger.warning(f"Type invalide reçu pour doc_id: {type(doc_id)}")
            raise TypeError("Identifiant invalide")  # message générique

        # 2. Validation du format (alphanumérique + underscore uniquement)
        if not re.match(r'^[a-zA-Z0-9_]{1,32}$', doc_id):
            logger.warning(f"Format doc_id non conforme: {doc_id!r}")
            raise ValueError("Identifiant invalide")  # message générique

        # 3. Vérification existence
        if doc_id not in _DOCUMENTS:
            logger.info(f"Document non trouvé: {doc_id}")
            raise KeyError("Document introuvable")

        logger.info(f"Document servi: {doc_id}")
        return _DOCUMENTS[doc_id]

    def _reload_index(self):
        # Méthode INTERNE — PAS d'@expose → inaccessible à distance
        pass


def main():
    with Pyro5.api.Daemon() as daemon:
        ns = Pyro5.api.locate_ns()
        uri = daemon.register(DocumentService)
        ns.register("bank.documents.service", uri)
        print(f"DocumentService prêt — URI: {uri}")
        daemon.requestLoop()

if __name__ == "__main__":
    main()