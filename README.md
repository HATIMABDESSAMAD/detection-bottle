# 🍶 Unified Bottle Detection System

**Système intelligent de détection et classification de bouteilles en temps réel combinant YOLOv8 et ResNet50v2**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-red)](https://pytorch.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.13%2B-orange)](https://tensorflow.org)
[![YOLO](https://img.shields.io/badge/YOLO-v8-important)](https://docs.ultralytics.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table des matières

- [Description](#description)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Commandes Clavier](#commandes-clavier)
- [Structure du Projet](#structure-du-projet)
- [Configuration](#configuration)
- [Logging et Données](#logging-et-données)
- [Communication Arduino](#communication-arduino)
- [Performances](#performances)
- [Troubleshooting](#troubleshooting)
- [Contribution](#contribution)
- [Licence](#licence)

---

## 🎯 Description

Ce projet fournit une solution **complète et modulaire** pour la détection, le suivi et la classification de bouteilles en temps réel. Il combine intelligemment deux modèles de deep learning pour une analyse précise :

### 📌 Cas d'usage
- ✅ Systèmes d'automatisation industrielle
- ✅ Contrôle qualité en usine
- ✅ Gestion d'inventaire
- ✅ Systèmes robotiques
- ✅ Application de tri et recyclage

---

## ✨ Fonctionnalités

### 🔍 **Modèle 1 : Détection en Temps Réel (YOLOv8)**
- **Détection multi-classe** : Bouteille, Avec Bouchon, Sans Bouchon
- **Bounding Boxes** : Localisation précise des objets
- **Suivi des objets (Tracking)** : Assignation d'ID unique à chaque objet
- **Trajectoires** : Affichage des trails de mouvement
- **Performance GPU** : Utilisation CUDA pour accélération (640x640 inference)

### 🧠 **Modèle 2 : Classification du Remplissage (ResNet50v2 CNN)**
- **Classification binaire** : Remplie vs Vide
- **Précision CNN** : Architecture ResNet50v2 pré-entraînée
- **Lissage temporel** : Hystérésis sur 15 frames pour stabilité
- **Taille optimisée** : 224x224 pour inférence rapide

### 🎮 **Interface et Contrôles**
- **Affichage simultané** : Deux modèles côte à côte
- **Mode pause** : Arrêter l'analyse sans quitter
- **Enregistrement vidéo** : Format MP4 avec codec H.264
- **Captures d'écran** : PNG haute résolution
- **Statistiques en direct** : FPS, compteurs, pourcentages
- **Aide interactive** : Touches de clavier affichées

### 📊 **Logging et Données**
- **JSON en temps réel** : `data_logs/realtime_status.json`
- **CSV historique** : `data_logs/detection_unifie.csv`
- **Métadonnées** : Timestamps, confiance, classes, IDs
- **Sauvegarde automatique** : Toutes les frames

### 🤖 **Intégration Hardware**
- **Communication Arduino** : Port série automatique
- **Débit configurable** : 9600 baud (modifiable)
- **Envoi périodique** : Toutes les 5 secondes
- **Statuts d'états** : ACC, Finished, etc.

### 🎬 **Optimisations Vidéo**
- **Désentrelacement** : Support des formats progressifs/entrelacés
- **Adaptation résolution** : Redimensionnement automatique
- **Saut de frames** : Traitement optimisé (GPU)
- **Cache layer** : Optimisation mémoire

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  UNIFIED BOTTLE DETECTION                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  SOURCE VIDEO / WEBCAM                                      │
│  (File, Webcam, Stream)                                    │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────────────────────────────────────┐          │
│  │      FRAME PREPROCESSING & ENHANCEMENT      │          │
│  │  • Deinterlacing                            │          │
│  │  • Transpose/Rotate                          │          │
│  │  • Resize (640x640 YOLO / 224x224 CNN)     │          │
│  └──────────────────────────────────────────────┘          │
│         │                                                   │
│         ├─────────────┬────────────────────────┐           │
│         ▼             ▼                        ▼           │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────────┐    │
│  │   YOLO v8   │ │ ResNet50v2  │ │ TRACKING ENGINE  │    │
│  │ DETECTION   │ │ CNN CLASS   │ │ (Byte-Track)     │    │
│  │             │ │             │ │                  │    │
│  │ • Bottles   │ │ • Remplie   │ │ • ID Assignment  │    │
│  │ • Caps      │ │ • Vide      │ │ • Trajectory     │    │
│  │ • Confidence│ │ • Confidence│ │ • State History  │    │
│  └─────────────┘ └─────────────┘ └──────────────────┘    │
│         │             │                 │                 │
│         └─────────────┼─────────────────┘                 │
│                       ▼                                    │
│          ┌────────────────────────────┐                   │
│          │   DATA FUSION & ANALYSIS   │                   │
│          │ • Fill Percentage           │                   │
│          │ • Cap Status               │                   │
│          │ • Temporal Smoothing       │                   │
│          └────────────────────────────┘                   │
│                       │                                    │
│         ┌─────────────┼─────────────┬───────────┐         │
│         ▼             ▼             ▼           ▼         │
│   VISUALIZATION   CSV LOG      JSON LOG    ARDUINO        │
│   (Live Stream)   (Timestamped) (Real-time) (Serial)     │
│                                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation

### Prérequis
```bash
✓ Python 3.8 ou supérieur
✓ Pip ou Conda
✓ CUDA 11.8+ (optionnel mais recommandé pour GPU)
✓ 4GB RAM minimum (8GB recommandé)
```

### 1️⃣ Cloner le repository
```bash
git clone https://github.com/HATIMABDESSAMAD/detection-bottle.git
cd detection-bottle
```

### 2️⃣ Créer un environnement virtuel
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Installer les dépendances
```bash
pip install --upgrade pip setuptools wheel
pip install -r regroupement\ des\ 3\ modeles/requirements.txt
```

### 4️⃣ Vérifier l'installation GPU (optionnel)
```bash
python -c "import torch; print('GPU Available:', torch.cuda.is_available())"
```

### 5️⃣ Télécharger les modèles pré-entraînés
Les modèles doivent être placés dans les emplacements suivants :
```
regroupement des 3 modeles/
├── Bottle-Bottle-Cap-Detection-System-main/
│   └── best.pt                    (YOLOv8 Detection)
└── remplie ou non/artifacts/models/
    └── best_resnet50v2.keras     (ResNet50v2 Classification)
```

---

## 📖 Utilisation

### Démarrage Basique

#### Mode Webcam
```bash
cd "regroupement des 3 modeles"
python unified_bottle_detection.py
```

#### Mode Vidéo Fichier
```bash
python unified_bottle_detection.py --source video.mp4
```

#### Mode Transposition (si vidéo de travers)
```bash
python unified_bottle_detection.py --transpose
```

### Paramètres Configurables

Modifier dans le code (ligne ~100) :
```python
self.confidence_detection = 0.5          # Seuil de confiance YOLOv8 (0-1)
self.confidence_segmentation = 0.3       # Seuil de confiance CNN (0-1)
self.iou = 0.5                          # NMS IoU Threshold
self.img_size = 640                     # Taille inférence YOLO
self.process_every_n_frames = 1         # Traiter 1 sur N frames
self.track_trail_length = 15            # Longueur des trajectoires
```

---

## ⌨️ Commandes Clavier

| Touche | Action |
|--------|--------|
| **SPACE** | ⏸️ Pause/Reprendre |
| **R** | 🎬 Démarrer/Arrêter enregistrement vidéo |
| **S** | 📸 Capturer screenshot |
| **H** | ❓ Afficher/Masquer l'aide |
| **D** | 📊 Afficher/Masquer détails debug |
| **C** | 🧮 Afficher/Masquer compteurs |
| **T** | 🛤️ Afficher/Masquer trajectoires |
| **Q / ESC** | ❌ Quitter l'application |

---

## 📁 Structure du Projet

```
detection-bottle/
│
├── 📄 README.md                           # Ce fichier
├── 📄 LICENSE                             # Licence MIT
├── 📄 CONTRIBUTING.md                     # Guide contribution
├── 📄 CHANGELOG.md                        # Historique des versions
│
└── 📁 regroupement des 3 modeles/
    ├── 📄 requirements.txt                # Dépendances Python
    ├── 🐍 unified_bottle_detection.py    # Script principal
    ├── 🐍 debug_run.py                   # Utilitaire debug
    ├── 🐍 import_serial.py               # Gestion communication série
    │
    ├── 📁 Bottle-Bottle-Cap-Detection-System-main/
    │   ├── best.pt                       # Modèle YOLO v8
    │   ├── detection.py                  # Utilities détection
    │   └── README.md                     # Doc modèle détection
    │
    ├── 📁 remplie ou non/
    │   ├── train_resnet50v2.py          # Script entraînement
    │   ├── evaluate_metrics.py           # Évaluation modèle
    │   └── artifacts/models/
    │       └── best_resnet50v2.keras    # Modèle ResNet50v2
    │
    ├── 📁 data_logs/                    # Données collectées
    ├── 📁 results/                      # Sorties
    ├── 📁 screenshots/                  # Captures d'écran
    └── 📁 videos/                       # Vidéos enregistrées
```

---

## ⚙️ Configuration Avancée

### Configuration Arduino

```python
# Détection automatique du port
self.init_arduino()

# Ou spécifier manuellement
self.arduino_port = "COM3"  # Windows
self.arduino_port = "/dev/ttyUSB0"  # Linux
```

### Optimisation GPU

```python
# Taille d'inférence pour YOLO
self.img_size = 640  # Recommandé pour GPU
# OU
self.img_size = 416  # Plus rapide mais moins précis
```

---

## 📊 Logging et Données

### Format JSON (realtime_status.json)
```json
{
  "timestamp": "2024-05-28 14:23:45.123456",
  "frame_number": 1523,
  "fps": 28.5,
  "total_bottles": 5,
  "bottles_filled": 3,
  "bottles_empty": 2,
  "detected_objects": [...]
}
```

### Format CSV (detection_unifie.csv)
```csv
Timestamp,Frame,BottleID,Class,Confidence,FillStatus,CapStatus
2024-05-28 14:23:45.123,1523,1,Bottle,0.95,REMPLIE,AVEC BOUCHON
```

---

## 📈 Performances

### Benchmarks (GPU: RTX 3070)

| Métrique | Valeur |
|----------|--------|
| **FPS (Détection)** | 28-35 |
| **FPS (Classification)** | 50-60 |
| **Latence YOLO** | ~30ms |
| **Latence CNN** | ~15ms |
| **Mémoire GPU** | ~2.1 GB |

### Benchmarks (CPU: Intel i7-11700K)

| Métrique | Valeur |
|----------|--------|
| **FPS (Détection)** | 8-12 |
| **FPS (Classification)** | 15-20 |
| **Mémoire RAM** | ~1.8 GB |

---

## 🔧 Troubleshooting

### ❌ Erreur: "No module named 'torch'"
```bash
pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### ❌ Erreur: "CUDA out of memory"
```python
self.img_size = 416  # Réduire la taille
```

### ❌ FPS très bas (< 5 FPS)
```python
# Vérifier GPU utilisé et réduire résolution
self.process_every_n_frames = 2
self.img_size = 416
```

---

## 👥 Contribution

Les contributions sont bienvenues ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour les directives.

### Comment contribuer
1. 🍴 Fork le repository
2. 🌿 Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. 🔀 Push vers la branche (`git push origin feature/AmazingFeature`)
5. 📝 Ouvrir une Pull Request

---

## 📄 Licence

Ce projet est sous licence **MIT** - voir [LICENSE](LICENSE) pour détails.

**Copyright © 2024 HATIM ABDESSAMAD**

---

## 📞 Support et Contact

- 📧 Email: hatim.abdessamad@email.com
- 🐛 Issues: [GitHub Issues](https://github.com/HATIMABDESSAMAD/detection-bottle/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/HATIMABDESSAMAD/detection-bottle/discussions)

---

**Merci d'utiliser Unified Bottle Detection System! 🍶**
