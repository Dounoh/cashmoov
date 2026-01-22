# API CashMoov – Assistant IA et Humain

## Présentation
L’API CashMoov fournit un système d’assistance hybride combinant intelligence artificielle
et support humain pour améliorer l’expérience client de la plateforme CashMoov.

## Fonctionnalités
- Authentification et gestion des utilisateurs
- Assistant conversationnel intelligent
- Transfert automatique vers un conseiller humain
- Historique des conversations
- Gestion des feedbacks utilisateur
- Conversion de money

## Technologies
- Django & Django REST Framework
- Djoser
- PostgreSQL
- pgvector (recherche vectorielle)
- E5-base (embeddings multilingues)
- Redis (WebSocket / Django Channels)
- Celery

---

## Démarrage de l’application (Docker)

### Prérequis
- Docker
- Docker Compose

### Lancer les services

Démarrer l’application Django :
docker compose up django

Démarrer la base de données PostgreSQL :
docker compose up postgres

Démarrer le worker Celery :
docker compose up celery

---

## Initialisation de la base de données

### Création des migrations
docker compose run --rm django python manage.py makemigrations

### Application des migrations
docker compose run --rm django python manage.py migrate

---

## Création du super administrateur
docker compose run --rm django python manage.py createsuperuser

---

## WebSocket – Chat temps réel

Endpoint :
ws://localhost:8000/ws/chat/group/

Permet une discussion temps réel entre le client et :
- l’assistant IA
- ou un assistant humain

### Exemple de message client
{
    "type": "chat.message",
    "username": "client",
    "groupe_name": "room1",
    "message": "Comment recharger mon compte CashMoov ?",
    "user_type": "customer"
}

### Réponse IA
{
    "type": "ia.message",
    "username": "CashMoov IA",
    "groupe_name": "Nom du groupe",
    "message": "Pour recharger,",
    "user_type": "ia"
}

### Réponse assistant humain
{
    "type": "chat.message",
    "username": "assistant nom",
    "groupe_name": "nom group",
    "message": "reponse a la question",
    "user_type": "assistant"
}

---

## Logique de support
1. L’IA répond automatiquement si une réponse fiable est trouvée
2. En cas d’incertitude, la demande est transférée à un assistant humain
3. Si aucun assistant n’est disponible, l’utilisateur est notifié
