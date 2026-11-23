import sys
import re
import csv
from pathlib import Path
from collections import Counter

<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
# Cartella in cui si trova questo script (qui verranno creati da_tradurre.csv e italian_final.csv)
BASE_DIR = Path(__file__).resolve().parent
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
# Rileva automaticamente la cartella in cui si trova questo script
BASE_DIR = Path(__file__).resolve().parent
INPUT_CSV = BASE_DIR / "english.0db084a7.csv"
>>>>>>> Stashed changes
WORK_CSV = BASE_DIR / "da_tradurre.csv"
OUTPUT_CSV = BASE_DIR / "italian_final.csv"

LINE_RX = re.compile(rb'^"([^"]*)","([^"]*)","(.*)"\s*$')

<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
# Byte reali 0xA1 0xF5 ('¡õ' in Latin-1)
RAW_SEP_BYTES = b"\xa1\xf5"
RAW_SEP_STR = RAW_SEP_BYTES.decode("latin1")
=======
# In Latin-1 (iso-8859-1) i byte 0xA1 0xF5 corrispondono ai caratteri '¡õ'
RAW_SEP_BYTES = b"\xa1\xf5"
RAW_SEP_STR = RAW_SEP_BYTES.decode("latin1")  # '¡õ'
>>>>>>> Stashed changes
=======
# In Latin-1 (iso-8859-1) i byte 0xA1 0xF5 corrispondono ai caratteri '¡õ'
RAW_SEP_BYTES = b"\xa1\xf5"
RAW_SEP_STR = RAW_SEP_BYTES.decode("latin1")  # '¡õ'
>>>>>>> Stashed changes
=======
# In Latin-1 (iso-8859-1) i byte 0xA1 0xF5 corrispondono ai caratteri '¡õ'
RAW_SEP_BYTES = b"\xa1\xf5"
RAW_SEP_STR = RAW_SEP_BYTES.decode("latin1")  # '¡õ'
>>>>>>> Stashed changes
=======
# In Latin-1 (iso-8859-1) i byte 0xA1 0xF5 corrispondono ai caratteri '¡õ'
RAW_SEP_BYTES = b"\xa1\xf5"
RAW_SEP_STR = RAW_SEP_BYTES.decode("latin1")  # '¡õ'
>>>>>>> Stashed changes

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

<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
def resolve_input_csv(arg_path: str | None) -> Path:
    # 1. Se passato da riga di comando, usa quel percorso esatto
    if arg_path:
        p = Path(arg_path).expanduser().resolve()
        if p.exists():
            return p
        print(f"Errore: il file specificato non esiste -> {p}")
        sys.exit(1)

    # 2. Altrimenti cerca nella cartella dello script
    local_default = BASE_DIR / "english.0db084a7.csv"
    if local_default.exists():
        return local_default

    # 3. Altrimenti cerca nella cartella corrente da cui hai aperto il terminale
    cwd_default = Path.cwd() / "english.0db084a7.csv"
    if cwd_default.exists():
        return cwd_default

    print("Errore: specifica il percorso del file CSV sorgente.")
    print("Esempio: python3 shenmue_tool.py estrai /percorso/qualsiasi/english.0db084a7.csv")
    sys.exit(1)

=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
def bytes_to_latin1_text(b: bytes) -> str:
    b = b.replace(b"\\xA1\\xF5", RAW_SEP_BYTES).replace(b"\\xa1\\xf5", RAW_SEP_BYTES)
    return b.decode("latin1")

def sanitize_italian(text: str) -> str:
    try:
        text = text.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    text = text.translate(ACCENT_MAP)
    text = (text.replace("\ufffd", RAW_SEP_STR)
                .replace("\\xA1\\xF5", RAW_SEP_STR)
                .replace("\\xa1\\xf5", RAW_SEP_STR))

<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    text = re.sub(r"\s*" + re.escape(RAW_SEP_STR) + r"\s*", RAW_SEP_STR, text)
    text = re.sub(r"\$\s*(\d+(?:[.,]\d+)?)", r"\1$", text)

=======
    # Rimuove spazi superflui attorno ai byte 0xA1 0xF5 ('¡õ')
    text = re.sub(r"\s*" + re.escape(RAW_SEP_STR) + r"\s*", RAW_SEP_STR, text)

    # Simbolo $ sempre dopo il numero (es. $50 -> 50$)
    text = re.sub(r"\$\s*(\d+(?:[.,]\d+)?)", r"\1$", text)

    # Regola lessicale: banco -> bancarella
>>>>>>> Stashed changes
=======
    # Rimuove spazi superflui attorno ai byte 0xA1 0xF5 ('¡õ')
    text = re.sub(r"\s*" + re.escape(RAW_SEP_STR) + r"\s*", RAW_SEP_STR, text)

    # Simbolo $ sempre dopo il numero (es. $50 -> 50$)
    text = re.sub(r"\$\s*(\d+(?:[.,]\d+)?)", r"\1$", text)

    # Regola lessicale: banco -> bancarella
>>>>>>> Stashed changes
=======
    # Rimuove spazi superflui attorno ai byte 0xA1 0xF5 ('¡õ')
    text = re.sub(r"\s*" + re.escape(RAW_SEP_STR) + r"\s*", RAW_SEP_STR, text)

    # Simbolo $ sempre dopo il numero (es. $50 -> 50$)
    text = re.sub(r"\$\s*(\d+(?:[.,]\d+)?)", r"\1$", text)

    # Regola lessicale: banco -> bancarella
>>>>>>> Stashed changes
=======
    # Rimuove spazi superflui attorno ai byte 0xA1 0xF5 ('¡õ')
    text = re.sub(r"\s*" + re.escape(RAW_SEP_STR) + r"\s*", RAW_SEP_STR, text)

    # Simbolo $ sempre dopo il numero (es. $50 -> 50$)
    text = re.sub(r"\$\s*(\d+(?:[.,]\d+)?)", r"\1$", text)

    # Regola lessicale: banco -> bancarella
>>>>>>> Stashed changes
    text = re.sub(r"\bbanco\b", "bancarella", text)
    text = re.sub(r"\bBanco\b", "Bancarella", text)
    text = re.sub(r"\bbanchi\b", "bancarelle", text)
    text = re.sub(r"\bBanchi\b", "Bancarelle", text)

<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
=======
    # Evita virgolette doppie interne che romperebbero il CSV
>>>>>>> Stashed changes
=======
    # Evita virgolette doppie interne che romperebbero il CSV
>>>>>>> Stashed changes
=======
    # Evita virgolette doppie interne che romperebbero il CSV
>>>>>>> Stashed changes
=======
    # Evita virgolette doppie interne che romperebbero il CSV
>>>>>>> Stashed changes
    text = text.replace('"', "'")
    return text

def text_to_exact_bytes(text: str) -> bytes:
    parts = text.split(RAW_SEP_STR)
    return RAW_SEP_BYTES.join(p.encode("utf-8") for p in parts)
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
=======
=======
=======
=======

def is_already_italian(text: str) -> bool:
    clean = text.replace(RAW_SEP_STR, " ").replace("=@", "").strip()
    if not clean:
        return True
    try:
        clean_utf8 = clean.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        clean_utf8 = clean
    return bool(IT_RX.search(clean_utf8))
>>>>>>> Stashed changes

def is_already_italian(text: str) -> bool:
    clean = text.replace(RAW_SEP_STR, " ").replace("=@", "").strip()
    if not clean:
        return True
    try:
        clean_utf8 = clean.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        clean_utf8 = clean
    return bool(IT_RX.search(clean_utf8))
>>>>>>> Stashed changes

def is_already_italian(text: str) -> bool:
    clean = text.replace(RAW_SEP_STR, " ").replace("=@", "").strip()
    if not clean:
        return True
    try:
        clean_utf8 = clean.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        clean_utf8 = clean
    return bool(IT_RX.search(clean_utf8))
>>>>>>> Stashed changes

def is_already_italian(text: str) -> bool:
    clean = text.replace(RAW_SEP_STR, " ").replace("=@", "").strip()
    if not clean:
        return True
    try:
        clean_utf8 = clean.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        clean_utf8 = clean
    return bool(IT_RX.search(clean_utf8))
>>>>>>> Stashed changes

def is_already_italian(text: str) -> bool:
    clean = text.replace(RAW_SEP_STR, " ").replace("=@", "").strip()
    if not clean:
        return True
    try:
        clean_utf8 = clean.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        clean_utf8 = clean
    return bool(IT_RX.search(clean_utf8))

def cmd_estrai(input_csv: Path):
    raw = input_csv.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]

    freq = Counter()
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes

>>>>>>> Stashed changes
    for line in raw.splitlines():
        m = LINE_RX.match(line)
        if not m:
            continue
        norm = bytes_to_latin1_text(m.group(3)).strip()
        if not norm or is_already_italian(norm):
            continue
        freq[norm] += 1

    with WORK_CSV.open("w", encoding="latin1", errors="replace", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["Frequenza", "Originale_EN", "Traduzione_IT"])
        for norm_text, count in freq.most_common():
            writer.writerow([count, norm_text, ""])

<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    print(f"File sorgente letto: {input_csv}")
    print(f"OK -> Creato {WORK_CSV}")
=======
    print(f"Cartella di lavoro: {BASE_DIR}")
    print(f"OK -> Creato {WORK_CSV.name} (3 colonne: Frequenza, Originale_EN, Traduzione_IT)")
>>>>>>> Stashed changes
    print(f"Stringhe uniche estratte: {len(freq)} (coprono {sum(freq.values())} righe nel CSV originale).")

def cmd_applica(input_csv: Path):
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
    print(f"Cartella di lavoro: {BASE_DIR}")
    print(f"OK -> Creato {WORK_CSV.name} (3 colonne: Frequenza, Originale_EN, Traduzione_IT)")
    print(f"Stringhe uniche estratte: {len(freq)} (coprono {sum(freq.values())} righe nel CSV originale).")

def cmd_applica():
    if not INPUT_CSV.exists():
        print(f"Errore: file originale non trovato in {INPUT_CSV}")
        sys.exit(1)
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
    if not WORK_CSV.exists():
        print(f"Errore: compila prima {WORK_CSV}")
        sys.exit(1)

    tm = {}
    with WORK_CSV.open("r", encoding="latin1", newline="") as f:
        for row in csv.DictReader(f):
            src = row["Originale_EN"].strip()
            trg = row["Traduzione_IT"].strip()
            if src and trg:
                tm[src] = sanitize_italian(trg)

    raw = input_csv.read_bytes()
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
        orig_text = bytes_to_latin1_text(m.group(3))

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

        final_bytes = text_to_exact_bytes(final_text)
        out_lines.append(b'"' + col_id + b'","' + col_2 + b'","' + final_bytes + b'"')

    with OUTPUT_CSV.open("wb") as f:
        if has_bom:
            f.write(b"\xef\xbb\xbf")
        f.write(b"\n".join(out_lines) + b"\n")

<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    print(f"File sorgente letto: {input_csv}")
    print(f"OK -> Creato {OUTPUT_CSV}")
=======
    print(f"Cartella di lavoro: {BASE_DIR}")
    print(f"OK -> Creato {OUTPUT_CSV.name}")
>>>>>>> Stashed changes
=======
    print(f"Cartella di lavoro: {BASE_DIR}")
    print(f"OK -> Creato {OUTPUT_CSV.name}")
>>>>>>> Stashed changes
=======
    print(f"Cartella di lavoro: {BASE_DIR}")
    print(f"OK -> Creato {OUTPUT_CSV.name}")
>>>>>>> Stashed changes
=======
    print(f"Cartella di lavoro: {BASE_DIR}")
    print(f"OK -> Creato {OUTPUT_CSV.name}")
>>>>>>> Stashed changes
    print(f"Righe aggiornate dal dizionario: {replaced}")
    print(f"Righe con accenti vietati residui: {forbidden_left}")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("estrai", "applica"):
        print("Uso: python3 shenmue_tool.py [estrai|applica] [percorso_file_inglese.csv]")
        sys.exit(1)

    arg_file = sys.argv[2] if len(sys.argv) > 2 else None
    source_csv = resolve_input_csv(arg_file)
    cmd_estrai(source_csv) if sys.argv[1] == "estrai" else cmd_applica(source_csv)
