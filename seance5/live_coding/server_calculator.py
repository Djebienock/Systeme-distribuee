import Pyro5.api

@Pyro5.api.expose          # Rend les méthodes accessibles à distance
class CalculatorService:
    """Service de calcul exposé comme objet distant."""

    def add(self, a: float, b: float) -> float:
        # Valider les types — ne jamais faire confiance au client
        if not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
            raise ValueError("Les arguments doivent être des nombres")
        return a + b

    def subtract(self, a: float, b: float) -> float:
        if not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
            raise ValueError("Les arguments doivent être des nombres")
        return a - b

    def _internal_reset(self):
        # Méthode INTERNE — PAS de @expose ici = non accessible à distance
        pass


def main():
    # Créer le daemon (serveur d'objets)
    with Pyro5.api.Daemon() as daemon:
        # Localiser le name server
        ns = Pyro5.api.locate_ns()

        # Enregistrer l'objet dans le daemon → obtenir son URI unique
        uri = daemon.register(CalculatorService)

        # Publier l'URI dans le name server sous un nom logique
        ns.register("example.calculator", uri)

        print(f"CalculatorService prêt. URI: {uri}")
        daemon.requestLoop()    # Boucle d'attente infinie (Ctrl+C pour arrêter)


if __name__ == "__main__":
    main()