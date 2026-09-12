"""
سیستم ثبت‌نام و ورود برای داشبورد QuantTrader - با تایید دستی ادمین.

لیست کاربرا (نام کاربری، رمز هش‌شده، وضعیت تایید) روی همون ریپوی گیت‌هابی که
سیگنال‌های ربات تلگرام هم توش سینک می‌شن ذخیره می‌شه - چون Streamlit Cloud
حافظه‌ی موقتی داره و با هر ری‌دیپلوی/اسلیپ پاک می‌شه، نمی‌شه رو خود سرور نگهش داشت.

⚠️ امنیت رمزها: هیچ‌وقت متن ساده ذخیره نمی‌شه؛ هر رمز با یه salt تصادفی جدا
(برای هر کاربر) و الگوریتم PBKDF2-SHA256 هش می‌شه. با این‌حال چون فایل نهایی
روی گیت‌هاب می‌مونه، حتماً مطمئن شو ریپو Private هست.

🔒 تقویت‌های امنیتی این نسخه:
  - محافظت در برابر حدس‌زدن رمز (brute-force): بعد از ۵ بار رمز اشتباه پشت‌سرهم،
    حساب برای ۱۵ دقیقه قفل می‌شه.
  - رمز عبور باید حداقل ۸ کاراکتر باشه و شامل حداقل یه حرف و یه عدد.
  - پشتیبانی از timeout خودکار جلسه (چک واقعیش توی app.py انجام می‌شه).

Secrets لازم (توی Streamlit Cloud -> App settings -> Secrets، یا متغیر محیطی):
  GITHUB_TOKEN       - همون Personal Access Token که برای ربات تلگرام ساختی؛
                       توصیه می‌شه یه توکن Fine-grained جدا و مخصوص همین یه ریپو
                       بسازی (نه یه توکن classic با دسترسی به همه‌ی ریپوهات) تا
                       اگه لو رفت، بقیه‌ی ریپوهات در امان بمونن.
  GITHUB_REPO        - مثلا "CodeForgeXX/Quanttrader"
  GITHUB_USERS_PATH  - اختیاری، پیش‌فرض "data/users.json"
  ADMIN_USERNAME     - نام کاربری حساب ادمین (خودت)
  ADMIN_PASSWORD     - رمز حساب ادمین (این یکی هش نمی‌شه، مستقیم از Secrets خونده می‌شه)
"""

import base64
import hashlib
import json
import os
import re
import secrets as pysecrets
from datetime import datetime, timedelta, timezone

import requests
import streamlit as st

GITHUB_API_BASE = "https://api.github.com"

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
MIN_PASSWORD_LENGTH = 8
SESSION_IDLE_TIMEOUT_HOURS = 12  # بعد از این مدت بی‌فعالیتی، باید دوباره لاگین کنی


def _cfg(key, default=None):
    """هم از st.secrets هم از متغیر محیطی می‌خونه (هرکدوم موجود بود)."""
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key, default)


GITHUB_TOKEN = _cfg("GITHUB_TOKEN")
GITHUB_REPO = _cfg("GITHUB_REPO")
GITHUB_USERS_PATH = _cfg("GITHUB_USERS_PATH", "data/users.json")
ADMIN_USERNAME = _cfg("ADMIN_USERNAME")
ADMIN_PASSWORD = _cfg("ADMIN_PASSWORD")


def is_configured() -> bool:
    return bool(GITHUB_TOKEN and GITHUB_REPO)


def _headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "QuantTraderDashboard",
    }


def _users_url():
    return f"{GITHUB_API_BASE}/repos/{GITHUB_REPO}/contents/{GITHUB_USERS_PATH}"


def _load_users_raw():
    """(users_dict, sha) رو برمی‌گردونه. اگه فایل هنوز وجود نداشت، ({}, None)."""
    res = requests.get(_users_url(), headers=_headers(), timeout=15)
    if res.status_code == 404:
        return {}, None
    res.raise_for_status()
    data = res.json()
    content = base64.b64decode(data["content"]).decode("utf-8")
    return json.loads(content), data["sha"]


def _save_users_raw(users: dict, sha, message: str):
    payload = {
        "message": message,
        "content": base64.b64encode(
            json.dumps(users, ensure_ascii=False, indent=2).encode("utf-8")
        ).decode("ascii"),
        "branch": _cfg("GITHUB_BRANCH", "main"),
    }
    if sha:
        payload["sha"] = sha
    res = requests.put(_users_url(), headers=_headers(), json=payload, timeout=15)
    res.raise_for_status()
    return res.json()


def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000).hex()


def _validate_password_strength(password: str):
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"رمز عبور باید حداقل {MIN_PASSWORD_LENGTH} کاراکتر باشه."
    if not re.search(r"[A-Za-z]", password):
        return False, "رمز عبور باید حداقل یه حرف داشته باشه."
    if not re.search(r"\d", password):
        return False, "رمز عبور باید حداقل یه عدد داشته باشه."
    return True, ""


def register_user(username: str, password: str):
    """(True, پیام) یا (False, پیام خطا) رو برمی‌گردونه."""
    username = username.strip().lower()
    if not username or not password:
        return False, "نام کاربری و رمز عبور نمی‌تونن خالی باشن."

    ok, msg = _validate_password_strength(password)
    if not ok:
        return False, msg

    try:
        users, sha = _load_users_raw()
    except Exception as e:
        return False, f"اتصال به سرور ثبت‌نام ناموفق بود: {e}"

    if username in users:
        return False, "این نام کاربری قبلاً ثبت شده."

    salt = pysecrets.token_hex(16)
    users[username] = {
        "password_hash": _hash_password(password, salt),
        "salt": salt,
        "approved": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "failed_attempts": 0,
        "locked_until": None,
    }
    try:
        _save_users_raw(users, sha, message=f"ثبت‌نام کاربر جدید: {username}")
    except Exception as e:
        return False, f"ذخیره‌ی ثبت‌نام ناموفق بود: {e}"
    return True, "ثبت‌نام انجام شد ✅ حالا باید منتظر تایید ادمین بمونی."


def _is_locked(user: dict) -> bool:
    locked_until = user.get("locked_until")
    if not locked_until:
        return False
    try:
        return datetime.fromisoformat(locked_until) > datetime.now(timezone.utc)
    except Exception:
        return False


def is_locked(user: dict) -> bool:
    """نسخه‌ی عمومی _is_locked - برای استفاده خارج از این ماژول (مثلاً پنل ادمین)."""
    return _is_locked(user)


def authenticate(username: str, password: str):
    """(True, "ok") یا (False, پیام خطا) رو برمی‌گردونه."""
    username = username.strip().lower()
    try:
        users, sha = _load_users_raw()
    except Exception as e:
        return False, f"اتصال به سرور ورود ناموفق بود: {e}"

    user = users.get(username)
    if not user:
        return False, "نام کاربری یا رمز عبور اشتباهه."

    if _is_locked(user):
        remaining = datetime.fromisoformat(user["locked_until"]) - datetime.now(timezone.utc)
        minutes_left = max(1, int(remaining.total_seconds() // 60) + 1)
        return False, f"به‌خاطر تلاش‌های ناموفق زیاد، حساب موقتاً قفله. {minutes_left} دقیقه دیگه امتحان کن."

    expected = _hash_password(password, user["salt"])
    if expected != user["password_hash"]:
        # رمز اشتباه - شمارنده رو زیاد کن و در صورت لزوم قفل کن
        user["failed_attempts"] = user.get("failed_attempts", 0) + 1
        if user["failed_attempts"] >= MAX_FAILED_ATTEMPTS:
            user["locked_until"] = (
                datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_MINUTES)
            ).isoformat()
            user["failed_attempts"] = 0
        try:
            _save_users_raw(users, sha, message=f"تلاش ورود ناموفق: {username}")
        except Exception:
            pass  # اگه ذخیره‌ی شمارنده شکست خورد، حداقل خودِ ورود رو رد کن
        return False, "نام کاربری یا رمز عبور اشتباهه."

    if not user.get("approved"):
        return False, "حسابت هنوز توسط ادمین تایید نشده."

    # ورود موفق - شمارنده‌ی تلاش‌های ناموفق رو صفر کن
    if user.get("failed_attempts", 0) > 0 or user.get("locked_until"):
        user["failed_attempts"] = 0
        user["locked_until"] = None
        try:
            _save_users_raw(users, sha, message=f"ورود موفق - بازنشانی شمارنده: {username}")
        except Exception:
            pass

    return True, "ok"


def is_admin(username: str, password: str) -> bool:
    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        return False
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD


def list_pending_usernames() -> list:
    users, _ = _load_users_raw()
    return [u for u, info in users.items() if not info.get("approved")]


def list_all_users() -> dict:
    users, _ = _load_users_raw()
    return users


def approve_user(username: str):
    users, sha = _load_users_raw()
    if username in users:
        users[username]["approved"] = True
        _save_users_raw(users, sha, message=f"تایید کاربر: {username}")


def reject_user(username: str):
    users, sha = _load_users_raw()
    if username in users:
        del users[username]
        _save_users_raw(users, sha, message=f"رد/حذف کاربر: {username}")


def unlock_user(username: str):
    """ادمین می‌تونه دستی یه حساب قفل‌شده رو زودتر باز کنه."""
    users, sha = _load_users_raw()
    if username in users:
        users[username]["failed_attempts"] = 0
        users[username]["locked_until"] = None
        _save_users_raw(users, sha, message=f"باز کردن دستی قفل: {username}")


def is_session_expired() -> bool:
    """چک می‌کنه آیا جلسه‌ی فعلی به‌خاطر بی‌فعالیتی طولانی باید منقضی بشه."""
    login_time = st.session_state.get("login_time")
    if not login_time:
        return False
    try:
        elapsed = datetime.now(timezone.utc) - datetime.fromisoformat(login_time)
        return elapsed > timedelta(hours=SESSION_IDLE_TIMEOUT_HOURS)
    except Exception:
        return False
