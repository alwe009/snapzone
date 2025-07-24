
# 📸 SnapZone

**SnapZone** is a powerful, user-friendly GUI application that allows you to automatically capture screenshots of a selected region of your screen at specified intervals. It runs in the system tray, supports custom capture durations, intervals, and provides real-time logging, notifications, and visual region selection.

---

## 🧩 Features

- 🎯 Select a custom region of the screen to capture  
- ⏱ Set capture interval and total duration  
- 💾 Automatically save screenshots in organized session folders  
- 📋 Real-time logging and capture status  
- 🖥️ Clean and responsive GUI built with Tkinter  
- 🧰 Runs in the background via a system tray icon  
- 🛑 Pause and resume capturing at any time  
- 🔔 Optional desktop notifications for each screenshot  

---

## 🖼️ Screenshot


<img width="504" height="634" alt="screenshot" src="https://github.com/user-attachments/assets/8430aee8-f6e7-4a69-bea7-a101ca70d2e7" />


---

## 🛠️ Installation

### 🔗 Requirements

- Python 3.7+
- Windows OS (recommended)

### 📦 Install dependencies

```bash
pip install pillow plyer pystray
```

---

## 🚀 Usage

### ▶️ Run from source

```bash
python snapzone.py
```

### 📦 Run as executable

Download the executable file

```bash
https://github.com/alwe009/snapzone/blob/main/dist/snapzone.exe
```

> 💡 Ideal for users without Python installed.

---

## 🧳 How It Works

1. Launch SnapZone
2. Set:
   - **Duration** (in seconds)
   - **Interval** (delay between screenshots)
   - **Save Directory**
3. Click `Select Region` to mark the area you want to capture
4. Click `Start Capture`
5. SnapZone minimizes to the tray and captures screenshots until stopped
6. Use tray or GUI to pause/resume/stop anytime

---

## ⚙️ Building an Executable

To build a standalone Windows executable using [PyInstaller](https://pyinstaller.org/):

```bash
pyinstaller --noconfirm --onefile --windowed snapzone.py
```

- Output `.exe` will be located in the `dist/` folder

---

## 🗃️ Screenshot Output Structure

Captured screenshots are saved in timestamped folders:

```
<Save Directory>/
└── SnapZone_Session_YYYYMMDD_HHMMSS/
    ├── screenshot_YYYYMMDD_HHMMSS_0001.png
    ├── screenshot_YYYYMMDD_HHMMSS_0002.png
    └── ...
```

---


## 🐞 Troubleshooting

- Make sure Python has screen capture permissions
- On Windows, run as administrator if ImageGrab fails
- Multi-monitor setups may require extra testing
- Region selection needs minimum 10x10 area

---

## Disclaimer

This software includes code generated with the help of AI tools. Although AI contributed significantly, the creation and effective use of this project rely on human knowledge—such as crafting proper prompts, reviewing, and integrating the code.

The project is provided "as-is" without any warranties or guarantees. No full ownership or credit is claimed by the author. Users are welcome to use, modify, and build upon this software at their own risk.

A foundational understanding of programming and active involvement are recommended to customize and operate the application successfully.

