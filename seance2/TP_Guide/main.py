import time
from services import APIGateway, StockageService
from security_engine import SecurityEngine

class ResilientClient:
    """Client applicatif intégrant des politiques de résilience réseau (Timeout & Backoff Exponentiel)"""
    
    def __init__(self, gateway: APIGateway, stockage: StockageService):
        self.gateway = gateway
        self.stockage = stockage

    def send_document_with_retry(self, client_ip: str, filename: str, content: bytes, max_retries: int = 3) -> None:
        """Exécute la requête d'upload en appliquant une stratégie de reprise robuste"""
        base_delay = 1.0  # Délai initial en secondes
        
        for attempt in range(max_retries + 1):
            try:
                # Émulation d'une exécution de requête avec Timeout applicatif
                # Dans une simulation locale, on appelle directement la méthode
                status_code, response = self.gateway.receive_document_upload(client_ip, filename, content, self.stockage)
                
                if status_code in [200, 201]:
                    print(f"[Client] 🎉 Succès au bout de {attempt} retry(ies) ! Réponse ({status_code}): {response}")
                    return
                elif status_code == 429:
                    # Erreur transitoire de Rate Limit : nécessite un retrait temporaire
                    if attempt == max_retries:
                        print(f"[Client] ❌ Échec critique (429 Too Many Requests) après {attempt} tentatives.")
                        return
                    
                    # Formule du Backoff Exponentiel agrémentée de son Jitter cryptographique
                    calculated_delay = base_delay * (2 ** attempt)
                    final_backoff = SecurityEngine.inject_jitter(calculated_delay)
                    print(f"[Client] ⚠️ Rate limit détecté (429). Retrying dans {final_backoff:.2f}s (Backoff Exponentiel)...")
                    time.sleep(final_backoff)
                else:
                    print(f"[Client] ❌ Erreur définitive ({status_code}) retournée par le serveur : {response}")
                    return
                    
            except Exception as e:
                print(f"[Client] 💥 Erreur réseau fatale détectée : {e}")
                if attempt == max_retries:
                    print("[Client] 🚨 Seuil maximal de tentatives épuisé. Abandon de la transaction.")
                    return


# =====================================================================
# LAB DE SIMULATION & SCÉNARIOS CYBERSEC (90 min)
# =====================================================================
def run_advanced_distributed_lab():
    print("=======================================================================")
    print("🔬 DÉMARRAGE DU LAB : SYSTÈME DE GESTION DOCUMENTAIRE DISTRIBUÉ (SGDD)")
    print("=======================================================================")
    
    # Instanciation de notre topologie réseau
    gateway = APIGateway(max_size_bytes=2 * 1024 * 1024, max_requests_per_min=3)
    stockage = StockageService()
    client = ResilientClient(gateway, stockage)

    # Définition de faux payloads binaires pour les tests
    vrai_pdf_content = b"%PDF-1.7 Document Academique Confidentiel Euromed Fes"
    faux_pdf_malicieux = b"<?php system($_GET['cmd']); ?> Code Malveillant PHP Camoufle"
    gros_fichier_content = b"%PDF-" + b"0" * (3 * 1024 * 1024) # 3 Mo (dépasse la limite de 2 Mo)

    print("\n🟢 [SCÉNARIO 1 : CAS NOMINAL]")
    client.send_document_with_retry("192.168.1.50", "rapport_stage.pdf", vrai_pdf_content)

    print("\n🟡 [SCÉNARIO 2 : PROTECTION CONTRE L'IDEMPOTENCE / REQUÊTES DUPLIQUÉES]")
    print("[Client] Envoi d'une copie identique du même document suite à un faux timeout...")
    client.send_document_with_retry("192.168.1.50", "rapport_stage.pdf", vrai_pdf_content)

    print("\n🔴 [SCÉNARIO 3 : CYBER-ATTAQUE - EXTENSION MASQUÉE / FALSIFICATION]")
    print("[Attaquant] Tente d'envoyer un script PHP renommé frauduleusement en '.pdf'")
    client.send_document_with_retry("203.0.113.5", "shell.pdf", faux_pdf_malicieux)

    print("\n🔴 [SCÉNARIO 4 : EXPLOITATION - DÉPASSEMENT DES CAPACITÉS (Taille)]")
    print("[Client] Tente d'uploader un fichier CAO volumineux de 3 Mo...")
    client.send_document_with_retry("192.168.1.55", "plan_batiment.pdf", gros_fichier_content)

    print("\n🚨 [SCÉNARIO 5 : CYBER-ATTAQUE - BYPASS DE LA GATEWAY (ZERO TRUST)]")
    print("[Attaquant] Tente d'attaquer directement le Stockage Service interne en forgeant un faux token...")
    fake_token = "StockageService:hash_inconnu:9999999999:mauvaise_signature_cryptographique"
    status, resp = stockage.persist_document("attaque_directe.pdf", vrai_pdf_content, "hash_inconnu", fake_token)
    print(f"[Stockage Interne] Résultat du blocage direct ({status}): {resp}")

    print("\n⏳ [SCÉNARIO 6 : RÉSILIENCE - DÉCLENCHEMENT DU RATE LIMITING & RETRIES]")
    print("[Client] Envoi de requêtes successives et rapprochées pour saturer le quota...")
    for i in range(3):
        client.send_document_with_retry("172.16.4.12", f"note_frais_{i}.pdf", vrai_pdf_content)


if __name__ == "__main__":
    run_advanced_distributed_lab()