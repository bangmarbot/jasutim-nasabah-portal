# JASUTIM Nasabah Portal

Portal sederhana untuk cek saldo nasabah JASUTIM secara mandiri.

## Fitur MVP
- Input nomor rekening
- Captcha sederhana
- Tampil total tonase
- Tampil saldo saat ini
- Nama nasabah dimasking

## Stack
- Python
- Flask
- Google Sheets API via gspread

## Environment Variables
- `SECRET_KEY`
- `JASUTIM_SPREADSHEET_ID`
- `GOOGLE_SERVICE_ACCOUNT_JSON` **atau** `GOOGLE_SERVICE_ACCOUNT_FILE`
- `PORT`

## Run local
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Lalu buka:
`http://localhost:8787`

## Notes
- Repo ini terpisah dari `jasutim-bot`
- Bisa deploy ke Vercel atau VPS/subdomain seperti `nasabah-jasutim.aidia.uk`

## Deploy ke Vercel
Set environment variables berikut di project Vercel:
- `SECRET_KEY`
- `JASUTIM_SPREADSHEET_ID`
- `GOOGLE_SERVICE_ACCOUNT_JSON`

`GOOGLE_SERVICE_ACCOUNT_JSON` berisi full JSON service account Google dalam satu string JSON.
