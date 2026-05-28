# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-05-28

### Added
- Unified bottle detection system combining multiple detection models
- Real-time bottle detection from webcam/video feeds
- Bottle classification (full/empty) using ResNet50V2
- YOLOv8-based bounding box detection
- Segmentation capabilities with YOLOv8
- CSV logging of detection results
- Real-time status JSON output
- Confusion matrix and metrics evaluation
- Multi-model analysis and comparison

### Features
- **Detection Module**: YOLOv8-based bounding box and segmentation
- **Classification Module**: ResNet50V2 for full/empty classification
- **Real-time Processing**: Live webcam support
- **Data Logging**: CSV and JSON output formats
- **Evaluation Tools**: Metrics and confusion matrix analysis

### Technical Details
- Python 3.x
- OpenCV for video processing
- PyTorch/TensorFlow for deep learning
- YOLOv8 for detection and segmentation
- ResNet50V2 for classification

## [0.1.0] - Initial Development

### Initial Setup
- Project structure created
- Model training pipeline established
- Data preprocessing tools developed
