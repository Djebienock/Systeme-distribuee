import Pyro5.api
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

_DOCUMENTS = {"doc_001": "Contenu A", "doc_002": "Contenu B"}

# Expression régulière limitant strictement aux caractères alphanumériques et underscores
ID_REGEX = re.compile(r"^[a-zA-Z0-9_]+$")

@Pyro5.api.expose
class ValidatedDocumentService:
    
    def get_document_content(self, doc_id: str) -> str:
        """Retourne le document après vérifications structurelles rigoureuses"""
        
        # 1. Validation de type (Contre l'envoi de dictionnaires/listes inattendus)
        if not isinstance(doc_id, str):
            logger.error(f"[SECURITY ALERT] Type invalide reçu : {type(doc_id)}")
            raise TypeError("Paramètre invalide") # Message client neutre
            
        # 2. Validation de longueur (Prévention des saturations mémoires)
        if len(doc_id) == 0 or len(doc_id) > 20:
            logger.warning(f"[SECURITY ALERT] Longueur d'identifiant anormale : {len(doc_id)}")
            raise ValueError("Identifiant invalide")

        # 3. Validation de format / Regex (Contre l'injection de '../' ou ';DROP')
        if not ID_REGEX.match(doc_id):
            logger.warning(f"[SECURITY ALERT] Caractères interdits détectés dans doc_id : {doc_id!r}")
            raise ValueError("Identifiant invalide")

        # 4. Récupération sécurisée et gestion des erreurs étanche
        try:
            # Traitement métier
            if doc_id not in _DOCUMENTS:
                raise KeyError("Ressource introuvable")
                
            return _DOCUMENTS[doc_id]
            
        except KeyError as ke:
            logger.info(f"Ressource demandée non trouvée : {doc_id}")
            raise KeyError("Document introuvable") # Exception contrôlée
            
        except Exception as e:
            # Audit : Trace complète enregistrée UNIQUEMENT dans les logs internes
            logger.error(f"[CRITICAL ERROR] Défaillance système lors de get_data({doc_id}) : {e}", exc_info=True)
            # Client : Reçoit un message générique et opaque (Pas d'Information Disclosure)
            raise RuntimeError("Erreur de service. Contactez l'administrateur.")