## 🗺️ 1. Architecture Globale du Système

Le système est découpé en plusieurs microservices autonomes qui collaborent de manière sécurisée pour réceptionner, analyser, stocker et indexer les documents académiques ou professionnels.

### Diagramme de Flux et Spécifications Réseau

```text
               ==================================================
               |              UTILISATEUR / CLIENT              |
               ==================================================
                                       |
                                       | HTTP/HTTPS (Port 443)
                                       v
               ==================================================
               |           API GATEWAY (Port 8080)              |
               ==================================================
                 /                     |                    \
  HTTP (Port 8081) /                      | HTTP (Port 8082)   \ gRPC (Port 50051)
               /                       v                    \
+-----------------------+   +-----------------------+   +-----------------------+
|     AUTH SERVICE      |   |   STOCKAGE SERVICE    |   |   RECHERCHE SERVICE   |
+-----------------------+   +-----------------------+   +-----------------------+
|  Moteur : FastAPI     |   |  Moteur : Flask/Python|   |  Moteur : Python-gRPC |
|  Stockage : Redis JWT |   |  Stockage : PostgreSQL|   |  Stockage : ElasSearch|
+-----------------------+   +-----------------------+   +-----------------------+
                                       |                             ^
                                       | Notification Événement      |
                                       +=============================+
                                            Pub/Sub / Async Worker
