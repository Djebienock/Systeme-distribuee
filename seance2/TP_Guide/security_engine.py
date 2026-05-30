import hmac
import hashlib
import time
import secrets

class SecurityEngine:
    """Moteur cryptographique et de sécurité du SGDD (Séance 6)"""
    
    SECRET_KEY = b"Fes_Euromed_Cyber_Secret_2026_Shared"
    
    # Signatures binaires standard (Magic Bytes) pour valider le type réel du fichier
    MAGIC_BYTES = {
        b"%PDF-": "PDF",
        b"\x89PNG\r\n\x1a\n": "PNG",
        b"\xff\xd8\xff": "JPEG",
        b"PK\x03\x04": "ZIP/DOCX"
    }

    @classmethod
    def generate_hmac_token(cls, service_name: str, file_hash: str, lifespan: float = 5.0) -> str:
        """Génère un jeton éphémère d'infrastructure signé par HMAC-SHA256"""
        expires_at = time.time() + lifespan
        payload = f"{service_name}:{file_hash}:{expires_at}"
        signature = hmac.new(cls.SECRET_KEY, payload.encode('utf-8'), hashlib.sha256).hexdigest()
        return f"{payload}:{signature}"

    @classmethod
    def verify_hmac_token(cls, token: str, expected_service: str, expected_hash: str) -> bool:
        """Vérifie l'intégrité, la provenance et l'expiration du jeton d'infrastructure"""
        try:
            parts = token.split(":")
            if len(parts) != 4:
                return False
            
            service_name, file_hash, expires_at_str, signature = parts
            expires_at = float(expires_at_str)
            
            # 1. Vérification temporelle (Anti-Replay / Expiration)
            if time.time() > expires_at:
                print("   [SecurityEngine] ❌ Jeton rejeté : Expiré !")
                return False
                
            # 2. Vérification du contexte d'usage
            if service_name != expected_service or file_hash != expected_hash:
                print("   [SecurityEngine] ❌ Jeton rejeté : Mauvais contexte de service/hash !")
                return False
            
            # 3. Vérification de l'intégrité cryptographique
            reconstructed_payload = f"{service_name}:{file_hash}:{expires_at_str}"
            expected_signature = hmac.new(cls.SECRET_KEY, reconstructed_payload.encode('utf-8'), hashlib.sha256).hexdigest()
            
            # Utilisation de compare_digest pour éviter les attaques par canaux cachés (timing attacks)
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception:
            return False

    @classmethod
    def inspect_magic_bytes(cls, content: bytes) -> str:
        """Contre-mesure Cyber : inspecte le contenu binaire réel au lieu de se fier à l'extension"""
        for signature, file_type in cls.MAGIC_BYTES.items():
            if content.startswith(signature):
                return file_type
        return "UNKNOWN_OR_MALICIOUS"

    @classmethod
    def calculate_sha256(cls, content: bytes) -> str:
        """Calcule l'empreinte unique du document pour en garantir l'intégrité"""
        return hashlib.sha256(content).hexdigest()

    @classmethod
    def inject_jitter(cls, base_delay: float) -> float:
        """Ajoute un bruit aléatoire (Jitter) au délai pour éviter le phénomène de Retry Storm"""
        # Full Jitter : Aléa entre 0 et base_delay
        return secrets.SystemRandom().uniform(0, base_delay)