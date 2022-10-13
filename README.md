# LabelTracking
Sequence labeling

## Dependencies
- Python3
- PySide6
- numpy
- opencv-python
- opencv-contrib-python

## Setup
Install dependencies from pip
```
pip3 install -r requirements.txt
```

## Run
You can easily run app with the following command
```
python3 main.py
```
If you are developer, you can hotreloading with jurigged
```
pip3 install jurigged
python3 -m jurigged -v main.py
```

## Packaging
You can create binary package with pyinstaller
```
pip3 install pyinstaller
pyinstaller main.py --windowed --onefile --add-data icons:icons
```

## Icons
Download from https://fonts.google.com/icons
