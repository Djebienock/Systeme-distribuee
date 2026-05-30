import Pyro5.api
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Jeton d'authentification partagé (simulé)
SECRET_AUTH_TOKEN = "SecureToken_2026_XYZ"

@Pyro5.api.expose
class SecureExposureService:
    """Service durci appliquant le principe du moindre privilège et de contrôle d'accès"""

    def _db_connect(self):
        """Méthode INTERNE - Jamais accessible à distance (Pas de @expose)"""
        logger.info("Connexion à la base de données interne réussie.")
        return True

    def _reload_index(self):
        """Méthode INTERNE de maintenance - Non exposée pour éviter les DoS réseau"""
        logger.info("Rechargement de l'index des documents.")
        return True

    def list_documents(self, auth_token: str) -> list:
        """Méthode EXPOSÉE - Requiert obligatoirement un token de sécurité valide"""
        if auth_token != SECRET_AUTH_TOKEN:
            logger.warning("Tentative d'accès non autorisée à list_documents : Token invalide.")
            raise PermissionError("Accès refusé : Authentification insuffisante.")
            
        logger.info("Accès autorisé : list_documents()")
        return ["doc_001", "doc_002", "doc_003"]