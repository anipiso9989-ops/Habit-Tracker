# Habit Tracker

A simple, local habit tracker built with Python, HTML, CSS, and vanilla JavaScript.

## Features

- Create, rename, and delete habits
- Mark habits complete for the day
- Undo today's completion
- Track current streaks
- Persist data locally in `habits.json`
- Responsive, minimal interface

## How it works

`app.py` runs a small HTTP server and exposes endpoints for managing habits. The frontend in `index.html` uses those endpoints to update the interface, while habit data is stored in `habits.json`.

No external packages are required. Make sure you have python installed on your device, though.

## Run

```bash
python app.py
```

Then open:

```
http://localhost:8000
```

## License

MIT
