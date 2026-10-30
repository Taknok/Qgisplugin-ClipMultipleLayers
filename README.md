[![QGIS Plugin](https://img.shields.io/badge/QGIS-Plugin-green?logo=qgis)](https://plugins.qgis.org/plugins/ClipMultipleLayers/)
[![Donate](https://img.shields.io/badge/Donate-PayPal-blue?logo=paypal)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=4DC3A78C398HW)

# Plugin for QGIS: Clip Multiple Layers

## Description
<p align="center">
<img height="400em" alt="dialog3" src="https://github.com/user-attachments/assets/0e90da45-996c-458c-8363-5525669d34e7" />
</p>
This plugin allows you to clip multiple vector and raster layers using a selected mask layer. The resulting layers can then be loaded into the project.
Optionally, create an output subfolder named after the selected mask layer.

---

## Issues
You can report a new issue [here](https://github.com/Taknok/Qgisplugin-ClipMultipleLayers/issues/new) and view existing ones [here](https://github.com/Taknok/Qgisplugin-ClipMultipleLayers/issues).


## Translators
Duplicate a `.ts` file for the new language and create a new PR.

## Developers

### 0. Development setup

```bash
python -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
sudo apt install qt6-tools-dev-tools   # Linux
```

### Development container

Open the repository from a WSL distribution with WSLg enabled, then choose
**Dev Containers: Reopen in Container** in VS Code. The container installs
QGIS, Python dependencies from `requirements.txt`, and Qt 6 tools. WSLg is used
to display the QGIS desktop application. Start QGIS from the container
terminal using `bash scripts/run-qgis.sh`. This launcher isolates QGIS from
the project's Python virtual environment, whose Qt bindings can conflict with
the system Qt used by QGIS.

Run these commands from the repository root inside the container:

```bash
# 1. Extract UI strings into every translation file
bash scripts/update-ui-translations.sh

# 2. Compile all translations
bash scripts/compile-translation.sh

# 3. Compile the Qt resources
bash scripts/compile-resources.sh
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
bash scripts/update-strings.sh
```

### 3. Compile translations
```bash
bash scripts/compile-translation.sh
```

### 4. Compile resources
For icon.
```bash
bash scripts/compile-resources.sh
```

### 5. UI editing
Edit the UI file using Qt Designer (Qt Creator): `src/ui/clip_multiple_layers_dialog_base.ui`

## Donation
If you find this plugin useful, feel free [to support me](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=4DC3A78C398HW)

## Acknowledgements
Thank to :
 - [shtirlitsDva](https://github.com/shtirlitsDva)
 - [zsiki](https://github.com/zsiki)
