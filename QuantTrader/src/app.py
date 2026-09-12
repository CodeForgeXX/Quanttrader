import os

import pandas as pd
import streamlit as st
from datetime import datetime, timezone
from streamlit_autorefresh import st_autorefresh

from src import auth
from src.backtest import run_backtest

# ⚠️ st.set_page_config باید همیشه اولین دستور Streamlit توی کل فایل باشه،
# برای همین قبل از load_css() (که خودش از st.markdown استفاده می‌کنه) آورده شده.
st.set_page_config(
    page_title="QuantTrader",
    page_icon="📈",
    layout="wide",
)


def load_css():
    css_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "assets",
        "styles.css",
    )
    with open(css_path) as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True,
        )


load_css()

from config.settings import VERSION
from src.dashboard_data import get_dashboard_data, get_klines
from src.charts import create_candlestick
from src.trade_history import FILE_PATH as TRADES_FILE_PATH


# ==========================
# گیت ورود / ثبت‌نام
# ==========================

def _login_gate():
    """اگه کاربر لاگین نکرده (یا جلسه‌ش منقضی شده)، فرم ورود/ثبت‌نام رو نشون می‌ده."""

    # چک انقضای جلسه به‌خاطر بی‌فعالیتی طولانی - حتی اگه قبلاً لاگین کرده باشه
    if st.session_state.get("authenticated") and auth.is_session_expired():
        st.session_state.clear()
        st.warning("⏱️ به‌خاطر بی‌فعالیتی طولانی، جلسه‌ت منقضی شد. دوباره وارد شو.")

    if st.session_state.get("authenticated"):
        return

    if not auth.is_configured():
        st.error(
            "⚠️ سیستم ورود هنوز تنظیم نشده (GITHUB_TOKEN / GITHUB_REPO رو توی "
            "Secrets داشبورد تنظیم کن)."
        )
        st.stop()

    st.markdown(
        """
        <h1 style='margin-bottom:0px;'>🚀 QuantTrader PRO X</h1>
        <p style='color:#9ca3af; font-size:18px; margin-top:0px;'>ورود به داشبورد</p>
        """,
        unsafe_allow_html=True,
    )

    tab_login, tab_register = st.tabs(["🔐 ورود", "📝 ثبت‌نام"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("نام کاربری")
            password = st.text_input("رمز عبور", type="password")
            submitted = st.form_submit_button("ورود")

        if submitted:
            if auth.is_admin(username, password):
                st.session_state.authenticated = True
                st.session_state.is_admin = True
                st.session_state.username = username
                st.session_state.login_time = datetime.now(timezone.utc).isoformat()
                st.rerun()
            else:
                ok, msg = auth.authenticate(username, password)
                if ok:
                    st.session_state.authenticated = True
                    st.session_state.is_admin = False
                    st.session_state.username = username
                    st.session_state.login_time = datetime.now(timezone.utc).isoformat()
                    st.rerun()
                else:
                    st.error(msg)

    with tab_register:
        st.caption(
            f"بعد از ثبت‌نام، باید منتظر تایید دستی ادمین بمونی. رمز عبور باید "
            f"حداقل {auth.MIN_PASSWORD_LENGTH} کاراکتر باشه و شامل حرف و عدد."
        )
        with st.form("register_form"):
            new_username = st.text_input("نام کاربری جدید")
            new_password = st.text_input("رمز عبور جدید", type="password")
            submitted_r = st.form_submit_button("ثبت‌نام")

        if submitted_r:
            ok, msg = auth.register_user(new_username, new_password)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    st.stop()


_login_gate()

with st.sidebar:
    st.write(f"👤 {st.session_state.get('username', '')}")
    if st.button("🚪 خروج"):
        st.session_state.clear()
        st.rerun()

    if st.session_state.get("is_admin"):
        st.divider()
        st.subheader("🛠 پنل ادمین")
        try:
            all_users = auth.list_all_users()
        except Exception as e:
            all_users = {}
            st.error(f"گرفتن لیست کاربرا ناموفق بود: {e}")

        pending = [u for u, info in all_users.items() if not info.get("approved")]
        locked = [u for u, info in all_users.items() if auth.is_locked(info)]

        if pending:
            st.caption(f"{len(pending)} کاربر در انتظار تایید:")
            for u in pending:
                c1, c2 = st.columns(2)
                if c1.button("✅ تایید", key=f"approve_{u}"):
                    auth.approve_user(u)
                    st.rerun()
                if c2.button("❌ رد", key=f"reject_{u}"):
                    auth.reject_user(u)
                    st.rerun()
                st.caption(u)
        else:
            st.caption("کاربر در انتظار تاییدی نیست.")

        if locked:
            st.divider()
            st.caption(f"🔒 {len(locked)} حساب قفل‌شده (تلاش ناموفق زیاد):")
            for u in locked:
                if st.button(f"🔓 باز کردن قفل {u}", key=f"unlock_{u}"):
                    auth.unlock_user(u)
                    st.rerun()


# ==========================
# از اینجا به بعد، همون داشبورد اصلی - بدون تغییر
# ==========================

st_autorefresh(
    interval=30000,
    key="quanttrader_refresh_001",
)

st.markdown(
    """
    <h1 style='margin-bottom:0px;'>
        🚀 QuantTrader PRO X
    </h1>
    <p style='color:#9ca3af;
              font-size:18px;
              margin-top:0px;'>
        Live Crypto Intelligence
    </p>
    """,
    unsafe_allow_html=True,
)

table, stats = get_dashboard_data()

# ==========================
# Best Trade
# ==========================
if not table.empty:
    best_trade = table.sort_values(
        by="Score",
        ascending=False,
    ).iloc[0]
    st.success(
        f"""
🔥 BEST TRADE NOW
🪙 {best_trade['Coin']}
📢 {best_trade['Signal']}
🎯 Probability : {best_trade['Probability']}
⭐ Score : {best_trade['Score']}
💰 Entry : {best_trade['Entry']}
🛑 Stop : {best_trade['Stop']}
🎯 TP1 : {best_trade['TP1']}
"""
    )

st.divider()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Coins", stats["coins"])
col2.metric("BUY", stats["buy"])
col3.metric("SELL", stats["sell"])
col4.metric("HOLD", stats["hold"])
st.divider()

if table.empty:
    st.error("❌ No market data received from Binance.")
    st.stop()

st.subheader("📊 Market Overview")
st.dataframe(
    table,
    width="stretch",
    hide_index=True,
)

if table.empty:
    st.error("No market data received.")
    st.stop()

selected = st.selectbox(
    "🪙 Select Coin",
    table["Coin"].tolist(),
)
df = get_klines(selected)
if df is None:
    st.error(f"Cannot load {selected}")
    st.stop()

st.subheader(f"📈 {selected} Live Chart")
fig = create_candlestick(
    df,
    selected,
)
st.plotly_chart(
    fig,
    width="stretch",
)

latest = df.iloc[-1]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Open", f"{latest['Open']:.2f}")
c2.metric("High", f"{latest['High']:.2f}")
c3.metric("Low", f"{latest['Low']:.2f}")
c4.metric("Close", f"{latest['Close']:.2f}")

st.divider()
st.subheader("📜 Trade History")
st.divider()
st.divider()
st.subheader("📈 Backtest")

if st.button("▶ Run Backtest"):
    result = run_backtest(df)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Trades", result["Trades"])
    c2.metric("Wins", result["Wins"])
    c3.metric("Losses", result["Losses"])
    c4.metric("Win Rate", f"{result['WinRate']}%")
    st.success(f"Net Profit : {result['Profit']}")

if os.path.exists(TRADES_FILE_PATH):
    history = pd.read_csv(TRADES_FILE_PATH)
    st.dataframe(
        history.tail(20),
        width="stretch",
        hide_index=True,
    )
else:
    st.info("No trades recorded.")
