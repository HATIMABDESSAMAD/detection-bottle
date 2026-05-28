# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/),
et ce projet adhère au [Semantic Versioning](https://semver.org/).

---

## [1.0.0] - 2024-05-28

### ✨ Added (Ajouté)

#### Fonctionnalités principales
- ✅ **Système de détection unifié** : Combinaison de YOLOv8 et ResNet50v2
- ✅ **Détection multi-classe (YOLOv8)** :
  - Détection de bouteilles
  - Détection de bouchons (avec/sans)
  - Support du tracking en temps réel avec assignation d'IDs
  - Trajectoires visuelles des objets

- ✅ **Classification CNN (ResNet50v2)** :
  - Classification binaire : Remplie vs Vide
  - Lissage temporel sur 15 frames
  - Hystérésis pour stabilité
  - Pourcentage de remplissage

#### Interface & Contrôles
- ✅ Affichage simultané côte à côte (Détection + Classification)
- ✅ Contrôles clavier complets :
  - Pause/Reprendre (SPACE)
  - Enregistrement vidéo (R)
  - Captures d'écran (S)
  - Affichage de l'aide (H)
  - Trajets visuels (T)
  - Quitter (Q/ESC)

#### Logging & Données
- ✅ Sortie JSON temps réel : `data_logs/realtime_status.json`
- ✅ Sortie CSV historique : `data_logs/detection_unifie.csv`
- ✅ Métadonnées complètes : Timestamps, confiance, classes, IDs
- ✅ Sauvegarde automatique des détections

#### Optimisations
- ✅ Support GPU CUDA avec détection automatique
- ✅ Cache des frames pour performance
- ✅ Saut de frames configurable
- ✅ Optimisation mémoire des trajectoires

#### Intégration Hardware
- ✅ Communication Arduino via port série
- ✅ Détection automatique du port COM
- ✅ Protocole de communication configurable
- ✅ Contrôle de broyage avec timing

#### Formats & Vidéos
- ✅ Enregistrement vidéo MP4 (codec H.264)
- ✅ Captures PNG haute résolution
- ✅ Support désentrelacement vidéo
- ✅ Transposition d'image (rotation 90°)

#### Documentation
- ✅ README.md complet et détaillé
- ✅ Guide CONTRIBUTING.md
- ✅ Licence MIT
- ✅ CHANGELOG.md
- ✅ Docstrings en français et anglais
- ✅ Commentaires de code explicites

### 🔧 Technical Details

- **Python** : 3.8+
- **PyTorch** : 2.0+
- **TensorFlow/Keras** : 2.13+
- **OpenCV** : 4.8+
- **YOLOv8** : Ultralytics v8.0+
- **GPU Support** : CUDA 11.8+
- **Performance** : 28-35 FPS (GPU RTX 3070)

---

## Roadmap - Versions Futures

### [1.1.0] - Prévu

- [ ] Support multi-GPU
- [ ] Web Dashboard (Flask/Dash)
- [ ] Quantization et optimisation ONNX
- [ ] Amélioration des performances CPU
- [ ] Support caméra réseau (RTSP)
- [ ] Calibration automatique

### [2.0.0] - Long terme

- [ ] Support Android/iOS
- [ ] Application mobile native
- [ ] Reconnaissance d'étiquettes
- [ ] Traçabilité QR code
- [ ] API REST complète
- [ ] Cloud integration (AWS/Azure)

---

## Format des versions

Les releases suivent [Semantic Versioning](https://semver.org/) :

- **MAJOR** : Changements incompatibles (1.0.0 → 2.0.0)
- **MINOR** : Nouvelles fonctionnalités (1.0.0 → 1.1.0)
- **PATCH** : Corrections de bugs (1.0.0 → 1.0.1)

---

## Installation des versions

```bash
# Cloner la version actuelle
git clone https://github.com/HATIMABDESSAMAD/detection-bottle.git

# Cloner une version spécifique
git clone --branch v1.0.0 https://github.com/HATIMABDESSAMAD/detection-bottle.git

# Récupérer les tags
git fetch --tags
git checkout v1.0.0
```

---

## Notes de Développement

### Dépendances principales
- `ultralytics` : YOLOv8 framework
- `torch` : Deep learning PyTorch
- `tensorflow` : Keras CNN models
- `opencv-python` : Traitement d'images
- `pyserial` : Communication Arduino

### Améliorations apportées
- Optimisation du cache pour réduire la latence
- Lissage temporel amélioré avec hystérésis
- Tracking ID plus stable avec Byte-Track
- Performance GPU optimisée pour batches

---

## Contribution

Les contributions sont bienvenues ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Auteur

**HATIM ABDESSAMAD**

## Licence

MIT License - Voir [LICENSE](LICENSE)

---

**Dernière mise à jour : 2024-05-28**
