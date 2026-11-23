import sys
import re
import csv
from pathlib import Path
from collections import Counter

# Cartella in cui si trova questo script (qui verranno creati da_tradurre.csv e italian_final.csv)
BASE_DIR = Path(__file__).resolve().parent
WORK_CSV = BASE_DIR / "da_tradurre.csv"
OUTPUT_CSV = BASE_DIR / "italian_final.csv"

LINE_RX = re.compile(rb'^"([^"]*)","([^"]*)","(.*)"\s*$')

# Byte reali 0xA1 0xF5 ('¡õ' in Latin-1)
RAW_SEP_BYTES = b"\xa1\xf5"
RAW_SEP_STR = RAW_SEP_BYTES.decode("latin1")

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

def resolve_input_csv(arg_path: str | None) -> Path:
    if arg_path:
        p = Path(arg_path).expanduser().resolve()
        if p.exists():
            return p
        print(f"Errore: il file specificato non esiste -> {p}")
        sys.exit(1)

    local_default = BASE_DIR / "english.0db084a7.csv"
    if local_default.exists():
        return local_default

    cwd_default = Path.cwd() / "english.0db084a7.csv"
    if cwd_default.exists():
        return cwd_default

    print("Errore: specifica il percorso del file CSV sorgente.")
    print("Esempio: python3 shenmue_tool.py estrai /percorso/qualsiasi/english.0db084a7.csv")
    sys.exit(1)

def bytes_to_work_str(b: bytes) -> str:
    # Separa PRIMA sui byte 0xA1 0xF5 così ogni segmento viene decodificato in UTF-8 pulito senza doppie codifiche
    b_norm = b.replace(b"\\xA1\\xF5", RAW_SEP_BYTES).replace(b"\\xa1\\xf5", RAW_SEP_BYTES)
    parts = b_norm.split(RAW_SEP_BYTES)
    decoded = []
    for p in parts:
        try:
            decoded.append(p.decode("utf-8"))
        except UnicodeDecodeError:
            decoded.append(p.decode("latin1"))
    return RAW_SEP_STR.join(decoded)

def sanitize_italian(text: str) -> str:
    text = text.translate(ACCENT_MAP)
    text = (text.replace("\ufffd", RAW_SEP_STR)
                .replace("\\xA1\\xF5", RAW_SEP_STR)
                .replace("\\xa1\\xf5", RAW_SEP_STR))

    # Rimuove spazi superflui attorno a 0xA1 0xF5 ('¡õ')
    text = re.sub(r"\s*" + re.escape(RAW_SEP_STR) + r"\s*", RAW_SEP_STR, text)

    # Simbolo $ sempre dopo il numero (es. $50 -> 50$)
    text = re.sub(r"\$\s*(\d+(?:[.,]\d+)?)", r"\1$", text)

    # Sostituisce 'banco'/'banchi' con 'bancarella'/'bancarelle' SENZA toccare 'banco dei pegni'
    text = re.sub(r"\bbanco\b(?!\s+dei\s+pegni)", "bancarella", text)
    text = re.sub(r"\bBanco\b(?!\s+dei\s+pegni)", "Bancarella", text)
    text = re.sub(r"\bbanchi\b(?!\s+dei\s+pegni)", "bancarelle", text)
    text = re.sub(r"\bBanchi\b(?!\s+dei\s+pegni)", "Bancarelle", text)

    # Evita virgolette doppie interne che romperebbero il CSV
    text = text.replace('"', "'")
    return text

def work_str_to_exact_bytes(text: str) -> bytes:
    parts = text.split(RAW_SEP_STR)
    return RAW_SEP_BYTES.join(p.encode("utf-8") for p in parts)

def is_already_italian(text: str) -> bool:
    clean = text.replace(RAW_SEP_STR, " ").replace("=@", "").strip()
    if not clean:
        return True
    return bool(IT_RX.search(clean))

def cmd_estrai(input_csv: Path):
    raw = input_csv.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]

    freq = Counter()
    for line in raw.splitlines():
        m = LINE_RX.match(line)
        if not m:
            continue
        norm = bytes_to_work_str(m.group(3)).strip()
        if not norm or is_already_italian(norm):
            continue
        freq[norm] += 1

    # Scrive in latin1 così i byte 0xA1 0xF5 ('¡õ') restano esatti a livello binario
    with WORK_CSV.open("w", encoding="latin1", errors="replace", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["Frequenza", "Originale_EN", "Traduzione_IT"])
        for norm_text, count in freq.most_common():
            writer.writerow([count, norm_text, ""])

    print(f"File sorgente letto: {input_csv}")
    print(f"OK -> Creato {WORK_CSV}")
    print(f"Stringhe uniche estratte: {len(freq)} (coprono {sum(freq.values())} righe nel CSV originale).")

def cmd_applica(input_csv: Path):
    if not WORK_CSV.exists():
        print(f"Errore: compila prima {WORK_CSV}")
        sys.exit(1)

    # Legge da_tradurre.csv a livello binario per gestire in sicurezza sia byte 0xA1 0xF5 sia accenti UTF-8/Latin-1
    raw_work = WORK_CSV.read_bytes()
    if raw_work.startswith(b"\xef\xbb\xbf"):
        raw_work = raw_work[3:]

    tm = {}
    for line in raw_work.splitlines()[1:]:
        m = LINE_RX.match(line)
        if not m:
            continue
        src = bytes_to_work_str(m.group(2)).strip()
        trg = bytes_to_work_str(m.group(3)).strip()
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
        orig_text = bytes_to_work_str(m.group(3))

        lead_ws = orig_text[:len(orig_text) - len(orig_text.lstrip(" "))]
        trail_ws = orig_text[len(orig_text.rstrip(" ")):]
        core = orig_text.strip()

        if core in tm:
            final_text = f"{lead_ws}{tm[core]}{trail_ws}"
            if re.search(r"[ìòóÈÒÌ]", final_text):
                forbidden_left += 1
            final_bytes = work_str_to_exact_bytes(final_text)
            out_lines.append(b'"' + col_id + b'","' + col_2 + b'","' + final_bytes + b'"')
            replaced += 1
        else:
            # Lascia la riga originale intatta al 100% byte per byte finché non viene tradotta
            out_lines.append(b'"' + col_id + b'","' + col_2 + b'","' + m.group(3) + b'"')

    with OUTPUT_CSV.open("wb") as f:
        if has_bom:
            f.write(b"\xef\xbb\xbf")
        f.write(b"\n".join(out_lines) + b"\n")

    print(f"File sorgente letto: {input_csv}")
    print(f"OK -> Creato {OUTPUT_CSV}")
    print(f"Righe aggiornate dal dizionario: {replaced}")
    print(f"Righe con accenti vietati residui: {forbidden_left}")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("estrai", "applica"):
        print("Uso: python3 shenmue_tool.py [estrai|applica] [percorso_file_inglese.csv]")
        sys.exit(1)

    arg_file = sys.argv[2] if len(sys.argv) > 2 else None
    source_csv = resolve_input_csv(arg_file)
    cmd_estrai(source_csv) if sys.argv[1] == "estrai" else cmd_applica(source_csv)
