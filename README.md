# Nightline

Nightline is a Raspberry Pi parking display for a 480×320 touchscreen. Its
sensor-first home and four-front-sensor parking view use a transport-neutral
provider boundary; realistic simulation is enabled until hardware is selected.

## UI toolkit

Nightline uses **PySide6**, the official Qt for Python binding. It provides the
Qt 6 API needed by the Raspberry Pi UI while allowing the application code to
remain portable and testable off-device.

## Raspberry Pi setup

The supported development target is the Raspberry Pi:

```sh
ssh rushilpunu@pi.local
cd /home/rushilpunu/Nightline/Nightline
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

`requirements.txt` installs Nightline itself in editable mode, so its
`src/`-layout package is available to both launch commands.

## Run

From an active desktop session on the Pi, launch either entry point:

```sh
.venv/bin/python -m nightline.app
scripts/run_dev.sh
```

When launching through SSH, forward the graphical session environment (for
example `DISPLAY=:0`) as appropriate for the Pi's desktop configuration.
Configuration can be supplied through environment variables; currently
`NIGHTLINE_APP_NAME`, `NIGHTLINE_WINDOW_WIDTH`, and
`NIGHTLINE_WINDOW_HEIGHT` are supported.

The production config launches fullscreen at 480×320. For a windowed developer
run use `NIGHTLINE_FULLSCREEN=false`; width and height may also be overridden.

For a headless startup/clean-shutdown check over SSH, use Qt's offscreen
backend and the development timeout:

```sh
QT_QPA_PLATFORM=offscreen .venv/bin/python -m nightline.app --quit-after-ms 100
QT_QPA_PLATFORM=offscreen scripts/run_dev.sh --quit-after-ms 100
```

## Test

```sh
.venv/bin/python -m pytest
```

The UI smoke test uses Qt's offscreen platform and does not require a display.
