# -*- coding: utf-8 -*-
"""
Module : services.py
Rôle : Modélisation des microservices communicants du SGDD
"""
import time
from security_engine import ZeroTrustSecurityEngine

security = ZeroTrustSecurityEngine()

class APIGateway:
    """Point d'entrée unique de l'architecture. Responsable du filtrage initial."""
    def __init__(self):
        self.name = "API_Gateway"
        # Simulation d'un registre des adresses IP pour un Rate Limiting rudimentaire
        self.request_history = {}

    def handle_user_upload(self, client_ip: str, filename: str, file_bytes: bytes, user_role: str) -> dict:
        print(f"\n[{self.name}] 📥 Requête reçue de l'IP {client_ip} pour le fichier '{filename}'.")
        
        # 1. Atténuation DDoS : Rate Limiting basique
        current_time = time.time()
        if client_ip in self.request_history:
            last_request = self.request_history[client_ip]
            if current_time - last_request < 0.5: # Interdire moins de 500ms d'intervalle
                return {"status": 429, "message": "Rate Limit Exceeded. Veuillez ralentir vos requêtes."}
        self.request_history[client_ip] = current_time

        # 2. Validation de sécurité initiale du fichier
        ext = filename.split(".")[-1] if "." in filename else ""
        safety_check = security.validate_file_safety(file_bytes, ext)
        if not safety_check["safe"]:
            print(f"[{self.name}] ❌ Blocage de sécurité immédiat : {safety_check['reason']}")
            return {"status": 400, "message": f"Sécurité refusée : {safety_check['reason']}"}

        print(f"[{self.name}] ✅ Fichier validé (SHA256: {safety_check['sha256']}).")

        # 3. Génération d'un jeton de confiance inter-service ciblé pour le service de stockage
        print(f"[{self.name}] 🔑 Génération d'un jeton sécurisé pour le 'Stockage_Service'.")
        inter_service_token = security.generate_token(
            source_service=self.name,
            target_service="Stockage_Service",
            user_role=user_role
        )

        # 4. Transmission sécurisée au Stockage Service (Appel réseau simulé)
        storage = StockageService()
        return storage.receive_and_store(inter_service_token, filename, file_bytes, safety_check['sha256'])


class StockageService:
    """Microservice gérant la persistance et les métadonnées."""
    def __init__(self):
        self.name = "Stockage_Service"
        self.database = {} # Simulation de la persistance PostgreSQL

    def receive_and_store(self, token: str, filename: str, file_bytes: bytes, file_hash: str) -> dict:
        print(f"[{self.name}] 📦 Réception d'une demande de stockage...")
        
        # Principe Zero Trust : Le service ne fait pas confiance aveuglément à la Gateway
        verification = security.verify_token(token, expected_audience=self.name)
        if not verification["valid"]:
            print(f"[{self.name}] 🚨 VIOLATION DE SÉCURITÉ : {verification['error']}")
            return {"status": 401, "message": f"Accès refusé par le service de Stockage : {verification['error']}"}

        claims = verification["claims"]
        print(f"[{self.name}] 🛡️ Jeton valide. Provenance certifiée : {claims['iss']}. Rôle Utilisateur : {claims['role']}")

        # Enregistrement simulé en BDD
        doc_id = len(self.database) + 1
        self.database[doc_id] = {
            "id": doc_id,
            "filename": filename,
            "hash": file_hash,
            "stored_at": time.time()
        }
        print(f"[{self.name}] 💾 Document mémorisé en Base de Données avec l'ID #{doc_id}.")

        # Communication avec le Recherche Service via gRPC simulé (Nouveau Jeton)
        print(f"[{self.name}] 🔑 Génération d'un jeton d'indexation pour 'Recherche_Service'.")
        recherche_token = security.generate_token(
            source_service=self.name,
            target_service="Recherche_Service",
            user_role=claims['role']
        )
        
        recherche_svc = RechercheService()
        recherche_svc.index_document(recherche_token, doc_id, filename)

        return {"status": 201, "message": "Document traité et répliqué avec succès.", "document_id": doc_id}


class RechercheService:
    """Microservice asynchrone d'indexation."""
    def __init__(self):
        self.name = "Recherche_Service"
        self.index = []

    def index_document(self, token: str, doc_id: int, filename: str):
        # Vérification d'authentification mutuelle
        verification = security.verify_token(token, expected_audience=self.name)
        if not verification["valid"]:
            print(f"[{self.name}] 🚨 REJET DE L'INDEXATION : Jeton invalide ({verification['error']}).")
            return False
            
        print(f"[{self.name}] 🔍 Indexation du document #{doc_id} ('{filename}') complétée de manière sécurisée.")
        self.index.append(doc_id)
        return True