[![QGIS Plugin](https://img.shields.io/badge/QGIS-Plugin-green?logo=qgis)](https://plugins.qgis.org/plugins/ClipMultipleLayers/)
[![Donate](https://img.shields.io/badge/Donate-PayPal-blue?logo=paypal)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=4DC3A78C398HW)

# Plugin for QGIS: Clip Multiple Layers

## Description
<p align="center">
<img height="400em" alt="dialog3" src="https://github.com/user-attachments/assets/0e90da45-996c-458c-8363-5525669d34e7" />
</p>
This plugin allows you to clip multiple vector and raster layers using a selected mask layer. The resulting layers can then be loaded into the project.

---

## Issues
You can report a new issue [here](https://github.com/Taknok/Qgisplugin-ClipMultipleLayers/issues/new) and view existing ones [here](https://github.com/Taknok/Qgisplugin-ClipMultipleLayers/issues).

---

## Developers

### 0. Development setup

```bash
python -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
sudo apt install qt6-tools-dev-tools   # Linux
```

### 1. Load the plugin dynamically in QGIS
Windows:
```cmd
cmd /c mklink /d %APPDATA%\QGIS\QGIS4\profiles\default\python\plugins\ClipMultipleLayers D:\path\to\ClipMultipleLayers
```

Linux:
```bash
ln -s ~/.local/share/QGIS/QGIS4/profiles/default/python/plugins/ClipMultipleLayers /path/to/ClipMultipleLayers
```

### 2. Extract translatable strings from UI files
```bash
pylupdate6 src/ui/*.ui -ts i18n/${LOCALE}.ts
```

### 3. Compile translations
```bash
./scripts/compile-translation.sh
```

### 4. Compile resources
For icon. 
```bash
pyrcc6 -o resources.py resources.qrc
```

### 5. UI editing
Edit the UI file using Qt Designer (Qt Creator): `src/ui/clip_multiple_layers_dialog_base.ui`

## Donation
If you find this plugin useful, feel free [to support me](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=4DC3A78C398HW)

## Acknowledgements
Thank to :
 - [shtirlitsDva](https://github.com/shtirlitsDva)
 - [zsiki](https://github.com/zsiki)
