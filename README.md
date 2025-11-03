# ListingEditor

A small, local CLI tool that lets you edit (mock) Amazon listings by entering an ASIN.

This project is intentionally small and offline: it uses a local JSON file (`data/listings.json`) as the data store so you can try editing listings without any external API keys or network calls.

## Features
- Enter an ASIN to look up a listing
- Create a new listing if the ASIN does not exist
- View and edit basic fields (title, price, description, quantity)
- Changes are saved back to `data/listings.json`

## Files added
- `src/listing_editor.py` — the CLI implementation
- `data/listings.json` — sample listings database
- `test.py` — small runner to launch the CLI

## Requirements
- Python 3.8+

## Quick start (Windows PowerShell)

1. Ensure you have Python 3 installed and on your PATH.
2. From the project root run:

```powershell
python .\test.py
```

3. Follow the prompts: enter an ASIN (for example `B000123`), then choose fields to edit.

## Notes and safety
- This is a local mock editor and does NOT connect to Amazon or modify any real listings.
- For production usage you'd replace the JSON backend with actual API calls and add authentication, rate-limiting and error handling.

## Next steps (optional)
- Add unit tests for the editor functions
- Add an API backend to sync edits with a real service

Happy editing!
