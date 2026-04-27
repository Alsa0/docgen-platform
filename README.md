# DocGen Platform

Une plateforme complète de génération de documents d'entreprise propulsée par l'IA Claude d'Anthropic. Conçue spécialement pour les professionnels de l'ingénierie IT et Télécom.

## 📋 Présentation des 5 types de documents

La plateforme permet de générer 5 types de documents professionnels au format DOCX :

1. **BOM (Bill of Materials)** : Liste détaillée des équipements avec recherche automatique des prix du marché via l'IA.
2. **SOW (Scope of Work)** : Définition précise du périmètre du projet, des tâches, des jalons et des livrables.
3. **OT (Offre Technique)** : Proposition commerciale complète incluant méthodologie, planning et annexes.
4. **IR (Rapport d'Intervention)** : Compte-rendu terrain avec analyse des problèmes et recommandations IA.
5. **LLD (Low Level Design)** : Document technique d'architecture détaillé exploitant la recherche web pour les spécifications techniques.

## 🛠️ Prérequis et Installation

- **Backend** : Python 3.10+
- **Frontend** : Node.js 18+
- (Optionnel) **Docker** et Docker Compose

### Option 1 : Installation avec Docker (Recommandée)

1. Clonez le dépôt
2. Configurez les variables d'environnement
3. Lancez le projet :
```bash
docker-compose up -d --build
```
L'application sera disponible sur `http://localhost:5173`.

### Option 2 : Installation manuelle

#### Backend
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Éditez le fichier .env avec vos clés API
uvicorn main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🔑 Configuration des clés API

Le fichier `backend/.env` nécessite :
- `ANTHROPIC_API_KEY` : Clé API pour l'accès à Claude (modèle *claude-opus-4-6*).
- `TAVILY_API_KEY` : Clé API optionnelle si web_search d'Anthropic requiert un provider externe.

## 🚀 Guide d'utilisation

1. Accédez à l'interface via votre navigateur.
2. Sélectionnez le type de document à générer depuis le tableau de bord.
3. Remplissez le formulaire de configuration.
4. **Pour les BOM et LLD** : Utilisez la fonction de recherche web pour trouver des équipements réels ou des datasheets.
5. Cochez l'option d'utilisation de l'IA (activée par défaut).
6. Cliquez sur "Générer le Document DOCX". Le téléchargement démarrera automatiquement.

## ➕ Ajouter un nouveau type de document

L'architecture est pensée pour être facilement extensible :
1. Créez un nouveau fichier `backend/templates/mon_doc.json` avec la définition des champs.
2. Ajoutez la fonction de génération de contenu IA dans `backend/services/ai_service.py`.
3. Ajoutez la fonction de formatage DOCX dans `backend/services/doc_generator.py`.
4. Ajoutez la route correspondante dans `backend/routes/documents.py`.
5. Côté frontend, ajoutez la carte sur `Home.jsx` et créez la page `GenerateMonDoc.jsx`.

## 🏗️ Architecture Technique

- **Backend** : FastAPI (Python) offre des performances élevées et gère les requêtes asynchrones vers l'API Claude. La génération de documents s'appuie sur `python-docx` pour un formatage professionnel précis.
- **Frontend** : React propulsé par Vite pour une expérience utilisateur rapide et fluide. Le design utilise une approche Glassmorphism premium sans framework CSS externe.
- **IA** : L'intégration Anthropic exploite la fonctionnalité native `web_search_20250305` pour enrichir les documents avec des données réelles du web (prix actuels, fiches techniques constructeurs).
