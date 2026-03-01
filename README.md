# SmartUni

A Streamlit-based university program recommender that helps you find Bachelor programs matching your preferences.

## Features

- **Form mode**: Select field, country, language, budget, and GPA via dropdowns
- **AI mode**: Describe your desires in natural language; Gemini parses them and finds matching programs

## Project Structure

```
SmartUni/
├── app.py                 # Main Streamlit entry point
├── config.py              # Constants (fields, countries, budgets, etc.)
├── requirements.txt
├── README.md
├── smartuni_dataset_v4.csv
├── data/                  # Data loading
│   └── loader.py
├── filtering/             # Filter logic
│   └── filters.py
├── scoring/               # Scoring logic
│   └── scorer.py
├── apply/                 # Application steps by system
│   └── steps.py
└── gemini/                # Gemini API for natural language parsing
    └── parser.py
```

## Setup

1. **Clone or download** the repository.

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Place your dataset** `smartuni_dataset_v4.csv` in the project root (same folder as `app.py`).

4. **For AI mode**, set your Gemini API key (environment or `.env` file):
   ```bash
   export GEMINI_API_KEY=your_api_key_here
   ```
   You can copy `.env.example` to `.env` and fill in your key.
   Get a key from [Google AI Studio](https://aistudio.google.com/apikey).

## Run

```bash
streamlit run app.py
```

The app opens in your browser. Use **Form** mode for dropdown-based search, or **AI** mode to describe your preferences in natural language.

## Environment Variables

| Variable        | Description                          |
|----------------|--------------------------------------|
| `GEMINI_API_KEY` | Google Gemini API key (for AI mode) |
| `GOOGLE_API_KEY` | Alternative env var for API key     |

## License

MIT
