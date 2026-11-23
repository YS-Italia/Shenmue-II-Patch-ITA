import sys
import re
import csv
from pathlib import Path
from collections import Counter

BASE_DIR = Path("/home/francesco/Scaricati")
INPUT_CSV = BASE_DIR / "english.0db084a7.csv"
WORK_CSV = BASE_DIR / "da_tradurre.csv"
OUTPUT_CSV = BASE_DIR / "italian_final.csv"

# True = scrive i 2 byte grezzi 0xA1 0xF5 (formato binario nativo del gioco)
# False = scrive la stringa ASCII letterale \xA1\xF5
USE_RAW_BYTES = True

LINE_RX = re.compile(rb'^"([^"]*)","([^"]*)","(.*)"\s*$')

IT_RX = re.compile(
    r"\b(il|lo|la|gli|le|un|una|che|non|sono|grazie|capisco|dove|posso|"
    r"trovare|scusa|scusi|bene|cosa|perché|perche'|qui|vicino|questo|questa|si')\b",
    re.I
)

ACCENT_MAP = str.maketrans({
    "ì": "i'",
    "Ì": "I'",
    "ò": "o'",
    "ó": "o'",
    "È": "E'",
    "Ò": "O'",
    "’": "'",
    "‘": "'",
    "“": '"',
    "”": '"',
})

def bytes_to_work_text(b: bytes) -> str:
    b = (b.replace(b"\xa1\xf5", b"[BR]")
          .replace(b"\\xA1\\xF5", b"[BR]")
          .replace(b"\\xa1\\xf5", b"[BR]"))
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("latin1")

def sanitize_italian(text: str) -> str:
    text = text.translate(ACCENT_MAP)
    text = (text.replace("¡õ", "[BR]")
                .replace("\ufffd", "[BR]")
                .replace("\\xA1\\xF5", "[BR]")
                .replace("\\xa1\\xf5", "[BR]"))
    text = re.sub(r"\s*\[BR\]\s*", "[BR]", text)
    text = re.sub(r"\$\s*(\d+(?:[.,]\d+)?)", r"\1$", text)
    text = re.sub(r"\bbanco\b", "bancarella", text)
    text = re.sub(r"\bBanco\b", "Bancarella", text)
    text = re.sub(r"\bbanchi\b", "bancarelle", text)
    text = re.sub(r"\bBanchi\b", "Bancarelle", text)
    text = text.replace('"', "'")
    return text

def text_to_final_bytes(text: str) -> bytes:
    sep = b"\xa1\xf5" if USE_RAW_BYTES else b"\\xA1\\xF5"
    return sep.join(p.encode("utf-8") for p in text.split("[BR]"))

def cmd_estrai():
    if not INPUT_CSV.exists():
        print(f"Errore: file non trovato in {INPUT_CSV}")
        sys.exit(1)

    raw = INPUT_CSV.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]

    freq = Counter()
    examples = {}

    for line in raw.splitlines():
        m = LINE_RX.match(line)
        if not m:
            continue
        line_id = m.group(1).decode("latin1")
        norm = bytes_to_work_text(m.group(3)).strip()
        clean = norm.replace("[BR]", " ").replace("=@", "").strip()
        if not clean or IT_RX.search(clean):
            continue
        freq[norm] += 1
        if norm not in examples:
            examples[norm] = line_id

    with WORK_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["Frequenza", "Esempio_ID", "Originale_EN", "Traduzione_IT"])
        for norm_text, count in freq.most_common():
            writer.writerow([count, examples[norm_text], norm_text, ""])

    print(f"OK -> Creato {WORK_CSV}")
    print(f"Stringhe uniche estratte: {len(freq)} (coprono {sum(freq.values())} righe nel CSV originale).")

def cmd_applica():
    if not WORK_CSV.exists():
        print(f"Errore: compila prima {WORK_CSV}")
        sys.exit(1)

    tm = {}
    with WORK_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            src = row["Originale_EN"].strip()
            trg = row["Traduzione_IT"].strip()
            if src and trg:
                tm[src] = sanitize_italian(trg)

    raw = INPUT_CSV.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    if has_bom:
        raw = raw[3:]

    out_lines = []
    replaced = 0
    forbidden_left = 0

    for line in raw.splitlines():
        m = LINE_RX.match(line)
        if not m:
            if line == b'"ZZF2057A013",""," ':
                out_lines.append(b'"ZZF2057A013",""," "')
            else:
                out_lines.append(line)
            continue

        col_id = m.group(1)
        col_2 = m.group(2)
        orig_text = bytes_to_work_text(m.group(3))

        lead_ws = orig_text[:len(orig_text) - len(orig_text.lstrip(" "))]
        trail_ws = orig_text[len(orig_text.rstrip(" ")):]
        core = orig_text.strip()

        if core in tm:
            final_text = f"{lead_ws}{tm[core]}{trail_ws}"
            replaced += 1
        else:
            final_text = sanitize_italian(orig_text)

        if re.search(r"[ìòóÈÒÌ]", final_text):
            forbidden_left += 1

        final_bytes = text_to_final_bytes(final_text)
        out_lines.append(b'"' + col_id + b'","' + col_2 + b'","' + final_bytes + b'"')

    with OUTPUT_CSV.open("wb") as f:
        if has_bom:
            f.write(b"\xef\xbb\xbf")
        f.write(b"\n".join(out_lines) + b"\n")

    print(f"OK -> Creato {OUTPUT_CSV}")
    print(f"Righe aggiornate dal dizionario: {replaced}")
    print(f"Righe con accenti vietati residui: {forbidden_left}")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("estrai", "applica"):
        print("Uso: python3 shenmue_tool.py [estrai|applica]")
        sys.exit(1)
    cmd_estrai() if sys.argv[1] == "estrai" else cmd_applica()
