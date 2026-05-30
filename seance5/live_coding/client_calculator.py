import Pyro5.api

def main():
    # Localiser le name server
    ns = Pyro5.api.locate_ns()

    # Récupérer l'URI du service par son nom logique
    uri = ns.lookup("example.calculator")

    # Créer le proxy — l'objet "local" qui représente le CalculatorService distant
    with Pyro5.api.Proxy(uri) as calc:
        result_add = calc.add(10, 5)       # → appel réseau transparent
        result_sub = calc.subtract(10, 3)  # → appel réseau transparent
        print(f"10 + 5 = {result_add}")
        print(f"10 - 3 = {result_sub}")


if __name__ == "__main__":
    main()
