# 📦 Guide de Déploiement et Push Git

Guide pas à pas pour pousser votre projet **Unified Bottle Detection System** à GitHub.

---

## ✅ Pré-requis

1. **Git installé** : [https://git-scm.com/download](https://git-scm.com/download)
2. **Compte GitHub** : [https://github.com/signup](https://github.com/signup)
3. **Repository GitHub créé** : `HATIMABDESSAMAD/detection-bottle`
4. **SSH ou HTTPS configuré** : Clé SSH ou token d'accès personnel

---

## 🚀 Étape 1 : Configuration Git Initiale (1ère fois seulement)

```bash
# Configurer votre identité Git (global)
git config --global user.name "HATIM ABDESSAMAD"
git config --global user.email "hatim.abdessamad@email.com"

# Optionnel : Configurer l'éditeur par défaut
git config --global core.editor "code"  # VS Code comme éditeur
```

---

## 📍 Étape 2 : Initialiser le Repository Local

Depuis le répertoire du projet :

```bash
cd "c:\Users\HATIM\Desktop\OD\A projet robotique\NOW\noow\gg\regroupement des 3 modeles\regroupement des 3 modeles"

# Initialiser Git (SI PAS DÉJÀ FAIT)
git init

# Vérifier l'état
git status
```

**Résultat attendu** : Les fichiers doivent être affichés en rouge (non stagés)

---

## 📝 Étape 3 : Ajouter les Fichiers

```bash
# Ajouter TOUS les fichiers
git add .

# OU : Ajouter sélectivement
git add README.md LICENSE CONTRIBUTING.md requirements.txt
git add unified_bottle_detection.py
git add .gitignore

# Vérifier les fichiers stagés
git status
```

**Résultat attendu** : Les fichiers doivent être en vert

---

## 💬 Étape 4 : Commit Initial

```bash
# Commit avec message descriptif
git commit -m "Initial commit: Unified Bottle Detection System v1.0

- Combined YOLOv8 detection model (bottle + caps)
- ResNet50v2 CNN classification model (filled/empty)
- Real-time detection and tracking
- Arduino serial communication
- Comprehensive documentation
- MIT License"
```

**Résultat attendu** : Message de succès avec nombre de fichiers changés

---

## 🔗 Étape 5 : Connecter au Repository GitHub

### Option A : Via HTTPS (Plus facile)

```bash
# Ajouter l'origin distant
git remote add origin https://github.com/HATIMABDESSAMAD/detection-bottle.git

# Vérifier la connexion
git remote -v
```

### Option B : Via SSH (Plus sécurisé)

```bash
# Ajouter l'origin distant avec SSH
git remote add origin git@github.com:HATIMABDESSAMAD/detection-bottle.git

# Vérifier la connexion
git remote -v
```

---

## 📤 Étape 6 : Premier Push

```bash
# Pousser vers la branche main
git branch -M main

# Push initial
git push -u origin main
```

**Note** : À la première utilisation :
- **HTTPS** : Entrez votre username + personal access token
- **SSH** : Confirmez la clé SSH si demandé

---

## ✨ Résultat Final

Votre repository GitHub devrait afficher :

```
✅ README.md          - Documentation complète
✅ LICENSE            - Licence MIT
✅ CONTRIBUTING.md    - Guide de contribution
✅ CHANGELOG.md       - Historique des versions
✅ requirements.txt   - Dépendances
✅ unified_bottle_detection.py - Script principal
✅ Et tous les autres fichiers importants
```

---

## 🔄 Commits Futurs

Pour les updates futures :

```bash
# Après modifications
git status

# Ajouter les changements
git add .

# Commit descriptif
git commit -m "feat(detection): improve tracking stability"

# Push
git push origin main
```

---

## 📊 Vérifier sur GitHub

1. Aller à : https://github.com/HATIMABDESSAMAD/detection-bottle
2. Vérifier que tous les fichiers sont présents
3. Lire le README pour confirmer le formatage
4. Vérifier les "Insights" > "Commits"

---

## 🆘 Troubleshooting

### ❌ Erreur: "fatal: remote origin already exists"
```bash
# Supprimer l'ancien remote
git remote remove origin

# Ajouter le nouveau
git remote add origin https://github.com/HATIMABDESSAMAD/detection-bottle.git
```

### ❌ Erreur: "Authentication failed"
```bash
# HTTPS : Utiliser un Personal Access Token
# https://github.com/settings/tokens

# SSH : Générer une clé
ssh-keygen -t ed25519 -C "hatim.abdessamad@email.com"
# Puis ajouter à GitHub Settings > SSH Keys
```

### ❌ Erreur: "Everything up-to-date"
```bash
# Vérifier le status
git log --oneline

# Si vous avez modifié des fichiers
git add .
git commit -m "Updated documentation"
git push origin main
```

### ❌ Fichiers volumineux rejetés
```bash
# Git LFS pour fichiers > 100MB
git lfs install
git lfs track "*.pt"
git lfs track "*.keras"
git add .gitattributes
git commit -m "Add Git LFS for large model files"
git push origin main
```

---

## 📋 Checklist Avant le Push

- [ ] Tous les fichiers nécessaires présents
- [ ] README.md complet et formaté
- [ ] LICENSE presente
- [ ] CONTRIBUTING.md explique comment contribuer
- [ ] .gitignore correctement configuré
- [ ] Aucun mot de passe ou clé API visible
- [ ] requirements.txt à jour
- [ ] Modèles (.pt, .keras) dans .gitignore
- [ ] Commit message descriptif

---

## 🎯 Bonnes Pratiques Git

### Messages de Commit
```bash
# ✅ BON
git commit -m "feat(detection): add confidence threshold adjustment

- Implement adjustable confidence levels
- Update UI with +/- keys
- Add documentation"

# ❌ MAUVAIS
git commit -m "update"
git commit -m "fix stuff"
```

### Branches
```bash
# Créer une branche pour une feature
git checkout -b feature/new-feature

# Faire les modifications
git add .
git commit -m "feat: add new feature"

# Merger vers main
git checkout main
git merge feature/new-feature
git push origin main
```

### Tags (Releases)
```bash
# Créer un tag pour v1.0.0
git tag -a v1.0.0 -m "Initial release"

# Pousser les tags
git push origin --tags
```

---

## 📚 Ressources Utiles

- 📖 [Git Documentation](https://git-scm.com/doc)
- 📖 [GitHub Guides](https://guides.github.com)
- 📖 [Conventional Commits](https://www.conventionalcommits.org)
- 📖 [GitHub Actions CI/CD](https://docs.github.com/en/actions)

---

## ✅ Prochaines Étapes

Après le premier push :

1. **Ajouter une CI/CD** : GitHub Actions pour tests automatiques
2. **Protéger la branche main** : Exiger les PR reviews
3. **Ajouter des badges** : Status de build, coverage, etc.
4. **Configurer GitHub Pages** : Documentation en ligne
5. **Publier sur PyPI** : Package officiel Python

```bash
# Exemple : Publier sur PyPI
pip install build twine
python -m build
twine upload dist/*
```

---

## 🎉 Félicitations !

Votre projet **Unified Bottle Detection System** est maintenant sur GitHub et prêt pour collaborer !

**Partagez le lien** : https://github.com/HATIMABDESSAMAD/detection-bottle

---

**Questions ?** Consultez les guides GitHub ou contactez un développeur senior.

