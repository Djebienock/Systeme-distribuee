import time
from typing import Dict, Any, Tuple
from security_engine import SecurityEngine

class APIGateway:
    """API Gateway distribuant les flux et appliquant les contrôles de sécurité globaux"""
    
    def __init__(self, max_size_bytes: int = 2 * 1024 * 1024, max_requests_per_min: int = 5):
        self.max_size_bytes = max_size_bytes
        self.max_requests_per_min = max_requests_per_min
        self.rate_limit_tracker: Dict[str, list] = {} # Suivi IP -> Liste de timestamps

    def check_rate_limit(self, client_ip: str) -> bool:
        """Applique une fenêtre glissante de Rate Limiting pour contrer les dénis de service (DoS)"""
        current_time = time.time()
        if client_ip not in self.rate_limit_tracker:
            self.rate_limit_tracker[client_ip] = []
            
        # On ne garde que les requêtes des 60 dernières secondes
        self.rate_limit_tracker[client_ip] = [t for t in self.rate_limit_tracker[client_ip] if current_time - t < 60]
        
        if len(self.rate_limit_tracker[client_ip]) >= self.max_requests_per_min:
            return False
            
        self.rate_limit_tracker[client_ip].append(current_time)
        return True

    def receive_document_upload(self, client_ip: str, filename: str, content: bytes, storage_service) -> Tuple[int, Dict[str, Any]]:
        """Contrat d'interface HTTP POST /api/v1/documents"""
        print(f"\n[Gateway] 📥 Réception de {filename} depuis l'adresse IP {client_ip}...")
        
        # 1. Contrôle de sécurité : Rate Limiting
        if not self.check_rate_limit(client_ip):
            return 429, {"error": "Too Many Requests. Fenêtre de limitation atteinte."}
            
        # 2. Contrôle de sécurité : Taille maximale du payload
        if len(content) > self.max_size_bytes:
            return 400, {"error": f"Bad Request. Fichier trop volumineux ({len(content)} octets). Maximum autorisé : {self.max_size_bytes} octets."}
            
        # 3. Validation de type : Inspection binaire des Magic Bytes
        detected_type = SecurityEngine.inspect_magic_bytes(content)
        print(f"[Gateway] 🔍 Analyse binaire. Type détecté : {detected_type}")
        if detected_type == "UNKNOWN_OR_MALICIOUS":
            return 400, {"error": "Bad Request. Signature binaire non reconnue ou malveillante."}
            
        # 4. Calcul de l'empreinte et émission du Token Zero-Trust éphémère
        file_hash = SecurityEngine.calculate_sha256(content)
        infrastructure_token = SecurityEngine.generate_hmac_token("StockageService", file_hash, lifespan=5.0)
        
        # 5. Transmission sécurisée au Stockage Service (Simule un appel RPC/REST interne)
        return storage_service.persist_document(filename, content, file_hash, infrastructure_token)


class StockageService:
    """Service de persistance des fichiers avec registre d'idempotence décentralisé"""
    
    def __init__(self):
        self.database: Dict[str, Dict[str, Any]] = {}
        self.idempotency_cache: Dict[str, Tuple[int, Dict[str, Any]]] = {} # Clé -> (Code, Réponse)

    def persist_document(self, filename: str, content: bytes, file_hash: str, token: str) -> Tuple[int, Dict[str, Any]]:
        """Point d'accès interne pour l'écriture des métadonnées du document"""
        
        # Injection d'une clé d'idempotence basée sur le hash unique du fichier
        idempotency_key = f"upload:{file_hash}"
        
        # Mécanisme de déduplication (Idempotence)
        if idempotency_key in self.idempotency_cache:
            print(f"   [Stockage] ♻️ Requête dupliquée détectée via clé d'idempotence. Renvoi du cache.")
            return self.idempotency_cache[idempotency_key]
            
        print(f"   [Stockage] 🔐 Vérification de la légitimité de la requête...")
        
        # Modèle Zero Trust : Le stockage valide l'authenticité du jeton émis par la Gateway
        if not SecurityEngine.verify_hmac_token(token, "StockageService", file_hash):
            print("   [Stockage] 🚨 ALERT: Tentative d'accès non autorisée ou jeton falsifié/expiré !")
            error_response = (403, {"error": "Forbidden. Accès direct interdit ou jeton invalide."})
            return error_response

        # Traitement nominal et écriture
        print(f"   [Stockage] 💾 Persistance réseau réussie. Fichier enregistré en BDD.")
        self.database[file_hash] = {
            "filename": filename,
            "size": len(content),
            "stored_at": time.time(),
            "integrity_hash": file_hash
        }
        
        success_response = (201, {"status": "Success", "document_id": file_hash, "msg": "Document sauvegardé et validé."})
        
        # Remplissage du cache d'idempotence pour les futures requêtes identiques
        self.idempotency_cache[idempotency_key] = success_response
        return success_response