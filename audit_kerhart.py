import streamlit as st
import json
import anthropic
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="AI Audit zdarma",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── API klíč — Streamlit Cloud secrets nebo lokální config.json ───────────────
def get_anthropic_key() -> str:
    try:
        return st.secrets.get("anthropic_api_key", "")
    except Exception:
        pass
    try:
        CONFIG_PATH = Path(__file__).parent / "config.json"
        return json.loads(CONFIG_PATH.read_text()).get("anthropic_api_key", "")
    except Exception:
        return ""

# ── Google Sheets helper ───────────────────────────────────────────────────────
def ulozit_do_sheets(radek: list) -> bool:
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds_info = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
        gc = gspread.authorize(creds)
        sheet = gc.open(st.secrets.get("sheet_name", "Kerhart AI Leady")).worksheet("Full Audit")
        sheet.append_row(radek)
        return True
    except Exception:
        return False

def ulozit_lokalne_csv(radek: list):
    """Záloha do CSV pokud Sheets nefunguje (lokální vývoj nebo výpadek)."""
    p = Path(__file__).parent / "audit_leads.csv"
    hlavicka = not p.exists()
    with p.open("a", encoding="utf-8") as f:
        if hlavicka:
            f.write("Čas,Jméno,Email,Firma,Obor,Velikost,Bolest,Čas/týden,Nástroje,Report\n")
        f.write(",".join(f'"{str(x).replace(chr(34), chr(39))}"' for x in radek) + "\n")

# Obsidian záloha jen při lokálním spuštění
OBSIDIAN_PATH = Path("/Users/majkl/Library/Mobile Documents/iCloud~md~obsidian/Documents/Trading")
LEADS_FILE = OBSIDIAN_PATH / "AUTOMATIZACE-LEADS.md"

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;color:#1e293b!important}
.stApp{background:#f8fafc}
.block-container{padding-left:1rem!important;padding-right:1rem!important;max-width:720px!important}

.hero{background:linear-gradient(135deg,#0f172a 0%,#1a2e4a 55%,#1d4ed8 100%);color:white!important;border-radius:16px;padding:32px 20px;text-align:center;margin-bottom:24px}
.hero h1{font-size:1.6rem;font-weight:800;margin:0 0 8px;color:white!important}
.hero p{font-size:.88rem;opacity:.82;margin:0;color:white!important}
.hero-badge{display:inline-block;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.25);border-radius:99px;padding:4px 14px;font-size:.75rem;font-weight:600;color:white!important;margin-bottom:14px;letter-spacing:.5px}

.prog-wrap{background:#e2e8f0;border-radius:99px;height:5px;margin-bottom:20px;overflow:hidden}
.prog-fill{height:100%;background:linear-gradient(90deg,#1d4ed8,#60a5fa);border-radius:99px;transition:width .4s}

.q-label{font-size:.72rem;font-weight:700;color:#1d4ed8!important;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:6px}
.q-title{font-size:1.2rem;font-weight:800;color:#0f172a!important;line-height:1.35;margin-bottom:4px}
.q-sub{font-size:.85rem;color:#64748b!important;margin-bottom:16px}

div[data-testid="stButton"]>button[kind="secondary"]{
    background:white!important;color:#0f172a!important;
    border:2px solid #e2e8f0!important;border-radius:14px!important;
    font-weight:400!important;font-size:.95rem!important;
    padding:14px 16px!important;width:100%!important;
    text-align:left!important;white-space:pre-wrap!important;
    height:auto!important;min-height:60px!important;line-height:1.5!important;
    justify-content:flex-start!important;margin-bottom:6px!important
}
div[data-testid="stButton"]>button[kind="secondary"]:hover{border-color:#1d4ed8!important;background:#eff6ff!important}
div[data-testid="stButton"]>button[kind="primary"]{
    background:linear-gradient(135deg,#1d4ed8,#3b82f6)!important;
    color:white!important;border:none!important;border-radius:12px!important;
    font-weight:700!important;font-size:1rem!important;
    padding:15px 28px!important;width:100%!important
}
div[data-testid="stButton"]>button[kind="primary"]:hover{opacity:.88!important}

.stTextInput>div>div>input{border:2px solid #e2e8f0!important;border-radius:12px!important;font-size:1rem!important;padding:13px 16px!important;color:#1e293b!important;background:white!important}
.stTextInput>div>div>input:focus{border-color:#1d4ed8!important;outline:none!important}

.result-hero{background:linear-gradient(135deg,#0f172a,#1a2e4a);border-radius:16px;padding:28px 20px;text-align:center;margin-bottom:20px}
.result-emoji{font-size:2.5rem;margin-bottom:8px}
.result-label{font-size:.72rem;font-weight:700;opacity:.6;text-transform:uppercase;letter-spacing:1px;color:white!important}
.result-title{font-size:1.5rem;font-weight:800;color:white!important;margin:6px 0 4px}
.result-sub{font-size:.9rem;opacity:.8;color:white!important}

.saving-card{background:white;border:2px solid #dbeafe;border-radius:14px;padding:18px 20px;margin-bottom:12px}
.saving-header{display:flex;align-items:center;gap:10px;margin-bottom:8px}
.saving-icon{font-size:1.4rem}
.saving-title{font-size:1rem;font-weight:700;color:#0f172a!important}
.saving-hours{font-size:1.4rem;font-weight:800;color:#1d4ed8!important}
.saving-desc{font-size:.85rem;color:#475569!important;line-height:1.6}
.saving-tag{display:inline-block;background:#dbeafe;color:#1d4ed8!important;border-radius:99px;padding:3px 10px;font-size:.72rem;font-weight:700;margin-top:8px}

.roi-box{background:linear-gradient(135deg,#f0fdf4,#dcfce7);border:2px solid #86efac;border-radius:14px;padding:16px 20px;margin:16px 0;text-align:center}
.roi-label{font-size:.75rem;font-weight:700;color:#15803d!important;text-transform:uppercase;letter-spacing:.8px}
.roi-number{font-size:2rem;font-weight:800;color:#15803d!important;margin:4px 0}
.roi-sub{font-size:.82rem;color:#166534!important}

.ai-box{background:white;border-radius:14px;padding:18px;box-shadow:0 2px 12px rgba(0,0,0,.06);margin-bottom:14px;line-height:1.75;font-size:.93rem;color:#1e293b!important}
.ai-label{font-size:.72rem;font-weight:700;color:#1d4ed8!important;text-transform:uppercase;letter-spacing:.8px;margin-bottom:10px}

.cta-box{background:linear-gradient(135deg,#1d4ed8,#3b82f6);border-radius:16px;padding:24px 20px;text-align:center;margin-top:20px}
.cta-title{font-size:1.2rem;font-weight:800;color:white!important;margin-bottom:8px}
.cta-sub{font-size:.88rem;color:rgba(255,255,255,.85)!important;margin-bottom:16px}
.cta-email{font-size:.85rem;color:rgba(255,255,255,.6)!important;margin-top:10px}
</style>
""", unsafe_allow_html=True)

# ── Otázky ────────────────────────────────────────────────────────────────────
QUESTIONS = [
    {
        "id": "obor",
        "label": "Krok 1 / 5 — Váš byznys",
        "title": "V jakém oboru podnikáte?",
        "sub": "Vybereme řešení přímo pro váš typ firmy.",
        "options": [
            "🛒  E-shop / online obchod",
            "🍕  Restaurace / kavárna / bar",
            "💇  Salon / barbershop / wellness",
            "🏠  Reality / nemovitosti",
            "📊  Účetnictví / daně / právo / poradenství",
            "🏭  Výroba / logistika / doprava",
            "💻  IT / software / marketing / agentura",
            "🎪  Eventy / pronájmy / zážitky",
            "🏥  Zdravotnictví / klinika / ordinace",
            "🔧  Řemeslo / služby / opravna",
        ],
    },
    {
        "id": "velikost",
        "label": "Krok 2 / 5 — Váš tým",
        "title": "Kolik lidí ve firmě pracuje?",
        "sub": "Určuje jak velkou automatizaci má smysl řešit.",
        "options": [
            "👤  Jen já — solo podnikatel",
            "👥  2–5 lidí",
            "🏢  6–15 lidí",
            "🏗️  16–50 lidí",
            "🏙️  50+ lidí",
        ],
    },
    {
        "id": "problem",
        "label": "Krok 3 / 5 — Největší bolest",
        "title": "Co vám každý týden zabere nejvíc času a nechcete to dělat?",
        "sub": "Vyberte to co vás nejvíc otravuje.",
        "options": [
            "💬  Odpovídání na dotazy zákazníků (email / WhatsApp / telefon)",
            "📋  Ruční zadávání objednávek, faktur nebo dat do systémů",
            "📈  Tvorba reportů, přehledů a tabulek",
            "📅  Plánování, rezervace a koordinace týmu",
            "📣  Sociální sítě, obsah a marketing",
            "🔗  Propojení systémů — data teču ručně mezi appkami",
            "🧾  Administrativa — smlouvy, výkazy, docházka",
            "📞  Nabídky, follow-upy a péče o zákazníky",
        ],
    },
    {
        "id": "cas",
        "label": "Krok 4 / 5 — Objem manuální práce",
        "title": "Kolik hodin týdně strávíte manuální opakující se prací?",
        "sub": "Jen odhadem — klidně zaokrouhlete.",
        "options": [
            "⏱️  1–5 hodin týdně",
            "⏱️  5–15 hodin týdně",
            "⏱️  15–30 hodin týdně",
            "⏱️  30+ hodin týdně",
        ],
    },
    {
        "id": "nastroje",
        "label": "Krok 5 / 5 — Aktuální nástroje",
        "title": "Jaké nástroje aktuálně používáte?",
        "sub": "Pomůže nám navrhnout kompatibilní řešení.",
        "options": [
            "📧  Jen email a Excel / Google Sheets",
            "🧾  Fakturační systém (Pohoda, Fakturoid, Money S3...)",
            "🤝  CRM systém (HubSpot, Raynet, Salesforce...)",
            "🛒  E-shopová platforma (Shopify, WooCommerce, Upgates...)",
            "📱  WhatsApp Business nebo jiný messaging",
            "📦  Skladový nebo ERP systém",
            "🔀  Kombinace více systémů — ale nepropojené",
        ],
    },
]

# ── Pomocné funkce ─────────────────────────────────────────────────────────────
HOURS_MAP = {
    "⏱️  1–5 hodin týdně": 3,
    "⏱️  5–15 hodin týdně": 10,
    "⏱️  15–30 hodin týdně": 22,
    "⏱️  30+ hodin týdně": 35,
}

def odhadnout_usporu(cas_odpoved: str) -> tuple[int, int]:
    tydenni = HOURS_MAP.get(cas_odpoved, 10)
    usporna_pct = 0.6
    tydenni_usp = round(tydenni * usporna_pct)
    mesicni_usp = tydenni_usp * 4
    return tydenni_usp, mesicni_usp

def ulozit_lead(jmeno: str, email: str, firma: str, odpovedi: dict, report: str):
    cas = datetime.now().strftime("%d.%m.%Y %H:%M")
    obor     = odpovedi.get("obor", "").replace("  ", " ")
    velikost = odpovedi.get("velikost", "").replace("  ", " ")
    problem  = odpovedi.get("problem", "").replace("  ", " ")
    hodiny   = odpovedi.get("cas", "").replace("  ", " ")
    nastroje = odpovedi.get("nastroje", "").replace("  ", " ")

    radek = [cas, jmeno, email, firma, obor, velikost, problem, hodiny, nastroje, report]

    # 1) Google Sheets (Streamlit Cloud)
    ok = ulozit_do_sheets(radek)

    # 2) CSV záloha pokud Sheets selže
    if not ok:
        ulozit_lokalne_csv(radek)

    # 3) Obsidian záloha pokud běžíme lokálně
    if LEADS_FILE.parent.exists():
        zaznam = f"\n---\n## {cas} — {jmeno} ({firma})\n\n| | |\n|---|---|\n| **Email** | {email} |\n| **Obor** | {obor} |\n| **Velikost** | {velikost} |\n| **Bolest** | {problem} |\n| **Čas/týden** | {hodiny} |\n| **Nástroje** | {nastroje} |\n\n**AI Report:**\n{report}\n\n"
        if not LEADS_FILE.exists():
            LEADS_FILE.write_text("# AUTOMATIZACE — Leady z dotazníku\n")
        with LEADS_FILE.open("a", encoding="utf-8") as f:
            f.write(zaznam)

def vygenerovat_report(jmeno: str, firma: str, odpovedi: dict) -> str:
    key = get_anthropic_key()
    if not key:
        return "_API klíč není nastaven — report nelze vygenerovat._"

    client = anthropic.Anthropic(api_key=key)
    prompt = f"""Jsi AI automatizační poradce pro malé a střední firmy v ČR. Analyzuj profil firmy a napiš stručný, konkrétní automatizační report.

**Firma:** {firma}
**Kontakt:** {jmeno}
**Obor:** {odpovedi.get('obor', '')}
**Velikost týmu:** {odpovedi.get('velikost', '')}
**Největší bolest:** {odpovedi.get('problem', '')}
**Čas na manuální práci:** {odpovedi.get('cas', '')}
**Aktuální nástroje:** {odpovedi.get('nastroje', '')}

Napiš report ve formátu:

**TOP 3 AI řešení pro {firma}:**

1. [Název řešení] — [1 věta co to dělá] | Úspora: X hodin/týden
2. [Název řešení] — [1 věta co to dělá] | Úspora: X hodin/týden
3. [Název řešení] — [1 věta co to dělá] | Úspora: X hodin/týden

**Doporučený první krok:**
[Konkrétní akce — co udělat jako první, do 2 týdnů]

**Proč právě teď:**
[1–2 věty proč má smysl začít hned]

Piš česky, konkrétně, bez omáčky. Žádné obecné věty. Přizpůsob oboru a velikosti firmy."""

    with client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        return stream.get_final_text()

# ── Session state init ─────────────────────────────────────────────────────────
if "krok" not in st.session_state:
    st.session_state.krok = 0
if "odpovedi" not in st.session_state:
    st.session_state.odpovedi = {}
if "jmeno" not in st.session_state:
    st.session_state.jmeno = ""
if "email" not in st.session_state:
    st.session_state.email = ""
if "firma" not in st.session_state:
    st.session_state.firma = ""
if "report" not in st.session_state:
    st.session_state.report = ""
if "ulozeno" not in st.session_state:
    st.session_state.ulozeno = False

# ── KROK 0 — Uvítání ──────────────────────────────────────────────────────────
if st.session_state.krok == 0:
    st.markdown("""
    <div class="hero">
        <div class="hero-badge">🤖 ZDARMA · 3 minuty · bez závazků</div>
        <h1>Zjistěte, kolik hodin týdně vám AI ušetří</h1>
        <p>Krátký audit odhalí, kde AI automatizace přinese vaší firmě největší úsporu času a peněz.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="q-title">Než začneme — jak vám říkat?</p>', unsafe_allow_html=True)

    jmeno = st.text_input("Vaše jméno", placeholder="Jan Novák", key="input_jmeno", label_visibility="collapsed")
    firma = st.text_input("Název firmy", placeholder="Novák s.r.o.", key="input_firma", label_visibility="collapsed")
    email = st.text_input("Váš email (pošleme report)", placeholder="jan@firma.cz", key="input_email", label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Začít audit →", type="primary"):
        if jmeno.strip() and firma.strip() and email.strip():
            st.session_state.jmeno = jmeno.strip()
            st.session_state.firma = firma.strip()
            st.session_state.email = email.strip()
            st.session_state.krok = 1
            st.rerun()
        else:
            st.warning("Vyplňte prosím jméno, firmu a email.")

    st.markdown('<p style="text-align:center;font-size:.78rem;color:#94a3b8;margin-top:12px">Žádný spam · Výsledky zdarma · Filipkerhart.cz</p>', unsafe_allow_html=True)

# ── KROKY 1–5 — Otázky ───────────────────────────────────────────────────────
elif 1 <= st.session_state.krok <= 5:
    q = QUESTIONS[st.session_state.krok - 1]
    progress = st.session_state.krok / 5 * 100

    st.markdown(f"""
    <div class="prog-wrap"><div class="prog-fill" style="width:{progress}%"></div></div>
    <p class="q-label">{q['label']}</p>
    <p class="q-title">{q['title']}</p>
    <p class="q-sub">{q['sub']}</p>
    """, unsafe_allow_html=True)

    for opt in q["options"]:
        if st.button(opt, key=f"opt_{q['id']}_{opt}", use_container_width=True):
            st.session_state.odpovedi[q["id"]] = opt
            st.session_state.krok += 1
            st.rerun()

# ── KROK 6 — Generování reportu ───────────────────────────────────────────────
elif st.session_state.krok == 6:
    st.markdown("""
    <div class="prog-wrap"><div class="prog-fill" style="width:100%"></div></div>
    <div style="text-align:center;padding:20px 0">
        <div style="font-size:2.5rem;margin-bottom:12px">🤖</div>
        <p style="font-size:1.1rem;font-weight:700;color:#0f172a">Analyzuji vaši firmu...</p>
        <p style="font-size:.88rem;color:#64748b">Připravuji personalizovaný report</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.report:
        with st.spinner(""):
            st.session_state.report = vygenerovat_report(
                st.session_state.jmeno,
                st.session_state.firma,
                st.session_state.odpovedi,
            )

    if not st.session_state.ulozeno:
        ulozit_lead(
            st.session_state.jmeno,
            st.session_state.email,
            st.session_state.firma,
            st.session_state.odpovedi,
            st.session_state.report,
        )
        st.session_state.ulozeno = True

    st.session_state.krok = 7
    st.rerun()

# ── KROK 7 — Výsledky ─────────────────────────────────────────────────────────
elif st.session_state.krok == 7:
    jmeno = st.session_state.jmeno
    firma = st.session_state.firma
    odpovedi = st.session_state.odpovedi

    tydenni, mesicni = odhadnout_usporu(odpovedi.get("cas", ""))

    # Hero
    st.markdown(f"""
    <div class="result-hero">
        <div class="result-emoji">✅</div>
        <div class="result-label">Váš AI audit je hotový</div>
        <div class="result-title">{firma}</div>
        <div class="result-sub">Potenciál pro automatizaci potvrzen</div>
    </div>
    """, unsafe_allow_html=True)

    # ROI kalkulace
    st.markdown(f"""
    <div class="roi-box">
        <div class="roi-label">Odhadovaná úspora</div>
        <div class="roi-number">~{mesicni} hodin / měsíc</div>
        <div class="roi-sub">({tydenni} hodin týdně · 60 % manuální práce automatizovatelné)</div>
    </div>
    """, unsafe_allow_html=True)

    # AI report
    st.markdown('<div class="ai-box"><div class="ai-label">🤖 Váš personalizovaný report</div>', unsafe_allow_html=True)
    st.markdown(st.session_state.report)
    st.markdown('</div>', unsafe_allow_html=True)

    # Shrnutí odpovědí
    with st.expander("📋 Vaše odpovědi"):
        for q in QUESTIONS:
            val = odpovedi.get(q["id"], "—").replace("  ", " ")
            st.markdown(f"**{q['title']}**  \n{val}")

    # CTA
    st.markdown(f"""
    <div class="cta-box">
        <div class="cta-title">Chcete to spustit?</div>
        <div class="cta-sub">Domluví se na bezplatnou 30minutovou konzultaci. Ukážeme přesně co automatizovat jako první.</div>
        <div class="cta-email">📧 filip@filipkerhart.cz · nebo odpovězte na email s reportem</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Spustit znovu", use_container_width=True):
            for key in ["krok", "odpovedi", "jmeno", "email", "firma", "report", "ulozeno"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    with col2:
        st.button("✅ Hotovo", type="primary", use_container_width=True)
