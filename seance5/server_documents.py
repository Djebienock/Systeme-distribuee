import Pyro5.api
import logging

# Configuration de la journalisation interne (Équipe technique)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Base de données simulée côté serveur (Persistance de l'état)
_DOCUMENTS = {
    "doc_001": "Rapport annuel 2024 — Données hautement confidentielles.",
    "doc_002": "Politique de sécurité de SecureBank — Version 3.2.",
    "doc_003": "Guide d'utilisation de l'API — Accès public.",
}

@Pyro5.api.expose
class DocumentService:
    """Service distant orienté objet pour la gestion des documents (Équivalent RMI)"""
    
    def list_documents(self) -> list:
        """Retourne la liste des identifiants de documents disponibles"""
        logger.info("Appel distant : list_documents()")
        return list(_DOCUMENTS.keys())

    def get_document_content(self, doc_id: str) -> str:
        """Retourne le contenu d'un document spécifique par son ID"""
        logger.info(f"Appel distant : get_document_content(doc_id='{doc_id}')")
        if doc_id in _DOCUMENTS:
            return _DOCUMENTS[doc_id]
        else:
            logger.warning(f"Ressource introuvable : '{doc_id}'")
            raise KeyError("Document introuvable")

def main():
    # Initialisation du Daemon (Serveur d'objets distants)
    with Pyro5.api.Daemon() as daemon:
        try:
            # Localisation de l'annuaire de noms (Name Server)
            ns = Pyro5.api.locate_ns()
            
            # Enregistrement de la classe dans le daemon pour générer l'URI unique
            uri = daemon.register(DocumentService)
            
            # Liaison de l'URI à un nom logique lisible par les clients
            ns.register("securebank.documents", uri)
            
            print(f" [+] DocumentService est prêt et publié sous : 'securebank.documents'")
            print(f" [!] URI de l'objet : {uri}")
            
            # Boucle d'écoute infinie des requêtes réseaux
            daemon.requestLoop()
            
        except Exception as e:
            logger.error(f"Impossible d'initialiser le serveur : {e}", exc_info=True)

if __name__ == "__main__":
    main()