import streamlit as st
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="AI pro Black Man Group?",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;color:#1e293b!important}
.stApp{background:#f8fafc}
.block-container{padding-left:1rem!important;padding-right:1rem!important;max-width:680px!important;padding-top:1.5rem!important}

.hero{background:linear-gradient(135deg,#0f172a 0%,#1a1a2e 60%,#16213e 100%);border-radius:16px;padding:28px 20px;text-align:center;margin-bottom:22px}
.hero-badge{display:inline-block;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);border-radius:99px;padding:4px 14px;font-size:.75rem;font-weight:600;color:white!important;margin-bottom:12px;letter-spacing:.5px;text-transform:uppercase}
.hero h1{font-size:1.55rem;font-weight:800;margin:0 0 8px;color:white!important;line-height:1.3}
.hero p{font-size:.86rem;opacity:.8;margin:0;color:white!important}

.prog-wrap{background:#e2e8f0;border-radius:99px;height:4px;margin-bottom:18px;overflow:hidden}
.prog-fill{height:100%;background:linear-gradient(90deg,#7c3aed,#a855f7);border-radius:99px;transition:width .4s}

.q-step{font-size:.7rem;font-weight:700;color:#7c3aed!important;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:5px}
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
div[data-testid="stButton"]>button[kind="secondary"]:hover{border-color:#7c3aed!important;background:#faf5ff!important}
div[data-testid="stButton"]>button[kind="primary"]{
    background:linear-gradient(135deg,#7c3aed,#a855f7)!important;
    color:white!important;border:none!important;border-radius:12px!important;
    font-weight:700!important;font-size:1rem!important;
    padding:14px 28px!important;width:100%!important
}
.stTextInput>div>div>input{border:2px solid #e2e8f0!important;border-radius:11px!important;font-size:.97rem!important;padding:12px 15px!important;color:#1e293b!important;background:white!important}
.stTextInput>div>div>input:focus{border-color:#7c3aed!important}

.res-box{border-radius:16px;padding:28px 20px;text-align:center;margin-bottom:18px;background:linear-gradient(135deg,#1e1b4b,#312e81);border:2px solid #6366f1}
.res-emoji{font-size:2.6rem;margin-bottom:10px}
.res-label{font-size:.7rem;font-weight:700;opacity:.55;text-transform:uppercase;letter-spacing:1px;color:white!important}
.res-title{font-size:1.5rem;font-weight:800;color:white!important;margin:5px 0}
.res-text{font-size:.87rem;opacity:.85;color:white!important;line-height:1.6}

.savings-row{background:white;border:2px solid #ede9fe;border-radius:14px;padding:16px 18px;margin-bottom:10px;display:flex;align-items:center;gap:14px}
.savings-num{font-size:1.6rem;font-weight:800;color:#7c3aed}
.savings-desc{font-size:.9rem;color:#374151;line-height:1.45}
.savings-desc strong{color:#0f172a}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
defaults = {"krok": 0, "oblast": "", "frekvence": "", "tym": ""}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Úspora ────────────────────────────────────────────────────────────────────
USPORA = {
    "🎪  Domlouvání a potvrzování akcí s klienty":         {"pct": 0.80, "popis": "Komunikace s klienty", "kde": "Automatické odpovědi, booking formuláře, potvrzení — bez jediného kliknutí"},
    "📣  Tvorba obsahu a propagace každé akce":             {"pct": 0.65, "popis": "Marketing a obsah", "kde": "Texty, popisky, posty — AI připraví draft za minuty místo hodin"},
    "📦  Sledování vybavení, pronájmů a skladových zásob": {"pct": 0.75, "popis": "Logistika pronájmů", "kde": "Automatický přehled co je kde, kdy se vrátí, co chybí"},
    "📋  Ruční vyplňování smluv, faktur a výkazů":          {"pct": 0.85, "popis": "Administrativa", "kde": "Smlouvy a faktury generované z jednoho formuláře za 10 sekund"},
    "📊  Přehled pro všechny 3 partnery — kdo co dělá":    {"pct": 0.70, "popis": "Koordinace partnerů", "kde": "Sdílený dashboard — každý vidí stav v reálném čase"},
    "💬  Odpovídání na stále stejné dotazy zájemců":        {"pct": 0.90, "popis": "Zákaznická komunikace", "kde": "Chatbot nebo automatické odpovědi vyřídí 90 % dotazů sám"},
}

FREKVENCE_HODINY = {
    "📅  1–3 akce měsíčně":   8,
    "📅  4–8 akcí měsíčně":   20,
    "📅  9–15 akcí měsíčně":  40,
    "📅  16+ akcí měsíčně":   70,
}

TYM_MULT = {
    "👤  Jen my 3 zakladatelé": 1.0,
    "👥  3 + 1–3 brigádníci":  1.3,
    "👥  Větší tým 5–10 lidí": 1.6,
}

# ── KROK 0 ────────────────────────────────────────────────────────────────────
if st.session_state.krok == 0:
    st.markdown("""
    <div class="hero">
        <div class="hero-badge">⚡ 90 sekund · zdarma</div>
        <h1>Filippe, kde vám AI ušetří nejvíc času?</h1>
        <p>3 otázky přímo pro Black Man Group — dostaneš konkrétní čísla, ne obecné rady.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="q-step">Otázka 1 / 3</p><p class="q-title">Co vám bere nejvíc času při každé akci?</p><p class="q-sub">Vyberte jednu oblast.</p>', unsafe_allow_html=True)

    for o in USPORA.keys():
        if st.button(o, key=f"oblast_{o}", use_container_width=True):
            st.session_state.oblast = o
            st.session_state.krok = 1
            st.rerun()

# ── KROK 1 ────────────────────────────────────────────────────────────────────
elif st.session_state.krok == 1:
    st.markdown('<div class="prog-wrap"><div class="prog-fill" style="width:50%"></div></div>', unsafe_allow_html=True)
    st.markdown('<p class="q-step">Otázka 2 / 3</p><p class="q-title">Kolik akcí Black Man Group pořádá za měsíc?</p><p class="q-sub">Počítejte i menší eventy a pronájmy.</p>', unsafe_allow_html=True)

    for f in FREKVENCE_HODINY.keys():
        if st.button(f, key=f"freq_{f}", use_container_width=True):
            st.session_state.frekvence = f
            st.session_state.krok = 2
            st.rerun()

# ── KROK 2 ────────────────────────────────────────────────────────────────────
elif st.session_state.krok == 2:
    st.markdown('<div class="prog-wrap"><div class="prog-fill" style="width:80%"></div></div>', unsafe_allow_html=True)
    st.markdown('<p class="q-step">Otázka 3 / 3</p><p class="q-title">Kdo teď dělá tuhle práci?</p><p class="q-sub">Kolik lidí se podílí na organizaci.</p>', unsafe_allow_html=True)

    for t in TYM_MULT.keys():
        if st.button(t, key=f"tym_{t}", use_container_width=True):
            st.session_state.tym = t
            st.session_state.krok = 3
            st.rerun()

# ── KROK 3 — Výsledek ─────────────────────────────────────────────────────────
elif st.session_state.krok == 3:
    data = USPORA.get(st.session_state.oblast, {"pct": 0.75, "popis": "Opakující se úkoly", "kde": "Automatizace ušetří čas napříč firmou"})
    hodiny_mesic = FREKVENCE_HODINY.get(st.session_state.frekvence, 20)
    mult = TYM_MULT.get(st.session_state.tym, 1.0)

    uspora_mesic = round(hodiny_mesic * data["pct"] * mult)
    uspora_tyden = round(uspora_mesic / 4)
    uspora_rok = uspora_mesic * 12

    # Uložit lokálně
    cas = datetime.now().strftime("%d.%m.%Y %H:%M")
    p = Path(__file__).parent / "leads_blackman.csv"
    hlavicka = not p.exists()
    with p.open("a", encoding="utf-8") as f:
        if hlavicka:
            f.write("Čas,Oblast,Frekvence,Tým,Úspora/měsíc\n")
        f.write(f'"{cas}","{st.session_state.oblast}","{st.session_state.frekvence}","{st.session_state.tym}","{uspora_mesic}"\n')

    st.markdown(f"""
    <div class="res-box">
        <div class="res-emoji">⚡</div>
        <div class="res-label">Odhadovaná úspora — {data['popis']}</div>
        <div class="res-title">~{uspora_tyden} hodin týdně · ~{uspora_mesic} hodin měsíčně</div>
        <div class="res-text">Ročně to dělá přibližně <strong style="color:#a5b4fc">{uspora_rok} hodin</strong>, které Black Man Group může věnovat růstu místo rutině.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="savings-row">
        <div class="savings-num">{uspora_mesic}h</div>
        <div class="savings-desc"><strong>{data['popis']}</strong><br>{data['kde']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    AUDIT_URL = "https://blackman-audit.streamlit.app"
    if st.button("🔍  Chci přesný plán pro Black Man Group", type="primary", use_container_width=True):
        st.markdown(f'<meta http-equiv="refresh" content="0; url={AUDIT_URL}">', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔄 Začít znovu", use_container_width=True):
        for k in defaults:
            st.session_state[k] = defaults[k]
        st.rerun()

    st.markdown('<p style="text-align:center;font-size:.76rem;color:#94a3b8;margin-top:14px">Black Man Group s.r.o. · AI Automatizace</p>', unsafe_allow_html=True)
