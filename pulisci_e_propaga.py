import re
import csv
import shutil
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
WORK_CSV = BASE_DIR / "da_tradurre.csv"

IT_STRONG = re.compile(
    r"\b(grazie|capisco|dove|posso|trovare|scusa|scusi|bene|cosa|perché|perche'|pero'|cosi'|qui|vicino|"
    r"questo|questa|questi|queste|sono|siamo|siete|hai|abbiamo|avete|hanno|fare|dire|andare|vedere|"
    r"sapere|volere|potere|dovere|molto|poco|troppo|tutto|tutti|tutte|niente|nulla|sempre|mai|ora|adesso|"
    r"dopo|prima|poi|allora|quindi|però|perciò|anche|solo|proprio|davvero|forse|certo|sicuro|"
    r"dispiace|favore|prego|buongiorno|buonasera|arrivederci|ciao|ehi|senti|guarda|aspetta|fermo|"
    r"sinistra|destra|dritto|avanti|indietro|sopra|sotto|dentro|fuori|strada|via|piazza|quartiere|"
    r"negozio|tempio|albergo|pensione|ristorante|bar|porto|molo|parco|palazzo|edificio|stanza|porta|"
    r"soldi|denaro|dollari|lavoro|aiuto|aiutare|cercando|cerco|sai|sa|conosci|conosce|visto|vista|"
    r"cui|quale|quali|quanto|quanta|quanti|quante|quando|mentre|oppure|ed|"
    r"del|della|dello|dei|degli|delle|alla|allo|ai|agli|alle|dal|dalla|dallo|dai|dagli|dalle|"
    r"nel|nella|nello|nei|negli|nelle|sul|sulla|sullo|sui|sugli|sulle|col|coi|tra|fra|"
    r"gioco|scommessa|puntata|vinto|perso|allenamento|tecnica|tecniche|mossa|mosse|"
    r"conferma|annulla|seleziona|esci|salva|carica|opzioni|partita|livello|benvenuto|d'accordo|voglio|già|gi)\b",
    re.I
)

EN_STOP = re.compile(
    r"\b(the|you|is|are|was|were|what|where|how|when|why|who|which|can|could|would|should|"
    r"do|does|did|have|has|had|looking|for|way|get|to|from|with|about|into|through|during|"
    r"before|after|above|below|between|out|off|over|under|again|further|then|once|here|there|"
    r"all|any|both|each|few|more|most|other|some|such|no|nor|not|only|own|same|so|than|too|"
    r"very|just|don't|now|i'm|you're|he's|she's|it's|we're|they're|i've|you've|i'd|i'll|"
    r"my|your|his|her|its|our|their|this|that|these|those|am|be|been|being|will|shall|may|"
    r"yes|yeah|okay|ok|excuse|thank|thanks|sorry|please|hello|hey|well|oh|ah|um|uh|huh|"
    r"right|sure|maybe|really|actually|anyway|straight|left|turn|go|walk|take|look|see|"
    r"know|think|want|need|tell|ask|find|come|back|later|man|woman|guy|person|people|place)\b",
    re.I
)

Q_ONLY_RX = re.compile(r"^[\?\.\s\\xA1F5\xa1\xf5]+$")

def read_csv_auto(path: Path):
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
        enc = "utf-8"
    except UnicodeDecodeError:
        text = raw.decode("latin1")
        enc = "latin1"
    rows = list(csv.DictReader(text.splitlines()))
    return rows, enc

def is_it_strict(text: str) -> bool:
    clean = text.replace("\\xA1\\xF5", " ").replace("\xa1\xf5", " ").replace("=@", "").strip()
    if not clean:
        return False
    en_c = len(EN_STOP.findall(clean))
    it_c = len(IT_STRONG.findall(clean)) + len(re.findall(r"[àèéìòù]", clean))
    return it_c > 0 and it_c >= en_c

def strip_ateq(s: str):
    lead = s.startswith("=@")
    trail = s.endswith("=@")
    core = s
    if lead:
        core = core[2:].lstrip()
    if trail:
        core = core[:-2].rstrip()
    return core, lead, trail

def reattach_ateq(trg: str, lead: bool, trail: bool) -> str:
    t = trg.strip()
    if lead and not t.startswith("=@"):
        t = "=@" + t
    if trail and not t.endswith("=@"):
        t = t + "=@"
    return t

def main():
    if not WORK_CSV.exists():
        print(f"Errore: {WORK_CSV} non trovato.")
        return

    # 1. Backup automatico con timestamp
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BASE_DIR / f"da_tradurre_backup_{ts}.csv"
    shutil.copy2(WORK_CSV, backup_path)
    print(f"Backup creato: {backup_path.name}")

    rows, enc = read_csv_auto(WORK_CSV)
    if not rows:
        print("File vuoto.")
        return

    # Rileva formato separatore usato nel file (\xA1\xF5 testuale oppure byte grezzo \xa1\xf5)
    lit_count = sum(1 for r in rows if "\\xA1\\xF5" in r["Originale_EN"])
    raw_count = sum(1 for r in rows if "\xa1\xf5" in r["Originale_EN"])
    sep = "\\xA1\\xF5" if lit_count >= raw_count else "\xa1\xf5"

    def norm_sep(s: str) -> str:
        return s.replace("\\xA1\\xF5", sep).replace("\xa1\xf5", sep)

    # 2. Costruisce la Memoria di Traduzione dalle righe gia' compilate
    tm_case = {}
    tm_nobr = {}
    tm_single = {}

    for r in rows:
        trg_raw = r["Traduzione_IT"].strip()
        if not trg_raw:
            continue
        src = norm_sep(r["Originale_EN"].strip())
        trg = norm_sep(trg_raw)
        s_core, _, _ = strip_ateq(src)
        t_core, _, _ = strip_ateq(trg)
        if not s_core or not t_core:
            continue

        k_case = s_core.lower()
        if k_case not in tm_case:
            tm_case[k_case] = t_core

        k_nobr = re.sub(r"\s+", " ", s_core.replace(sep, " ")).strip().lower()
        if k_nobr not in tm_nobr:
            tm_nobr[k_nobr] = t_core

        if sep not in s_core and k_case not in tm_single:
            tm_single[k_case] = t_core

    def propagate(src_raw: str) -> str:
        src = norm_sep(src_raw.strip())
        s_core, s_lead, s_trail = strip_ateq(src)
        if not s_core:
            return ""
        k_case = s_core.lower()

        # A) Stessa identica frase (anche con maiuscole/minuscole diverse o =@)
        if k_case in tm_case:
            return reattach_ateq(tm_case[k_case], s_lead, s_trail)

        # B) Stessa frase con a capo spostato
        k_nobr = re.sub(r"\s+", " ", s_core.replace(sep, " ")).strip().lower()
        if k_nobr in tm_nobr:
            return reattach_ateq(tm_nobr[k_nobr], s_lead, s_trail)

        # C) Frase composta A + sep + B dove entrambi i segmenti sono gia' tradotti singolarmente
        parts = [p.strip() for p in s_core.split(sep) if p.strip()]
        if len(parts) > 1 and all(p.lower() in tm_single for p in parts):
            joined = sep.join(tm_single[p.lower()] for p in parts)
            return reattach_ateq(joined, s_lead, s_trail)

        return ""

    # 3. Filtra righe inutili e auto-propaga sulle righe vuote
    cleaned_rows = []
    removed_q = 0
    removed_it = 0
    auto_filled = 0
    auto_occ = 0

    for r in rows:
        src = r["Originale_EN"]
        trg = r["Traduzione_IT"].strip()
        freq = int(r["Frequenza"]) if r["Frequenza"].isdigit() else 1

        if not trg:
            if Q_ONLY_RX.match(src):
                removed_q += 1
                continue
            if is_it_strict(src):
                removed_it += 1
                continue

            prop = propagate(src)
            if prop:
                r["Traduzione_IT"] = prop
                auto_filled += 1
                auto_occ += freq

        cleaned_rows.append(r)

    # Salva mantenendo la stessa codifica del file (utf-8 o latin1)
    out_enc = "utf-8" if enc == "utf-8" else "latin1"
    with WORK_CSV.open("w", encoding=out_enc, errors="replace", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Frequenza", "Originale_EN", "Traduzione_IT"], quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    already_done = sum(1 for r in cleaned_rows if r["Traduzione_IT"].strip())
    remaining = len(cleaned_rows) - already_done

    print("-" * 55)
    print(f"Righe iniziali:                   {len(rows)}")
    print(f"Rimosse (giapponese/cinese ???):  -{removed_q}")
    print(f"Rimosse (gia' in italiano):       -{removed_it}")
    print(f"Auto-compilate in questa passata: +{auto_filled} righe ({auto_occ} battute nel gioco)")
    print("-" * 55)
    print(f"Totale righe nel nuovo file:      {len(cleaned_rows)}")
    print(f"Gia' tradotte (manuali + auto):   {already_done}")
    print(f"Righe effettive ancora da fare:   {remaining}")

if __name__ == "__main__":
    main()
