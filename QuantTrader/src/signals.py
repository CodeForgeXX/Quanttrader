"""
موتور امتیازدهی داشبورد - نسخه‌ی هماهنگ با ربات تلگرام.

طبق تصمیم مشترک: یه سیگنال فقط وقتی معتبر/قوی اعلام می‌شه که دو موتور مستقل
(اندیکاتورهای کلاسیک EMA/RSI/MACD + Smart Money Concepts) با هم موافق باشن.
اگه مخالف بودن، محافظه‌کارانه HOLD برمی‌گرده - دقیقاً همون منطقی که ربات تلگرام
(signals.py آنجا، تابع combine_signals) استفاده می‌کنه، تا داشبورد و ربات همیشه
یک‌جور تصمیم بگیرن، نه دو تا نتیجه‌ی متفاوت برای یه نماد.
"""

_BULLISH_KEYS = {"STRONG_BUY", "BUY"}
_BEARISH_KEYS = {"STRONG_SELL", "WEAK_SELL"}


# ---------- موتور ۱: اندیکاتورهای کلاسیک (بدون تغییر نسبت به قبل) ----------

def calculate_score(price, ema20, ema50, ema200, rsi, macd_line, signal_line, volume, avg_volume):
    score = 0
    if price > ema20:
        score += 1
    if price > ema50:
        score += 2
    if price > ema200:
        score += 3
    if rsi < 30:
        score += 3
    elif rsi < 45:
        score += 1
    elif rsi > 70:
        score -= 3
    elif rsi > 55:
        score -= 1
    if macd_line > signal_line:
        score += 3
    else:
        score -= 3
    if volume > avg_volume:
        score += 2
    return score


def _ema_key_from_score(score):
    if score >= 10:
        return "STRONG_BUY"
    elif score >= 6:
        return "BUY"
    elif score >= 3:
        return "HOLD"
    elif score >= 0:
        return "WEAK_SELL"
    else:
        return "STRONG_SELL"


def ema_signal_from_score(score):
    key = _ema_key_from_score(score)
    return {
        "STRONG_BUY": {"key": "STRONG_BUY", "en": "STRONG BUY", "emoji": "🟢"},
        "BUY": {"key": "BUY", "en": "BUY", "emoji": "🟢"},
        "HOLD": {"key": "HOLD", "en": "HOLD", "emoji": "🟡"},
        "WEAK_SELL": {"key": "WEAK_SELL", "en": "WEAK SELL", "emoji": "🟠"},
        "STRONG_SELL": {"key": "STRONG_SELL", "en": "STRONG SELL", "emoji": "🔴"},
    }[key]


def signal_from_score(score):
    """برای سازگاری با هر کد قدیمی که هنوز رشته‌ی مستقیم می‌خواد."""
    s = ema_signal_from_score(score)
    return f"{s['emoji']} {s['en']}"


def probability(score):
    return max(0, min(100, 50 + score * 5))


# ---------- موتور ۲: Smart Money Concepts (src/smc.py) ----------

def smc_signal_from_score(score):
    """معادل ema_signal_from_score ولی با آستانه‌های متناسب با مقیاس امتیاز SMC (تقریباً -83 تا 83)."""
    if score >= 35:
        return {"key": "STRONG_BUY", "en": "STRONG BUY", "emoji": "🟢"}
    if score >= 15:
        return {"key": "BUY", "en": "BUY", "emoji": "🟢"}
    if score >= -15:
        return {"key": "HOLD", "en": "HOLD", "emoji": "🟡"}
    if score >= -35:
        return {"key": "WEAK_SELL", "en": "WEAK SELL", "emoji": "🟠"}
    return {"key": "STRONG_SELL", "en": "STRONG SELL", "emoji": "🔴"}


def smc_probability(score):
    return max(5, min(95, 50 + score))


# ---------- ترکیب دو موتور (دقیقاً همون منطق ربات تلگرام) ----------

def combine_signals(ema_signal: dict, ema_prob: int, smc_signal: dict, smc_prob: int):
    """
    قانون ترکیب (طبق تصمیم: کیفیت مهم‌تر از تعداده):
      - اگه هردو موتور هم‌جهت (هردو صعودی یا هردو نزولی) باشن -> سیگنال معتبر می‌شه؛
        اگه هردوشون هم "قوی" بودن -> STRONG، وگرنه سطح معمولی.
      - اگه با هم مخالف بودن (یا یکی خنثی) -> HOLD محافظه‌کارانه، فارغ از این‌که
        تک‌تک موتورها چقدر مطمئن به‌نظر می‌رسیدن.

    خروجی: (final_signal_dict, combined_prob, agree)
    """
    ema_key, smc_key = ema_signal["key"], smc_signal["key"]
    agree = False

    if ema_key in _BULLISH_KEYS and smc_key in _BULLISH_KEYS:
        agree = True
        combined_prob = round((ema_prob + smc_prob) / 2)
        both_strong = ema_key == "STRONG_BUY" and smc_key == "STRONG_BUY"
        final = {"key": "STRONG_BUY", "en": "STRONG BUY", "emoji": "🟢"} if both_strong \
            else {"key": "BUY", "en": "BUY", "emoji": "🟢"}
    elif ema_key in _BEARISH_KEYS and smc_key in _BEARISH_KEYS:
        agree = True
        combined_prob = round((ema_prob + smc_prob) / 2)
        both_strong = ema_key == "STRONG_SELL" and smc_key == "STRONG_SELL"
        final = {"key": "STRONG_SELL", "en": "STRONG SELL", "emoji": "🔴"} if both_strong \
            else {"key": "WEAK_SELL", "en": "SELL", "emoji": "🟠"}
    else:
        final = {"key": "HOLD", "en": "HOLD", "emoji": "🟡"}
        combined_prob = 50

    return final, combined_prob, agree


def signal_dict_to_string(signal_dict: dict) -> str:
    """برای نمایش توی جدول - همون فرمت قدیمی ('🟢 STRONG BUY' و ...)."""
    return f"{signal_dict['emoji']} {signal_dict['en']}"
