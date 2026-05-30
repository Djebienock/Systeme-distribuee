import json
import logging
import sys

# Importation de nos propres fichiers découpés
from models import deserialize_document_v2
from security_lab import simulate_threat_modeling_lab

# Importation du fichier généré par protoc
try:
    import document_pb2
except ImportError:
    print("Erreur : Le fichier 'document_pb2.py' est introuvable. Veuillez compiler 'document.proto' d'abord.")
    sys.exit(1)

# Configuration des logs applicatifs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

if __name__ == "__main__":
    print("\n=== [1] EXECUTION DES TEST CASES (TP 7.1 & 7.2) ===")

    tests = {
        "1. Valide Complet (V2)": '{"id": 42, "title": "Rapport Annuel Q1", "author": "Alice", "tags": ["cyber"], "classification": "confidential"}',
        "2. Valide Minimal (Rétrocompatibilité V1)": '{"id": 101, "title": "Note Interne", "author": "Bob"}',
        "3. INVALIDE (Champ requis manquant)": '{"id": 102, "author": "Bob Martin"}',
        "4. INVALIDE (Type incorrect)": '{"id": "id-invalide", "title": "Titre", "author": "Alice"}',
        "5. INVALIDE (Attaque Mass Assignment / Champ inconnu)": '{"id": 5, "title": "Titre", "author": "Eve", "priority": "high"}',
    }

    for nom, payload in tests.items():
        print(f"\n--> Test : {nom}")
        try:
            doc = deserialize_document_v2(payload, strict_unknown_fields=True)
            print(f"    [SUCCÈS] Objet instancié : {doc}")
        except ValueError as client_err:
            print(f"    [REJET CLIENT] Message renvoyé : {client_err}")

    print("\n=== [2] COMPARATIF PERFORMANCE JSON vs PROTOBUF (TP 7.3) ===")

    data_dict = {
        "id": 1450,
        "title": "Rapport d'évaluation de l'infrastructure Cloud Securisee - Version Finale",
        "author": "Département Cyber-Sécurité Globale",
        "tags": ["cloud", "security", "audit", "infrastructure", "2026", "production"],
        "classification": "confidential",
    }

    # Sérialisation textuelle JSON
    json_bytes = json.dumps(data_dict).encode("utf-8")

    # Sérialisation binaire Protobuf
    proto_doc = document_pb2.DocumentProto()
    proto_doc.id = data_dict["id"]
    proto_doc.title = data_dict["title"]
    proto_doc.author = data_dict["author"]
    proto_doc.tags.extend(data_dict["tags"])
    proto_doc.classification = data_dict["classification"]

    protobuf_bytes = proto_doc.SerializeToString()

    print(f"Taille du message en JSON     : {len(json_bytes)} octets")
    print(f"Taille du message en Protobuf : {len(protobuf_bytes)} octets")
    gain = round((1 - len(protobuf_bytes) / len(json_bytes)) * 100, 2)
    print(f"-> Protobuf est {gain}% plus léger que le JSON sur ce message.")
    
    # Exécution du Lab Sécurité
    simulate_threat_modeling_lab()