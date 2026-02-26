# SentinelFS Atlas

SentinelFS Atlas is a Streamlit multipage proof-of-concept for monitoring country-level food-system risk using synthetic indicators and scenario stress testing.

## Project structure

```text
app.py
pages/
sentinelfs/
data/
.streamlit/
```

## Local run

1. Create a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional for Action Tracking) set Neon URL:
   ```bash
   export NEON_DATABASE_URL="postgresql://..."
   ```
4. Start Streamlit:
   ```bash
   streamlit run app.py
   ```

## Streamlit Cloud deployment

1. Push this repository to GitHub.
2. In Streamlit Community Cloud, create a new app from this repo.
3. Set **Main file path** to `app.py`.
4. Add secrets in **App settings → Secrets**:
   ```toml
   NEON_DATABASE_URL = "postgresql://..."
   ```
5. Deploy.

## Notes

- Map join key is ISO3 only (`properties.ISO_A3` in `data/world_countries.geojson`).
- Action Tracking uses Neon Postgres via SQLAlchemy and never uses SQLite.
- Demo dataset is synthetic and intended for PoC behavior only.
