# 🖐️ Virtual Mouse Using Hand Gesture

This project implements a **Virtual Mouse Controller** using **Google MediaPipe** and **OpenCV**. It enables users to control the mouse pointer through **hand gestures** in real-time via webcam.

> Built with Python 3.10–3.11, this application provides a hands-free, AI-driven alternative to traditional mouse input.

---

## 🚀 Features

- Real-time hand detection and tracking via webcam  
- Control mouse cursor using index finger movement  
- Click, drag, scroll actions using specific hand gestures  
- Smooth and responsive experience using gesture stabilization

---

## 🛠️ Environment Setup

This project requires **Python 3.10–3.11**. It is highly recommended to use a **virtual environment (`venv`)** to avoid conflicts with global packages.

### ✅ 1. Clone the repository

```bash
git clone https://github.com/roddely/VirtualMouse.git
cd VirtualMouse
```
### ✅ 2. Create and activate virtual environment

We recommend using a [virtual environment](https://docs.python.org/3/library/venv.html) to isolate dependencies.

```bash
python -m venv venv
```
then activate it (depends on your OS)

### ✅ 3. Install dependencies
```bash
pip intall -r requirements.txt
```

### ▶️ How to Run
After setting up the environment, simply run:
```bash
python src/AiVirtualMouseProject.py
```

---

### 🤏 Hand Gestures Supported

☝️ Index Finger Up: Move Cursor 

🖐️ Index tap middle finger: Right click

✌️ Only Index + Middle Up: Toggle mode

🖐️ Index tap thumb: Left click

🤏 Only index + thumb: Scroll mode

✊ Fist:  win + tab

 🖐️✊🖐️ Fist and open immediately: Back to desk top (win + d)
 

- Movement is based on normalized hand landmarks, mapped to screen resolution.
- Clicking is detected when the distance between index and middle fingertips is below a threshold.
- Dragging is active when index and middle touch and remain together.

---

### 📦 Dependencies

MediaPipe

OpenCV

PyAutoGUI / Autopy (for controlling mouse)

NumPy

All dependencies are included in requirements.txt

---
[Video demo](demo.mp4)
---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

© 2025 Nguyễn Hoàng Phúc (roddely)


