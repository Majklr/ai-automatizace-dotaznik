import streamlit as st
import json
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="AI pro vaši firmu?",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_ebar_state="collapsed"
)

# ── Google Sheets helper ───────────────────────────────────────────────────────
def ulozit_do_sheets(radek: list) -> bool:
    """Uloží řádek do Google Sheets. Vrátí True při úspěchu."""
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
        sheet = gc.open(st.secrets.get("sheet_name", "Kerhart AI Leady")).worksheet("Screening")
        sheet.append_row(radek)
        return True
    except Exception:
        return False

def ulozit_lokalne(radek: list):
    """Záložní uložení do CSV pokud Sheets nefunguje."""
    p = Path(__file__).parent / "screening_leads.csv"
    hlavicka = not p.exists()
    with p.open("a", encoding="utf-8") as f:
        if hlavicka:
            f.write("Čas,Jméno,Firma,Email,Obor,Bolest,Hodiny,Skóre,Verdikt\n")
        f.write(",".join(f'"{x}"' for x in radek) + "\n")

def ulozit_lead(jmeno, firma, email, obor, bolest, hodiny, skore, verdikt):
    cas = datetime.now().strftime("%d.%m.%Y %H:%M")
    radek = [cas, jmeno, firma, email, obor, bolest, hodiny, str(skore), verdikt]
    ok = ulozit_do_sheets(radek)
    if not ok:
        ulozit_lokalne(radek)

# ── Skórovací logika ───────────────────────────────────────────────────────────
HODINY_SKORE = {
    "⏱️  Méně než 3 hodiny týdně": 1,
    "⏱️  3–10 hodin týdně":        2,
    "⏱️  10–20 hodin týdně":       3,
    "⏱️  20+ hodin týdně":         4,
}

BOLEST_SKORE = {
    "💬  Odpovídám na stále stejné dotazy zákazníků":           2,
    "📋  Ručně zadávám data, objednávky nebo faktury":          3,
    "📣  Vytvářím obsah a posty na sítě":                      2,
    "📅  Plánuju schůzky, rezervace nebo koordinuju tým":       2,
    "📈  Dělám reporty a tabulky ručně každý týden":            3,
    "🔗  Kopíruju data mezi systémy které nejsou propojené":    3,
    "🧾  Řeším papírování — smlouvy, výkazy, docházka":        2,
}

def vypocitat_skore(hodiny_odp, bolest_odp):
    return HODINY_SKORE.get(hodiny_odp, 0) + BOLEST_SKORE.get(bolest_odp, 0)

def verdikt(skore):
    if skore <= 2:
        return "low", "Zatím nespěcháme", "🙂"
    elif skore <= 4:
        return "medium", "Potenciál vidíme", "🔥"
    else:
        return "high", "Velký potenciál!", "🚀"

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;color:#1e293b!important}
.stApp{background:#f8fafc}
.block-container{padding-left:1rem!important;padding-right:1rem!important;max-width:680px!important;padding-top:1.5rem!important}

.hero{background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 60%,#0369a1 100%);border-radius:16px;padding:28px 20px;text-align:center;margin-bottom:22px}
.hero-badge{display:inline-block;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.3);border-radius:99px;padding:4px 14px;font-size:.75rem;font-weight:600;color:white!important;margin-bottom:12px;letter-spacing:.5px;text-transform:uppercase}
.hero h1{font-size:1.55rem;font-weight:800;margin:0 0 8px;color:white!important;line-height:1.3}
.hero p{font-size:.86rem;opacity:.8;margin:0;color:white!important}

.prog-wrap{background:#e2e8f0;border-radius:99px;height:4px;margin-bottom:18px;overflow:hidden}
.prog-fill{height:100%;background:linear-gradient(90deg,#0369a1,#38bdf8);border-radius:99px;transition:width .4s}

.q-step{font-size:.7rem;font-weight:700;color:#0369a1!important;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:5px}
.q-title{font-size:1.2rem;font-weight:800;color:#0f172a!important;line-height:1.35;margin-bottom:3px}
.q-sub{font-size:.84rem;color:#64748b!important;margin-bottom:14px}

div[data-testid="stButton"]>button[kind="secondary"]{
    background:white!important;color:#0f172a!important;
    border:2px solid #e2e8f0!important;border-radius:14px!important;
    font-size:.94rem!important;padding:13px 16px!important;
    width:100%!important;text-align:left!important;
    height:auto!important;min-height:54px!important;line-height:1.45!important;
    justify-content:flex-start!important;margin-bottom:6px!important;font-weight:400!important
}
div[data-testid="stButton"]>button[kind="secondary"]:hover{border-color:#0369a1!important;background:#f0f9ff!important}
div[data-testid="stButton"]>button[kind="primary"]{
    background:linear-gradient(135deg,#0369a1,#0ea5e9)!important;
    color:white!important;border:none!important;border-radius:12px!important;
    font-weight:700!important;font-size:1rem!important;
    padding:14px 28px!important;width:100%!important
}
.stTextInput>div>div>input{border:2px solid #e2e8f0!important;border-radius:11px!important;font-size:.97rem!important;padding:12px 15px!important;color:#1e293b!important;background:white!important}
.stTextInput>div>div>input:focus{border-color:#0369a1!important}

/* výsledky */
.res-box{border-radius:16px;padding:24px 20px;text-align:center;margin-bottom:18px}
.res-box.high{background:linear-gradient(135deg,#052e16,#14532d);border:2px solid #22c55e}
.res-box.medium{background:linear-gradient(135deg,#1c1917,#292524);border:2px solid #f59e0b}
.res-box.low{background:linear-gradient(135deg,#0f172a,#1e293b);border:2px solid #475569}
.res-emoji{font-size:2.4rem;margin-bottom:10px}
.res-label{font-size:.7rem;font-weight:700;opacity:.55;text-transform:uppercase;letter-spacing:1px;color:white!important}
.res-title{font-size:1.45rem;font-weight:800;color:white!important;margin:5px 0}
.res-text{font-size:.87rem;opacity:.82;color:white!important;line-height:1.6}

.next-step{background:white;border:2px solid #dbeafe;border-radius:14px;padding:18px 20px;margin-top:14px}
.next-label{font-size:.7rem;font-weight:700;color:#0369a1!important;text-transform:uppercase;letter-spacing:.9px;margin-bottom:6px}
.next-text{font-size:.92rem;color:#0f172a!important;font-weight:500;line-height:1.55}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
defaults = {"krok": 0, "obor": "", "bolest": "", "hodiny": "", "jmeno": "", "firma": "", "email": ""}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── KROK 0 — Kontakt ──────────────────────────────────────────────────────────
if st.session_state.krok == 0:
    st.markdown("""
    <div class="hero">
        <div class="hero-badge">⚡ 2 minuty · zdarma · bez závazků</div>
        <h1>Může AI ušetřit čas vaší firmě?</h1>
        <p>Odpovězte na 3 rychlé otázky a zjistěte, jestli AI automatizace dává smysl právě pro vás.</p>
    </div>
    """, unsafe_allow_html=True)

    jmeno = st.text_input("Vaše jméno", placeholder="Jan Novák", label_visibility="collapsed", key="i_jmeno")
    firma = st.text_input("Název firmy", placeholder="Novák s.r.o.", label_visibility="collapsed", key="i_firma")
    email = st.text_input("Váš email", placeholder="jan@firma.cz", label_visibility="collapsed", key="i_email")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Zjistit výsledek →", type="primary"):
        if jmeno.strip() and firma.strip() and email.strip():
            st.session_state.jmeno = jmeno.strip()
            st.session_state.firma = firma.strip()
            st.session_state.email = email.strip()
            st.session_state.krok = 1
            st.rerun()
        else:
            st.warning("Vyplňte prosím všechna pole.")

    st.markdown('<p style="text-align:center;font-size:.76rem;color:#94a3b8;margin-top:10px">Bez spamu · Výsledek okamžitě</p>', unsafe_allow_html=True)

# ── KROK 1 — Obor ─────────────────────────────────────────────────────────────
elif st.session_state.krok == 1:
    st.markdown('<div class="prog-wrap"><div class="prog-fill" style="width:33%"></div></div>', unsafe_allow_html=True)
    st.markdown("""
    <p class="q-step">Otázka 1 / 3</p>
    <p class="q-title">V jakém oboru podnikáte?</p>
    <p class="q-sub">Přizpůsobíme doporučení vašemu typu firmy.</p>
    """, unsafe_allow_html=True)

    obory = [
        "🛒  E-shop / online obchod",
        "🍕  Restaurace / kavárna / bar",
        "💇  Salon / barbershop / wellness",
        "🏠  Reality / nemovitosti",
        "📊  Účetnictví / poradenství / právo",
        "🏭  Výroba / logistika / doprava",
        "💻  IT / marketing / agentura",
        "🎪  Eventy / pronájmy / zážitky",
        "🔧  Řemeslo / opravna / služby",
        "🏥  Zdravotnictví / klinika",
    ]
    for o in obory:
        if st.button(o, key=f"obor_{o}", use_container_width=True):
            st.session_state.obor = o
            st.session_state.krok = 2
            st.rerun()

# ── KROK 2 — Největší bolest ──────────────────────────────────────────────────
elif st.session_state.krok == 2:
    st.markdown('<div class="prog-wrap"><div class="prog-fill" style="width:66%"></div></div>', unsafe_allow_html=True)
    st.markdown("""
    <p class="q-step">Otázka 2 / 3</p>
    <p class="q-title">Co vás ve firmě nejvíc zdržuje?</p>
    <p class="q-sub">Vyberte jednu věc, která vám bere nejvíc času.</p>
    """, unsafe_allow_html=True)

    bolesti = list(BOLEST_SKORE.keys())
    for b in bolesti:
        if st.button(b, key=f"bolest_{b}", use_container_width=True):
            st.session_state.bolest = b
            st.session_state.krok = 3
            st.rerun()

# ── KROK 3 — Hodiny ──────────────────────────────────────────────────────────
elif st.session_state.krok == 3:
    st.markdown('<div class="prog-wrap"><div class="prog-fill" style="width:99%"></div></div>', unsafe_allow_html=True)
    st.markdown("""
    <p class="q-step">Otázka 3 / 3</p>
    <p class="q-title">Kolik hodin týdně tomu věnujete?</p>
    <p class="q-sub">Jen odhad stačí.</p>
    """, unsafe_allow_html=True)

    for h in HODINY_SKORE.keys():
        if st.button(h, key=f"hod_{h}", use_container_width=True):
            st.session_state.hodiny = h
            st.session_state.krok = 4
            st.rerun()

# ── KROK 4 — Výsledek ────────────────────────────────────────────────────────
elif st.session_state.krok == 4:
    skore = vypocitat_skore(st.session_state.hodiny, st.session_state.bolest)
    uroven, nadpis, emoji = verdikt(skore)

    ulozit_lead(
        st.session_state.jmeno, st.session_state.firma, st.session_state.email,
        st.session_state.obor.replace("  ", " "),
        st.session_state.bolest.replace("  ", " "),
        st.session_state.hodiny.replace("  ", " "),
        skore, nadpis,
    )

    hodiny_txt = st.session_state.hodiny.replace("⏱️  ", "")

    if uroven == "high":
        popis = f"Na základě vašich odpovědí vidíme velký potenciál. {hodiny_txt} manuální práce každý týden = ideální kandidát pro AI automatizaci."
        dalsi = "Doporučujeme hned vyplnit detailní audit — ukáže přesně kde a kolik ušetříte."
        dalsi_akce = "🔍  Vyplnit detailní audit zdarma"
    elif uroven == "medium":
        popis = f"Potenciál tam je. {hodiny_txt} opakující se práce je hranice kde AI začíná dávat smysl."
        dalsi = "Detailní audit odhalí 2–3 konkrétní místa kde AI pomůže nejvíc."
        dalsi_akce = "🔍  Zkusit detailní audit"
    else:
        popis = "Zatím nemáme co výrazně ušetřit. AI automatizace dává největší smysl firmám s více opakující se manuální prací."
        dalsi = "Ozvěte se znovu až bude váš tým větší nebo agendy přibyde — pak to bude mít větší efekt."
        dalsi_akce = None

    st.markdown(f"""
    <div class="res-box {uroven}">
        <div class="res-emoji">{emoji}</div>
        <div class="res-label">Váš výsledek</div>
        <div class="res-title">{nadpis}</div>
        <div class="res-text">{popis}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="next-step">
        <div class="next-label">{'Doporučený další krok' if dalsi_akce else 'Co dál'}</div>
        <div class="next-text">{dalsi}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if dalsi_akce:
        AUDIT_URL = st.secrets.get("audit_url", "http://localhost:8507") if hasattr(st, "secrets") else "http://localhost:8507"
        st.link_button(dalsi_akce, url=AUDIT_URL, use_container_width=True, type="primary")
        st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔄 Začít znovu", use_container_width=True):
        for k in defaults:
            st.session_state[k] = defaults[k]
        st.rerun()

    st.markdown('<p style="text-align:center;font-size:.76rem;color:#94a3b8;margin-top:14px">Filip Kerhart · AI Automatizace pro firmy</p>', unsafe_allow_html=True)
