# QuickWEBPer

## Description
Convert your images to net-ready WEBPs (and back)!

No tweaking needed, vector and raster files supported.

![Image](<https://raw.githubusercontent.com/MariaWasNotAvailable/QuickWEBPer/main/qw.webp>)

![Image](<https://raw.githubusercontent.com/MariaWasNotAvailable/QuickWEBPer/main/qwg.webp>)

## Installation

Requires Python 3.

Windows:
```
git clone https://github.com/MariaWasNotAvailable/QuickWEBPer.git
cd QuickWEBPer
python -m venv venv
venv\Scripts\Activate
python -m pip install -r requirements.txt
```
(or just run the .exe release)

Linux:
```
git clone https://github.com/MariaWasNotAvailable/QuickWEBPer.git
cd QuickWEBPer
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Usage
```
python webper filename.png
```
or
```
python webper C:\filename.webp
```
or
```
python webper entire\folder\path
```
or
```
python webper # either of these...
webper.exe    # ...will open the GUI
```

## Rationale
QuickWEBPer was conceived as a "no-config" batch converter, i. e. with a web-ready input content-reactive compression profile. It silently skips non-image files so you don't have to be too careful about multiple file input. 
