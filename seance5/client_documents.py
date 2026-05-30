import Pyro5.api
import sys

def main():
    print(" === Client de Consultation de Documents SecureBank ===")
    try:
        # 1. Localiser l'annuaire explicitement sur 127.0.0.1
        ns = Pyro5.api.locate_ns(host="127.0.0.1")
        
        # 2. Rechercher le NOM EXACT enregistré par le serveur durci
        uri = ns.lookup("securebank.hardened.documents")
        
        # 3. Création du Proxy
        service = Pyro5.api.Proxy(uri)
        
        # 4. Appel de la méthode avec le bon jeton d'authentification et une clé valide
        token_valide = "BankToken_Production_2026!"
        print("\n[+] Tentative de lecture sécurisée du document 'doc_a'...")
        resultat = service.get_secure_document(token_valide, "doc_a")
        print(f" -> Réponse du serveur :\n {resultat}")
        
    except Pyro5.errors.NamingError as ne:
        print(f"[-] Erreur Pyro5 : Impossible de trouver l'annuaire ou le nom spécifié. Détails : {ne}")
    except Exception as e:
        print(f"[-] Erreur interceptée : {e}")

if __name__ == "__main__":
    main()