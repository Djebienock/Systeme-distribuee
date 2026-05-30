import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, UTC

logger = logging.getLogger("CyberSec_API")

@dataclass
class Document:
    id: int
    title: str
    author: str
    tags: list[str] = field(default_factory=list)
    classification: str = "internal"
    created_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat().replace("+00:00", "Z")
    )

def validate_document(data: dict) -> None:
    errors = []
    
    # 1. Vérification des champs obligatoires
    for field_name in ("id", "title", "author"):
        if field_name not in data:
            raise ValueError(f"Champ obligatoire manquant : {field_name}")

    # 2. Validation stricte de l'ID
    if not isinstance(data["id"], int) or isinstance(data["id"], bool):
        errors.append("'id' doit être un entier.")
    elif data["id"] <= 0:
        errors.append("'id' doit être un entier strictement positif.")

    # 3. Validation du titre (1-200 caractères)
    if not isinstance(data["title"], str):
        errors.append("'title' doit être une chaîne.")
    elif not (1 <= len(data["title"].strip()) <= 200):
        errors.append("'title' doit faire entre 1 et 200 caractères.")

    # 4. Validation de l'auteur (1-100 caractères)
    if not isinstance(data["author"], str):
        errors.append("'author' doit être une chaîne.")
    elif not (1 <= len(data["author"]) <= 100):
        errors.append("'author' doit faire entre 1 et 100 caractères.")

    # 5. Validation des tags (max 20 éléments, 1-50 caractères par tag)
    if "tags" in data:
        if not isinstance(data["tags"], list):
            errors.append("'tags' doit être une liste.")
        elif len(data["tags"]) > 20:
            errors.append("La liste 'tags' ne peut pas dépasser 20 éléments.")
        else:
            for i, tag in enumerate(data["tags"]):
                if not isinstance(tag, str) or not (1 <= len(tag) <= 50):
                    errors.append(f"Tag à l'index {i} invalide.")

    # 6. Validation de la classification (Allowlist)
    if "classification" in data:
        if data["classification"] not in {"public", "internal", "confidential", "secret"}:
            errors.append(f"Classification '{data['classification']}' non autorisée.")

    # 7. Validation de la date (Format ISO 8601 strict)
    if "created_at" in data:
        if not isinstance(data["created_at"], str):
            errors.append("'created_at' doit être une chaîne.")
        else:
            try:
                datetime.strptime(data["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                try:
                    datetime.strptime(data["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    pass

    if errors:
        raise ValueError(" | ".join(errors))

def deserialize_document_v2(raw_json: str, strict_unknown_fields: bool = True) -> Document:
    """Désérialiseur V2 avec gestion fail-closed et rétrocompatibilité V1"""
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError:
        logger.error("JSON mal formé syntaxiquement.")
        raise ValueError("Payload mal formé : syntaxe JSON invalide.")

    # Détection des attaques par Mass Assignment (Champs inconnus)
    champs_officiels = {"id", "title", "author", "tags", "classification", "created_at"}
    champs_inconnus = set(data.keys()) - champs_officiels

    if champs_inconnus and strict_unknown_fields:
        logger.warning(f"REJET : Tentative d'injection de champs inconnus : {champs_inconnus}")
        raise ValueError("Requête non conforme : présence de propriétés interdites.")

    # Validation du contenu
    try:
        validate_document(data)
    except ValueError as e:
        logger.warning(f"REJET - Violation des règles du contrat : {e}")
        raise ValueError("Requête non conforme aux exigences de sécurité du contrat de données.")

    return Document(
        id=data["id"],
        title=data["title"],
        author=data["author"],
        tags=data.get("tags", []),
        classification=data.get("classification", "internal"),
        created_at=data.get("created_at", datetime.now(UTC).isoformat().replace("+00:00", "Z")),
    )