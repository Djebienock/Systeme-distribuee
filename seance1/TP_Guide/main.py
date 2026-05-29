# -*- coding: utf-8 -*-
"""
Module : main.py
Rôle : Démonstration pratique et validation des contrôles du Lab Sécurité
"""
import time
from services import APIGateway
from security_engine import ZeroTrustSecurityEngine

def run_security_lab_simulation():
    gateway = APIGateway()
    sec_engine = ZeroTrustSecurityEngine()
    
    # Préparation des charges de fichiers (Payloads)
    # Contenu légitime d'un PDF commmençant par ses octets magiques
    pdf_legitime = b"%PDF-1.7\n%Contenu confidentiel de l'internship..."
    
    # ATTAQUE 1 : Un script malveillant PHP déguisé en document PDF (Extension masquée)
    payload_malveillant = b"<?php echo system($_GET['cmd']); ?>" 
    
    # ATTAQUE 2 : Une attaque par déni de service (Bombe de données volumineuse)
    bombe_de_donnees = b"A" * (3 * 1024 * 1024) # 3 Mo (Limite fixée à 2 Mo)

    print("=" * 70)
    print("      LANCEMENT DES SCÉNARIOS DE TEST DU LAB SÉCURITÉ (ZERO TRUST)      ")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # CAS NOMINAL : Transmission parfaitement valide d'un document
    # -------------------------------------------------------------------------
    print("\n--- [SCÉNARIO 1 : CAS NOMINAL] ---")
    status_nominal = gateway.handle_user_upload(
        client_ip="10.20.30.45",
        filename="rapport_cybersec.pdf",
        file_bytes=pdf_legitime,
        user_role="student"
    )
    print(f"Résultat final de l'infrastructure : {status_nominal}")

    # -------------------------------------------------------------------------
    # MENACE B & M4 : Tentative d'injection d'un fichier déguisé (Extension Spoofing)
    # -------------------------------------------------------------------------
    print("\n--- [SCÉNARIO 2 : ATTAQUE D'EXTENSION MASQUÉE (Vecteur C / M4)] ---")
    status_attaque_extension = gateway.handle_user_upload(
        client_ip="192.168.1.100",
        filename="facture_falsifiee.pdf", # L'attaquant prétend que c'est un PDF
        file_bytes=payload_malveillant,    # Mais injecte du code PHP
        user_role="attacker"
    )
    print(f"Résultat final de l'infrastructure : {status_attaque_extension}")

    # -------------------------------------------------------------------------
    # MENACE B & M2 : Inondation par fichier trop volumineux (DDoS)
    # -------------------------------------------------------------------------
    print("\n--- [SCÉNARIO 3 : TENTATIVE DE SATURATION DE DISQUE / DDOS (M2)] ---")
    status_ddos = gateway.handle_user_upload(
        client_ip="172.16.5.8",
        filename="gros_fichier.pdf",
        file_bytes=bombe_de_donnees,
        user_role="user"
    )
    print(f"Résultat final de l'infrastructure : {status_ddos}")

    # -------------------------------------------------------------------------
    # MENACE C & M1 : Tentative de contournement (Contourner la Gateway)
    # -------------------------------------------------------------------------
    print("\n--- [SCÉNARIO 4 : REJET PAR LE STOCKAGE D'UN JETON ALTERÉ (Zero Trust)] ---")
    from services import StockageService
    storage_svc = StockageService()
    
    # L'attaquant essaie de forger lui-même un faux jeton ou d'altérer un jeton existant
    header_b64 = "eyJhbGciOiAiSE1BQy1TSEEyNTYiLCAidHlwIjogIkludGVyU2VydmljZVRva2VuIn0"
    payload_falsifie_b64 = "eyJpc3MiOiAiQVBJX0dhdGV3YXkiLCAiYXVkIjogIlN0b2NrYWdlX1NlcnZpY2UiLCAicm9sZSI6ICJhZG1pbiIsICJleHAiOiAyNTE0NjI4ODAwfQ" # Expire en l'an 2049
    token_falsifie = f"{header_b64}.{payload_falsifie_b64}.signature_invalide_ou_devinee"
    
    # Appel direct du service de stockage sans passer par la Gateway
    status_bypass = storage_svc.receive_and_store(
        token=token_falsifie,
        filename="document_pirate.pdf",
        file_bytes=pdf_legitime,
        file_hash="fake_hash_123"
    )
    print(f"Résultat final de l'infrastructure : {status_bypass}")
    print("\n" + "=" * 70)
    print("                    FIN DES SIMULATIONS DU LAB SÉCURITÉ                 ")
    print("=" * 70)

if __name__ == "__main__":
    run_security_lab_simulation()