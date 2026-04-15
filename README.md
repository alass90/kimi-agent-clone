# 🤖 Kimi Agent Clone (Production-Ready Backend)

Ce projet est une reproduction fidèle à 100% de l'architecture et des capacités de l'agent **Kimi (modèle K2.5)** de Moonshot AI, basée sur une rétro-ingénierie complète. Il s'agit d'un backend d'agent IA autonome, prêt pour la production, capable d'utiliser des outils complexes, de gérer des sessions persistantes et d'exécuter du code dans des environnements isolés.

---

## 🚀 Fonctionnalités Clés

### 🛠️ Orchestration & Cognition
- **Prompt "OK Computer"** : Intégration du prompt système original de Kimi, incluant toutes les règles de comportement, de communication et d'utilisation des outils.
- **Injection Dynamique de Skills** : Chargement à la volée de fichiers `SKILL.md` (Word, PDF, Excel, Webapp, Slides, etc.) selon l'intention de l'utilisateur pour enrichir le contexte.
- **Multi-Mode** : Support des modes `base_chat` (conversationnel rapide) et `ok_computer` (agentique complet avec outils illimités).
- **Streaming & WebSocket** : Support natif du streaming de réponses via SSE et WebSocket pour une interface utilisateur réactive.

### 🧰 27 Outils Intégrés (Fidélité 100%)
- **Exécution de Code (IPython)** : Intégration de **E2B** pour un bac à sable cloud sécurisé, avec repli local sur un kernel Jupyter robuste.
- **Navigation Web (Playwright)** : Navigateur complet avec mode **stealth** (anti-détection), gestion des éléments interactifs par index, captures d'écran et recherche de texte.
- **Gestion de Fichiers** : Lecture, écriture et édition (avec garde "read-before-edit") dans un workspace persistant.
- **Génération de Médias** : Création d'images (DALL-E), de parole (TTS) et synthèse de sons (numpy/scipy).
- **Sources de Données** : Connecteurs pour Yahoo Finance, World Bank, arXiv et Google Scholar.
- **Productivité** : Gestionnaire de tâches (Todo) persistant, générateur de présentations (PPTX) et déploiement de sites statiques.

---

## 🏗️ Architecture du Projet

```text
kimi-clone/
├── agent/                  # Cœur de l'intelligence
│   ├── prompts.py          # Système de prompts (OK Computer)
│   └── orchestrator.py     # Boucle d'agent et gestion de sessions
├── tools/                  # Connectivité (Outils)
│   ├── registry.py         # Schémas JSON des 27 outils
│   └── executors.py        # Implémentations (E2B, Playwright, etc.)
├── config/                 # Configuration centralisée
│   └── settings.py         # Paramètres, modes et limites
├── workspace/              # Espace de travail persistant
│   ├── output/             # Résultats générés (images, PDF, etc.)
│   ├── upload/             # Fichiers téléchargés par l'utilisateur
│   └── deploy/             # Sites web déployés
├── skills/                 # Base de connaissances dynamique (SKILL.md)
├── static/                 # (À venir) Interface Frontend
├── server.py               # Serveur API FastAPI principal
├── Dockerfile              # Image de production (Playwright + FFmpeg)
└── docker-compose.yml      # Orchestration des conteneurs
```

---

## 🛠️ Installation & Démarrage

### Prérequis
- Docker & Docker Compose
- Clé API OpenAI
- Clé API E2B (Optionnel, pour le sandbox cloud)

### Lancement avec Docker (Recommandé)
1. Clonez le dépôt :
   ```bash
   git clone https://github.com/alass90/kimi-agent-internals.git
   cd kimi-agent-internals/kimi-clone
   ```
2. Configurez vos variables d'environnement dans un fichier `.env` :
   ```env
   OPENAI_API_KEY=votre_cle_ici
   E2B_API_KEY=votre_cle_e2b_ici
   ```
3. Démarrez le backend :
   ```bash
   docker-compose up -d
   ```
Le serveur sera accessible sur `http://localhost:8000`.

---

## 🧪 Tests
Pour valider le bon fonctionnement du backend et des outils (mockés) :
```bash
python3 test_backend.py
```

---

## 📜 Licence
Ce projet est destiné à des fins éducatives et de recherche sur les architectures d'agents IA. Les prompts et structures sont inspirés de l'agent Kimi de Moonshot AI.
