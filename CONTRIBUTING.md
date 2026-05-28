# Guide de Contribution

Merci d'avoir l'intérêt de contribuer à **Unified Bottle Detection System** ! 🎉

Ce document fournit les directives et instructions pour contribuer au projet.

## 🚀 Comment Commencer

### 1. Fork et Clone
```bash
# Fork le repository depuis GitHub

# Clone votre fork
git clone https://github.com/VOTRE_USERNAME/detection-bottle.git
cd detection-bottle

# Ajouter le repo upstream
git remote add upstream https://github.com/HATIMABDESSAMAD/detection-bottle.git
```

### 2. Créer une branche feature
```bash
# Mettre à jour main
git fetch upstream
git checkout main
git merge upstream/main

# Créer votre branche
git checkout -b feature/ma-fonctionnalite
```

### 3. Développer et Tester
```bash
# Installer les dépendances
pip install -r regroupement\ des\ 3\ modeles/requirements.txt

# Faire vos modifications
# Tester localement
cd regroupement\ des\ 3\ modeles
python unified_bottle_detection.py --help
```

### 4. Commit et Push
```bash
# Commit avec un message descriptif
git commit -m "Add: Description claire de la fonctionnalité"

# Push vers votre fork
git push origin feature/ma-fonctionnalite
```

### 5. Pull Request
- Ouvrir une PR depuis votre fork vers le repo principal
- Fournir une description détaillée des changements
- Lier les issues pertinentes

---

## 📝 Convention de Commit

Utiliser le format **Conventional Commits** :

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types autorisés:
- **feat**: Nouvelle fonctionnalité
- **fix**: Correction de bug
- **docs**: Modifications documentation
- **style**: Formatage, pas de changement logique
- **refactor**: Restructuration sans changement fonctionnel
- **perf**: Amélioration performance
- **test**: Ajout/modification tests
- **chore**: Autres changements (dépendances, config)

### Exemples:
```bash
git commit -m "feat(detection): add confidence threshold adjustment"
git commit -m "fix(tracking): resolve ID reassignment on occlusion"
git commit -m "docs(readme): add Arduino integration section"
git commit -m "perf(inference): optimize memory usage for CNN"
```

---

## 💻 Style de Code

### Python
- Suivre [PEP 8](https://pep8.org/)
- Utiliser **4 espaces** pour l'indentation
- Noms de variables/functions en `snake_case`
- Noms de classes en `PascalCase`
- Ajouter des **docstrings** pour les fonctions publiques

### Exemple:
```python
def calculate_fill_percentage(bottle_mask, water_mask):
    """
    Calculate the water fill percentage of a bottle.
    
    Args:
        bottle_mask (np.ndarray): Binary mask of bottle region
        water_mask (np.ndarray): Binary mask of water region
    
    Returns:
        float: Percentage (0-100) of bottle filled
    
    Raises:
        ValueError: If masks have different shapes
    """
    if bottle_mask.shape != water_mask.shape:
        raise ValueError("Masks must have the same shape")
    
    bottle_area = np.count_nonzero(bottle_mask)
    water_area = np.count_nonzero(water_mask)
    
    if bottle_area == 0:
        return 0.0
    
    percentage = (water_area / bottle_area) * 100
    return min(percentage, 100.0)
```

---

## 🧪 Tests

Écrire des tests pour les nouvelles fonctionnalités :

```python
# tests/test_detection.py
import pytest
from unified_bottle_detection import UnifiedBottleDetection

def test_model_initialization():
    """Test que les modèles se chargent correctement"""
    system = UnifiedBottleDetection()
    assert system.model_detection is not None
    assert system.model_segmentation is not None
```

---

## 📖 Documentation

Mettre à jour la documentation pertinente :

1. **README.md** : Pour les utilisateurs finaux
2. **Code comments** : Pour les développeurs
3. **Docstrings** : Pour l'API
4. **CHANGELOG.md** : Pour l'historique des versions

---

## 📚 Bonnes Pratiques

### Git
```bash
# ❌ MAUVAIS
git commit -m "updates"

# ✅ BON
git commit -m "feat(tracking): improve ID stability with IOU threshold"
```

### Code
```python
# ❌ MAUVAIS
def process(img):
    # ... 200 lignes ...
    return result

# ✅ BON
def process_image(image):
    """Process image through detection pipeline."""
    detections = detect_objects(image)
    classifications = classify_detections(detections)
    return merge_results(detections, classifications)
```

---

## 📞 Support

- 🐛 **Bugs**: [Issues GitHub](https://github.com/HATIMABDESSAMAD/detection-bottle/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/HATIMABDESSAMAD/detection-bottle/discussions)
- 📧 **Email**: hatim.abdessamad@email.com

---

## ✨ Merci!

Votre contribution rend ce projet meilleur pour tous! 🌟

**Happy Coding!** 🚀
