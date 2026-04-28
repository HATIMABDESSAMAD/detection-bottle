#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Unifiée - Détection et Segmentation de Bouteilles
Affichage simultané des 2 modèles dans une seule fenêtre OpenCV
"""

import cv2
import numpy as np
import sys
import torch
from collections import deque
from ultralytics import YOLO
import tensorflow as tf
import os
from pathlib import Path
import time
from datetime import datetime
import csv
import json
import threading
import queue as _queue
import zipfile
import tempfile
import serial
import serial.tools.list_ports


def find_arduino():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Arduino" in port.description or "CH340" in port.description or "wch" in port.description.lower():
            print(f"Arduino détecté sur {port.device} - {port.description}")
            return port.device
    return None

def connect():
    port = find_arduino()
    
    if not port:
        print("Aucune Arduino détectée, sélection manuelle :")
        ports = serial.tools.list_ports.comports()
        for i, p in enumerate(ports):
            print(f"  [{i}] {p.device} - {p.description}")
        choix = input("Choisir le numéro du port : ")
        port = ports[int(choix)].device

    try:
        ser = serial.Serial(port, 115200, timeout=1)
        time.sleep(2)
        print(f"Connecté sur {port}\n")
        return ser
    except Exception as e:
        print(f"Erreur de connexion : {e}")
        return None

def print_menu():
    print("\n=============================")
    print("  ARDUINO CONTROLLER")
    print("=============================")
    print("  [m1] Mode Manuel")
    print("  [m3] Mode Auto")
    print("-----------------------------")
    print("  MODE MANUEL :")
    print("  [1]  Sous-mode Servo")
    print("  [2]  Sous-mode Convoyeur")
    print("  [3]  Sous-mode Pusher")
    print("  [4]  Sous-mode Broyeur")
    print("-----------------------------")
    print("  MODE AUTO :")
    print("  [1]  Lancer le cycle")
    print("  [0]  Arrêt d'urgence")
    print("-----------------------------")
    print("  [q]  Quitter")
    print("=============================")

def read_serial(ser):
    while ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line:
            print(f"  Arduino > {line}")


# Paramètres incompatibles selon la version Keras (2 → 3)
_LAYER_COMPAT_STRIP = {
    'BatchNormalization': {'renorm', 'renorm_clipping', 'renorm_momentum'},
}
_GLOBAL_STRIP_IF_NONE = {'quantization_config'}

def _load_keras_model_legacy(path):
    """Charge un modèle .keras en corrigeant les incompatibilités Keras 2→3."""
    with zipfile.ZipFile(path, 'r') as zin:
        contents = {name: zin.read(name) for name in zin.namelist()}

    config = json.loads(contents['config.json'].decode('utf-8'))

    def strip_compat(obj):
        if isinstance(obj, dict):
            if 'class_name' in obj and 'config' in obj:
                cfg = obj['config']
                for key in _LAYER_COMPAT_STRIP.get(obj['class_name'], set()):
                    cfg.pop(key, None)
                for key in list(cfg.keys()):
                    if key in _GLOBAL_STRIP_IF_NONE and cfg[key] is None:
                        cfg.pop(key)
            for v in obj.values():
                strip_compat(v)
        elif isinstance(obj, list):
            for item in obj:
                strip_compat(item)

    strip_compat(config)
    contents['config.json'] = json.dumps(config).encode('utf-8')

    tmp = tempfile.mktemp(suffix='.keras')
    try:
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
            for name, data in contents.items():
                zout.writestr(name, data)
        model = tf.keras.models.load_model(tmp, compile=False)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return model

class UnifiedBottleDetection:
    def __init__(self):
        """Initialise l'interface unifiée avec les 2 modèles"""
        print("=" * 70)
        print("🍶 UNIFIED BOTTLE DETECTION - DOUBLE MODEL DISPLAY")
        print("=" * 70)
        
        # === MODÈLE 1: DÉTECTION (Bouteille + Bouchon) ===
        self.model_detection_path = 'Bottle-Bottle-Cap-Detection-System-main/best.pt'
        self.model_detection = None
        self.detection_classes = {0: 'Bottle', 1: 'Avec Bouchon', 2: 'Sans Bouchon'}
        self.detection_colors = {0: (0, 255, 0), 1: (0, 0, 255), 2: (255, 165, 0)}  # Vert, Rouge, Orange
        
        # === MODÈLE 2: CLASSIFICATION CNN (Remplie / Vide) ===
        self.model_segmentation_path = 'remplie ou non/artifacts/models/best_resnet50v2.keras'
        self.model_segmentation = None
        self.cnn_img_size = (224, 224)  # Taille d'entrée du CNN
        # Classes triées alphabétiquement: 0=bouteuille remplie, 1=bouteuille vide
        self.segmentation_classes = {0: 'remplie', 1: 'vide'}
        self.segmentation_colors = {0: (0, 255, 0), 1: (0, 165, 255)}  # Vert, Orange
        
        # === PARAMÈTRES ===
        self.confidence_detection = 0.5
        self.confidence_segmentation = 0.3
        self.iou = 0.5
        self.transpose_image = True  # Transpose activé par défaut
        self.img_size = 640  # Taille augmentée pour meilleure précision avec GPU
        self.process_every_n_frames = 1  # Traiter toutes les frames avec GPU
        self.frame_skip_counter = 0
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'  # Device GPU
        
        # === STATISTIQUES ===
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        
        # === DÉTECTION DE REMPLISSAGE ===
        self.water_percentage_history = []  # Historique des pourcentages
        self.history_size = 10  # Nombre de frames à garder en mémoire
        
        # === TRACKING ===
        self.track_history_detection = {}  # {id: [(x,y), ...]}
        self.track_history_segmentation = {}
        self.total_tracked_caps = set()  # IDs uniques vus (caps)
        self.total_tracked_bottles = set()  # IDs uniques vus (bottles)
        self.bottle_fill_status = {}  # {id: 0 ou 1} - Une fois remplie=1, reste à 1
        self.bottle_cap_status = {}   # {id: bool} True=avec bouchon, False=sans bouchon
        self.bottle_water_percentage = {}  # {id: pourcentage actuel}
        self._printed_status = {}  # {id: (fill_str, cap_str)} dernier statut imprimé par ID
        self.fill_history = {}  # {id: deque(maxlen=15)} - Historique binaire pour lissage temporel
        self.bottle_hysteresis_state = {}  # {id: 0/1} état courant pour hystérésis (non permanent)
        self.bottle_smoothed_label = {}    # {id: "REMPLIE"/"VIDE"} label lissé pour affichage
        self.bottle_label_locked = set()   # IDs dont le label est verrouillé (après 5 premières frames)
        self.global_fill_history = deque(maxlen=15)  # Historique global (indépendant du track_id)
        self.global_label_locked = False             # Verrou global (persiste malgré changements track_id)
        self.global_locked_label = None              # Label global verrouillé
        # === LISSAGE BOUCHON (vote 15 frames, même logique que fill) ===
        self.cap_history = {}          # {id: deque(maxlen=15)} 1=avec bouchon, 0=sans
        self.cap_label_locked = set()  # IDs dont le statut bouchon est verrouillé
        self.global_cap_history = deque(maxlen=15)  # historique global bouchon
        self.global_cap_locked = False
        self.global_cap_locked_value = None  # True/False une fois verrouillé
        self.saved_bottle_track_ids = set()  # IDs déjà sauvegardés (crop bbox bouteille)
        self.last_unknown_bottle_save_time = 0  # Dernière sauvegarde sans track_id
        self.unknown_bottle_save_interval = 2.0  # Intervalle mini (sec) sans track_id
        self.track_trail_length = 15  # Longueur des trails réduite pour performance
        self.cap_detection_padding = 80  # Pixels de padding autour bbox bouteille pour détection bouchon
        
        # === ÉTAT ===
        self.paused = False
        self.recording = False
        self.video_writer = None
        self.show_help = True
        self.record_button_coords = (0, 0, 0, 0)  # Coordonnées du bouton d'enregistrement
        
        # === CACHE POUR OPTIMISATION ===
        self.cached_detection_frame = None
        self.cached_segmentation_frame = None
        self.cached_detection_data = (0, 0, None, False, [])
        self.cached_segmentation_data = (0, 0.0, None)
        
        # === DOSSIERS ===
        os.makedirs('results', exist_ok=True)
        os.makedirs('screenshots', exist_ok=True)
        os.makedirs('videos', exist_ok=True)
        os.makedirs('data_logs', exist_ok=True)
        os.makedirs('results/bottle_boxes', exist_ok=True)
        
        # === SAUVEGARDE EN TEMPS RÉEL ===
        self.realtime_data_file = None
        self.realtime_csv_writer = None
        self.realtime_json_file = 'data_logs/realtime_status.json'
        self.last_saved_data = None
        
        # === ARDUINO SERIAL ===
        self.arduino_serial = None
        self.arduino_port = None  # Sera détecté automatiquement
        self.arduino_baudrate = 115200
        self.arduino_send_interval = 5  # Envoyer toutes les 5 secondes
        self.last_arduino_send_time = 0
        self.arduino_enabled = True  # Activer/désactiver l'envoi Arduino
        
        # Charger les modèles
        self.load_models()
        
        # Initialiser la connexion Arduino
        self.init_arduino()
    
    def load_models(self):
        """Charge les deux modèles"""
        print("\n🔄 Chargement des modèles...")
        
        # Modèle 1: Détection (YOLO)
        if os.path.exists(self.model_detection_path):
            try:
                self.model_detection = YOLO(self.model_detection_path)

            except Exception as e:
                print(f"❌ Erreur chargement détection: {e}")
        else:
            print(f"❌ Modèle détection introuvable: {self.model_detection_path}")
        
        # Modèle 2: Classification CNN Keras (Remplie/Vide)
        if os.path.exists(self.model_segmentation_path):
            try:
                self.model_segmentation = _load_keras_model_legacy(self.model_segmentation_path)

            except Exception as e:
                print(f"❌ Erreur chargement classification CNN: {e}")
        else:
            print(f"❌ Modèle classification CNN introuvable: {self.model_segmentation_path}")
        
        # Vérifier et configurer GPU pour YOLO
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

        
        if self.model_detection is not None:
            self.model_detection.to(device)

        # Note: le CNN Keras utilise automatiquement le GPU via TensorFlow
        if self.model_segmentation is not None:
            pass
        if self.model_detection is None or self.model_segmentation is None:
            print("\n⚠️ ATTENTION: Au moins un modèle n'a pas pu être chargé!")
            return False
        
        return True
    
    def init_arduino(self):
        """Initialise la connexion série avec Arduino"""
        print("\n🔌 Recherche de l'Arduino...")
        
        # Lister tous les ports disponibles
        ports = serial.tools.list_ports.comports()
        
        if not ports:
            print("⚠️ Aucun port série détecté")
            self.arduino_enabled = False
            return False
        
        print("📡 Ports disponibles:")
        for port in ports:
            print(f"   - {port.device}: {port.description}")
        
        # Chercher un Arduino (généralement CH340, Arduino, ou USB Serial)
        arduino_port = None
        for port in ports:
            desc_lower = port.description.lower()
            if any(keyword in desc_lower for keyword in ['arduino', 'ch340', 'usb serial', 'usb-serial', 'ftdi']):
                arduino_port = port.device
                print(f"✅ Arduino trouvé sur {arduino_port}")
                break
        
        # Si pas trouvé automatiquement, ne pas se connecter à un port inconnu (Bluetooth etc.)
        if arduino_port is None:
            print("⚠️ Arduino non identifié (ports Bluetooth ignorés)")
            self.arduino_enabled = False
            return False
        
        # Tenter la connexion
        try:
            self.arduino_serial = serial.Serial(
                port=arduino_port,
                baudrate=self.arduino_baudrate,
                timeout=1
            )
            self.arduino_port = arduino_port
            time.sleep(2)  # Attendre que l'Arduino redémarre
            print(f"✅ Connexion Arduino établie sur {arduino_port} @ {self.arduino_baudrate} baud")
            return True
        except serial.SerialException as e:
            print(f"❌ Erreur connexion Arduino: {e}")
            self.arduino_enabled = False
            return False
    
    def close_arduino(self):
        """Ferme la connexion série Arduino"""
        if self.arduino_serial is not None and self.arduino_serial.is_open:
            self.arduino_serial.close()
            print("🔌 Connexion Arduino fermée")
    
    def send_to_arduino(self, bottle_exists, num_bottles, is_filled, has_cap):
        """
        Envoie les données à l'Arduino via série
        Format: <BOTTLE_EXIST,NUM_BOTTLES,FILLED,CAP>
        Exemple: <1,1,1,0> = bouteille existe, 1 bouteille, remplie, sans bouchon
        
        Args:
            bottle_exists: True si bouteille détectée
            num_bottles: Nombre de bouteilles
            is_filled: True si remplie
            has_cap: True si avec bouchon
        """
        if not self.arduino_enabled or self.arduino_serial is None:
            return False
        
        if not self.arduino_serial.is_open:
            print("⚠️ Port série fermé, tentative de reconnexion...")
            self.init_arduino()
            if not self.arduino_serial or not self.arduino_serial.is_open:
                return False
        
        # Convertir en 0/1 (logique inversée pour remplie et bouchon)
        # 1 = bouteille existe, 1 = NON remplie, 1 = SANS bouchon
        b_exist = 1 if bottle_exists else 0
        b_not_filled = 1 if not is_filled else 0  # 1 = NON remplie
        b_no_cap = 1 if not has_cap else 0        # 1 = SANS bouchon
        
        # Format de message: <B,N,F,C> où B=existe, N=nombre, F=non_remplie, C=sans_bouchon
        message = f"<{b_exist},{num_bottles},{b_not_filled},{b_no_cap}>\n"
        
        try:
            self.arduino_serial.write(message.encode('utf-8'))
            self.arduino_serial.flush()
            print(f"📤 Arduino: {message.strip()}")
            return True
        except serial.SerialException as e:
            print(f"❌ Erreur envoi Arduino: {e}")
            return False
    
    def check_and_send_arduino(self, bottle_exists, num_bottles, is_filled, has_cap):
        """
        Vérifie si 5 secondes sont passées et envoie les données à Arduino
        
        Args:
            bottle_exists: True si bouteille détectée
            num_bottles: Nombre de bouteilles
            is_filled: True si remplie
            has_cap: True si avec bouchon
        """
        current_time = time.time()
        
        # Vérifier si l'intervalle est écoulé
        if current_time - self.last_arduino_send_time >= self.arduino_send_interval:
            self.send_to_arduino(bottle_exists, num_bottles, is_filled, has_cap)
            self.last_arduino_send_time = current_time
    
    def get_color_by_id(self, track_id):
        """Génère une couleur unique basée sur l'ID de tracking"""
        np.random.seed(int(track_id))
        return tuple(np.random.randint(0, 255, 3).tolist())
    
    def draw_track_trail(self, frame, track_history, track_id, color):
        """Dessine la trajectoire d'un objet tracké"""
        if track_id in track_history:
            points = track_history[track_id]
            for i in range(1, len(points)):
                if points[i - 1] is None or points[i] is None:
                    continue
                thickness = int(np.sqrt(float(i + 1)) * 1.5)
                cv2.line(frame, points[i - 1], points[i], color, thickness)
    
    def process_detection(self, frame):
        """
        Applique le modèle de détection en 2 passes :
        - Passe 1 (frame complète) : tracking des bouteilles (classe 0)
        - Passe 2 (crop bouteille + padding) : détection des bouchons (classes 1,2)
          Le padding autour de la bbox bouteille garantit que le bouchon est visible dans l'input.

        Args:
            frame: Image OpenCV

        Returns:
            Image annotée, nombre d'objets actifs, total objets trackés, bool si bouteille détectée
        """
        if self.model_detection is None:
            return frame, 0, 0, None, False, []

        # Transposer si nécessaire
        processed_frame = frame.copy()
        if self.transpose_image:
            processed_frame = np.transpose(processed_frame, (1, 0, 2))
            processed_frame = np.ascontiguousarray(processed_frame)

        h_proc, w_proc = processed_frame.shape[:2]
        annotated = processed_frame.copy()
        bottle_detected = False
        num_objects = 0
        current_cap_has_cap = None
        bottle_boxes = []
        bottle_bboxes_in_proc = []  # (x1, y1, x2, y2, track_id, conf) coords dans processed_frame

        # === PASSE 1: Tracking des bouteilles sur la frame complète ===
        results = self.model_detection.track(processed_frame,
                                             conf=self.confidence_detection,
                                             iou=self.iou,
                                             persist=True,
                                             tracker="bytetrack.yaml",
                                             verbose=False,
                                             imgsz=self.img_size,
                                             device=self.device,
                                             half=True if self.device == 'cuda' else False,
                                             classes=[0])  # Seulement classe Bottle

        if results and len(results) > 0:
            result = results[0]
            if hasattr(result, 'boxes') and result.boxes is not None:
                boxes = result.boxes.xyxy.cpu().numpy()
                confidences = result.boxes.conf.cpu().numpy()
                track_ids = None
                if hasattr(result.boxes, 'id') and result.boxes.id is not None:
                    track_ids = result.boxes.id.cpu().numpy().astype(int)

                for idx, (box, conf) in enumerate(zip(boxes, confidences)):
                    x1, y1, x2, y2 = map(int, box)
                    track_id_bottle = track_ids[idx] if track_ids is not None else None
                    bottle_detected = True

                    # Coordonnées frame originale pour la segmentation CNN
                    if self.transpose_image:
                        orig = (int(y1), int(x1), int(y2), int(x2), track_id_bottle)
                    else:
                        orig = (int(x1), int(y1), int(x2), int(y2), track_id_bottle)
                    bottle_boxes.append(orig)
                    bottle_bboxes_in_proc.append((x1, y1, x2, y2, track_id_bottle, float(conf)))

                    # Sauvegarde crop désactivée
                    # ox1, oy1, ox2, oy2, _ = orig
                    # self.save_bottle_bbox_image(frame, ox1, oy1, ox2, oy2,
                    #                             track_id=track_id_bottle, confidence=conf)

                    # Dessiner la bbox bouteille
                    bottle_color = (0, 255, 0)
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), bottle_color, 2)
                    if track_id_bottle is not None:
                        blabel = f"ID:{track_id_bottle} Bottle: {conf:.2f}"
                    else:
                        blabel = f"Bottle: {conf:.2f}"
                    blabel_size = cv2.getTextSize(blabel, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                    cv2.rectangle(annotated, (x1, y1 - blabel_size[1] - 10),
                                  (x1 + blabel_size[0] + 5, y1), bottle_color, -1)
                    cv2.putText(annotated, blabel, (x1 + 2, y1 - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # === PASSE 2: Détection des bouchons sur crop bouteille + padding ===
        # Input = bbox bouteille élargie de cap_detection_padding pixels de chaque côté
        for (bx1, by1, bx2, by2, track_id_bottle, _) in bottle_bboxes_in_proc:
            pad = self.cap_detection_padding
            cap_this_bottle = False  # False = sans bouchon par défaut
            # Clamp aux dimensions de la frame (pas de padding en bas : le bouchon est en haut)
            cx1 = max(0, bx1 - pad)
            cy1 = max(0, by1 - pad)
            cx2 = min(w_proc, bx2 + pad)
            cy2 = min(h_proc, by2)  # Pas de padding bas

            cap_crop = processed_frame[cy1:cy2, cx1:cx2]
            if cap_crop.size == 0:
                continue

            results_caps = self.model_detection.predict(
                cap_crop,
                conf=self.confidence_detection,
                iou=self.iou,
                verbose=False,
                imgsz=self.img_size,
                device=self.device,
                half=True if self.device == 'cuda' else False,
                classes=[1, 2])  # Seulement classes bouchon

            if results_caps and len(results_caps) > 0:
                result_cap = results_caps[0]
                if hasattr(result_cap, 'boxes') and result_cap.boxes is not None:
                    cap_boxes_arr = result_cap.boxes.xyxy.cpu().numpy()
                    cap_confs = result_cap.boxes.conf.cpu().numpy()
                    cap_classes_arr = result_cap.boxes.cls.cpu().numpy()

                    for cap_box, cap_conf, cap_cls in zip(cap_boxes_arr, cap_confs, cap_classes_arr):
                        # Décaler vers coordonnées frame complète
                        cx1_cap = int(cap_box[0]) + cx1
                        cy1_cap = int(cap_box[1]) + cy1
                        cx2_cap = int(cap_box[2]) + cx1
                        cy2_cap = int(cap_box[3]) + cy1

                        class_id = int(cap_cls)
                        class_name = self.detection_classes.get(class_id, f"Class {class_id}")
                        num_objects += 1
                        color = self.detection_colors.get(class_id, (255, 255, 255))

                        cv2.rectangle(annotated, (cx1_cap, cy1_cap), (cx2_cap, cy2_cap), color, 3)
                        label = f"{class_name}: {cap_conf:.2f}"
                        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                        cv2.rectangle(annotated,
                                      (cx1_cap, cy1_cap - label_size[1] - 10),
                                      (cx1_cap + label_size[0] + 5, cy1_cap),
                                      color, -1)
                        cv2.putText(annotated, label, (cx1_cap + 2, cy1_cap - 5),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                        has_cap_detected = (class_name.lower() == 'avec bouchon')
                        cap_this_bottle = has_cap_detected
                        if current_cap_has_cap is None:
                            current_cap_has_cap = has_cap_detected

            # Stocker le statut bouchon par ID bouteille — avec lissage 15 frames
            if track_id_bottle is not None:
                if track_id_bottle not in self.cap_history:
                    self.cap_history[track_id_bottle] = deque(maxlen=15)
                self.cap_history[track_id_bottle].append(1 if cap_this_bottle else 0)
                # Verrouillage par ID après 15 frames
                if track_id_bottle not in self.cap_label_locked:
                    smoothed_cap = sum(self.cap_history[track_id_bottle]) >= 8  # AVEC si >= 8/15
                    self.bottle_cap_status[track_id_bottle] = smoothed_cap
                    if len(self.cap_history[track_id_bottle]) >= 15:
                        self.cap_label_locked.add(track_id_bottle)
            # Lissage global bouchon
            if not self.global_cap_locked:
                self.global_cap_history.append(1 if cap_this_bottle else 0)
                if len(self.global_cap_history) >= 15:
                    self.global_cap_locked_value = sum(self.global_cap_history) >= 8
                    self.global_cap_locked = True

        return annotated, num_objects, len(self.total_tracked_caps), current_cap_has_cap, bottle_detected, bottle_boxes

    def process_segmentation(self, frame, bottle_boxes=None):
        """
        Applique le modèle CNN de classification (Remplie/Vide) sur les crops de bouteilles
        détectées par le modèle 1.

        Args:
            frame: Image OpenCV originale (non transposée)
            bottle_boxes: Liste de (x1, y1, x2, y2, track_id) en coordonnées frame originale
                          issues du modèle de détection

        Returns:
            Image annotée, nombre d'objets classifiés, score de remplissage (0-100), ID bouteille actuelle
        """
        if self.model_segmentation is None:
            return frame, 0, 0.0, None

        if not bottle_boxes:
            # Fond noir + message d'attente
            empty = np.zeros_like(frame)
            h0, w0 = frame.shape[:2]
            cv2.putText(empty, "En attente de bouteille...",
                        (w0 // 2 - 200, h0 // 2),
                        cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 255, 255), 2)
            return empty, 0, 0.0, None

        # Fond noir : seules les régions détectées par modèle 1 seront visibles
        annotated = np.zeros_like(frame)
        num_objects = 0
        water_percentage = 0.0
        current_bottle_id = None
        h_frame, w_frame = frame.shape[:2]

        for box_info in bottle_boxes:
            x1_orig, y1_orig, x2_orig, y2_orig, track_id = box_info

            # Clamp aux dimensions de la frame
            x1c = max(0, x1_orig)
            y1c = max(0, y1_orig)
            x2c = min(w_frame, x2_orig)
            y2c = min(h_frame, y2_orig)

            if x2c <= x1c or y2c <= y1c:
                continue

            # === CROP DE LA BOUTEILLE ===
            crop = frame[y1c:y2c, x1c:x2c]

            # Afficher les pixels originaux dans la bbox
            annotated[y1c:y2c, x1c:x2c] = crop

            # Mettre à jour le tracking bouteille
            if track_id is not None:
                self.total_tracked_bottles.add(track_id)
                if track_id not in self.bottle_fill_status:
                    self.bottle_fill_status[track_id] = 0
                current_bottle_id = track_id

            # === INFÉRENCE CNN (Keras ResNet50V2) ===
            # Convertir BGR→RGB, redimensionner à 224×224, float32 [0-255]
            # (preprocess_input est intégré dans le modèle)
            crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            crop_resized = cv2.resize(crop_rgb, self.cnn_img_size)
            batch = np.expand_dims(crop_resized.astype(np.float32), axis=0)

            # Score sigmoid : ~0 = remplie, ~1 = vide (ordre alphabétique des classes)
            score = float(self.model_segmentation(batch, training=False)[0][0])

            # Mapper le score en pourcentage de remplissage (0-100)
            bottle_pct = (1.0 - score) * 100.0

            # === HYSTÉRÉSIS : seuil différent selon l'état courant pour éviter oscillation ===
            if track_id is not None:
                current_hyst = self.bottle_hysteresis_state.get(track_id, 0)
                if current_hyst == 1:  # Actuellement REMPLIE → besoin score > 0.72 pour passer VIDE
                    is_remplie = score < 0.72
                else:              # Actuellement VIDE → besoin score < 0.50 pour passer REMPLIE
                    is_remplie = score < 0.50
                self.bottle_hysteresis_state[track_id] = 1 if is_remplie else 0
            else:
                is_remplie = score < 0.50

            # === LISSAGE TEMPOREL : vote majoritaire sur 5 dernières frames ===
            if track_id is not None:
                if track_id not in self.fill_history:
                    self.fill_history[track_id] = deque(maxlen=15)
                self.fill_history[track_id].append(1 if is_remplie else 0)
                smoothed_remplie = sum(self.fill_history[track_id]) >= 5  # REMPLIE dès 5/15, VIDE seulement si 11/15
            else:
                smoothed_remplie = is_remplie

            label_class = "REMPLIE" if smoothed_remplie else "VIDE"

            # === VERROUILLAGE GLOBAL (indépendant du track_id) ===
            if not self.global_label_locked:
                self.global_fill_history.append(1 if smoothed_remplie else 0)
                if len(self.global_fill_history) >= 15:
                    global_vote = sum(self.global_fill_history) >= 5  # REMPLIE dès 5/15, VIDE seulement si 11/15
                    self.global_locked_label = "REMPLIE" if global_vote else "VIDE"
                    self.global_label_locked = True

            # Sauvegarder le label lissé UNIQUEMENT si pas encore verrouillé
            # Le label se verrouille définitivement après 5 premières frames (deque pleine)
            if track_id is not None and track_id not in self.bottle_label_locked:
                self.bottle_smoothed_label[track_id] = label_class
                if len(self.fill_history[track_id]) >= 15:
                    self.bottle_label_locked.add(track_id)

            if track_id is not None:
                if smoothed_remplie:
                    self.bottle_fill_status[track_id] = 1
                self.bottle_water_percentage[track_id] = bottle_pct

            num_objects += 1
            water_percentage = bottle_pct  # Valeur de la dernière bouteille traitée

            # Couleur : vert = remplie, orange = vide
            color = self.get_color_by_id(track_id) if track_id is not None \
                    else ((0, 255, 0) if smoothed_remplie else (0, 165, 255))

            # Overlay coloré semi-transparent sur le crop
            overlay = annotated.copy()
            cv2.rectangle(overlay, (x1c, y1c), (x2c, y2c), color, -1)
            cv2.addWeighted(overlay, 0.15, annotated, 0.85, 0, annotated)

            # Bounding box
            cv2.rectangle(annotated, (x1c, y1c), (x2c, y2c), color, 3)

            # Label
            label = f"ID:{track_id} {label_class} {bottle_pct:.1f}%"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(annotated,
                          (x1c, y1c - label_size[1] - 10),
                          (x1c + label_size[0] + 5, y1c),
                          color, -1)
            cv2.putText(annotated, label, (x1c + 2, y1c - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # Trail de trajectoire
            if track_id is not None:
                center = (int((x1c + x2c) / 2), int((y1c + y2c) / 2))
                if track_id not in self.track_history_segmentation:
                    self.track_history_segmentation[track_id] = []
                self.track_history_segmentation[track_id].append(center)
                if len(self.track_history_segmentation[track_id]) > self.track_trail_length:
                    self.track_history_segmentation[track_id].pop(0)
                self.draw_track_trail(annotated, self.track_history_segmentation, track_id, color)

        return annotated, num_objects, water_percentage, current_bottle_id
    
    def is_bottle_filled(self, track_id=None):
        """
        Détermine si la bouteille est remplie en utilisant le tracking
        Une fois qu'une bouteille a été détectée avec de l'eau (pourcentage > 0),
        elle reste marquée comme remplie même si le pourcentage retombe à 0
        
        Args:
            track_id: ID de la bouteille trackée (si disponible)
            
        Returns:
            1 si remplie (a déjà eu un pourcentage > 0)
            0 si vide (jamais eu de pourcentage > 0)
        """
        # Si on a un track_id, utiliser le statut tracké
        if track_id is not None and track_id in self.bottle_fill_status:
            return self.bottle_fill_status[track_id]
        
        # Sinon, utiliser l'historique global (comportement par défaut)
        if len(self.water_percentage_history) < 5:
            return 0  # Pas assez de données
        
        # Vérifier si tous les pourcentages sont à 0
        all_zero = all(p == 0.0 for p in self.water_percentage_history)
        
        if all_zero:
            return 0  # Bouteille vide
        else:
            return 1  # Bouteille remplie (pourcentage > 0)
    
    def draw_panel_info(self, frame, title, fps, conf, num_objects, water_percentage=None, current_bottle_id=None, current_cap_has_cap=None, is_left=True):
        """
        Dessine les informations sur un panneau
        
        Args:
            frame: Image à annoter
            title: Titre du panneau
            fps: FPS actuel
            conf: Niveau de confiance
            num_objects: Nombre d'objets détectés
            water_percentage: Pourcentage eau/bouteille (si disponible)
            current_bottle_id: ID de la bouteille actuelle
            current_cap_has_cap: Statut du bouchon
            is_left: True si panneau de gauche, False si droite
        """
        h, w = frame.shape[:2]
        
        # Position du texte
        x = 10 if is_left else 10
        
        # Fond semi-transparent pour le titre
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 35), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Titre
        cv2.putText(frame, title, (x, 25), 
                   cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 255, 255), 2)
        
        # Informations - calculer les infos d'abord pour déterminer la hauteur
        infos = [
            f"FPS: {fps:.1f}",
            f"Conf: {conf:.2f}",
            f"Active: {num_objects}"
        ]
        
        # Ajouter stats de tracking selon le panneau
        if water_percentage is None:
            # Panneau gauche (détection caps) - Afficher uniquement le statut avec bouchon
            # Ajouter le statut "avec bouchon" du cap actuel
            if current_cap_has_cap is not None:
                cap_status = "OUI" if current_cap_has_cap else "NON"
                infos.append(f"Bouteille actuelle")
                infos.append(f"avec bouchon: {cap_status}")
        else:
            # Panneau droite (segmentation) - Afficher Water, statut remplie et transparence
            infos.append(f"Water: {water_percentage:.1f}%")
            
            # Afficher REMPLIE/VIDE avec verrouillage global (indépendant du track_id)
            if self.global_label_locked:
                infos.append(f"Etat: {self.global_locked_label}")
            else:
                frames_done = len(self.global_fill_history)
                if frames_done > 0:
                    infos.append(f"Etat: Analyse ({frames_done}/15)")
                # Sinon : aucune bouteille vue → champ Etat masqué
            
            # Ajouter le statut de la bouteille ACTUELLE dans la caméra
            if current_bottle_id is not None:
                if current_bottle_id in self.bottle_fill_status:
                    current_status = "OUI" if self.bottle_fill_status[current_bottle_id] == 1 else "NON"
                    infos.append(f"Bouteille ID:{current_bottle_id}")
                    infos.append(f"est remplie: {current_status}")
        
        # Ajuster la hauteur selon le nombre de lignes
        line_height = 22
        info_height = 68 + len(infos) * line_height
        
        # Ajuster la largeur selon le contenu
        info_width = 280 if water_percentage is not None else 180
        
        # Dessiner le rectangle
        overlay2 = frame.copy()
        cv2.rectangle(overlay2, (x, 45), (x + info_width, info_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay2, 0.6, frame, 0.4, 0, frame)
        
        for i, info in enumerate(infos):
            cv2.putText(frame, info, (x + 5, 68 + i * 22), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def draw_combined_interface(self, combined_frame, num_det, num_seg):
        """
        Dessine l'interface globale sur la frame combinée
        
        Args:
            combined_frame: Frame avec les deux modèles côte à côte
            num_det: Nombre d'objets détectés (modèle 1)
            num_seg: Nombre d'objets segmentés (modèle 2)
        """
        h, w = combined_frame.shape[:2]
        
        # === BARRE DU HAUT ===
        overlay = combined_frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 40), (30, 30, 30), -1)
        cv2.addWeighted(overlay, 0.8, combined_frame, 0.2, 0, combined_frame)
        
        # Titre principal centré
        title = "UNIFIED BOTTLE DETECTION - DUAL MODEL DISPLAY"
        title_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_DUPLEX, 0.8, 2)[0]
        title_x = (w - title_size[0]) // 2
        cv2.putText(combined_frame, title, (title_x, 28), 
                   cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
        
        # === LIGNE DE SÉPARATION VERTICALE ===
        mid_x = w // 2
        cv2.line(combined_frame, (mid_x, 40), (mid_x, h - 80), (255, 255, 255), 2)
        
        # === BARRE DU BAS (Contrôles) ===
        if self.show_help:
            overlay_bottom = combined_frame.copy()
            cv2.rectangle(overlay_bottom, (0, h - 80), (w, h), (30, 30, 30), -1)
            cv2.addWeighted(overlay_bottom, 0.8, combined_frame, 0.2, 0, combined_frame)
            
            controls = [
                "[SPACE] Pause/Resume",
                "[S] Screenshot",
                "[R] Start/Stop Recording",
                "[T] Transpose Image",
                "[H] Hide/Show Help",
                "[+/-] Adjust Confidence",
                "[Q/ESC] Quit"
            ]
            
            # Diviser les contrôles en 2 lignes
            line1 = " | ".join(controls[:4])
            line2 = " | ".join(controls[4:])
            
            cv2.putText(combined_frame, line1, (20, h - 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(combined_frame, line2, (20, h - 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        else:
            # Afficher juste un hint
            cv2.putText(combined_frame, "[H] Show Help", (20, h - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        # === INDICATEUR DE PAUSE ===
        if self.paused:
            pause_text = "|| PAUSED ||"
            pause_size = cv2.getTextSize(pause_text, cv2.FONT_HERSHEY_DUPLEX, 1.5, 3)[0]
            pause_x = (w - pause_size[0]) // 2
            
            # Fond
            cv2.rectangle(combined_frame, 
                         (pause_x - 10, 50), 
                         (pause_x + pause_size[0] + 10, 90), 
                         (0, 0, 0), -1)
            cv2.rectangle(combined_frame, 
                         (pause_x - 10, 50), 
                         (pause_x + pause_size[0] + 10, 90), 
                         (0, 0, 255), 3)
            
            cv2.putText(combined_frame, pause_text, (pause_x, 80), 
                       cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 255), 3)
        
        # === BOUTON D'ENREGISTREMENT (cliquable) ===
        button_x = w - 180
        button_y = 50
        button_w = 160
        button_h = 40
        
        # Dessiner le bouton
        if self.recording:
            # Bouton rouge "STOP RECORDING"
            cv2.rectangle(combined_frame, (button_x, button_y), 
                         (button_x + button_w, button_y + button_h), (0, 0, 200), -1)
            cv2.rectangle(combined_frame, (button_x, button_y), 
                         (button_x + button_w, button_y + button_h), (0, 0, 255), 2)
            
            # Cercle rouge clignotant
            if int(time.time() * 2) % 2 == 0:
                cv2.circle(combined_frame, (button_x + 20, button_y + 20), 8, (0, 0, 255), -1)
            
            cv2.putText(combined_frame, "STOP REC", (button_x + 35, button_y + 27), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        else:
            # Bouton vert "START RECORDING"
            cv2.rectangle(combined_frame, (button_x, button_y), 
                         (button_x + button_w, button_y + button_h), (0, 100, 0), -1)
            cv2.rectangle(combined_frame, (button_x, button_y), 
                         (button_x + button_w, button_y + button_h), (0, 200, 0), 2)
            
            cv2.circle(combined_frame, (button_x + 20, button_y + 20), 8, (255, 255, 255), -1)
            
            cv2.putText(combined_frame, "START REC", (button_x + 35, button_y + 27), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Stocker les coordonnées du bouton pour la détection de clic
        self.record_button_coords = (button_x, button_y, button_x + button_w, button_y + button_h)
    
    def mouse_callback(self, event, x, y, flags, param):
        """
        Callback pour gérer les clics de souris sur l'interface
        
        Args:
            event: Type d'événement souris
            x, y: Coordonnées du clic
            flags: Flags additionnels
            param: Paramètres additionnels
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            # Vérifier si le clic est sur le bouton d'enregistrement
            x1, y1, x2, y2 = self.record_button_coords
            if x1 <= x <= x2 and y1 <= y <= y2:
                # Toggle enregistrement
                if not self.recording:
                    # Démarrer l'enregistrement
                    # On récupère les dimensions de la frame courante
                    if hasattr(self, 'current_frame_size'):
                        w, h = self.current_frame_size
                        self.start_recording(w, h)
                else:
                    # Arrêter l'enregistrement
                    self.stop_recording()
    
    def _print_bottle_validity_status(self, current_ids, current_cap_has_cap):
        """Affiche ID:x | ACC ou REJ en utilisant exactement les mêmes valeurs que l'interface.
        - Fill : self.global_locked_label (VIDE/REMPLIE) apres verrouillage
        - Cap  : self.global_cap_locked_value (True/False) apres verrouillage 15 frames
        Une seule ligne par ID, uniquement quand les deux sont verrouillés.
        """
        if not self.global_label_locked:
            print(f"[DBG] fill pas lock ({len(self.global_fill_history)}/15)", flush=True)
            return
        if not self.global_cap_locked:
            print(f"[DBG] cap pas lock ({len(self.global_cap_history)}/15)", flush=True)
            return

        fill_label = self.global_locked_label
        cap_locked  = self.global_cap_locked_value
        cap_str     = "AVEC" if cap_locked else "SANS"
        current_state = (fill_label, cap_str)

        for tid in sorted(current_ids):
            if self._printed_status.get(tid) == current_state:
                continue
            self._printed_status[tid] = current_state
            is_valid = (not cap_locked) and (fill_label == "VIDE")
            cmd = "ACC" if is_valid else "REJ"
            print(f"ID:{tid} | {cmd}", flush=True)
            # Envoyer à l'Arduino via la connexion existante
            if self.arduino_serial is not None and self.arduino_serial.is_open:
                try:
                    self.arduino_serial.write((cmd + "\n").encode('utf-8'))
                    self.arduino_serial.flush()
                except Exception:
                    pass

    def calculate_fps(self):
        """Calcule le FPS actuel"""
        self.frame_count += 1
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            self.fps = self.frame_count / elapsed
    
    def save_screenshot(self, frame):
        """Sauvegarde une capture d'écran"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/screenshot_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        print(f"📸 Screenshot sauvegardé: {filename}")

    def save_bottle_bbox_image(self, frame, x1, y1, x2, y2, track_id=None, confidence=None):
        """Sauvegarde désactivée."""
        return False
    
    def start_recording(self, width, height):
        """Démarre l'enregistrement vidéo"""
        if not self.recording:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"videos/recording_{timestamp}.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (width, height))
            self.recording = True
            print(f"🔴 Enregistrement démarré: {filename}")
    
    def stop_recording(self):
        """Arrête l'enregistrement vidéo"""
        if self.recording and self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
            self.recording = False
            print("⏹️ Enregistrement arrêté")
    
    def start_realtime_logging(self):
        """Démarre la sauvegarde en temps réel des données"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"data_logs/detection_log_{timestamp}.csv"
        
        self.realtime_data_file = open(csv_filename, 'w', newline='', encoding='utf-8')
        self.realtime_csv_writer = csv.writer(self.realtime_data_file)
        
        # Écrire l'en-tête du CSV
        self.realtime_csv_writer.writerow([
            'Timestamp',
            'Bouteille_Existe',
            'Nombre_Bouteilles',
            'Bouteille_Remplie',
            'Bouteille_Avec_Bouchon'
        ])
        

    
    def stop_realtime_logging(self):
        """Arrête la sauvegarde en temps réel"""
        if self.realtime_data_file is not None:
            self.realtime_data_file.close()
            self.realtime_data_file = None
            self.realtime_csv_writer = None

    
    def save_realtime_data(self, bottle_exists, num_bottles, is_filled, has_cap):
        """Sauvegarde désactivée."""
        return
    
    def _detection_worker(self, input_q, result_q, stop_event):
        """Thread GPU : détection + segmentation en continu."""
        _no_det_count = 0   # frames consécutives sans bouteille
        _RESET_AFTER  = 8   # grace period avant reset de l'état
        while not stop_event.is_set():
            try:
                frame = input_q.get(timeout=0.05)
            except _queue.Empty:
                continue

            frame_left, num_det, total_caps, current_cap_has_cap, bottle_detected, bottle_boxes = \
                self.process_detection(frame.copy())

            if bottle_detected:
                _no_det_count = 0   # bouteille vue → reset compteur
                frame_right, num_seg, water_pct, current_bottle_id = \
                    self.process_segmentation(frame.copy(), bottle_boxes)
            else:
                _no_det_count += 1
                frame_right = np.zeros_like(frame)
                num_seg, water_pct, current_bottle_id = 0, 0.0, None
                h, w = frame_right.shape[:2]
                overlay = frame_right.copy()
                cv2.rectangle(overlay, (w//2 - 200, h//2 - 40), (w//2 + 200, h//2 + 40), (50, 50, 50), -1)
                cv2.addWeighted(overlay, 0.8, frame_right, 0.2, 0, frame_right)
                cv2.putText(frame_right, "En attente de bouteille...", (w//2 - 180, h//2 + 10),
                            cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
                # Reset uniquement après grace period → évite reset sur faux-négatif YOLO
                if _no_det_count >= _RESET_AFTER:
                    self.global_fill_history.clear()
                    self.global_label_locked = False
                    self.global_locked_label = None
                    self._printed_status.clear()
                    self.bottle_label_locked.clear()
                    self.bottle_smoothed_label.clear()
                    self.bottle_cap_status.clear()
                    self.bottle_fill_status.clear()
                    self.fill_history.clear()
                    self.bottle_hysteresis_state.clear()
                    self.cap_history.clear()
                    self.cap_label_locked.clear()
                    self.global_cap_history.clear()
                    self.global_cap_locked = False
                    self.global_cap_locked_value = None

            result = (frame_left, frame_right, num_det, num_seg, water_pct,
                      current_bottle_id, current_cap_has_cap, bottle_detected, bottle_boxes, total_caps)
            # Toujours garder le résultat le plus récent
            if result_q.full():
                try:
                    result_q.get_nowait()
                except _queue.Empty:
                    pass
            try:
                result_q.put_nowait(result)
            except _queue.Full:
                pass

    def webcam_mode(self):
        """Mode webcam avec affichage simultané des 2 modèles"""
        cap = None
        for camera_index in [1, 0, 2]:
            cap = cv2.VideoCapture(camera_index)
            if cap.isOpened():
                break
            cap.release()
        
        if cap is None or not cap.isOpened():
            print("❌ Impossible d'ouvrir la webcam!")
            return
        
        # Configuration webcam haute résolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Vérifier la résolution réelle obtenue
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        window_name = 'Unified Bottle Detection - Dual Model'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1920, 1080)
        
        # Ajouter le callback pour les clics de souris
        cv2.setMouseCallback(window_name, self.mouse_callback)
        
        # Reset statistiques
        self.frame_count = 0
        self.start_time = time.time()
        
        # Démarrer la sauvegarde en temps réel
        self.start_realtime_logging()

        # === THREAD GPU : détection tourne en parallèle de l'affichage ===
        _input_q  = _queue.Queue(maxsize=1)
        _result_q = _queue.Queue(maxsize=1)
        _stop_ev  = threading.Event()
        _det_thread = threading.Thread(target=self._detection_worker,
                                       args=(_input_q, _result_q, _stop_ev),
                                       daemon=True)
        _det_thread.start()

        while True:
          try:
            if not self.paused:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Erreur lecture webcam")
                    break
                
                self.frame_skip_counter += 1

                # Envoyer la frame au thread GPU (non-bloquant, drop si déjà occupé)
                try:
                    _input_q.put_nowait(frame)
                except _queue.Full:
                    pass

                # Récupérer dernier résultat GPU disponible (non-bloquant)
                try:
                    (frame_left, frame_right, num_det, num_seg, water_pct,
                     current_bottle_id, current_cap_has_cap, bottle_detected,
                     bottle_boxes, total_caps) = _result_q.get_nowait()
                    self.cached_detection_frame = frame_left
                    self.cached_detection_data  = (num_det, total_caps, current_cap_has_cap, bottle_detected, bottle_boxes)
                    self.cached_segmentation_frame = frame_right
                    self.cached_segmentation_data  = (num_seg, water_pct, current_bottle_id)
                except _queue.Empty:
                    # GPU encore en train de traiter → utiliser dernier résultat en cache
                    frame_left = self.cached_detection_frame if self.cached_detection_frame is not None else frame.copy()
                    num_det, total_caps, current_cap_has_cap, bottle_detected, bottle_boxes = self.cached_detection_data
                    frame_right = self.cached_segmentation_frame if self.cached_segmentation_frame is not None else frame.copy()
                    num_seg, water_pct, current_bottle_id = self.cached_segmentation_data
                
                # Mettre à jour l'historique des pourcentages
                self.water_percentage_history.append(water_pct)
                if len(self.water_percentage_history) > self.history_size:
                    self.water_percentage_history.pop(0)  # Garder seulement les N dernières valeurs
                
                # S'assurer que les deux frames ont la même taille
                # (Important si transpose est activé sur le modèle de détection)
                if frame_left.shape != frame_right.shape:
                    # Redimensionner frame_left pour correspondre à frame_right
                    frame_left = cv2.resize(frame_left, (frame_right.shape[1], frame_right.shape[0]))
                
                # Calculer FPS
                self.calculate_fps()

                # Affichage terminal
                if bottle_detected and bottle_boxes:
                    current_ids = [box[4] for box in bottle_boxes if box[4] is not None]
                    if not current_ids:
                        current_ids = [0]  # fallback si ByteTrack n'a pas encore assigné d'ID
                    self._print_bottle_validity_status(current_ids, current_cap_has_cap)

                # Ajouter les infos sur chaque panneau
                self.draw_panel_info(frame_left, "DETECTION (Bottle+Cap)", 
                                    self.fps, self.confidence_detection, num_det, None, None, current_cap_has_cap, is_left=True)
                self.draw_panel_info(frame_right, "SEGMENTATION (Bottle+Water)", 
                                    self.fps, self.confidence_segmentation, num_seg, water_pct, current_bottle_id, None, is_left=False)
                
                # Combiner les deux frames côte à côte
                combined = np.hstack([frame_left, frame_right])
                
                # Sauvegarder les dimensions pour le callback souris
                h_combined, w_combined = combined.shape[:2]
                self.current_frame_size = (w_combined, h_combined)
                
                # Ajouter l'interface globale
                self.draw_combined_interface(combined, num_det, num_seg)
                
                # Enregistrer si actif
                if self.recording and self.video_writer is not None:
                    self.video_writer.write(combined)
                
                # Envoyer à Arduino (toutes les 5 secondes)
                self.check_and_send_arduino(bottle_detected, 1 if bottle_detected else 0,
                                            False, current_cap_has_cap if current_cap_has_cap is not None else False)
                
                current_frame = combined
            
            # Afficher
            cv2.imshow(window_name, current_frame)
            
            # Gestion clavier (waitKey plus court pour meilleure réactivité)
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27 or key == ord('q'):  # ESC ou Q
                break
            elif key == ord(' '):  # SPACE - Pause
                self.paused = not self.paused
                print(f"{'⏸️ PAUSE' if self.paused else '▶️ REPRISE'}")
            elif key == ord('s'):  # S - Screenshot
                self.save_screenshot(current_frame)
            elif key == ord('r'):  # R - Recording
                if not self.recording:
                    h, w = current_frame.shape[:2]
                    self.start_recording(w, h)
                else:
                    self.stop_recording()
            elif key == ord('t'):  # T - Transpose
                self.transpose_image = not self.transpose_image
                print(f"🔄 Transpose: {'ON' if self.transpose_image else 'OFF'}")
            elif key == ord('h'):  # H - Help
                self.show_help = not self.show_help
            elif key == ord('+') or key == ord('='):  # + - Augmenter confiance
                self.confidence_detection = min(0.95, self.confidence_detection + 0.05)
                self.confidence_segmentation = min(0.95, self.confidence_segmentation + 0.05)
                print(f"⬆️ Confidence: Det={self.confidence_detection:.2f}, Seg={self.confidence_segmentation:.2f}")
            elif key == ord('-') or key == ord('_'):  # - - Diminuer confiance
                self.confidence_detection = max(0.1, self.confidence_detection - 0.05)
                self.confidence_segmentation = max(0.1, self.confidence_segmentation - 0.05)
                print(f"⬇️ Confidence: Det={self.confidence_detection:.2f}, Seg={self.confidence_segmentation:.2f}")
          except Exception as e:
            import traceback
            print(f"\n❌ ERREUR dans la boucle: {type(e).__name__}: {e}")
            traceback.print_exc()
            break
        
        # Nettoyage
        _stop_ev.set()
        _det_thread.join(timeout=2.0)

        if self.recording:
            self.stop_recording()
        
        # Arrêter la sauvegarde en temps réel
        self.stop_realtime_logging()
        
        # Fermer la connexion Arduino
        self.close_arduino()
        
        cap.release()
        cv2.destroyAllWindows()
        print("👋 Interface fermée")
    
    def single_image_mode(self):
        """Mode image unique avec les 2 modèles"""
        print("\n🖼️ Mode IMAGE UNIQUE")
        print("📁 Entrez le chemin de l'image:")
        
        image_path = input("Chemin: ").strip().strip('"').strip("'")
        
        if not os.path.exists(image_path):
            print(f"❌ Image introuvable: {image_path}")
            return
        
        # Charger image
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"❌ Impossible de lire l'image: {image_path}")
            return
        
        print(f"✅ Image chargée: {frame.shape}")
        print("🔄 Application des modèles...")
        
        # Appliquer les deux modèles
        frame_left, num_det, total_caps, current_cap_has_cap, bottle_detected, bottle_boxes = self.process_detection(frame.copy())

        # Appliquer segmentation uniquement si bouteille détectée
        if bottle_detected:
            frame_right, num_seg, water_pct, current_bottle_id = self.process_segmentation(frame.copy(), bottle_boxes)
        else:
            frame_right = frame.copy()
            num_seg, water_pct, current_bottle_id = 0, 0.0, None
            h, w = frame_right.shape[:2]
            cv2.putText(frame_right, "Aucune bouteille detectee", (w//2 - 150, h//2), 
                       cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 255), 2)
        
        # Ajouter les infos
        self.draw_panel_info(frame_left, "DETECTION (Bottle+Cap)", 
                            0, self.confidence_detection, num_det, None, None, current_cap_has_cap, is_left=True)
        self.draw_panel_info(frame_right, "SEGMENTATION (Bottle+Water)", 
                            0, self.confidence_segmentation, num_seg, water_pct, current_bottle_id, None, is_left=False)
        
        # Combiner
        combined = np.hstack([frame_left, frame_right])
        self.draw_combined_interface(combined, num_det, num_seg)
        
        # Afficher
        window_name = f'Unified Detection - {os.path.basename(image_path)}'
        cv2.imshow(window_name, combined)
        
        print("✅ Résultat affiché")
        print("💾 Appuyez sur 'S' pour sauvegarder, ou n'importe quelle touche pour fermer")
        
        key = cv2.waitKey(0) & 0xFF
        
        if key == ord('s'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"results/result_{timestamp}_{os.path.basename(image_path)}"
            cv2.imwrite(output_path, combined)
            print(f"💾 Résultat sauvegardé: {output_path}")
        
        cv2.destroyAllWindows()
    
    def folder_mode(self):
        """Mode dossier avec les 2 modèles"""
        print("\n📁 Mode DOSSIER MULTIPLE")
        print("📂 Entrez le chemin du dossier:")
        
        folder_path = input("Chemin: ").strip().strip('"').strip("'")
        
        if not os.path.exists(folder_path):
            print(f"❌ Dossier introuvable: {folder_path}")
            return
        
        # Liste des images
        extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        image_files = []
        
        for ext in extensions:
            image_files.extend(list(Path(folder_path).glob(f'*{ext}')))
            image_files.extend(list(Path(folder_path).glob(f'*{ext.upper()}')))
        
        if len(image_files) == 0:
            print(f"❌ Aucune image trouvée dans: {folder_path}")
            return
        
        print(f"✅ {len(image_files)} images trouvées")
        print("🔄 Traitement en cours...")
        
        # Créer sous-dossier pour les résultats
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_folder = f"results/batch_{timestamp}"
        os.makedirs(output_folder, exist_ok=True)
        
        for i, image_path in enumerate(image_files, 1):
            print(f"   [{i}/{len(image_files)}] {image_path.name}...", end='')
            
            # Charger image
            frame = cv2.imread(str(image_path))
            if frame is None:
                print(" ❌ Erreur lecture")
                continue
            
            # Appliquer les modèles
            frame_left, num_det, total_caps, current_cap_has_cap, bottle_detected, bottle_boxes = self.process_detection(frame.copy())

            # Appliquer segmentation uniquement si bouteille détectée
            if bottle_detected:
                frame_right, num_seg, water_pct, current_bottle_id = self.process_segmentation(frame.copy(), bottle_boxes)
                frame_right = frame.copy()
                num_seg, water_pct, current_bottle_id = 0, 0.0, None
            
            # Ajouter infos
            self.draw_panel_info(frame_left, "DETECTION", 0, self.confidence_detection, num_det, None, None, current_cap_has_cap)
            self.draw_panel_info(frame_right, "SEGMENTATION", 0, self.confidence_segmentation, num_seg, water_pct, current_bottle_id, None)
            
            # Combiner
            combined = np.hstack([frame_left, frame_right])
            self.draw_combined_interface(combined, num_det, num_seg)
            
            # Sauvegarder
            output_path = os.path.join(output_folder, f"unified_{image_path.name}")
            cv2.imwrite(output_path, combined)
            
            print(f" ✅ Det:{num_det} Seg:{num_seg}")
        
        print(f"\n✅ Traitement terminé!")
        print(f"📁 Résultats sauvegardés dans: {output_folder}")


def main():
    """Point d'entrée principal"""
    print("\n" + "=" * 70)
    print("🍶 UNIFIED BOTTLE DETECTION SYSTEM")
    print("   Affichage simultané: Détection (Bottle+Cap) | Segmentation (Bottle+Water)")
    print("=" * 70)
    
    # Initialiser
    detector = UnifiedBottleDetection()
    
    if detector.model_detection is None or detector.model_segmentation is None:
        print("\n❌ Les modèles n'ont pas pu être chargés correctement.")
        print("💡 Vérifiez les chemins vers les fichiers .pt")
        input("\nAppuyez sur Entrée pour quitter...")
        return
    
    detector.webcam_mode()



if __name__ == "__main__":
    # Forcer le flush immédiat de stdout (affichage terminal en temps réel)
    sys.stdout.reconfigure(line_buffering=True)
    # Se placer dans le dossier du script pour que les chemins relatifs fonctionnent
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Programme interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        input("\nAppuyez sur Entrée pour quitter...")
