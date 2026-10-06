import streamlit as st
from pathlib import Path
from datetime import datetime

def ulozit_sheets(radek: list, worksheet: str) -> bool:
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]), scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open("Black Man Group AI Leady")
        sh.worksheet(worksheet).append_row(radek)
        return True
    except Exception:
        return False

st.set_page_config(
    page_title="Audit AI — Black Man Group",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;color:#1e293b!important}
.stApp{background:#f8fafc}
.block-container{padding-left:1rem!important;padding-right:1rem!important;max-width:720px!important;padding-top:1.5rem!important}

.hero{background:linear-gradient(135deg,#0f172a 0%,#1a1a2e 60%,#16213e 100%);border-radius:16px;padding:28px 20px;text-align:center;margin-bottom:22px}
.hero-badge{display:inline-block;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);border-radius:99px;padding:4px 14px;font-size:.75rem;font-weight:600;color:white!important;margin-bottom:12px;letter-spacing:.5px;text-transform:uppercase}
.hero h1{font-size:1.5rem;font-weight:800;margin:0 0 8px;color:white!important;line-height:1.3}
.hero p{font-size:.85rem;opacity:.8;margin:0;color:white!important}

.prog-wrap{background:#e2e8f0;border-radius:99px;height:4px;margin-bottom:20px;overflow:hidden}
.prog-fill{height:100%;background:linear-gradient(90deg,#7c3aed,#a855f7);border-radius:99px;transition:width .4s}

.q-step{font-size:.7rem;font-weight:700;color:#7c3aed!important;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:5px}
.q-title{font-size:1.15rem;font-weight:800;color:#0f172a!important;line-height:1.35;margin-bottom:3px}
.q-sub{font-size:.83rem;color:#64748b!important;margin-bottom:14px}

div[data-testid="stButton"]>button[kind="secondary"]{
    background:white!important;color:#0f172a!important;
    border:2px solid #e2e8f0!important;border-radius:14px!important;
    font-size:.92rem!important;padding:12px 15px!important;
    width:100%!important;text-align:left!important;
    height:auto!important;min-height:52px!important;line-height:1.45!important;
    justify-content:flex-start!important;margin-bottom:6px!important;font-weight:400!important
}
div[data-testid="stButton"]>button[kind="secondary"]:hover{border-color:#7c3aed!important;background:#faf5ff!important}
div[data-testid="stButton"]>button[kind="primary"]{
    background:linear-gradient(135deg,#7c3aed,#a855f7)!important;
    color:white!important;border:none!important;border-radius:12px!important;
    font-weight:700!important;font-size:1rem!important;
    padding:14px 28px!important;width:100%!important
}
.stTextInput>div>div>input,.stTextArea textarea{border:2px solid #e2e8f0!important;border-radius:11px!important;font-size:.96rem!important;padding:11px 14px!important;color:#1e293b!important;background:white!important}
.stTextInput>div>div>input:focus,.stTextArea textarea:focus{border-color:#7c3aed!important;box-shadow:none!important}

.saving-card{background:white;border-left:4px solid #7c3aed;border-radius:0 14px 14px 0;padding:16px 18px;margin-bottom:12px;box-shadow:0 1px 4px rgba(0,0,0,.06)}
.saving-title{font-size:.95rem;font-weight:700;color:#0f172a;margin-bottom:4px}
.saving-hours{font-size:1.3rem;font-weight:800;color:#7c3aed}
.saving-desc{font-size:.83rem;color:#6b7280;margin-top:3px;line-height:1.5}

.total-box{background:linear-gradient(135deg,#1e1b4b,#312e81);border-radius:16px;padding:22px 20px;text-align:center;margin:18px 0;border:2px solid #6366f1}
.total-label{font-size:.72rem;font-weight:700;color:rgba(255,255,255,.6);text-transform:uppercase;letter-spacing:1px}
.total-num{font-size:2rem;font-weight:800;color:white;margin:6px 0}
.total-sub{font-size:.85rem;color:rgba(255,255,255,.75)}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
defaults = {
    "krok": 0,
    "akce_mesic": "",
    "akce_typy": "",
    "booking_jak": "",
    "booking_cas": "",
    "marketing_jak": "",
    "marketing_cas": "",
    "pronajem": "",
    "pronajem_cas": "",
    "smlouvy": "",
    "smlouvy_cas": "",
    "komunikace_kanal": "",
    "komunikace_cas": "",
    "nastroje": "",
    "nejvetsi_bolest": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

KROKY_CELKEM = 8

def progress(k):
    return f'<div class="prog-wrap"><div class="prog-fill" style="width:{int(k/KROKY_CELKEM*100)}%"></div></div>'

CAS_MOZNOSTI = [
    "⏱️  Méně než 2 hodiny týdně",
    "⏱️  2–5 hodin týdně",
    "⏱️  5–10 hodin týdně",
    "⏱️  10–20 hodin týdně",
    "⏱️  20+ hodin týdně",
]
CAS_HODNOTY = {
    "⏱️  Méně než 2 hodiny týdně": 1,
    "⏱️  2–5 hodin týdně":         3,
    "⏱️  5–10 hodin týdně":        7,
    "⏱️  10–20 hodin týdně":       15,
    "⏱️  20+ hodin týdně":         25,
}

# ── KROK 0 — Úvod ─────────────────────────────────────────────────────────────
if st.session_state.krok == 0:
    st.markdown("""
    <div class="hero">
        <div class="hero-badge">🔍 Detailní audit · 5 minut</div>
        <h1>Filippe, pojďme projít Black Man Group do hloubky</h1>
        <p>8 otázek o tom jak firma teď funguje. Na konci dostaneš přehled kde a kolik hodin AI ušetří — konkrétně pro vás.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="q-step">Otázka 1 / 8</p><p class="q-title">Kolik akcí Black Man Group pořádá za měsíc?</p><p class="q-sub">Počítejte eventy, pronájmy i spolupráce.</p>', unsafe_allow_html=True)

    for moznost in ["📅  1–3 akce", "📅  4–8 akcí", "📅  9–15 akcí", "📅  16–25 akcí", "📅  25+ akcí"]:
        if st.button(moznost, key=f"akce_{moznost}", use_container_width=True):
            st.session_state.akce_mesic = moznost
            st.session_state.krok = 1
            st.rerun()

# ── KROK 1 — Typy akcí ────────────────────────────────────────────────────────
elif st.session_state.krok == 1:
    st.markdown(progress(1), unsafe_allow_html=True)
    st.markdown('<p class="q-step">Otázka 2 / 8</p><p class="q-title">Jaké typy akcí nejčastěji organizujete?</p><p class="q-sub">Vyberte co nejlépe popisuje vaše hlavní zaměření.</p>', unsafe_allow_html=True)

    for moznost in [
        "🎉  Soukromé párty a narozeniny",
        "🎪  Firemní eventy a teambuildingy",
        "🎵  Hudební akce a koncerty",
        "🏢  Pronájem prostor / vybavení",
        "🌍  Kulturní akce a festivaly",
        "🍾  VIP a luxusní eventy",
    ]:
        if st.button(moznost, key=f"typ_{moznost}", use_container_width=True):
            st.session_state.akce_typy = moznost
            st.session_state.krok = 2
            st.rerun()

# ── KROK 2 — Booking ──────────────────────────────────────────────────────────
elif st.session_state.krok == 2:
    st.markdown(progress(2), unsafe_allow_html=True)
    st.markdown('<p class="q-step">Otázka 3 / 8</p><p class="q-title">Jak teď přijímáte a potvrzujete nové poptávky?</p><p class="q-sub">Jak klient domluví akci s vámi?</p>', unsafe_allow_html=True)

    for moznost in [
        "📱  Hlavně přes WhatsApp nebo Instagram DM",
        "📧  E-mailem nebo přes formulář na webu",
        "📞  Telefonicky, pak e-mail pro shrnutí",
        "🤝  Osobní schůzka, pak papírová smlouva",
    ]:
        if st.button(moznost, key=f"book_{moznost}", use_container_width=True):
            st.session_state.booking_jak = moznost
            st.session_state.krok = 3
            st.rerun()

# ── KROK 3 — Čas na booking ───────────────────────────────────────────────────
elif st.session_state.krok == 3:
    st.markdown(progress(3), unsafe_allow_html=True)
    st.markdown('<p class="q-step">Otázka 4 / 8</p><p class="q-title">Kolik času týdně zabere komunikace s klienty a domlouvání akcí?</p><p class="q-sub">Zprávy, e-maily, potvrzení, smlouvy.</p>', unsafe_allow_html=True)

    for c in CAS_MOZNOSTI:
        if st.button(c, key=f"booktime_{c}", use_container_width=True):
            st.session_state.booking_cas = c
            st.session_state.krok = 4
            st.rerun()

# ── KROK 4 — Marketing ────────────────────────────────────────────────────────
elif st.session_state.krok == 4:
    st.markdown(progress(4), unsafe_allow_html=True)
    st.markdown('<p class="q-step">Otázka 5 / 8</p><p class="q-title">Jak vytváříte obsah a propagujete každou akci?</p><p class="q-sub">Posty, stories, event stránky, letáky.</p>', unsafe_allow_html=True)

    for moznost in [
        "✍️  Ručně píšeme každý post od začátku",
        "📸  Grafik / fotograf — pak my text upravíme",
        "🔄  Šablony — jen měníme datum a detail",
        "📱  Postujeme nepravidelně, jak nás napadne",
    ]:
        if st.button(moznost, key=f"mkt_{moznost}", use_container_width=True):
            st.session_state.marketing_jak = moznost
            st.session_state.krok = 5
            st.rerun()

# ── KROK 5 — Čas na marketing ─────────────────────────────────────────────────
elif st.session_state.krok == 5:
    st.markdown(progress(5), unsafe_allow_html=True)
    st.markdown('<p class="q-step">Otázka 6 / 8</p><p class="q-title">Kolik času týdně věnujete marketingu a obsahu?</p><p class="q-sub">Psaní textů, tvorba grafiky, plánování postů.</p>', unsafe_allow_html=True)

    for c in CAS_MOZNOSTI:
        if st.button(c, key=f"mkttime_{c}", use_container_width=True):
            st.session_state.marketing_cas = c
            st.session_state.krok = 6
            st.rerun()

# ── KROK 6 — Administrativa ───────────────────────────────────────────────────
elif st.session_state.krok == 6:
    st.markdown(progress(6), unsafe_allow_html=True)
    st.markdown('<p class="q-step">Otázka 7 / 8</p><p class="q-title">Jak řešíte smlouvy, faktury a výkazy?</p><p class="q-sub">Co děláte ručně a co máte automatizované.</p>', unsafe_allow_html=True)

    for moznost in [
        "📝  Vše ručně — Word / Excel, posíláme e-mailem",
        "🖨️  Šablony — vyplňujeme ručně pro každého klienta",
        "💻  Máme účetní software, ale stále dost manuální práce",
        "✅  Máme to celkem dobře pokryté",
    ]:
        if st.button(moznost, key=f"adm_{moznost}", use_container_width=True):
            st.session_state.smlouvy = moznost
            st.session_state.krok = 7
            st.rerun()

# ── KROK 7 — Čas na administrativu ───────────────────────────────────────────
elif st.session_state.krok == 7:
    st.markdown(progress(7), unsafe_allow_html=True)
    st.markdown('<p class="q-step">Otázka 8 / 8</p><p class="q-title">Kolik času týdně zabere administrativa a papírování?</p><p class="q-sub">Smlouvy, faktury, výkazy, reporting pro partnery.</p>', unsafe_allow_html=True)

    for c in CAS_MOZNOSTI:
        if st.button(c, key=f"admtime_{c}", use_container_width=True):
            st.session_state.smlouvy_cas = c
            st.session_state.krok = 8
            st.rerun()

# ── KROK 8 — Výsledek ─────────────────────────────────────────────────────────
elif st.session_state.krok == 8:

    h_booking = CAS_HODNOTY.get(st.session_state.booking_cas, 5)
    h_marketing = CAS_HODNOTY.get(st.session_state.marketing_cas, 5)
    h_admin = CAS_HODNOTY.get(st.session_state.smlouvy_cas, 3)

    uspora_booking   = round(h_booking * 0.80)
    uspora_marketing = round(h_marketing * 0.65)
    uspora_admin     = round(h_admin * 0.85)
    uspora_celkem    = uspora_booking + uspora_marketing + uspora_admin
    uspora_mesic     = uspora_celkem * 4
    uspora_rok       = uspora_mesic * 12

    cas = datetime.now().strftime("%d.%m.%Y %H:%M")
    radek = [
        cas,
        st.session_state.akce_mesic,
        st.session_state.akce_typy,
        st.session_state.booking_jak,
        st.session_state.booking_cas,
        st.session_state.marketing_jak,
        st.session_state.marketing_cas,
        st.session_state.smlouvy,
        st.session_state.smlouvy_cas,
        str(uspora_celkem),
    ]
    ulozit_sheets(radek, "Audit")

    st.markdown(f"""
    <div class="total-box">
        <div class="total-label">Celková odhadovaná úspora týdně</div>
        <div class="total-num">~{uspora_celkem} hodin</div>
        <div class="total-sub">~{uspora_mesic} hodin měsíčně · ~{uspora_rok} hodin ročně</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Kde konkrétně:**")

    BOOKING_POPIS = {
        "📱  Hlavně přes WhatsApp nebo Instagram DM": "automatické odpovědi na DM, booking bot, potvrzení bez kliknutí",
        "📧  E-mailem nebo přes formulář na webu": "AI zpracuje poptávku, pošle nabídku a smlouvu automaticky",
        "📞  Telefonicky, pak e-mail pro shrnutí": "automatický e-mail s přepisem po každém hovoru",
        "🤝  Osobní schůzka, pak papírová smlouva": "digitální smlouva připravená z formuláře za 30 sekund",
    }
    booking_detail = BOOKING_POPIS.get(st.session_state.booking_jak, "automatizace komunikace s klienty")

    st.markdown(f"""
    <div class="saving-card">
        <div class="saving-title">📱 Komunikace a booking</div>
        <div class="saving-hours">~{uspora_booking}h / týden</div>
        <div class="saving-desc">Z {h_booking}h týdně na komunikaci ušetříte ~{uspora_booking}h — {booking_detail}.</div>
    </div>
    """, unsafe_allow_html=True)

    MARKETING_POPIS = {
        "✍️  Ručně píšeme každý post od začátku": "AI napíše post, popisek i hashtahy na základě názvu akce — za 60 sekund",
        "📸  Grafik / fotograf — pak my text upravíme": "AI připraví textový brief pro grafika i finální popisky najednou",
        "🔄  Šablony — jen měníme datum a detail": "plně automatické generování obsahu ze šablony bez manuálního zásahu",
        "📱  Postujeme nepravidelně, jak nás napadne": "AI připraví contenový plán a drafty dopředu na celý měsíc",
    }
    marketing_detail = MARKETING_POPIS.get(st.session_state.marketing_jak, "AI generuje obsah pro každou akci automaticky")

    st.markdown(f"""
    <div class="saving-card">
        <div class="saving-title">📣 Marketing a obsah</div>
        <div class="saving-hours">~{uspora_marketing}h / týden</div>
        <div class="saving-desc">Z {h_marketing}h týdně na obsah ušetříte ~{uspora_marketing}h — {marketing_detail}.</div>
    </div>
    """, unsafe_allow_html=True)

    ADMIN_POPIS = {
        "📝  Vše ručně — Word / Excel, posíláme e-mailem": "smlouva a faktura vygenerovaná automaticky z jednoho formuláře",
        "🖨️  Šablony — vyplňujeme ručně pro každého klienta": "AI vyplní šablonu z dat klienta — žádné ruční kopírování",
        "💻  Máme účetní software, ale stále dost manuální práce": "propojení systémů — data tečou automaticky bez ručního zadávání",
        "✅  Máme to celkem dobře pokryté": "reporting pro 3 partnery automaticky každý týden",
    }
    admin_detail = ADMIN_POPIS.get(st.session_state.smlouvy, "automatizace papírování a reportingu")

    st.markdown(f"""
    <div class="saving-card">
        <div class="saving-title">📋 Administrativa a smlouvy</div>
        <div class="saving-hours">~{uspora_admin}h / týden</div>
        <div class="saving-desc">Z {h_admin}h týdně na admin ušetříte ~{uspora_admin}h — {admin_detail}.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;font-size:.76rem;color:#94a3b8">Black Man Group s.r.o. · AI Automatizace · Detailní audit</p>', unsafe_allow_html=True)

    if st.button("🔄 Začít znovu", use_container_width=True):
        for k in defaults:
            st.session_state[k] = defaults[k]
        st.rerun()
