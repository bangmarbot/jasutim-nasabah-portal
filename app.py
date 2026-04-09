#!/usr/bin/env python3
"""JASUTIM Nasabah Portal - saldo checker web app."""

import os
import random
from flask import Flask, jsonify, render_template, request
import gspread

SPREADSHEET_ID = os.environ.get("JASUTIM_SPREADSHEET_ID", "1rxCkiD_C2rMbFBU5tfTjV6UuBAXoRVO2nAEKPDoFWZ4")
GOOGLE_SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
GOOGLE_SERVICE_ACCOUNT_FILE = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret")

_gc = None
_sh = None


def get_sheet():
    global _gc, _sh
    if _sh is not None:
        return _sh

    if GOOGLE_SERVICE_ACCOUNT_JSON:
        _gc = gspread.service_account_from_dict(__import__("json").loads(GOOGLE_SERVICE_ACCOUNT_JSON))
    else:
        _gc = gspread.service_account(filename=GOOGLE_SERVICE_ACCOUNT_FILE)

    _sh = _gc.open_by_key(SPREADSHEET_ID)
    return _sh


def ws(name: str):
    return get_sheet().worksheet(name)


def format_rp(n):
    return f"Rp {n:,.0f}".replace(",", ".")


def format_kg(n):
    s = f"{n:.2f}".rstrip("0").rstrip(".")
    return s.replace(".", ",")


def mask_name(name: str) -> str:
    if not name:
        return "-"
    parts = name.split()
    masked = []
    for part in parts:
        if len(part) <= 2:
            masked.append(part[0] + "*")
        else:
            masked.append(part[:2] + "*" * (len(part) - 2))
    return " ".join(masked)


def find_nasabah(no_rek: str):
    rows = ws("Nasabah").get_all_records()
    for row in rows:
        if row.get("No Rek") == no_rek and row.get("Status") == "Aktif":
            return row
    return None


def get_harga_map():
    rows = ws("Master Harga").get_all_records()
    harga = {}
    for row in rows:
        kode = row.get("Kode")
        if not kode:
            continue
        try:
            harga[kode] = int(round(float(row.get("Harga Nasabah Default") or row.get("Harga Nasabah") or 0)))
        except Exception:
            harga[kode] = 0
    return harga


def get_saldo(no_rek: str):
    rows = ws("Transaksi Nasabah").get_all_records()
    harga_map = get_harga_map()

    total_kg = 0.0
    total_rp = 0
    for row in rows:
        if row.get("No Rek") != no_rek:
            continue

        try:
            qty = float(row.get("Qty") or row.get("Berat (Kg)") or 0)
        except Exception:
            qty = 0.0

        unit = row.get("Unit") or "kg"
        kode = row.get("Kode") or ""

        try:
            jumlah = int(round(float(row.get("Jumlah") or 0)))
        except Exception:
            jumlah = 0

        if jumlah <= 0:
            jumlah = int(round(qty * harga_map.get(kode, 0)))

        if unit == "kg":
            total_kg += qty
        total_rp += jumlah

    return {
        "total_kg": total_kg,
        "total_rp": total_rp,
    }


def new_captcha():
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    return {"a": a, "b": b, "answer": a + b}


@app.get("/")
def index():
    captcha = new_captcha()
    return render_template("index.html", captcha=captcha)


@app.get("/health")
def health():
    return jsonify({"ok": True})


@app.post("/api/check-saldo")
def check_saldo():
    payload = request.get_json(silent=True) or {}
    no_rek = (payload.get("no_rek") or "").strip().upper()
    captcha_answer = str(payload.get("captcha_answer") or "").strip()
    captcha_expected = str(payload.get("captcha_expected") or "").strip()

    if not no_rek:
        return jsonify({"ok": False, "error": "Nomor rekening wajib diisi."}), 400

    if not captcha_answer or captcha_answer != captcha_expected:
        return jsonify({"ok": False, "error": "Captcha tidak valid."}), 400

    nasabah = find_nasabah(no_rek)
    if not nasabah:
        return jsonify({"ok": False, "error": "Nomor rekening tidak ditemukan."}), 404

    saldo = get_saldo(no_rek)

    return jsonify({
        "ok": True,
        "data": {
            "nama": mask_name(nasabah.get("Nama", "")),
            "no_rek": no_rek,
            "total_kg": format_kg(saldo["total_kg"]),
            "total_rp": format_rp(saldo["total_rp"]),
        }
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8787"))
    app.run(host="0.0.0.0", port=port, debug=False)
