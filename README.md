<div align="center">

# <img src="neoray_icon.png" width="72" height="72" align="absmiddle"/> NEORAY

### Unlock Frame Generation & DLSS for every GPU

[![Python](https://img.shields.io/badge/Python-3.10%2B-FFD700?style=for-the-badge&logo=python&logoColor=black)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/UI-PyQt6-FF8C00?style=for-the-badge&logo=qt&logoColor=white)](https://www.riverbankcomputing.com/software/pyqt/)
[![Platform](https://img.shields.io/badge/Platform-Windows-9B59FF?style=for-the-badge&logo=windows&logoColor=white)](#)
[![License](https://img.shields.io/badge/Status-Active-00E5FF?style=for-the-badge)](#)

```text
 ███╗   ██╗███████╗ ██████╗ ██████╗  █████╗ ██╗   ██╗
 ████╗  ██║██╔════╝██╔═══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝
 ██╔██╗ ██║█████╗  ██║   ██║██████╔╝███████║ ╚████╔╝ 
 ██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██╔══██║  ╚██╔╝  
 ██║ ╚████║███████╗╚██████╔╝██║  ██║██║  ██║   ██║   
 ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   
```

**One click. Any card. Frame Gen + DLSS 5.**

[Features](#-features) · [Install](#-install) · [Usage](#-usage) · [Spoof](#-gpu-spoof) · [Build](#-build-exe)

---

<img src="https://readme-typing-svg.demolab.com?font=Orbitron&weight=700&size=28&duration=3500&pause=800&color=FFD700&center=true&vCenter=true&multiline=true&repeat=true&width=700&height=90&lines=Frame+Generation+for+ALL+GPUs;DLSS+5+for+RTX;117%2B+GPU+Spoof+Profiles;Neon+UI+%C2%B7+One-Click+Install" alt="typing" />

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🚀 Core
- **FG Modules** — OptiScaler pack for any GPU
- **DLSS 5** — Neural pack for RTX (`nvngx_dlss` + `dlssnr`)
- **Install Both** / **Recommended for GPU**
- Parallel downloads (max speed + LFS fix)
- Live size + speed meter

</td>
<td width="50%">

### 🎮 Library
- Save games · search · favorites
- Batch FG / Batch DLSS 5
- Open folder · copy path
- Stats in sidebar

</td>
</tr>
<tr>
<td>

### ⚡ Quick Setup
- Quality profiles (UQ → Ultra Perf)
- Upscaler: FSR / XeSS / DLSS / auto
- Sharpness + CAS sliders
- One-click FG / HDR / VSync / Overlays

</td>
<td>

### 🛠 Advanced & Tools
- FPS cap · ratio · anisotropy · mipmap
- Init flags · HUD presets
- Export / import INI profiles
- Backup · restore · verify · logs
- Floating overlay (`Ctrl+O`)

</td>
</tr>
</table>

<div align="center">

| Module | Target | Source |
|:------:|:------:|:------:|
| **FG** | All GPUs | `DB/FG` |
| **DLSS 5** | RTX | `DB/dls5` |
| **Spoof** | 117 cards | RTX · GTX · RX |

</div>

---

## 🎨 UI

<div align="center">

**14 auto-cycling neon themes**

`Gold` · `Orange` · `Amber` · `Rose` · `Crimson` · `Purple` · `Violet`  
`Magenta` · `Cyan` · `Teal` · `Lime` · `Sky` · `Indigo` · `Coral`

Particle network background · glass cards · animated accents

</div>

---

## 📦 Install

```bash
pip install PyQt6 requests
```

```bash
python NeoRay_FG_Installer.py
```

> Keep `neoray_icon.png` next to the script for the window icon.

**requirements.txt**
```text
PyQt6>=6.5.0
requests>=2.28.0
```

---

## ▶️ Usage

```text
 1. HOME  →  Select game .exe
 2.       →  INSTALL FG  (any GPU)
 3.       →  INSTALL DLSS 5  (RTX)  or  INSTALL BOTH
 4. QUICK →  Profile + upscaler + spoof if needed
 5.       →  Launch game
 6.       →  Insert  = OptiScaler overlay (in-game)
```

### Shortcuts

| Key | Action |
|:---:|:-------|
| `Ctrl+1…4` | Home · Library · Quick · Advanced |
| `Ctrl+S` | Settings |
| `Ctrl+O` | Floating overlay |
| `Ctrl+B` | Backup |

<div align="center">

⚠️ **After changing FG Input / Output → Save INI → restart the game**

</div>

---

## 🎯 GPU Spoof

**117 profiles** — type to search in the combo.

<details>
<summary><b>NVIDIA RTX / GTX</b></summary>

RTX 50 · 40 · 30 · 20 series · Laptop variants  
GTX 16 · 10 · 900 series · Titan · Quadro · RTX A / Ada

</details>

<details>
<summary><b>AMD Radeon RX</b></summary>

RX 9000 · 7000 · 6000 · 5000 · 500 · Vega · Mobile

</details>

---

## 🧱 Build EXE

**Single file (console):**
```bash
pyinstaller --noconfirm --onefile --name NeoRay --icon icon.ico NeoRay.py
```

**Single file (GUI only, no console):**
```bash
pyinstaller --noconfirm --onefile --noconsole --name NeoRay --icon icon.ico NeoRay.py
```

```bash
pip install pyinstaller
```

---

## 📁 Project layout

```text
NeoRay/
├── NeoRay_FG_Installer.py   # main app
├── neoray_icon.png          # icon
├── requirements.txt
└── README.md
```

Data (library, backups, settings):

```text
~/.neoray/          # default
./neoray_data/      # portable mode (portable.flag)
```

---

## 🔗 Modules origin

| Pack | Repo path |
|------|-----------|
| Frame Generation | [`DB/FG`](https://github.com/857seif/NeoRay/tree/main/DB/FG) |
| DLSS 5 | [`DB/dls5`](https://github.com/857seif/NeoRay/tree/main/DB/dls5) |

Based on **OptiScaler** ecosystem · [FG Options Wiki](https://github.com/optiscaler/OptiScaler/wiki/Frame-Generation-Options) · [Config](https://github.com/optiscaler/OptiScaler/blob/master/Config.md)

---

## 💡 Tips

- Base FPS **45–60+** before enabling FG  
- Disable Discord / EOS / heavy overlays if crashes  
- Use **TOOLS → BACKUP** before experiments  
- **Verify files** if a download looks incomplete  
- Intel HD / non-RTX → FG only (app suggests this automatically)

---

<div align="center">

### <img src="neoray_icon.png" width="36" align="absmiddle"/> NEORAY

**Frame Gen · DLSS · Spoof · Neon**

```text
████████████████████████████████████████
█  MADE FOR EVERY GPU  ·  ONE CLICK  █
████████████████████████████████████████
```

<img src="https://img.shields.io/badge/★-Star_the_repo-FFD700?style=for-the-badge" alt="star"/>

</div>
