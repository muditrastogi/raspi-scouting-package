# Quick Start Guide - Windows Scouting Package

## 🚀 Super Quick Setup (5 minutes)

### Prerequisites Check
- ✅ Windows 10/11
- ✅ Python 3.7+ installed with PATH
- ✅ 3 USB cameras connected
- ✅ Git installed

### 1. Get the Code
```cmd
git clone https://github.com/your-repo/raspi-scouting-package.git
cd raspi-scouting-package
git checkout win-scripts
```

### 2. Complete Setup (Automated)
**Double-click:** `Setup_Project.bat`

This will automatically:
- Check Python
- Install packages
- Test cameras
- Configure cameras
- Create shortcuts

### 3. Start Using
**Double-click:** `Start_Camera_UI.bat`

---

## 🎯 Manual Setup (Step by Step)

### Step 1: Install Dependencies
```cmd
pip install -r windows_requirements.txt
```

### Step 2: Test Cameras
**Double-click:** `Test_Camera_Detection.bat`

### Step 3: Configure Camera Positions
**Double-click:** `Configure_Cameras.bat`

### Step 4: Create Shortcuts
**Run as Administrator:**
```cmd
powershell -ExecutionPolicy Bypass -File Create_Desktop_Shortcuts.ps1
```

### Step 5: Launch Application
**Double-click:** `Start_Camera_UI.bat`

---

## 🔧 Clickable Files Overview

| File | Purpose | When to Use |
|------|---------|-------------|
| `Setup_Project.bat` | Complete automated setup | First time setup |
| `Start_Camera_UI.bat` | Launch main application | Daily use |
| `Configure_Cameras.bat` | Set up camera positions | When cameras change |
| `Test_Camera_Detection.bat` | Troubleshoot camera issues | When cameras not working |
| `Create_Desktop_Shortcuts.ps1` | Create desktop shortcuts | For convenience |
| `Install_Start_Menu.bat` | Add to Start Menu | For system integration |

---

## 🎬 Using the Application

### Basic Workflow
1. **Start Application**: Double-click `Start_Camera_UI.bat`
2. **Start Cameras**: Click "Start All Streams"
3. **Begin Recording**: Click "Start Recording All"
4. **Navigate Grids**: Use Forward/Back buttons
5. **Switch A/B**: Use "Toggle A/B" button
6. **Stop Recording**: Click "Stop Recording All"

### Camera Layout
- **Left Panel**: Bottom camera (first)
- **Middle Panel**: Middle camera (second)
- **Right Panel**: Top camera (third)

### Recording Location
Videos saved to: `C:\Users\{username}\Desktop\scout-videos\`

---

## ⚠️ Troubleshooting Quick Fixes

### "No cameras found"
1. Run `Test_Camera_Detection.bat`
2. Check USB connections
3. Run `Configure_Cameras.bat`

### "Python not found"
1. Reinstall Python with "Add to PATH" checked
2. Restart Command Prompt

### "Permission denied"
1. Close other camera applications
2. Run as Administrator
3. Check antivirus settings

### "wmic command failed"
1. Run Command Prompt as Administrator
2. Try: `net start winmgmt`

---

## 📱 Contact & Support

- **Documentation**: See `PROJECT_SETUP_GUIDE.md`
- **Camera Config**: See `WINDOWS_CAMERA_CONFIG.md`
- **Issues**: Create GitHub issue
- **Questions**: Check troubleshooting sections

---

## 💡 Pro Tips

- **Use USB 3.0 ports** for better performance
- **Avoid USB hubs** when possible
- **Close other camera apps** before starting
- **Configure cameras once**, then just use `Start_Camera_UI.bat`
- **Check config.txt** if camera order seems wrong
