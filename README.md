# Habit Tracker

A standalone, offline habit tracker in **one file: `index.html`**. No Python, server, packages, or network connection required.

## Run

Download `index.html` and open it in your browser.

Create, rename, and delete habits; complete or undo today; track current streaks. A streak includes yesterday if you have not completed today yet. Dates follow your device's local calendar.

## Storage and JSON backups

Changes automatically save in browser `localStorage`. **Your exported JSON files are your durable backups.** Browser data can disappear if you clear site data, use private browsing, change browsers, or move the HTML file. Keep using the same browser and file location, and export after important changes.

- **Export JSON:** downloads all habits and completion history to `habits-YYYY-MM-DD.json`. Keep the download somewhere safe. It is a snapshot; later edits require another export. The app requests a download but cannot confirm that you retained the file.
- **Import JSON:** choose an existing backup and confirm replacement of all current habits. Export first to preserve the current set. Imports do not merge. Invalid files leave current data untouched.
- If browser storage is unavailable, the app still works in memory and displays a warning. Export before closing.
- An unreadable browser save is left untouched; import a valid backup to recover.

Existing `habits.json` files from the Python version can be imported directly. Nothing is read or written automatically to a disk JSON file. Imports and exports use the original array format:

```json
[
  {
    "id": 1,
    "name": "Read",
    "created": "2026-10-06",
    "completions": ["2026-10-06"]
  }
]
```

IDs must be unique positive safe integers. Names must be nonempty strings. Dates must be valid `YYYY-MM-DD` calendar dates, and completion dates must not repeat within a habit. The empty array `[]` is valid. Derived fields from the old API are recalculated.

## Validation

Run `node --test tests/storage.test.cjs` for import validation, storage failure/recovery, export round trips, and local-calendar streak checks. Node is only needed for development tests.

## License

MIT
