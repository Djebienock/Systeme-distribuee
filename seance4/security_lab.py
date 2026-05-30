import hmac
import hashlib
import json

SECRET_KEY = b"Cl3_S3cr3t3_D_An4lys3_123!"

def verify_and_load_data(payload: str, signature: str) -> dict:
    """Contremesure Threat Modeling : Validation d'intégrité via HMAC avant désérialisation"""
    expected_signature = hmac.new(SECRET_KEY, payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_signature, signature):
        raise PermissionError("STRATÉGIE THREAT MODELING [BLOQUÉE] : Signature invalide ! Payload altéré en transit.")
    return json.loads(payload)

def simulate_threat_modeling_lab():
    print("\n=== [3] LAB SÉCURITÉ (30 MIN) — THREAT MODELING SÉRIALISATION ===")

    # --- MENACE 1 : Injection d'objet dynamique (RCE) ---
    print("\n--> Menace 1 : Injection d'objet dynamique (Ex: patron de type YAML Unsafe / Pickle)")
    payload_malveillant_yaml = "!!python/object/apply:os.system ['echo EXPLOTATION_REUSSIE_RCE']"
    print(f"    Payload intercepté : {payload_malveillant_yaml}")
    print("    [CONTRE-MESURE ACTIVED] : Utilisation exclusive de formats de données inertes (JSON/Protobuf).")
    print("    Résultat : Le parseur refuse intrinsèquement d'interpréter les instructions d'exécution d'objets.")

    # --- MENACE 2 : Déni de service par saturation mémoire (Bombe JSON) ---
    print("\n--> Menace 2 : Déni de Service (DoS via Bombe d'imbrication récursive)")
    bombe_json = "{" + '"a":'*1000 + '"fin"' + "}"*1000
    
    MAX_PAYLOAD_SIZE = 5000  # Limite stricte à 5 Ko
    taille_bombe = len(bombe_json.encode('utf-8'))
    print(f"    Taille du payload reçu : {taille_bombe} octets (Seuil max autorisé : {MAX_PAYLOAD_SIZE} octets)")
    
    if taille_bombe > MAX_PAYLOAD_SIZE:
        print("    [SÉCURITÉ ACTIVED] STRATÉGIE THREAT MODELING [BLOQUÉE] : Payload trop volumineux en amont du parsing. Évitement du DoS.")
    else:
        json.loads(bombe_json)

    # --- MENACE 3 : Falsification de données (Data Tampering) ---
    print("\n--> Menace 3 : Altération de données métier (Modification de la classification en transit)")
    payload_original = '{"id": 99, "title": "Fichier Public", "classification": "public"}'
    payload_modifie  = '{"id": 99, "title": "Fichier Public", "classification": "secret"}'
    
    sig_legitime = hmac.new(SECRET_KEY, payload_original.encode(), hashlib.sha256).hexdigest()
    
    print(f"    Payload d'origine : {payload_original}")
    print(f"    Payload modifié par l'attaquant : {payload_modifie}")
    
    try:
        verify_and_load_data(payload_modifie, sig_legitime)
    except PermissionError as crypto_err:
        print(f"    [SÉCURITÉ ACTIVED] {crypto_err}")