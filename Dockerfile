# Dockerfile pour déploiement
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les requirements et installer les dépendances
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Exposer le port
EXPOSE 5050

# Commande de démarrage
CMD ["gunicorn", "backend.main:app", "--bind", "0.0.0.0:5050", "--workers", "2"]
