# -*- coding: utf-8 -*-
"""
Module : security_engine.py
Rôle : Moteur de sécurité Zero Trust pour le SGDD
"""
import time
import hmac
import hashlib
import json
import base64

class ZeroTrustSecurityEngine:
    def __init__(self):
        # Clé secrète maîtresse simulant le keystore centralisé (ex: HashiCorp Vault)
        self._cluster_secret = b"K3y_S3cur3_uR0m3d_2026_Cyb3r"
        
        # Signatures magiques (Magic Bytes) pour la validation stricte du type MIME
        self.MAGIC_BYTES = {
            b'%PDF-': 'application/pdf',
            b'\x89PNG\r\n\x1a\n': 'image/png',
            b'\xff\xd8\xff': 'image/jpeg'
        }

    def _generate_hmac(self, message: str) -> str:
        """Génère une signature cryptographique HMAC-SHA256."""
        return hmac.new(self._cluster_secret, message.encode('utf-8'), hashlib.sha256).hexdigest()

    def generate_token(self, source_service: str, target_service: str, user_role: str = "user") -> str:
        """
        Génère un jeton d'authentification inter-service éphémère (similaire à un JWT compact).
        Durée de validité stricte : 5 secondes pour éviter le rejeu.
        """
        header = {"alg": "HMAC-SHA256", "typ": "InterServiceToken"}
        payload = {
            "iss": source_service,
            "aud": target_service,
            "role": user_role,
            "exp": time.time() + 5.0,  # Validité de 5 secondes
            "iat": time.time()
        }
        
        # Encodage en Base64 URL-safe
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().strip("=")
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().strip("=")
        
        message_to_sign = f"{header_b64}.{payload_b64}"
        signature = self._generate_hmac(message_to_sign)
        
        return f"{message_to_sign}.{signature}"

    def verify_token(self, token: str, expected_audience: str) -> dict:
        """
        Vérification stricte à chaque étape (Zero Trust).
        Vérifie l'intégrité, la provenance, l'audience et l'expiration.
        """
        try:
            parts = token.split(".")
            if len(parts) != 3:
                raise ValueError("Format de jeton invalide.")
            
            header_b64, payload_b64, signature = parts
            
            # 1. Vérification de la signature (Anti-altération)
            expected_signature = self._generate_hmac(f"{header_b64}.{payload_b64}")
            if not hmac.compare_digest(signature, expected_signature):
                raise PermissionError("Signature du jeton falsifiée ou invalide.")
                
            # Décoder le payload
            # Réajustement du padding Base64 si nécessaire
            rem = len(payload_b64) % 4
            if rem > 0:
                payload_b64 += "=" * (4 - rem)
            
            payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode()).decode())
            
            # 2. Vérification de l'expiration
            if time.time() > payload["exp"]:
                raise TimeoutError("Le jeton inter-service a expiré.")
                
            # 3. Vérification de l'audience (Droits d'accès du composant cible)
            if payload["aud"] != expected_audience:
                raise PermissionError(f"Audience non autorisée. Attendu: {expected_audience}")
                
            return {"valid": True, "claims": payload}
            
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def validate_file_safety(self, file_bytes: bytes, declared_extension: str) -> dict:
        """
        Analyse de sécurité "By Design" des fichiers.
        Vérifie la taille maximale et inspecte les Magic Bytes pour bloquer le masquage d'extensions.
        """
        # 1. Protection DDoS : Limitation de la taille (ex: max 2 Mo pour la simulation)
        MAX_SIZE = 2 * 1024 * 1024  
        if len(file_bytes) > MAX_SIZE:
            return {"safe": False, "reason": f"Fichier trop volumineux ({len(file_bytes)} octets). Limite fixée à {MAX_SIZE} octets."}

        # 2. Inspection des Magic Bytes (Vérification du vrai type MIME)
        detected_mime = None
        for magic, mime in self.MAGIC_BYTES.items():
            if file_bytes.startswith(magic):
                detected_mime = mime
                break
        
        if not detected_mime:
            return {"safe": False, "reason": "Format de fichier non identifié ou potentiellement malveillant (Exécutable déguisé, script, etc.)."}

        # Cross-validation avec l'extension déclarée
        if declared_extension.lower() == "pdf" and detected_mime != "application/pdf":
            return {"safe": False, "reason": f"Incohérence critique : Extension déclarée 'pdf' mais signature réelle '{detected_mime}'."}
        if declared_extension.lower() in ["png", "jpg", "jpeg"] and "image" not in detected_mime:
            return {"safe": False, "reason": "Incohérence critique entre l'extension d'image déclarée et la signature binaire."}

        return {"safe": True, "mime": detected_mime, "sha256": hashlib.sha256(file_bytes).hexdigest()}