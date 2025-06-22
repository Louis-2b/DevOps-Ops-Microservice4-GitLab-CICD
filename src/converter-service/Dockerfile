##############################################
# Étape 1 : build de l'application Spring boot
##############################################
# Construction de l'environnement de build
FROM python:3.11-slim AS builder

# Définir le répertoire de travail dans l'image
WORKDIR /app

# Copier le fichier requirements.txt pour installer les dépendances
COPY requirements.txt .

# Installer les dépendances dans un environnement virtuel
# Utilisation de --no-cache-dir pour réduire la taille de l'image
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt


################################
# Étape 2 : exécution de l'image
################################    
# Image finale légère
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier l'environnement virtuel depuis le builder
COPY --from=builder /app/venv /app/venv

# Copier le code source de l'application
COPY convert ./convert
COPY tests ./tests
COPY consumer.py .

# Définir les variables d'environnement
# Activer l'environnement virtuel pour les commandes
ENV PATH="/app/venv/bin:$PATH"

# Commande pour lancer l'application
CMD ["python", "consumer.py"]