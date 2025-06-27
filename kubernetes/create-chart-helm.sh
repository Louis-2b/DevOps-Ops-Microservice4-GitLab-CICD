#!/bin/bash

## Script simple pour créer un chart Helm

set -e  # Arrêt du script en cas d'erreur

echo "Début de la création du chart Helm..."

# Vérification de Helm
if ! command -v helm >/dev/null 2>&1; then
    echo "Helm n'est pas installé. Veuillez l'installer."
    exit 1
fi

echo "Helm trouvé : $(helm version --short)"

# Nom du chart
CHART_NAME="tubie-ops"
CHART_DIR="./$CHART_NAME"
TEMPLATES_DIR="$CHART_DIR/templates"
CHARTS_DIR="$CHART_DIR/charts"

# Créer le chart
echo "Création du chart Helm '$CHART_NAME'..."
helm create "$CHART_NAME"

# Supprimer le dossier charts/ s'il existe
if [ -d "$CHARTS_DIR" ]; then
    echo "Suppression du dossier charts/ inutile..."
    rm -rf "$CHARTS_DIR"
fi

# Nettoyage des templates
if [ -d "$TEMPLATES_DIR" ]; then
    echo "Suppression des fichiers inutiles..."
    rm -rf "$TEMPLATES_DIR/tests" 2>/dev/null
    rm -f "$TEMPLATES_DIR/NOTES.txt" 2>/dev/null
    rm -f "$TEMPLATES_DIR/serviceaccount.yaml" 2>/dev/null
    rm -f "$TEMPLATES_DIR/deployment.yaml" 2>/dev/null
    rm -f "$TEMPLATES_DIR/service.yaml" 2>/dev/null
    rm -f "$TEMPLATES_DIR/hpa.yaml" 2>/dev/null
    rm -f "$TEMPLATES_DIR/ingress.yaml" 2>/dev/null
else
    echo "⚠️ Dossier templates introuvable dans $TEMPLATES_DIR"
    exit 1
fi

# Vider le fichier values.yaml
: > "$CHART_DIR/values.yaml"

echo ""
echo "✅ Chart '$CHART_NAME' créé avec succès !"
echo "📁 Vous pouvez maintenant éditer les fichiers dans '$CHART_DIR'"