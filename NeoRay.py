import sys
import os
import json
import configparser
import requests
import random
import math
import shutil
import platform
import subprocess
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QProgressBar, QScrollArea, QFrame, QCheckBox,
    QLineEdit, QDoubleSpinBox, QSpinBox, QGroupBox, QMessageBox,
    QStackedWidget, QListWidget, QListWidgetItem, QComboBox, QSlider,
    QTextEdit, QFormLayout, QInputDialog, QSplitter, QGridLayout, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPointF, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient, QKeySequence, QShortcut, QRadialGradient, QIcon

def app_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent

PORTABLE_FLAG = app_base_dir() / "portable.flag"
APP_DIR = (app_base_dir() / "neoray_data") if PORTABLE_FLAG.exists() else (Path.home() / ".neoray")
APP_DIR.mkdir(parents=True, exist_ok=True)
LIBRARY_FILE = APP_DIR / "library.json"
SETTINGS_FILE = APP_DIR / "app_settings.json"
BACKUPS_DIR = APP_DIR / "backups"
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

REPO = "857seif/NeoRay"
FG_API = f"https://api.github.com/repos/{REPO}/contents/DB/FG"
DLSS_API = f"https://api.github.com/repos/{REPO}/contents/DB/dls5"
MEDIA_BASE = f"https://media.githubusercontent.com/media/{REPO}/main/"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/main/"
REPO_COMMITS = f"https://api.github.com/repos/{REPO}/commits/main"

FG_MARKERS = ["version.dll", "OptiScaler.ini", "amd_fidelityfx_framegeneration_dx12.dll"]
DLSS_MARKERS = ["nvngx_dlss.dll", "nvngx_dlssnr.dll"]
ALL_MODULE_FILES = list(dict.fromkeys(FG_MARKERS + DLSS_MARKERS + [
    "amd_fidelityfx_dx12.dll", "amd_fidelityfx_upscaler_dx12.dll", "amd_fidelityfx_vk.dll",
    "dlssg_to_fsr3_amd_is_better.dll", "fakenvapi.dll", "fakenvapi.ini",
    "nvngx_dlssnr.dll", "renodx-dlss5.addon64"
]))

GPU_SPOOF = {
    # ===== NVIDIA RTX 50 Series =====
    "RTX 5090": ("0x10DE", "0x2B85", "NVIDIA GeForce RTX 5090"),
    "RTX 5080": ("0x10DE", "0x2B80", "NVIDIA GeForce RTX 5080"),
    "RTX 5070 Ti": ("0x10DE", "0x2B87", "NVIDIA GeForce RTX 5070 Ti"),
    "RTX 5070": ("0x10DE", "0x2B86", "NVIDIA GeForce RTX 5070"),
    "RTX 5060 Ti": ("0x10DE", "0x2B88", "NVIDIA GeForce RTX 5060 Ti"),
    "RTX 5060": ("0x10DE", "0x2B89", "NVIDIA GeForce RTX 5060"),
    # ===== NVIDIA RTX 40 Series =====
    "RTX 4090": ("0x10DE", "0x2684", "NVIDIA GeForce RTX 4090"),
    "RTX 4090 D": ("0x10DE", "0x2685", "NVIDIA GeForce RTX 4090 D"),
    "RTX 4080 SUPER": ("0x10DE", "0x2702", "NVIDIA GeForce RTX 4080 SUPER"),
    "RTX 4080": ("0x10DE", "0x2704", "NVIDIA GeForce RTX 4080"),
    "RTX 4070 Ti SUPER": ("0x10DE", "0x2705", "NVIDIA GeForce RTX 4070 Ti SUPER"),
    "RTX 4070 Ti": ("0x10DE", "0x2782", "NVIDIA GeForce RTX 4070 Ti"),
    "RTX 4070 SUPER": ("0x10DE", "0x2783", "NVIDIA GeForce RTX 4070 SUPER"),
    "RTX 4070": ("0x10DE", "0x2786", "NVIDIA GeForce RTX 4070"),
    "RTX 4060 Ti 16GB": ("0x10DE", "0x2805", "NVIDIA GeForce RTX 4060 Ti"),
    "RTX 4060 Ti 8GB": ("0x10DE", "0x2803", "NVIDIA GeForce RTX 4060 Ti"),
    "RTX 4060": ("0x10DE", "0x2882", "NVIDIA GeForce RTX 4060"),
    "RTX 4050 Laptop": ("0x10DE", "0x28E1", "NVIDIA GeForce RTX 4050 Laptop GPU"),
    "RTX 4060 Laptop": ("0x10DE", "0x28E0", "NVIDIA GeForce RTX 4060 Laptop GPU"),
    "RTX 4070 Laptop": ("0x10DE", "0x2860", "NVIDIA GeForce RTX 4070 Laptop GPU"),
    "RTX 4080 Laptop": ("0x10DE", "0x27A0", "NVIDIA GeForce RTX 4080 Laptop GPU"),
    "RTX 4090 Laptop": ("0x10DE", "0x2717", "NVIDIA GeForce RTX 4090 Laptop GPU"),
    # ===== NVIDIA RTX 30 Series =====
    "RTX 3090 Ti": ("0x10DE", "0x2203", "NVIDIA GeForce RTX 3090 Ti"),
    "RTX 3090": ("0x10DE", "0x2204", "NVIDIA GeForce RTX 3090"),
    "RTX 3080 Ti": ("0x10DE", "0x2208", "NVIDIA GeForce RTX 3080 Ti"),
    "RTX 3080 12GB": ("0x10DE", "0x2216", "NVIDIA GeForce RTX 3080"),
    "RTX 3080 10GB": ("0x10DE", "0x2206", "NVIDIA GeForce RTX 3080"),
    "RTX 3070 Ti": ("0x10DE", "0x2482", "NVIDIA GeForce RTX 3070 Ti"),
    "RTX 3070": ("0x10DE", "0x2484", "NVIDIA GeForce RTX 3070"),
    "RTX 3060 Ti": ("0x10DE", "0x2486", "NVIDIA GeForce RTX 3060 Ti"),
    "RTX 3060 12GB": ("0x10DE", "0x2503", "NVIDIA GeForce RTX 3060"),
    "RTX 3060 8GB": ("0x10DE", "0x2504", "NVIDIA GeForce RTX 3060"),
    "RTX 3050": ("0x10DE", "0x2507", "NVIDIA GeForce RTX 3050"),
    "RTX 3050 Laptop": ("0x10DE", "0x25A2", "NVIDIA GeForce RTX 3050 Laptop GPU"),
    "RTX 3060 Laptop": ("0x10DE", "0x2520", "NVIDIA GeForce RTX 3060 Laptop GPU"),
    "RTX 3070 Laptop": ("0x10DE", "0x249D", "NVIDIA GeForce RTX 3070 Laptop GPU"),
    "RTX 3080 Laptop": ("0x10DE", "0x249C", "NVIDIA GeForce RTX 3080 Laptop GPU"),
    # ===== NVIDIA RTX 20 Series =====
    "RTX 2080 Ti": ("0x10DE", "0x1E07", "NVIDIA GeForce RTX 2080 Ti"),
    "RTX 2080 SUPER": ("0x10DE", "0x1E81", "NVIDIA GeForce RTX 2080 SUPER"),
    "RTX 2080": ("0x10DE", "0x1E82", "NVIDIA GeForce RTX 2080"),
    "RTX 2070 SUPER": ("0x10DE", "0x1E84", "NVIDIA GeForce RTX 2070 SUPER"),
    "RTX 2070": ("0x10DE", "0x1F02", "NVIDIA GeForce RTX 2070"),
    "RTX 2060 SUPER": ("0x10DE", "0x1F06", "NVIDIA GeForce RTX 2060 SUPER"),
    "RTX 2060 12GB": ("0x10DE", "0x1F03", "NVIDIA GeForce RTX 2060"),
    "RTX 2060 6GB": ("0x10DE", "0x1F08", "NVIDIA GeForce RTX 2060"),
    "RTX 2050 Laptop": ("0x10DE", "0x25A9", "NVIDIA GeForce RTX 2050"),
    # ===== NVIDIA GTX 16 Series =====
    "GTX 1660 Ti": ("0x10DE", "0x2182", "NVIDIA GeForce GTX 1660 Ti"),
    "GTX 1660 SUPER": ("0x10DE", "0x21C4", "NVIDIA GeForce GTX 1660 SUPER"),
    "GTX 1660": ("0x10DE", "0x2184", "NVIDIA GeForce GTX 1660"),
    "GTX 1650 SUPER": ("0x10DE", "0x2187", "NVIDIA GeForce GTX 1650 SUPER"),
    "GTX 1650": ("0x10DE", "0x1F82", "NVIDIA GeForce GTX 1650"),
    "GTX 1630": ("0x10DE", "0x1F9F", "NVIDIA GeForce GTX 1630"),
    # ===== NVIDIA GTX 10 Series =====
    "GTX 1080 Ti": ("0x10DE", "0x1B06", "NVIDIA GeForce GTX 1080 Ti"),
    "GTX 1080": ("0x10DE", "0x1B80", "NVIDIA GeForce GTX 1080"),
    "GTX 1070 Ti": ("0x10DE", "0x1B82", "NVIDIA GeForce GTX 1070 Ti"),
    "GTX 1070": ("0x10DE", "0x1B81", "NVIDIA GeForce GTX 1070"),
    "GTX 1060 6GB": ("0x10DE", "0x1C03", "NVIDIA GeForce GTX 1060 6GB"),
    "GTX 1060 3GB": ("0x10DE", "0x1C02", "NVIDIA GeForce GTX 1060 3GB"),
    "GTX 1050 Ti": ("0x10DE", "0x1C82", "NVIDIA GeForce GTX 1050 Ti"),
    "GTX 1050": ("0x10DE", "0x1C81", "NVIDIA GeForce GTX 1050"),
    # ===== NVIDIA GTX 900 Series =====
    "GTX 980 Ti": ("0x10DE", "0x17C8", "NVIDIA GeForce GTX 980 Ti"),
    "GTX 980": ("0x10DE", "0x13C0", "NVIDIA GeForce GTX 980"),
    "GTX 970": ("0x10DE", "0x13C2", "NVIDIA GeForce GTX 970"),
    "GTX 960": ("0x10DE", "0x1401", "NVIDIA GeForce GTX 960"),
    "GTX 950": ("0x10DE", "0x1402", "NVIDIA GeForce GTX 950"),
    # ===== NVIDIA Titan / Pro =====
    "TITAN RTX": ("0x10DE", "0x1E02", "NVIDIA TITAN RTX"),
    "TITAN V": ("0x10DE", "0x1D81", "NVIDIA TITAN V"),
    "TITAN Xp": ("0x10DE", "0x1B02", "NVIDIA TITAN Xp"),
    "TITAN X Pascal": ("0x10DE", "0x1B00", "NVIDIA TITAN X"),
    "RTX A6000": ("0x10DE", "0x2230", "NVIDIA RTX A6000"),
    "RTX A5000": ("0x10DE", "0x2231", "NVIDIA RTX A5000"),
    "RTX A4000": ("0x10DE", "0x24B0", "NVIDIA RTX A4000"),
    "RTX 6000 Ada": ("0x10DE", "0x26B1", "NVIDIA RTX 6000 Ada Generation"),
    "RTX 4000 Ada": ("0x10DE", "0x27B2", "NVIDIA RTX 4000 Ada Generation"),
    "Quadro RTX 8000": ("0x10DE", "0x1E30", "NVIDIA Quadro RTX 8000"),
    "Quadro RTX 6000": ("0x10DE", "0x1E36", "NVIDIA Quadro RTX 6000"),
    # ===== AMD RX 8000 / 9000 =====
    "RX 9070 XT": ("0x1002", "0x7550", "AMD Radeon RX 9070 XT"),
    "RX 9070": ("0x1002", "0x7551", "AMD Radeon RX 9070"),
    "RX 9060 XT": ("0x1002", "0x7590", "AMD Radeon RX 9060 XT"),
    # ===== AMD RX 7000 Series =====
    "RX 7900 XTX": ("0x1002", "0x744C", "AMD Radeon RX 7900 XTX"),
    "RX 7900 XT": ("0x1002", "0x7448", "AMD Radeon RX 7900 XT"),
    "RX 7900 GRE": ("0x1002", "0x744B", "AMD Radeon RX 7900 GRE"),
    "RX 7800 XT": ("0x1002", "0x747E", "AMD Radeon RX 7800 XT"),
    "RX 7700 XT": ("0x1002", "0x7470", "AMD Radeon RX 7700 XT"),
    "RX 7600 XT": ("0x1002", "0x7480", "AMD Radeon RX 7600 XT"),
    "RX 7600": ("0x1002", "0x7483", "AMD Radeon RX 7600"),
    "RX 7700S": ("0x1002", "0x7481", "AMD Radeon RX 7700S"),
    "RX 7600S": ("0x1002", "0x7422", "AMD Radeon RX 7600S"),
    "RX 7600M XT": ("0x1002", "0x7420", "AMD Radeon RX 7600M XT"),
    # ===== AMD RX 6000 Series =====
    "RX 6950 XT": ("0x1002", "0x73A5", "AMD Radeon RX 6950 XT"),
    "RX 6900 XT": ("0x1002", "0x73BF", "AMD Radeon RX 6900 XT"),
    "RX 6800 XT": ("0x1002", "0x73BF", "AMD Radeon RX 6800 XT"),
    "RX 6800": ("0x1002", "0x73BF", "AMD Radeon RX 6800"),
    "RX 6750 XT": ("0x1002", "0x73DF", "AMD Radeon RX 6750 XT"),
    "RX 6700 XT": ("0x1002", "0x73DF", "AMD Radeon RX 6700 XT"),
    "RX 6700": ("0x1002", "0x73DF", "AMD Radeon RX 6700"),
    "RX 6650 XT": ("0x1002", "0x73EF", "AMD Radeon RX 6650 XT"),
    "RX 6600 XT": ("0x1002", "0x73FF", "AMD Radeon RX 6600 XT"),
    "RX 6600": ("0x1002", "0x73FF", "AMD Radeon RX 6600"),
    "RX 6500 XT": ("0x1002", "0x743F", "AMD Radeon RX 6500 XT"),
    "RX 6400": ("0x1002", "0x743F", "AMD Radeon RX 6400"),
    # ===== AMD RX 5000 Series =====
    "RX 5700 XT": ("0x1002", "0x731F", "AMD Radeon RX 5700 XT"),
    "RX 5700": ("0x1002", "0x731F", "AMD Radeon RX 5700"),
    "RX 5600 XT": ("0x1002", "0x731F", "AMD Radeon RX 5600 XT"),
    "RX 5500 XT": ("0x1002", "0x7340", "AMD Radeon RX 5500 XT"),
    # ===== AMD RX 500 Series =====
    "RX 590": ("0x1002", "0x67DF", "AMD Radeon RX 590"),
    "RX 580": ("0x1002", "0x67DF", "AMD Radeon RX 580"),
    "RX 570": ("0x1002", "0x67DF", "AMD Radeon RX 570"),
    "RX 560": ("0x1002", "0x67EF", "AMD Radeon RX 560"),
    "RX 550": ("0x1002", "0x699F", "AMD Radeon RX 550"),
    # ===== AMD RX Vega =====
    "RX Vega 64": ("0x1002", "0x687F", "AMD Radeon RX Vega 64"),
    "RX Vega 56": ("0x1002", "0x687F", "AMD Radeon RX Vega 56"),
    "Radeon VII": ("0x1002", "0x66AF", "AMD Radeon VII"),
    # ===== AMD RX 600M / iGPU-ish =====
    "RX 6800M": ("0x1002", "0x73DF", "AMD Radeon RX 6800M"),
    "RX 6700M": ("0x1002", "0x73DF", "AMD Radeon RX 6700M"),
    "RX 6600M": ("0x1002", "0x73FF", "AMD Radeon RX 6600M"),
    "RX 6500M": ("0x1002", "0x73FF", "AMD Radeon RX 6500M"),
}

QUALITY_PROFILES = {
    "Ultra Quality": {"QualityOverrides": {"QualityRatioOverrideEnabled": "true", "QualityRatioUltraQuality": "1.3"}, "FrameGen": {"Enabled": "true"}, "Sharpness": {"OverrideSharpness": "true", "Sharpness": "0.25"}},
    "Quality": {"QualityOverrides": {"QualityRatioOverrideEnabled": "true", "QualityRatioQuality": "1.5"}, "FrameGen": {"Enabled": "true"}, "Sharpness": {"OverrideSharpness": "true", "Sharpness": "0.3"}},
    "Balanced": {"QualityOverrides": {"QualityRatioOverrideEnabled": "true", "QualityRatioBalanced": "1.7"}, "FrameGen": {"Enabled": "true"}, "Sharpness": {"OverrideSharpness": "true", "Sharpness": "0.35"}},
    "Performance": {"QualityOverrides": {"QualityRatioOverrideEnabled": "true", "QualityRatioPerformance": "2.0"}, "FrameGen": {"Enabled": "true"}, "Sharpness": {"OverrideSharpness": "true", "Sharpness": "0.4"}},
    "Ultra Performance": {"QualityOverrides": {"QualityRatioOverrideEnabled": "true", "QualityRatioUltraPerformance": "3.0"}, "FrameGen": {"Enabled": "true"}, "Sharpness": {"OverrideSharpness": "true", "Sharpness": "0.5"}},
    "Native AA": {"QualityOverrides": {"QualityRatioOverrideEnabled": "true", "QualityRatioDLAA": "1.0"}, "FrameGen": {"Enabled": "true"}, "Sharpness": {"OverrideSharpness": "true", "Sharpness": "0.2"}},
    "FG Off": {"FrameGen": {"Enabled": "false"}},
    "Max FG Smooth": {"FrameGen": {"Enabled": "true", "AllowedFrameAhead": "1", "PreserveSwapChain": "true"}, "FSRFG": {"AllowAsync": "true", "FramePacingTuning": "true", "FPTSafetyMarginInMs": "0.01"}},
}

THEMES = {
    "gold": {
        "primary": "#ffd700", "primary_dim": "#daa520", "primary_dark": "#b8860b",
        "accent": "#ffe566", "bg": "#0c0a05", "bg2": "#1a1508", "card": "rgba(40,30,5,190)",
        "text": "#ffe9a0", "border": "#c9a227", "particle": (255, 200, 40), "glow": (255, 215, 80)
    },
    "orange": {
        "primary": "#ff8c00", "primary_dim": "#e67300", "primary_dark": "#cc6600",
        "accent": "#ffb347", "bg": "#0c0805", "bg2": "#1a1008", "card": "rgba(40,20,5,190)",
        "text": "#ffd4a0", "border": "#cc7722", "particle": (255, 140, 30), "glow": (255, 160, 60)
    },
    "amber": {
        "primary": "#ffbf00", "primary_dim": "#e6a800", "primary_dark": "#cc9200",
        "accent": "#ffd54f", "bg": "#0d0b04", "bg2": "#1a1606", "card": "rgba(35,28,5,190)",
        "text": "#ffe9a8", "border": "#d4a017", "particle": (255, 191, 0), "glow": (255, 210, 50)
    },
    "rose": {
        "primary": "#ff4d6d", "primary_dim": "#e63950", "primary_dark": "#c9184a",
        "accent": "#ff8fa3", "bg": "#0f0508", "bg2": "#1a0a10", "card": "rgba(40,10,18,190)",
        "text": "#ffb3c1", "border": "#c9184a", "particle": (255, 77, 109), "glow": (255, 120, 140)
    },
    "crimson": {
        "primary": "#dc143c", "primary_dim": "#b01030", "primary_dark": "#8b0a24",
        "accent": "#ff6b81", "bg": "#0c0406", "bg2": "#18080c", "card": "rgba(35,8,12,190)",
        "text": "#ffc9d1", "border": "#a01030", "particle": (220, 20, 60), "glow": (255, 60, 90)
    },
    "purple": {
        "primary": "#c44dff", "primary_dim": "#a020f0", "primary_dark": "#8b00cc",
        "accent": "#e0a0ff", "bg": "#0a0510", "bg2": "#140a1a", "card": "rgba(30,10,40,190)",
        "text": "#e8c4ff", "border": "#9933cc", "particle": (180, 70, 255), "glow": (200, 100, 255)
    },
    "violet": {
        "primary": "#9b59ff", "primary_dim": "#7c3aed", "primary_dark": "#6d28d9",
        "accent": "#c4b5fd", "bg": "#080510", "bg2": "#120a1c", "card": "rgba(25,10,45,190)",
        "text": "#ddd6fe", "border": "#7c3aed", "particle": (155, 89, 255), "glow": (180, 120, 255)
    },
    "magenta": {
        "primary": "#ff00aa", "primary_dim": "#d4008f", "primary_dark": "#aa0072",
        "accent": "#ff66cc", "bg": "#0c0510", "bg2": "#180a18", "card": "rgba(35,8,30,190)",
        "text": "#ffb3e0", "border": "#cc0088", "particle": (255, 0, 170), "glow": (255, 80, 200)
    },
    "cyan": {
        "primary": "#00e5ff", "primary_dim": "#00b8d4", "primary_dark": "#0097a7",
        "accent": "#84ffff", "bg": "#041014", "bg2": "#081820", "card": "rgba(5,30,40,190)",
        "text": "#b2ebf2", "border": "#00838f", "particle": (0, 229, 255), "glow": (80, 240, 255)
    },
    "teal": {
        "primary": "#1de9b6", "primary_dim": "#00bfa5", "primary_dark": "#00897b",
        "accent": "#64ffda", "bg": "#04120e", "bg2": "#081a14", "card": "rgba(5,35,28,190)",
        "text": "#a7ffeb", "border": "#00897b", "particle": (29, 233, 182), "glow": (100, 255, 220)
    },
    "lime": {
        "primary": "#c6ff00", "primary_dim": "#aeea00", "primary_dark": "#827717",
        "accent": "#eeff41", "bg": "#0a1004", "bg2": "#121806", "card": "rgba(25,35,5,190)",
        "text": "#f0f4c3", "border": "#9e9d24", "particle": (198, 255, 0), "glow": (220, 255, 80)
    },
    "sky": {
        "primary": "#40c4ff", "primary_dim": "#00b0ff", "primary_dark": "#0091ea",
        "accent": "#80d8ff", "bg": "#050c14", "bg2": "#0a1520", "card": "rgba(8,25,40,190)",
        "text": "#b3e5fc", "border": "#0277bd", "particle": (64, 196, 255), "glow": (120, 210, 255)
    },
    "indigo": {
        "primary": "#7c4dff", "primary_dim": "#651fff", "primary_dark": "#5200db",
        "accent": "#b388ff", "bg": "#080614", "bg2": "#100c20", "card": "rgba(20,12,45,190)",
        "text": "#d1c4e9", "border": "#6200ea", "particle": (124, 77, 255), "glow": (160, 120, 255)
    },
    "coral": {
        "primary": "#ff6e40", "primary_dim": "#ff3d00", "primary_dark": "#dd2c00",
        "accent": "#ff9e80", "bg": "#100805", "bg2": "#1a1008", "card": "rgba(40,18,10,190)",
        "text": "#ffccbc", "border": "#bf360c", "particle": (255, 110, 64), "glow": (255, 140, 100)
    },
}
THEME_ORDER = list(THEMES.keys())


SETTINGS_OPTIONS = {
    "Dx11Upscaler": ["auto", "fsr22", "fsr21", "fsr22_12", "fsr21_12", "xess", "dlss", "fsr31"],
    "Dx12Upscaler": ["auto", "xess", "fsr21", "fsr22", "fsr31", "dlss"],
    "VulkanUpscaler": ["auto", "fsr21", "fsr22", "fsr31", "xess"],
    "FGInput": ["auto", "nukems", "fsr3", "optifg", "xefg", "dlssg"],
    "FGOutput": ["auto", "fsrfg", "xefg", "nukems", "optifg"],
    "Fsr4Preset": ["auto", "native", "quality", "balanced", "performance", "ultra_performance"],
    "RoundInternalResolution": ["auto", "2", "4", "8", "16"],
    "SkipFirstFrames": ["auto", "0", "1", "2", "3", "5", "10"],
    "AllowedFrameAhead": ["auto", "1", "2", "3"],
    "AnisotropyOverride": ["auto", "1", "2", "4", "8", "16"],
    "MipmapBiasOverride": ["auto", "-1.0", "-0.5", "0", "0.5", "1.0", "1.5", "2.0"],
    "ForceVsync": ["auto", "true", "false"],
    "SyncInterval": ["auto", "0", "1", "2", "3", "4"],
    "ColorResourceBarrier": ["auto", "0", "1", "2", "3", "4", "5"],
    "MotionVectorResourceBarrier": ["auto", "0", "1", "2", "3", "4", "5"],
    "DepthResourceBarrier": ["auto", "0", "1", "2", "3", "4", "5"],
    "ColorMaskResourceBarrier": ["auto", "0", "1", "2", "3", "4", "5"],
    "ExposureResourceBarrier": ["auto", "0", "1", "2", "3", "4", "5"],
    "OutputResourceBarrier": ["auto", "0", "1", "2", "3", "4", "5"],
    "NetworkModel": ["auto", "0", "1", "2", "3", "4", "5"],
    "UpscalerIndex": ["auto", "0", "1", "2", "3"],
    "FGIndex": ["auto", "0", "1", "2"],
    "Downscaler": ["auto", "0", "1", "2"],
    "LogLevel": ["0", "1", "2", "3"],
    "AutoExposure": ["auto", "true", "false"],
    "HDR": ["auto", "true", "false"],
    "DepthInverted": ["auto", "true", "false"],
    "JitterCancellation": ["auto", "true", "false"],
    "DisplayResolution": ["auto", "true", "false"],
    "DisableReactiveMask": ["auto", "true", "false"],
    "DxgiBlacklist": ["auto"],
    "DxgiVRAM": ["auto"],
    "VulkanVRAM": ["auto"],
    "TargetVendorId": ["auto", "0x10DE", "0x1002", "0x8086"],
    "TargetDeviceId": ["auto"],
    "Path": ["auto"],
    "TargetProcessName": ["auto"],
    "ProcessExclusionList": ["auto"],
    "LogFileName": ["auto"],
}

class Particle:
    def __init__(self, w, h):
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.vx = random.uniform(-1.1, 1.1)
        self.vy = random.uniform(-1.1, 1.1)
        self.size = random.uniform(1.0, 4.2)
        self.alpha = random.uniform(50, 210)
        self.pulse = random.uniform(0, math.pi * 2)

    def update(self, w, h):
        self.x += self.vx
        self.y += self.vy
        self.pulse += 0.045
        if self.x < 0 or self.x > w: self.vx *= -1
        if self.y < 0 or self.y > h: self.vy *= -1
        self.x = max(0, min(w, self.x))
        self.y = max(0, min(h, self.y))

class ParticleBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_name = "gold"
        self.particles = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def set_theme(self, name):
        self.theme_name = name
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w, h = max(1, self.width()), max(1, self.height())
        if not self.particles:
            self.particles = [Particle(w, h) for _ in range(90)]
        else:
            for p in self.particles:
                p.x = min(p.x, w)
                p.y = min(p.y, h)

    def animate(self):
        w, h = max(1, self.width()), max(1, self.height())
        for p in self.particles:
            p.update(w, h)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        t = THEMES[self.theme_name]
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0, QColor(t["bg"]))
        grad.setColorAt(0.45, QColor(t["bg2"]))
        grad.setColorAt(1, QColor(t["bg"]))
        painter.fillRect(self.rect(), grad)
        cx, cy = self.width() / 2, self.height() / 3
        rg = QRadialGradient(cx, cy, max(self.width(), self.height()) * 0.55)
        pr, pg, pb = t["particle"]
        rg.setColorAt(0, QColor(pr, pg, pb, 28))
        rg.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), rg)
        gr, gg, gb = t["glow"]
        for p in self.particles:
            a = int(p.alpha * (0.5 + 0.5 * math.sin(p.pulse)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(pr, pg, pb, a)))
            painter.drawEllipse(QPointF(p.x, p.y), p.size, p.size)
            painter.setBrush(QBrush(QColor(gr, gg, gb, max(6, a // 5))))
            painter.drawEllipse(QPointF(p.x, p.y), p.size * 3.0, p.size * 3.0)
        for i, p1 in enumerate(self.particles):
            for p2 in self.particles[i + 1:i + 7]:
                dist = math.hypot(p1.x - p2.x, p1.y - p2.y)
                if dist < 130:
                    alpha = int(40 * (1 - dist / 130))
                    painter.setPen(QPen(QColor(pr, pg, pb, alpha), 1.2))
                    painter.drawLine(QPointF(p1.x, p1.y), QPointF(p2.x, p2.y))

def format_size(b):
    if b < 1024: return f"{b} B"
    if b < 1024 ** 2: return f"{b / 1024:.1f} KB"
    if b < 1024 ** 3: return f"{b / 1024 ** 2:.1f} MB"
    return f"{b / 1024 ** 3:.2f} GB"

def check_installed(folder, markers):
    return any(os.path.exists(os.path.join(folder, m)) for m in markers)

def load_json(path, default):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def detect_gpu():
    info = {"name": "Unknown", "vendor": "unknown", "is_rtx": False, "is_nvidia": False, "is_amd": False, "is_intel": False}
    try:
        if platform.system() == "Windows":
            out = subprocess.check_output('wmic path win32_VideoController get Name', shell=True, text=True, timeout=8, stderr=subprocess.DEVNULL)
            lines = [l.strip() for l in out.splitlines() if l.strip() and l.strip().lower() != "name"]
            if lines:
                info["name"] = lines[0]
        else:
            try:
                out = subprocess.check_output(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True, timeout=5)
                info["name"] = out.strip().split("\n")[0]
            except Exception:
                try:
                    out = subprocess.check_output("lspci 2>/dev/null | grep -iE 'vga|3d|display'", shell=True, text=True, timeout=5)
                    info["name"] = out.strip().split("\n")[0]
                except Exception:
                    pass
    except Exception:
        pass
    n = info["name"].lower()
    if any(x in n for x in ("nvidia", "geforce", "rtx", "gtx", "quadro")):
        info["is_nvidia"] = True
        info["vendor"] = "nvidia"
        if "rtx" in n:
            info["is_rtx"] = True
    elif any(x in n for x in ("amd", "radeon", "rx ")):
        info["is_amd"] = True
        info["vendor"] = "amd"
    elif "intel" in n or "arc" in n:
        info["is_intel"] = True
        info["vendor"] = "intel"
    return info

def read_ini(path):
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    if os.path.exists(path):
        cfg.read(path, encoding="utf-8")
    return cfg

def write_ini(path, cfg):
    with open(path, "w", encoding="utf-8") as f:
        cfg.write(f)

def ensure_section(cfg, section):
    if not cfg.has_section(section):
        cfg.add_section(section)

def apply_profile_to_ini(ini_path, profile_dict):
    cfg = read_ini(ini_path)
    for section, keys in profile_dict.items():
        ensure_section(cfg, section)
        for k, v in keys.items():
            cfg.set(section, k, str(v))
    write_ini(ini_path, cfg)

def list_repo_files(api_url, rel=""):
    files = []
    r = requests.get(api_url, timeout=30, headers={"Accept": "application/vnd.github+json"})
    r.raise_for_status()
    for item in r.json():
        name = item["name"]
        path = f"{rel}/{name}" if rel else name
        full_repo_path = item["path"]
        if item["type"] == "file":
            size = item.get("size", 0)
            url = item.get("download_url") or (RAW_BASE + full_repo_path)
            # Only treat as LFS when API returns null download_url or content is pointer
            # Small text/ini/dll that are NOT LFS must stay on raw.githubusercontent.com
            is_lfs = False
            if item.get("download_url") is None:
                is_lfs = True
            elif size < 1024 and url and "raw.githubusercontent.com" in url:
                try:
                    head = requests.get(url, timeout=15, stream=True)
                    chunk = next(head.iter_content(256), b"")
                    if b"git-lfs" in chunk or chunk.startswith(b"version https://git-lfs"):
                        is_lfs = True
                except Exception:
                    pass
            if is_lfs:
                url = MEDIA_BASE + full_repo_path
                try:
                    hr = requests.head(url, timeout=15, allow_redirects=True)
                    cl = hr.headers.get("Content-Length")
                    if cl:
                        size = int(cl)
                    elif hr.status_code == 404:
                        # fallback raw
                        url = RAW_BASE + full_repo_path
                except Exception:
                    url = RAW_BASE + full_repo_path
            files.append({"path": path, "url": url, "size": size, "repo_path": full_repo_path})
        elif item["type"] == "dir":
            files.extend(list_repo_files(item["url"], path))
    return files


class SizeFetcher(QThread):
    done = pyqtSignal(str, list, int)
    error = pyqtSignal(str)
    def __init__(self, mode):
        super().__init__()
        self.mode = mode
    def run(self):
        try:
            files = list_repo_files(FG_API if self.mode == "fg" else DLSS_API)
            for f in files:
                # only upgrade size via media if URL already points to media (real LFS)
                if f["size"] < 1024 and "media.githubusercontent.com" in f.get("url", ""):
                    try:
                        hr = requests.head(f["url"], timeout=20, allow_redirects=True)
                        cl = hr.headers.get("Content-Length")
                        if cl and int(cl) > 1024:
                            f["size"] = int(cl)
                        elif hr.status_code == 404:
                            f["url"] = RAW_BASE + f.get("repo_path", "")
                    except Exception:
                        f["url"] = RAW_BASE + f.get("repo_path", "")
            self.done.emit(self.mode, files, sum(f["size"] for f in files))
        except Exception as e:
            self.error.emit(str(e))

class DownloadWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    speed = pyqtSignal(str)
    def __init__(self, target_dir, files):
        super().__init__()
        self.target_dir = target_dir
        self.files = files
        self._cancel = False
        self._bytes = 0
        self._t0 = time.time()
    def cancel(self):
        self._cancel = True
    def download_one(self, info):
        if self._cancel:
            return False, info["path"]
        rel, url = info["path"], info["url"]
        dest = os.path.join(self.target_dir, rel)
        os.makedirs(os.path.dirname(dest) if os.path.dirname(dest) else self.target_dir, exist_ok=True)
        def do_download(u):
            with requests.get(u, stream=True, timeout=300) as r:
                r.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(chunk_size=512 * 1024):
                        if self._cancel:
                            return False
                        if chunk:
                            f.write(chunk)
                            self._bytes += len(chunk)
            return True
        ok = do_download(url)
        if not ok:
            return False, rel
        actual = os.path.getsize(dest) if os.path.exists(dest) else 0
        if actual < 2048:
            with open(dest, "rb") as f:
                head = f.read(200)
            if b"git-lfs" in head or head.startswith(b"version https://git-lfs"):
                media = MEDIA_BASE + info.get("repo_path", "")
                try:
                    ok = do_download(media)
                except Exception:
                    ok = False
                if not ok:
                    raw = RAW_BASE + info.get("repo_path", "")
                    try:
                        ok = do_download(raw)
                    except Exception:
                        ok = False
                if not ok:
                    return False, rel
        return True, rel
    def run(self):
        try:
            total = len(self.files)
            done = 0
            self._t0 = time.time()
            with ThreadPoolExecutor(max_workers=6) as pool:
                futures = {pool.submit(self.download_one, f): f for f in self.files}
                for fut in as_completed(futures):
                    if self._cancel:
                        self.finished.emit(False, "Cancelled")
                        return
                    ok, name = fut.result()
                    if not ok:
                        self.finished.emit(False, f"Failed: {name}")
                        return
                    done += 1
                    elapsed = max(0.1, time.time() - self._t0)
                    spd = self._bytes / elapsed
                    self.speed.emit(f"{format_size(spd)}/s")
                    self.progress.emit(int(100 * done / total), f"{name}  ({done}/{total})")
            self.progress.emit(100, "Complete")
            self.finished.emit(True, "Installed successfully")
        except Exception as e:
            self.finished.emit(False, str(e))

class UpdateChecker(QThread):
    done = pyqtSignal(str)
    error = pyqtSignal(str)
    def run(self):
        try:
            r = requests.get(REPO_COMMITS, timeout=20, headers={"Accept": "application/vnd.github+json"})
            r.raise_for_status()
            d = r.json()
            self.done.emit(f"{d.get('sha','')[:7]} — {d.get('commit',{}).get('message','').split(chr(10))[0]}\n{d.get('commit',{}).get('author',{}).get('date','')}")
        except Exception as e:
            self.error.emit(str(e))

class SettingsWidget(QWidget):
    def __init__(self, ini_path, theme, parent=None):
        super().__init__(parent)
        self.ini_path = ini_path
        self.theme = theme
        self.config = read_ini(ini_path)
        self.widgets = {}
        self.build()
    def is_bool(self, v):
        return str(v).lower() in ("true", "false")
    def is_float(self, v):
        try:
            float(v)
            return "." in str(v) or "e" in str(v).lower()
        except Exception:
            return False
    def is_int(self, v):
        try:
            int(v)
            return not str(v).startswith("0x")
        except Exception:
            return False
    def build(self):
        t = self.theme
        layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea{{background:transparent;border:none;}} QScrollBar:vertical{{background:{t['bg2']};width:8px;border-radius:4px;}} QScrollBar::handle:vertical{{background:{t['primary']};border-radius:4px;min-height:24px;}}")
        container = QWidget()
        container.setStyleSheet("background:transparent;")
        cl = QVBoxLayout(container)
        for section in self.config.sections():
            group = QGroupBox(section)
            group.setStyleSheet(
                f"QGroupBox{{font-size:12px;font-weight:bold;color:{t['accent']};"
                f"border:1px solid {t['border']};border-radius:12px;margin-top:12px;padding-top:10px;background:{t['card']};}}"
                f"QGroupBox::title{{subcontrol-origin:margin;left:12px;padding:0 8px;color:{t['primary']};}}"
            )
            gl = QVBoxLayout(group)
            for key, value in self.config.items(section):
                row = QHBoxLayout()
                lbl = QLabel(key)
                lbl.setStyleSheet(f"color:{t['text']};font-size:11px;min-width:200px;")
                lbl.setWordWrap(True)
                row.addWidget(lbl)
                wkey = f"{section}|{key}"
                if self.is_bool(value):
                    cb = QCheckBox()
                    cb.setChecked(str(value).lower() == "true")
                    cb.setStyleSheet(
                        f"QCheckBox::indicator{{width:20px;height:20px;border-radius:5px;border:2px solid {t['primary']};background:{t['bg']};}}"
                        f"QCheckBox::indicator:checked{{background:{t['primary']};border-color:{t['accent']};}}"
                    )
                    self.widgets[wkey] = ("bool", cb)
                    row.addWidget(cb)
                    row.addStretch()
                elif key in SETTINGS_OPTIONS:
                    cbx = QComboBox()
                    opts = list(SETTINGS_OPTIONS[key])
                    if value not in opts:
                        opts = [value] + opts
                    cbx.addItems(opts)
                    cbx.setCurrentText(str(value))
                    cbx.setEditable(False)
                    cbx.setStyleSheet(f"QComboBox{{background:{t['bg']};color:{t['primary']};border:1px solid {t['border']};border-radius:6px;padding:5px;min-width:160px;}} QComboBox QAbstractItemView{{background:{t['bg2']};color:{t['text']};selection-background-color:{t['primary']};}}")
                    self.widgets[wkey] = ("combo", cbx)
                    row.addWidget(cbx)
                elif str(value).lower() == "auto":
                    cbx = QComboBox()
                    cbx.addItems(["auto", "true", "false", "0", "1"])
                    cbx.setCurrentText("auto")
                    cbx.setStyleSheet(f"QComboBox{{background:{t['bg']};color:{t['primary']};border:1px solid {t['border']};border-radius:6px;padding:5px;min-width:160px;}} QComboBox QAbstractItemView{{background:{t['bg2']};color:{t['text']};}}")
                    self.widgets[wkey] = ("combo", cbx)
                    row.addWidget(cbx)
                elif self.is_float(value):
                    sp = QDoubleSpinBox()
                    sp.setRange(-999999, 999999)
                    sp.setDecimals(4)
                    sp.setValue(float(value))
                    sp.setStyleSheet(f"QDoubleSpinBox{{background:{t['bg']};color:{t['primary']};border:1px solid {t['border']};border-radius:6px;padding:4px;min-width:110px;}}")
                    self.widgets[wkey] = ("float", sp)
                    row.addWidget(sp)
                elif self.is_int(value):
                    sp = QSpinBox()
                    sp.setRange(-999999, 999999)
                    sp.setValue(int(value))
                    sp.setStyleSheet(f"QSpinBox{{background:{t['bg']};color:{t['primary']};border:1px solid {t['border']};border-radius:6px;padding:4px;min-width:110px;}}")
                    self.widgets[wkey] = ("int", sp)
                    row.addWidget(sp)
                else:
                    le = QLineEdit(value)
                    le.setStyleSheet(f"QLineEdit{{background:{t['bg']};color:{t['primary']};border:1px solid {t['border']};border-radius:6px;padding:5px;min-width:160px;}}")
                    self.widgets[wkey] = ("str", le)
                    row.addWidget(le)
                gl.addLayout(row)
            cl.addWidget(group)
        cl.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)
        save_btn = QPushButton("SAVE SETTINGS")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(f"QPushButton{{background:{t['primary']};color:#111;font-weight:bold;font-size:13px;border:none;border-radius:12px;padding:12px 28px;}} QPushButton:hover{{background:{t['accent']};}}")
        save_btn.clicked.connect(self.save)
        hb = QHBoxLayout()
        hb.addStretch()
        hb.addWidget(save_btn)
        hb.addStretch()
        layout.addLayout(hb)
    def save(self):
        for wkey, (typ, w) in self.widgets.items():
            section, key = wkey.split("|", 1)
            if typ == "bool":
                val = "true" if w.isChecked() else "false"
            elif typ == "float":
                val = str(w.value())
            elif typ == "int":
                val = str(w.value())
            elif typ == "combo":
                val = w.currentText()
            else:
                val = w.text()
            ensure_section(self.config, section)
            self.config.set(section, key, val)
        try:
            write_ini(self.ini_path, self.config)
            QMessageBox.information(self, "Saved", "Settings saved.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

class FloatingOverlay(QWidget):
    def __init__(self, main_ref):
        super().__init__()
        self.main = main_ref
        self.setWindowTitle("NeoRay")
        _icon = Path(__file__).resolve().parent / "neoray_icon.png"
        if _icon.exists():
            self.setWindowIcon(QIcon(str(_icon)))
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(260, 300)
        t = main_ref.theme()
        self.setStyleSheet(f"background:{t['bg2']};color:{t['text']};border:1px solid {t['border']};border-radius:14px;")
        lay = QVBoxLayout(self)
        title = QLabel("NeoRay Quick")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"font-weight:900;color:{t['primary']};font-size:15px;letter-spacing:2px;")
        lay.addWidget(title)
        for text, slot in [
            ("Toggle FG", self.toggle_fg),
            ("Quality", lambda: self.apply_p("Quality")),
            ("Balanced", lambda: self.apply_p("Balanced")),
            ("Performance", lambda: self.apply_p("Performance")),
            ("Ultra Perf", lambda: self.apply_p("Ultra Performance")),
            ("FG Off", lambda: self.apply_p("FG Off")),
            ("Settings", lambda: self.main.open_settings_for_current()),
            ("Close", self.close),
        ]:
            b = QPushButton(text)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(f"QPushButton{{background:transparent;color:{t['primary']};border:1px solid {t['border']};border-radius:8px;padding:7px;font-weight:bold;}} QPushButton:hover{{background:{t['primary']};color:#111;}}")
            b.clicked.connect(slot)
            lay.addWidget(b)
    def ini(self):
        return self.main.current_ini()
    def toggle_fg(self):
        p = self.ini()
        if not p: return
        cfg = read_ini(p)
        ensure_section(cfg, "FrameGen")
        cur = cfg.get("FrameGen", "Enabled", fallback="true").lower() == "true"
        cfg.set("FrameGen", "Enabled", "false" if cur else "true")
        write_ini(p, cfg)
    def apply_p(self, name):
        p = self.ini()
        if not p: return
        apply_profile_to_ini(p, QUALITY_PROFILES[name])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeoRay")
        _icon = Path(__file__).resolve().parent / "neoray_icon.png"
        if _icon.exists():
            self.setWindowIcon(QIcon(str(_icon)))
        self.resize(1180, 780)
        self.setMinimumSize(960, 660)
        self.theme_name = "gold"
        self.theme_idx = 0
        self.library = load_json(LIBRARY_FILE, [])
        self.app_settings = load_json(SETTINGS_FILE, {"disable_overlays": False})
        self.current_game = None
        self.fg_files = self.dlss_files = None
        self.fg_size = self.dlss_size = 0
        self.worker = None
        self.gpu_info = detect_gpu()
        self.overlay = None
        self.batch_queue = []
        self.setup_ui()
        self.apply_theme()
        self.refresh_library()
        self.prefetch_sizes()
        self.update_gpu_label()
        self.update_stats()
        self.theme_timer = QTimer(self)
        self.theme_timer.timeout.connect(self.cycle_theme)
        self.theme_timer.start(14000)
        QShortcut(QKeySequence("Ctrl+O"), self, self.toggle_overlay)
        QShortcut(QKeySequence("Ctrl+S"), self, self.open_settings_for_current)
        QShortcut(QKeySequence("Ctrl+B"), self, self.backup_game)
        QShortcut(QKeySequence("Ctrl+1"), self, lambda: self.stack.setCurrentIndex(0))
        QShortcut(QKeySequence("Ctrl+2"), self, lambda: self.stack.setCurrentIndex(1))
        QShortcut(QKeySequence("Ctrl+3"), self, lambda: self.stack.setCurrentIndex(2))
        QShortcut(QKeySequence("Ctrl+4"), self, lambda: self.stack.setCurrentIndex(3))

    def theme(self):
        return THEMES[self.theme_name]

    def cycle_theme(self):
        self.theme_idx = (self.theme_idx + 1) % len(THEME_ORDER)
        self.theme_name = THEME_ORDER[self.theme_idx]
        self.apply_theme()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        self.bg = ParticleBackground(central)
        self.bg.setGeometry(0, 0, 2400, 1600)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("background:transparent;")
        sl = QVBoxLayout(self.sidebar)
        sl.setContentsMargins(14, 22, 14, 16)
        sl.setSpacing(8)
        self.logo = QLabel("NEORAY")
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sl.addWidget(self.logo)
        self.tagline = QLabel("Frame Gen  ·  DLSS")
        self.tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sl.addWidget(self.tagline)
        sl.addSpacing(10)
        self.nav = {}
        for key, label in [("home", "HOME"), ("lib", "LIBRARY"), ("quick", "QUICK"),
                           ("advanced", "ADVANCED"), ("tools", "TOOLS"), ("settings", "SETTINGS")]:
            b = QPushButton(label)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFixedHeight(40)
            self.nav[key] = b
            sl.addWidget(b)
        self.nav["home"].clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.nav["lib"].clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.nav["quick"].clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.nav["advanced"].clicked.connect(lambda: self.stack.setCurrentIndex(3))
        self.nav["tools"].clicked.connect(lambda: self.stack.setCurrentIndex(4))
        self.nav["settings"].clicked.connect(self.open_settings_for_current)
        sl.addStretch()
        self.stats_lbl = QLabel("")
        self.stats_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stats_lbl.setWordWrap(True)
        sl.addWidget(self.stats_lbl)
        self.gpu_lbl = QLabel("")
        self.gpu_lbl.setWordWrap(True)
        self.gpu_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sl.addWidget(self.gpu_lbl)
        root.addWidget(self.sidebar)

        content = QFrame()
        content.setStyleSheet("background:transparent;")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(18, 14, 18, 14)
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background:transparent;")
        self.stack.addWidget(self.build_home())
        self.stack.addWidget(self.build_library())
        self.stack.addWidget(self.build_quick())
        self.stack.addWidget(self.build_advanced())
        self.stack.addWidget(self.build_tools())
        self.settings_page = QWidget()
        self.settings_page.setStyleSheet("background:transparent;")
        self.settings_layout = QVBoxLayout(self.settings_page)
        self.settings_layout.setContentsMargins(0, 0, 0, 0)
        self.stack.addWidget(self.settings_page)
        cl.addWidget(self.stack)
        root.addWidget(content, 1)

    def btn(self, text, primary=True):
        b = QPushButton(text)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        return b

    def build_home(self):
        page = QWidget()
        page.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(page)
        self.home_title = QLabel("Game Setup")
        layout.addWidget(self.home_title)
        card = QFrame()
        card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(22, 18, 22, 18)
        cl.setSpacing(12)
        self.path_lbl = QLabel("No game selected")
        self.path_lbl.setWordWrap(True)
        cl.addWidget(self.path_lbl)
        row = QHBoxLayout()
        self.select_btn = self.btn("SELECT EXE")
        self.select_btn.clicked.connect(self.select_exe)
        row.addWidget(self.select_btn)
        self.add_lib_btn = self.btn("ADD TO LIBRARY")
        self.add_lib_btn.setEnabled(False)
        self.add_lib_btn.clicked.connect(self.add_to_library)
        row.addWidget(self.add_lib_btn)
        self.open_folder_btn = self.btn("OPEN FOLDER")
        self.open_folder_btn.clicked.connect(self.open_game_folder)
        row.addWidget(self.open_folder_btn)
        self.copy_path_btn = self.btn("COPY PATH")
        self.copy_path_btn.clicked.connect(self.copy_path)
        row.addWidget(self.copy_path_btn)
        cl.addLayout(row)
        self.status_box = QFrame()
        self.status_box.setObjectName("status")
        sbl = QVBoxLayout(self.status_box)
        self.fg_status = QLabel("FG: —")
        self.dlss_status = QLabel("DLSS 5: —")
        self.verify_lbl = QLabel("")
        sbl.addWidget(self.fg_status)
        sbl.addWidget(self.dlss_status)
        sbl.addWidget(self.verify_lbl)
        cl.addWidget(self.status_box)
        self.size_lbl = QLabel("")
        cl.addWidget(self.size_lbl)
        self.suggest_lbl = QLabel("")
        self.suggest_lbl.setWordWrap(True)
        cl.addWidget(self.suggest_lbl)
        grid = QGridLayout()
        self.fg_btn = self.btn("INSTALL FG")
        self.fg_btn.setEnabled(False)
        self.fg_btn.clicked.connect(lambda: self.start_install("fg"))
        grid.addWidget(self.fg_btn, 0, 0)
        self.dlss_btn = self.btn("INSTALL DLSS 5")
        self.dlss_btn.setEnabled(False)
        self.dlss_btn.clicked.connect(lambda: self.start_install("dlss"))
        grid.addWidget(self.dlss_btn, 0, 1)
        self.both_btn = self.btn("INSTALL BOTH")
        self.both_btn.setEnabled(False)
        self.both_btn.clicked.connect(self.install_both)
        grid.addWidget(self.both_btn, 0, 2)
        self.rec_btn = self.btn("RECOMMENDED FOR GPU")
        self.rec_btn.setEnabled(False)
        self.rec_btn.clicked.connect(self.install_recommended)
        grid.addWidget(self.rec_btn, 1, 0)
        self.rm_fg_btn = self.btn("REMOVE FG")
        self.rm_fg_btn.clicked.connect(lambda: self.remove_partial("fg"))
        grid.addWidget(self.rm_fg_btn, 1, 1)
        self.rm_dlss_btn = self.btn("REMOVE DLSS5")
        self.rm_dlss_btn.clicked.connect(lambda: self.remove_partial("dlss"))
        grid.addWidget(self.rm_dlss_btn, 1, 2)
        self.remove_btn = self.btn("REMOVE ALL")
        self.remove_btn.setEnabled(False)
        self.remove_btn.clicked.connect(self.remove_modules)
        grid.addWidget(self.remove_btn, 2, 0, 1, 3)
        cl.addLayout(grid)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(True)
        self.progress.hide()
        cl.addWidget(self.progress)
        self.speed_lbl = QLabel("")
        cl.addWidget(self.speed_lbl)
        self.status_lbl = QLabel("")
        cl.addWidget(self.status_lbl)
        layout.addWidget(card)
        layout.addStretch()
        return page

    def build_library(self):
        page = QWidget()
        page.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(page)
        self.lib_title = QLabel("Library")
        layout.addWidget(self.lib_title)
        search_row = QHBoxLayout()
        self.lib_search = QLineEdit()
        self.lib_search.setPlaceholderText("Search games...")
        self.lib_search.textChanged.connect(self.filter_library)
        search_row.addWidget(self.lib_search)
        layout.addLayout(search_row)
        self.lib_list = QListWidget()
        layout.addWidget(self.lib_list)
        row = QHBoxLayout()
        for text, slot in [
            ("OPEN", self.open_from_lib), ("SETTINGS", self.settings_from_lib),
            ("FAVORITE", self.toggle_favorite), ("BATCH FG", lambda: self.batch_install("fg")),
            ("BATCH DLSS5", lambda: self.batch_install("dlss")), ("REMOVE", self.remove_from_lib)
        ]:
            b = self.btn(text)
            b.clicked.connect(slot)
            row.addWidget(b)
            if text == "OPEN": self.lib_open_btn = b
            elif text == "SETTINGS": self.lib_settings_btn = b
            elif text == "FAVORITE": self.lib_fav_btn = b
            elif text == "BATCH FG": self.lib_batch_fg = b
            elif text == "BATCH DLSS5": self.lib_batch_dlss = b
            elif text == "REMOVE": self.lib_remove_btn = b
        layout.addLayout(row)
        return page

    def build_quick(self):
        page = QWidget()
        page.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(page)
        self.quick_title = QLabel("Quick Setup")
        layout.addWidget(self.quick_title)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background:transparent;border:none;")
        inner = QWidget()
        inner.setStyleSheet("background:transparent;")
        il = QVBoxLayout(inner)

        def group(title):
            g = QGroupBox(title)
            return g

        g1 = group("Quality Profile")
        g1l = QHBoxLayout(g1)
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(list(QUALITY_PROFILES.keys()))
        g1l.addWidget(self.profile_combo)
        bp = self.btn("APPLY")
        bp.clicked.connect(self.apply_quality_profile)
        g1l.addWidget(bp)
        il.addWidget(g1)

        g2 = group("Upscaler")
        g2l = QHBoxLayout(g2)
        self.upscaler_combo = QComboBox()
        self.upscaler_combo.addItems(["auto", "fsr", "fsr31", "xess", "dlss", "dlssg"])
        g2l.addWidget(self.upscaler_combo)
        bu = self.btn("APPLY")
        bu.clicked.connect(self.apply_upscaler)
        g2l.addWidget(bu)
        il.addWidget(g2)

        g3 = group("GPU Spoof")
        g3l = QHBoxLayout(g3)
        self.spoof_combo = QComboBox()
        self.spoof_combo.setEditable(True)
        self.spoof_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.spoof_combo.addItems(list(GPU_SPOOF.keys()))
        self.spoof_combo.setMaxVisibleItems(20)
        g3l.addWidget(self.spoof_combo)
        bs = self.btn("APPLY")
        bs.clicked.connect(self.apply_spoof)
        g3l.addWidget(bs)
        il.addWidget(g3)

        g4 = group("Sharpness / CAS")
        g4l = QFormLayout(g4)
        self.sharp_slider = QSlider(Qt.Orientation.Horizontal)
        self.sharp_slider.setRange(0, 100)
        self.sharp_slider.setValue(30)
        self.sharp_val = QLabel("0.30")
        self.sharp_slider.valueChanged.connect(lambda v: self.sharp_val.setText(f"{v/100:.2f}"))
        rs = QHBoxLayout()
        rs.addWidget(self.sharp_slider)
        rs.addWidget(self.sharp_val)
        g4l.addRow("Sharpness", rs)
        self.cas_check = QCheckBox("Enable CAS")
        g4l.addRow(self.cas_check)
        self.cas_slider = QSlider(Qt.Orientation.Horizontal)
        self.cas_slider.setRange(0, 100)
        self.cas_slider.setValue(40)
        self.cas_val = QLabel("0.40")
        self.cas_slider.valueChanged.connect(lambda v: self.cas_val.setText(f"{v/100:.2f}"))
        rc = QHBoxLayout()
        rc.addWidget(self.cas_slider)
        rc.addWidget(self.cas_val)
        g4l.addRow("CAS", rc)
        bc = self.btn("APPLY SHARPENING")
        bc.clicked.connect(self.apply_sharpening)
        g4l.addRow(bc)
        il.addWidget(g4)

        g5 = group("One-click toggles")
        g5l = QGridLayout(g5)
        toggles = [
            ("FG On", lambda: self.quick_set("FrameGen", "Enabled", "true")),
            ("FG Off", lambda: self.quick_set("FrameGen", "Enabled", "false")),
            ("HDR Force", lambda: self.quick_set("HDR", "ForceHDR", "true")),
            ("HDR Off", lambda: self.quick_set("HDR", "ForceHDR", "false")),
            ("VSync On", lambda: self.quick_multi({"V-Sync": {"OverrideVsync": "true", "ForceVsync": "true"}})),
            ("VSync Off", lambda: self.quick_multi({"V-Sync": {"OverrideVsync": "true", "ForceVsync": "false"}})),
            ("Disable Overlays", lambda: self.quick_set("Hudfix", "DisableOverlays", "true")),
            ("Enable Overlays", lambda: self.quick_set("Hudfix", "DisableOverlays", "false")),
            ("Async FG", lambda: self.quick_set("FSRFG", "AllowAsync", "true")),
            ("Streamline Spoof", lambda: self.quick_set("Spoofing", "StreamlineSpoofing", "true")),
            ("Output Scale 1.5x", lambda: self.quick_multi({"OutputScaling": {"Enabled": "true", "Multiplier": "1.5"}})),
            ("Output Scale Off", lambda: self.quick_set("OutputScaling", "Enabled", "false")),
        ]
        self.quick_toggle_btns = []
        for i, (text, slot) in enumerate(toggles):
            b = self.btn(text)
            b.clicked.connect(slot)
            g5l.addWidget(b, i // 3, i % 3)
            self.quick_toggle_btns.append(b)
        il.addWidget(g5)

        g6 = group("Overlay")
        g6l = QVBoxLayout(g6)
        bo = self.btn("FLOATING OVERLAY  (Ctrl+O)")
        bo.clicked.connect(self.toggle_overlay)
        g6l.addWidget(bo)
        il.addWidget(g6)

        il.addStretch()
        scroll.setWidget(inner)
        layout.addWidget(scroll)
        self._quick_groups = [g1, g2, g3, g4, g5, g6]
        self._quick_btns = [bp, bu, bs, bc, bo]
        return page

    def build_advanced(self):
        page = QWidget()
        page.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(page)
        self.adv_title = QLabel("Advanced")
        layout.addWidget(self.adv_title)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background:transparent;border:none;")
        inner = QWidget()
        inner.setStyleSheet("background:transparent;")
        il = QVBoxLayout(inner)

        g1 = QGroupBox("Framerate Limit")
        g1l = QHBoxLayout(g1)
        self.fps_spin = QDoubleSpinBox()
        self.fps_spin.setRange(0, 1000)
        self.fps_spin.setValue(0)
        self.fps_spin.setSuffix("  (0 = unlimited)")
        g1l.addWidget(self.fps_spin)
        bf = self.btn("APPLY FPS CAP")
        bf.clicked.connect(self.apply_fps)
        g1l.addWidget(bf)
        il.addWidget(g1)

        g2 = QGroupBox("Upscale Ratio Override")
        g2l = QHBoxLayout(g2)
        self.ratio_spin = QDoubleSpinBox()
        self.ratio_spin.setRange(1.0, 5.0)
        self.ratio_spin.setSingleStep(0.1)
        self.ratio_spin.setValue(1.5)
        g2l.addWidget(self.ratio_spin)
        br = self.btn("APPLY RATIO")
        br.clicked.connect(self.apply_ratio)
        g2l.addWidget(br)
        il.addWidget(g2)

        g3 = QGroupBox("Anisotropy / Mipmap")
        g3l = QFormLayout(g3)
        self.aniso_combo = QComboBox()
        self.aniso_combo.addItems(["auto", "1", "2", "4", "8", "16"])
        g3l.addRow("Anisotropy", self.aniso_combo)
        self.mip_spin = QDoubleSpinBox()
        self.mip_spin.setRange(-5.0, 5.0)
        self.mip_spin.setSingleStep(0.1)
        self.mip_spin.setValue(0.0)
        g3l.addRow("Mipmap Bias", self.mip_spin)
        ba = self.btn("APPLY TEXTURE")
        ba.clicked.connect(self.apply_texture)
        g3l.addRow(ba)
        il.addWidget(g3)

        g4 = QGroupBox("Init Flags")
        g4l = QGridLayout(g4)
        self.init_flags = {}
        for i, flag in enumerate(["AutoExposure", "HDR", "DepthInverted", "JitterCancellation", "DisplayResolution", "DisableReactiveMask"]):
            cb = QCheckBox(flag)
            self.init_flags[flag] = cb
            g4l.addWidget(cb, i // 3, i % 3)
        bi = self.btn("APPLY INIT FLAGS")
        bi.clicked.connect(self.apply_init_flags)
        g4l.addWidget(bi, 3, 0, 1, 3)
        il.addWidget(g4)

        g5 = QGroupBox("HUD Fix Presets")
        g5l = QHBoxLayout(g5)
        for name, vals in [
            ("Safe", {"DisableHUDFix": "false", "HUDFix": "true", "HUDLimit": "1"}),
            ("Aggressive", {"DisableHUDFix": "false", "HUDFix": "true", "HUDFixExtended": "true", "HUDLimit": "2"}),
            ("Off", {"DisableHUDFix": "true", "HUDFix": "false"}),
        ]:
            b = self.btn(name)
            b.clicked.connect(lambda checked, v=vals: self.apply_hud(v))
            g5l.addWidget(b)
        il.addWidget(g5)

        g6 = QGroupBox("Export / Import Profile")
        g6l = QHBoxLayout(g6)
        be = self.btn("EXPORT INI PROFILE")
        be.clicked.connect(self.export_profile)
        bi2 = self.btn("IMPORT INI PROFILE")
        bi2.clicked.connect(self.import_profile)
        g6l.addWidget(be)
        g6l.addWidget(bi2)
        il.addWidget(g6)

        g7 = QGroupBox("Portable Mode")
        g7l = QVBoxLayout(g7)
        self.portable_check = QCheckBox("Store data next to app (restart required)")
        self.portable_check.setChecked(PORTABLE_FLAG.exists())
        self.portable_check.stateChanged.connect(self.toggle_portable)
        g7l.addWidget(self.portable_check)
        il.addWidget(g7)

        il.addStretch()
        scroll.setWidget(inner)
        layout.addWidget(scroll)
        self._adv_groups = [g1, g2, g3, g4, g5, g6, g7]
        self._adv_btns = [bf, br, ba, bi, be, bi2]
        return page



    def build_tools(self):
        page = QWidget()
        page.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(page)
        self.tools_title = QLabel("Tools")
        layout.addWidget(self.tools_title)
        row1 = QHBoxLayout()
        self.backup_btn = self.btn("BACKUP")
        self.backup_btn.clicked.connect(self.backup_game)
        self.restore_btn = self.btn("RESTORE")
        self.restore_btn.clicked.connect(self.restore_game)
        self.verify_btn = self.btn("VERIFY FILES")
        self.verify_btn.clicked.connect(self.verify_files)
        self.sysinfo_btn = self.btn("SYSTEM INFO")
        self.sysinfo_btn.clicked.connect(self.show_sysinfo)
        for b in (self.backup_btn, self.restore_btn, self.verify_btn, self.sysinfo_btn):
            row1.addWidget(b)
        layout.addLayout(row1)
        row2 = QHBoxLayout()
        self.update_btn = self.btn("CHECK UPDATES")
        self.update_btn.clicked.connect(self.check_updates)
        self.log_btn = self.btn("VIEW LOGS")
        self.log_btn.clicked.connect(self.view_logs)
        self.enable_log_btn = self.btn("ENABLE LOGGING")
        self.enable_log_btn.clicked.connect(self.enable_logging)
        self.cancel_btn = self.btn("CANCEL DOWNLOAD")
        self.cancel_btn.clicked.connect(self.cancel_download)
        for b in (self.update_btn, self.log_btn, self.enable_log_btn, self.cancel_btn):
            row2.addWidget(b)
        layout.addLayout(row2)
        self.tools_info = QTextEdit()
        self.tools_info.setReadOnly(True)
        layout.addWidget(self.tools_info)
        return page

    def apply_theme(self):
        t = self.theme()
        self.bg.set_theme(self.theme_name)
        self.setStyleSheet(
            f"QMainWindow,QWidget{{background:{t['bg']};color:{t['text']};}}"
            f"QMessageBox{{background:{t['bg2']};color:{t['text']};}}"
            f"QMessageBox QLabel{{color:{t['text']};}}"
            f"QMessageBox QPushButton{{background:{t['primary']};color:#111;border-radius:8px;padding:6px 14px;font-weight:bold;}}"
        )
        self.logo.setStyleSheet(f"font-size:28px;font-weight:900;letter-spacing:6px;color:{t['primary']};")
        self.tagline.setStyleSheet(f"font-size:10px;letter-spacing:3px;color:{t['text']};")
        self.gpu_lbl.setStyleSheet(f"font-size:10px;color:{t['text']};")
        self.stats_lbl.setStyleSheet(f"font-size:10px;color:{t['accent']};")
        nav = (
            f"QPushButton{{background:transparent;color:{t['text']};border:1px solid transparent;"
            f"border-radius:12px;font-weight:bold;font-size:11px;letter-spacing:1px;}}"
            f"QPushButton:hover{{background:rgba(255,255,255,18);border:1px solid {t['border']};color:{t['primary']};}}"
        )
        for b in self.nav.values():
            b.setStyleSheet(nav)
        for lbl in [self.home_title, self.lib_title, self.quick_title, self.adv_title, self.tools_title]:
            lbl.setStyleSheet(f"font-size:20px;font-weight:800;color:{t['primary']};letter-spacing:1px;")
        self.stack.widget(0).setStyleSheet(
            f"QFrame#card,QFrame#status{{background:{t['card']};border:1px solid {t['border']};border-radius:16px;}}"
        )
        self.path_lbl.setStyleSheet(
            f"font-size:12px;padding:12px;border-radius:10px;background:{t['bg']};color:{t['primary']};border:1px solid {t['border']};"
        )
        primary_btn = (
            f"QPushButton{{background:{t['primary']};color:#111;font-weight:bold;font-size:11px;"
            f"border:none;border-radius:10px;padding:10px 12px;}}"
            f"QPushButton:hover{{background:{t['accent']};}}"
            f"QPushButton:disabled{{background:#2a2a2a;color:#666;}}"
        )
        ghost_btn = (
            f"QPushButton{{background:transparent;color:{t['primary']};border:1px solid {t['border']};"
            f"border-radius:10px;font-weight:bold;font-size:11px;padding:10px 12px;}}"
            f"QPushButton:hover{{background:{t['primary_dark']};color:#fff;}}"
            f"QPushButton:disabled{{color:#555;border-color:#333;}}"
        )
        all_primary = [
            self.select_btn, self.add_lib_btn, self.fg_btn, self.dlss_btn, self.both_btn, self.rec_btn,
            self.lib_open_btn, self.lib_settings_btn, self.lib_fav_btn, self.lib_batch_fg, self.lib_batch_dlss,
            self.backup_btn, self.restore_btn, self.verify_btn, self.sysinfo_btn,
            self.update_btn, self.log_btn, self.enable_log_btn, self.open_folder_btn, self.copy_path_btn,
        ] + self._quick_btns + self._adv_btns + self.quick_toggle_btns
        for b in all_primary:
            b.setStyleSheet(primary_btn)
        for b in [self.remove_btn, self.rm_fg_btn, self.rm_dlss_btn, self.lib_remove_btn, self.cancel_btn]:
            b.setStyleSheet(ghost_btn)
        for g in self._quick_groups + self._adv_groups:
            g.setStyleSheet(
                f"QGroupBox{{font-weight:bold;color:{t['accent']};border:1px solid {t['border']};"
                f"border-radius:12px;margin-top:12px;padding-top:12px;background:{t['card']};}}"
                f"QGroupBox::title{{subcontrol-origin:margin;left:12px;padding:0 8px;color:{t['primary']};}}"
            )
        self.progress.setStyleSheet(
            f"QProgressBar{{background:{t['bg']};border:1px solid {t['border']};border-radius:10px;height:22px;"
            f"text-align:center;color:{t['primary']};font-weight:bold;}}"
            f"QProgressBar::chunk{{background:{t['primary']};border-radius:9px;}}"
        )
        self.lib_list.setStyleSheet(
            f"QListWidget{{background:{t['card']};border:1px solid {t['border']};border-radius:12px;padding:6px;color:{t['text']};}}"
            f"QListWidget::item{{padding:12px;border-radius:8px;}}"
            f"QListWidget::item:selected{{background:{t['primary']};color:#111;}}"
        )
        self.tools_info.setStyleSheet(f"background:{t['bg']};color:{t['text']};border:1px solid {t['border']};border-radius:10px;padding:10px;")
        self.lib_search.setStyleSheet(f"QLineEdit{{background:{t['bg']};color:{t['primary']};border:1px solid {t['border']};border-radius:10px;padding:8px;}}")
        for cb in [self.profile_combo, self.upscaler_combo, self.spoof_combo, self.aniso_combo]:
            cb.setStyleSheet(f"QComboBox{{background:{t['bg']};color:{t['primary']};border:1px solid {t['border']};border-radius:8px;padding:6px;}} QComboBox QAbstractItemView{{background:{t['bg2']};color:{t['text']};selection-background-color:{t['primary']};}}")
        self.fg_status.setStyleSheet(f"font-size:12px;color:{t['text']};")
        self.dlss_status.setStyleSheet(f"font-size:12px;color:{t['text']};")
        self.size_lbl.setStyleSheet(f"font-size:11px;color:{t['text']};")
        self.status_lbl.setStyleSheet(f"font-size:12px;color:{t['primary']};")
        self.speed_lbl.setStyleSheet(f"font-size:11px;color:{t['accent']};")
        self.suggest_lbl.setStyleSheet(f"font-size:11px;color:{t['accent']};")
        self.verify_lbl.setStyleSheet(f"font-size:11px;color:{t['text']};")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg.setGeometry(0, 0, self.width(), self.height())

    def update_gpu_label(self):
        g = self.gpu_info
        tip = "RTX → DLSS 5 + FG" if g["is_rtx"] else ("NVIDIA → FG / DLSS" if g["is_nvidia"] else "Use FG modules")
        self.gpu_lbl.setText(f"{g['name']}\n{tip}")
        self.suggest_lbl.setText(f"Recommended: {tip}")

    def update_stats(self):
        total = len(self.library)
        fg = sum(1 for g in self.library if g.get("fg"))
        dlss = sum(1 for g in self.library if g.get("dlss"))
        fav = sum(1 for g in self.library if g.get("favorite"))
        self.stats_lbl.setText(f"{total} games\n{fg} FG · {dlss} DLSS\n{fav} favorites")

    def current_ini(self):
        if not self.current_game:
            return None
        p = os.path.join(os.path.dirname(self.current_game), "OptiScaler.ini")
        return p if os.path.exists(p) else None

    def require_ini(self):
        p = self.current_ini()
        if not p:
            QMessageBox.warning(self, "Need FG", "Select a game and install FG first.")
            return None
        return p

    def prefetch_sizes(self):
        self.size_lbl.setText("Fetching sizes...")
        self.fg_fetcher = SizeFetcher("fg")
        self.fg_fetcher.done.connect(self.on_size)
        self.fg_fetcher.error.connect(lambda e: self.size_lbl.setText(str(e)))
        self.fg_fetcher.start()
        self.dlss_fetcher = SizeFetcher("dlss")
        self.dlss_fetcher.done.connect(self.on_size)
        self.dlss_fetcher.start()

    def on_size(self, mode, files, total):
        if mode == "fg":
            self.fg_files, self.fg_size = files, total
        else:
            self.dlss_files, self.dlss_size = files, total
        parts = []
        if self.fg_size: parts.append(f"FG {format_size(self.fg_size)}")
        if self.dlss_size: parts.append(f"DLSS5 {format_size(self.dlss_size)}")
        self.size_lbl.setText("  ·  ".join(parts))

    def select_exe(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select EXE", "", "Executable (*.exe);;All (*)")
        if not path:
            return
        self.current_game = path
        self.path_lbl.setText(path)
        self.add_lib_btn.setEnabled(True)
        self.fg_btn.setEnabled(True)
        self.dlss_btn.setEnabled(True)
        self.both_btn.setEnabled(True)
        self.rec_btn.setEnabled(True)
        self.update_status()

    def update_status(self):
        if not self.current_game:
            return
        folder = os.path.dirname(self.current_game)
        fg = check_installed(folder, FG_MARKERS)
        dlss = check_installed(folder, DLSS_MARKERS)
        t = self.theme()
        self.fg_status.setText(f"FG:  {'INSTALLED' if fg else 'Not installed'}")
        self.fg_status.setStyleSheet(f"font-size:12px;color:{t['primary'] if fg else t['text']};")
        self.dlss_status.setText(f"DLSS 5:  {'INSTALLED' if dlss else 'Not installed'}")
        self.dlss_status.setStyleSheet(f"font-size:12px;color:{t['primary'] if dlss else t['text']};")
        self.remove_btn.setEnabled(fg or dlss)
        self.fg_btn.setText("REINSTALL FG" if fg else "INSTALL FG")
        self.dlss_btn.setText("REINSTALL DLSS 5" if dlss else "INSTALL DLSS 5")
        present = sum(1 for n in ALL_MODULE_FILES if os.path.exists(os.path.join(folder, n)))
        self.verify_lbl.setText(f"Module files present: {present}")

    def add_to_library(self):
        if not self.current_game:
            return
        name = Path(self.current_game).stem
        folder = os.path.dirname(self.current_game)
        entry = {"name": name, "path": self.current_game, "folder": folder,
                 "fg": check_installed(folder, FG_MARKERS), "dlss": check_installed(folder, DLSS_MARKERS),
                 "favorite": False, "last_used": datetime.now().isoformat()}
        self.library = [g for g in self.library if g["path"] != self.current_game]
        self.library.append(entry)
        save_json(LIBRARY_FILE, self.library)
        self.refresh_library()
        self.update_stats()
        QMessageBox.information(self, "Library", f"Added {name}")

    def refresh_library(self):
        self.filter_library(self.lib_search.text() if hasattr(self, "lib_search") else "")

    def filter_library(self, text=""):
        self.lib_list.clear()
        q = (text or "").lower()
        games = sorted(self.library, key=lambda g: (not g.get("favorite", False), g.get("name", "").lower()))
        for g in games:
            if q and q not in g.get("name", "").lower() and q not in g.get("path", "").lower():
                continue
            flags = []
            if g.get("favorite"): flags.append("★")
            if g.get("fg"): flags.append("FG")
            if g.get("dlss"): flags.append("DLSS5")
            tag = f"  [{' '.join(flags)}]" if flags else ""
            item = QListWidgetItem(f"{g['name']}{tag}\n{g['path']}")
            item.setData(Qt.ItemDataRole.UserRole, g)
            self.lib_list.addItem(item)

    def open_from_lib(self):
        item = self.lib_list.currentItem()
        if not item: return
        g = item.data(Qt.ItemDataRole.UserRole)
        self.current_game = g["path"]
        g["last_used"] = datetime.now().isoformat()
        save_json(LIBRARY_FILE, self.library)
        self.path_lbl.setText(g["path"])
        self.add_lib_btn.setEnabled(True)
        self.fg_btn.setEnabled(True)
        self.dlss_btn.setEnabled(True)
        self.both_btn.setEnabled(True)
        self.rec_btn.setEnabled(True)
        self.update_status()
        self.stack.setCurrentIndex(0)

    def settings_from_lib(self):
        item = self.lib_list.currentItem()
        if not item: return
        self.current_game = item.data(Qt.ItemDataRole.UserRole)["path"]
        self.open_settings_for_current()

    def toggle_favorite(self):
        item = self.lib_list.currentItem()
        if not item: return
        g = item.data(Qt.ItemDataRole.UserRole)
        for x in self.library:
            if x["path"] == g["path"]:
                x["favorite"] = not x.get("favorite", False)
        save_json(LIBRARY_FILE, self.library)
        self.refresh_library()
        self.update_stats()

    def remove_from_lib(self):
        item = self.lib_list.currentItem()
        if not item: return
        g = item.data(Qt.ItemDataRole.UserRole)
        self.library = [x for x in self.library if x["path"] != g["path"]]
        save_json(LIBRARY_FILE, self.library)
        self.refresh_library()
        self.update_stats()

    def open_game_folder(self):
        if not self.current_game: return
        folder = os.path.dirname(self.current_game)
        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])

    def copy_path(self):
        if not self.current_game: return
        QApplication.clipboard().setText(self.current_game)
        self.status_lbl.setText("Path copied")

    def open_settings_for_current(self):
        ini = self.current_ini()
        if not ini:
            QMessageBox.information(self, "Settings", "Select a game with FG installed.")
            return
        while self.settings_layout.count():
            it = self.settings_layout.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        t = self.theme()
        top = QHBoxLayout()
        back = self.btn("← BACK")
        back.setStyleSheet(f"QPushButton{{background:transparent;color:{t['primary']};border:1px solid {t['border']};border-radius:8px;padding:8px 14px;font-weight:bold;}} QPushButton:hover{{background:{t['primary']};color:#111;}}")
        back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        top.addWidget(back)
        ttl = QLabel("OPTISCALER")
        ttl.setStyleSheet(f"font-size:18px;font-weight:bold;color:{t['primary']};")
        top.addWidget(ttl)
        top.addStretch()
        wrap = QWidget()
        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.addLayout(top)
        wl.addWidget(SettingsWidget(ini, t))
        self.settings_layout.addWidget(wrap)
        self.stack.setCurrentIndex(5)

    def apply_quality_profile(self):
        ini = self.require_ini()
        if not ini: return
        apply_profile_to_ini(ini, QUALITY_PROFILES[self.profile_combo.currentText()])
        QMessageBox.information(self, "OK", "Profile applied.")

    def apply_upscaler(self):
        ini = self.require_ini()
        if not ini: return
        val = self.upscaler_combo.currentText()
        cfg = read_ini(ini)
        ensure_section(cfg, "Upscalers")
        for k in ("Dx11Upscaler", "Dx12Upscaler", "VulkanUpscaler"):
            cfg.set("Upscalers", k, val)
        write_ini(ini, cfg)
        QMessageBox.information(self, "OK", f"Upscaler → {val}")

    def apply_spoof(self):
        ini = self.require_ini()
        if not ini: return
        key = self.spoof_combo.currentText().strip()
        if key not in GPU_SPOOF:
            # try case-insensitive / partial match
            matches = [k for k in GPU_SPOOF if key.lower() in k.lower()]
            if len(matches) == 1:
                key = matches[0]
            else:
                QMessageBox.warning(self, "Spoof", "Select a GPU from the list.")
                return
        vendor, device, name = GPU_SPOOF[key]
        cfg = read_ini(ini)
        ensure_section(cfg, "Spoofing")
        cfg.set("Spoofing", "SpoofedVendorId", vendor)
        cfg.set("Spoofing", "SpoofedDeviceId", device)
        cfg.set("Spoofing", "SpoofedGPUName", name)
        cfg.set("Spoofing", "StreamlineSpoofing", "true")
        cfg.set("Spoofing", "Dxgi", "true")
        write_ini(ini, cfg)
        QMessageBox.information(self, "OK", f"Spoofed as {name}")

    def apply_sharpening(self):
        ini = self.require_ini()
        if not ini: return
        cfg = read_ini(ini)
        ensure_section(cfg, "Sharpness")
        cfg.set("Sharpness", "OverrideSharpness", "true")
        cfg.set("Sharpness", "Sharpness", str(self.sharp_slider.value() / 100))
        ensure_section(cfg, "CAS")
        cfg.set("CAS", "Enabled", "true" if self.cas_check.isChecked() else "false")
        cfg.set("CAS", "MotionSharpness", str(self.cas_slider.value() / 100))
        write_ini(ini, cfg)
        QMessageBox.information(self, "OK", "Sharpening applied.")

    def quick_set(self, section, key, val):
        ini = self.require_ini()
        if not ini: return
        cfg = read_ini(ini)
        ensure_section(cfg, section)
        cfg.set(section, key, val)
        write_ini(ini, cfg)
        self.status_lbl.setText(f"{section}.{key} = {val}")

    def quick_multi(self, mapping):
        ini = self.require_ini()
        if not ini: return
        apply_profile_to_ini(ini, mapping)
        self.status_lbl.setText("Applied")

    def apply_fps(self):
        ini = self.require_ini()
        if not ini: return
        cfg = read_ini(ini)
        ensure_section(cfg, "Framerate")
        cfg.set("Framerate", "FramerateLimit", str(self.fps_spin.value()))
        write_ini(ini, cfg)
        QMessageBox.information(self, "OK", "FPS limit set.")

    def apply_ratio(self):
        ini = self.require_ini()
        if not ini: return
        cfg = read_ini(ini)
        ensure_section(cfg, "UpscaleRatio")
        cfg.set("UpscaleRatio", "UpscaleRatioOverrideEnabled", "true")
        cfg.set("UpscaleRatio", "UpscaleRatioOverrideValue", str(self.ratio_spin.value()))
        write_ini(ini, cfg)
        QMessageBox.information(self, "OK", "Ratio override set.")

    def apply_texture(self):
        ini = self.require_ini()
        if not ini: return
        cfg = read_ini(ini)
        ensure_section(cfg, "Anisotropy")
        cfg.set("Anisotropy", "AnisotropyOverride", self.aniso_combo.currentText())
        ensure_section(cfg, "Mipmap")
        cfg.set("Mipmap", "MipmapBiasOverride", str(self.mip_spin.value()))
        write_ini(ini, cfg)
        QMessageBox.information(self, "OK", "Texture settings applied.")

    def apply_init_flags(self):
        ini = self.require_ini()
        if not ini: return
        cfg = read_ini(ini)
        ensure_section(cfg, "InitFlags")
        for flag, cb in self.init_flags.items():
            cfg.set("InitFlags", flag, "true" if cb.isChecked() else "false")
        write_ini(ini, cfg)
        QMessageBox.information(self, "OK", "Init flags applied.")

    def apply_hud(self, vals):
        ini = self.require_ini()
        if not ini: return
        apply_profile_to_ini(ini, {"OptiFG": vals, "Hudfix": vals})
        QMessageBox.information(self, "OK", "HUD preset applied.")

    def export_profile(self):
        ini = self.require_ini()
        if not ini: return
        path, _ = QFileDialog.getSaveFileName(self, "Export", "profile.ini", "INI (*.ini)")
        if path:
            shutil.copy2(ini, path)
            QMessageBox.information(self, "OK", "Exported.")

    def import_profile(self):
        if not self.current_game:
            QMessageBox.information(self, "Import", "Select a game first.")
            return
        path, _ = QFileDialog.getOpenFileName(self, "Import", "", "INI (*.ini)")
        if not path: return
        dest = os.path.join(os.path.dirname(self.current_game), "OptiScaler.ini")
        shutil.copy2(path, dest)
        QMessageBox.information(self, "OK", "Imported as OptiScaler.ini")

    def toggle_portable(self, state):
        on = state == Qt.CheckState.Checked or state == 2
        if on:
            PORTABLE_FLAG.write_text("1")
        elif PORTABLE_FLAG.exists():
            PORTABLE_FLAG.unlink()
        QMessageBox.information(self, "Portable", "Restart the app to apply.")

    def toggle_overlay(self):
        if self.overlay and self.overlay.isVisible():
            self.overlay.close()
            self.overlay = None
        else:
            self.overlay = FloatingOverlay(self)
            self.overlay.show()

    def backup_game(self):
        if not self.current_game:
            QMessageBox.information(self, "Backup", "Select a game.")
            return
        folder = os.path.dirname(self.current_game)
        name = Path(self.current_game).stem
        dest = BACKUPS_DIR / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        dest.mkdir(parents=True, exist_ok=True)
        n = 0
        for fn in ALL_MODULE_FILES:
            src = os.path.join(folder, fn)
            if os.path.exists(src):
                shutil.copy2(src, dest / fn)
                n += 1
        sub = os.path.join(folder, "D3D12_Optiscaler")
        if os.path.isdir(sub):
            shutil.copytree(sub, dest / "D3D12_Optiscaler", dirs_exist_ok=True)
            n += 1
        self.tools_info.append(f"Backup → {dest} ({n})")
        QMessageBox.information(self, "Backup", f"{n} items saved.")

    def restore_game(self):
        if not self.current_game:
            QMessageBox.information(self, "Restore", "Select a game.")
            return
        backups = sorted([b for b in BACKUPS_DIR.iterdir() if b.is_dir()], key=lambda p: p.stat().st_mtime, reverse=True)
        if not backups:
            QMessageBox.information(self, "Restore", "No backups.")
            return
        choice, ok = QInputDialog.getItem(self, "Restore", "Backup:", [b.name for b in backups], 0, False)
        if not ok: return
        src = BACKUPS_DIR / choice
        folder = os.path.dirname(self.current_game)
        n = 0
        for f in src.iterdir():
            if f.is_file():
                shutil.copy2(f, os.path.join(folder, f.name)); n += 1
            elif f.is_dir():
                shutil.copytree(f, os.path.join(folder, f.name), dirs_exist_ok=True); n += 1
        self.update_status()
        self.tools_info.append(f"Restored {choice}")
        QMessageBox.information(self, "Restore", f"{n} items restored.")

    def verify_files(self):
        if not self.current_game:
            QMessageBox.information(self, "Verify", "Select a game.")
            return
        folder = os.path.dirname(self.current_game)
        lines = ["File verification:"]
        for fn in ALL_MODULE_FILES:
            p = os.path.join(folder, fn)
            if os.path.exists(p):
                lines.append(f"  OK  {fn}  ({format_size(os.path.getsize(p))})")
            else:
                lines.append(f"  --  {fn}")
        sub = os.path.join(folder, "D3D12_Optiscaler")
        lines.append(f"  {'OK' if os.path.isdir(sub) else '--'}  D3D12_Optiscaler/")
        self.tools_info.setPlainText("\n".join(lines))
        self.stack.setCurrentIndex(4)

    def show_sysinfo(self):
        g = self.gpu_info
        lines = [
            f"OS: {platform.system()} {platform.release()}",
            f"Machine: {platform.machine()}",
            f"Python: {platform.python_version()}",
            f"GPU: {g['name']}",
            f"Vendor: {g['vendor']}  RTX={g['is_rtx']}  NVIDIA={g['is_nvidia']}",
            f"App data: {APP_DIR}",
            f"Portable: {PORTABLE_FLAG.exists()}",
            f"Library games: {len(self.library)}",
        ]
        self.tools_info.setPlainText("\n".join(lines))
        self.stack.setCurrentIndex(4)

    def check_updates(self):
        self.tools_info.append("Checking updates...")
        self.uc = UpdateChecker()
        self.uc.done.connect(lambda s: self.tools_info.append(s))
        self.uc.error.connect(lambda e: self.tools_info.append(str(e)))
        self.uc.start()

    def view_logs(self):
        if not self.current_game:
            QMessageBox.information(self, "Logs", "Select a game.")
            return
        folder = Path(os.path.dirname(self.current_game))
        texts = []
        for c in list(folder.glob("*.log"))[:8]:
            if c.is_file() and c.stat().st_size < 3_000_000:
                try:
                    texts.append(f"===== {c.name} =====\n{c.read_text(encoding='utf-8', errors='ignore')[-10000:]}\n")
                except Exception:
                    pass
        self.tools_info.setPlainText("".join(texts) if texts else "No logs. Enable logging and run the game.")
        self.stack.setCurrentIndex(4)

    def enable_logging(self):
        ini = self.require_ini()
        if not ini: return
        cfg = read_ini(ini)
        ensure_section(cfg, "Log")
        cfg.set("Log", "LogToFile", "true")
        cfg.set("Log", "LogLevel", "2")
        cfg.set("Log", "SingleFile", "true")
        write_ini(ini, cfg)
        QMessageBox.information(self, "OK", "Logging enabled.")

    def cancel_download(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.status_lbl.setText("Cancelling...")

    def start_install(self, mode):
        if not self.current_game: return
        folder = os.path.dirname(self.current_game)
        if mode == "fg":
            if not self.fg_files:
                QMessageBox.warning(self, "Wait", "Still fetching FG list.")
                return
            files, size, label = self.fg_files, self.fg_size, "FG"
        else:
            if not self.dlss_files:
                QMessageBox.warning(self, "Wait", "Still fetching DLSS list.")
                return
            if not self.gpu_info.get("is_rtx") and not self.gpu_info.get("is_nvidia"):
                if QMessageBox.question(self, "DLSS 5", "GPU may not be RTX. Continue?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
                    return
            files, size, label = self.dlss_files, self.dlss_size, "DLSS 5"
        if QMessageBox.question(self, "Download", f"{label}\n{format_size(size)} · {len(files)} files\n{folder}",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        self._run_download(folder, files, label, mode)

    def install_both(self):
        if not self.current_game or not self.fg_files or not self.dlss_files:
            QMessageBox.warning(self, "Wait", "Select game and wait for size fetch.")
            return
        folder = os.path.dirname(self.current_game)
        files = self.fg_files + self.dlss_files
        size = self.fg_size + self.dlss_size
        if QMessageBox.question(self, "Both", f"FG + DLSS 5\n{format_size(size)}\n{folder}",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        self._run_download(folder, files, "FG+DLSS5", "both")

    def install_recommended(self):
        if self.gpu_info.get("is_rtx") or self.gpu_info.get("is_nvidia"):
            self.install_both()
        else:
            self.start_install("fg")

    def _run_download(self, folder, files, label, mode):
        self.progress.show()
        self.progress.setValue(0)
        self.status_lbl.setText(f"Downloading {label}...")
        for b in (self.fg_btn, self.dlss_btn, self.both_btn, self.rec_btn):
            b.setEnabled(False)
        self.worker = DownloadWorker(folder, files)
        self.worker.progress.connect(self.on_progress)
        self.worker.speed.connect(lambda s: self.speed_lbl.setText(s))
        self.worker.finished.connect(lambda ok, msg: self.on_finished(ok, msg, mode))
        self.worker.start()

    def batch_install(self, mode):
        if not self.library:
            QMessageBox.information(self, "Batch", "Library empty.")
            return
        files = self.fg_files if mode == "fg" else self.dlss_files
        if not files:
            QMessageBox.warning(self, "Wait", "File list not ready.")
            return
        if QMessageBox.question(self, "Batch", f"Install on {len(self.library)} games?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        self.batch_queue = list(self.library)
        self.batch_mode = mode
        self.batch_files = files
        self._batch_next()

    def _batch_next(self):
        if not self.batch_queue:
            self.status_lbl.setText("Batch done")
            self.refresh_library()
            self.update_stats()
            QMessageBox.information(self, "Batch", "Finished.")
            return
        g = self.batch_queue.pop(0)
        self.current_game = g["path"]
        self.path_lbl.setText(g["path"])
        self.status_lbl.setText(f"Batch: {g['name']} ({len(self.batch_queue)} left)")
        self.worker = DownloadWorker(g["folder"], self.batch_files)
        self.progress.show()
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self._batch_one_done)
        self.worker.start()

    def _batch_one_done(self, ok, msg):
        if self.current_game:
            folder = os.path.dirname(self.current_game)
            for g in self.library:
                if g["path"] == self.current_game:
                    g["fg"] = check_installed(folder, FG_MARKERS)
                    g["dlss"] = check_installed(folder, DLSS_MARKERS)
            save_json(LIBRARY_FILE, self.library)
        self._batch_next()

    def on_progress(self, val, msg):
        self.progress.setValue(val)
        self.status_lbl.setText(msg)

    def on_finished(self, ok, msg, mode):
        for b in (self.fg_btn, self.dlss_btn, self.both_btn, self.rec_btn):
            b.setEnabled(True)
        if ok:
            self.status_lbl.setText("✓ " + msg)
            self.update_status()
            if self.current_game:
                folder = os.path.dirname(self.current_game)
                for g in self.library:
                    if g["path"] == self.current_game:
                        g["fg"] = check_installed(folder, FG_MARKERS)
                        g["dlss"] = check_installed(folder, DLSS_MARKERS)
                save_json(LIBRARY_FILE, self.library)
                self.refresh_library()
                self.update_stats()
            if mode in ("fg", "both") and self.current_ini():
                if QMessageBox.question(self, "Settings", "Open settings?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                    self.open_settings_for_current()
        else:
            self.status_lbl.setText("✗ " + msg)
            QMessageBox.critical(self, "Error", msg)

    def remove_partial(self, mode):
        if not self.current_game: return
        folder = os.path.dirname(self.current_game)
        names = FG_MARKERS + ["amd_fidelityfx_dx12.dll", "amd_fidelityfx_upscaler_dx12.dll", "amd_fidelityfx_vk.dll",
                              "dlssg_to_fsr3_amd_is_better.dll", "fakenvapi.dll", "fakenvapi.ini"] if mode == "fg" else DLSS_MARKERS + ["nvngx_dlssnr.dll", "renodx-dlss5.addon64"]
        if QMessageBox.question(self, "Remove", f"Remove {mode.upper()} modules?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        n = 0
        for name in names:
            p = os.path.join(folder, name)
            if os.path.exists(p):
                try:
                    os.remove(p); n += 1
                except Exception:
                    pass
        if mode == "fg":
            sub = os.path.join(folder, "D3D12_Optiscaler")
            if os.path.isdir(sub):
                shutil.rmtree(sub, ignore_errors=True); n += 1
        self.update_status()
        QMessageBox.information(self, "Removed", f"{n} items")

    def remove_modules(self):
        if not self.current_game: return
        folder = os.path.dirname(self.current_game)
        if QMessageBox.question(self, "Remove", "Remove all modules?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        n = 0
        for name in ALL_MODULE_FILES:
            p = os.path.join(folder, name)
            if os.path.exists(p):
                try:
                    os.remove(p); n += 1
                except Exception:
                    pass
        sub = os.path.join(folder, "D3D12_Optiscaler")
        if os.path.isdir(sub):
            shutil.rmtree(sub, ignore_errors=True); n += 1
        self.update_status()
        if self.current_game:
            for g in self.library:
                if g["path"] == self.current_game:
                    g["fg"] = g["dlss"] = False
            save_json(LIBRARY_FILE, self.library)
            self.refresh_library()
            self.update_stats()
        QMessageBox.information(self, "Removed", f"{n} items")

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
