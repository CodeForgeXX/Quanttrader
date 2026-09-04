"""
موتور Smart Money Concepts (SMC) — نسخه اصلاح‌شده.

این ماژول همون ایده‌های داشبورد Streamlit (Structure, BOS, CHOCH, Liquidity,
Order Block, Fair Value Gap) رو پیاده می‌کنه، ولی با رفع باگ‌هایی که توی کد اصلی
داشبورد پیدا شدن:

  1. تشخیص Structure: به‌جای if/if که DOWNTREND همیشه UPTREND رو رونویسی می‌کرد،
     الان "سقف بالاتر + کف بالاتر" = UPTREND، "سقف پایین‌تر + کف پایین‌تر" = DOWNTREND،
     و اگه هم‌زمان سقف تازه و کف تازه بزنه (نوسان شدید) = VOLATILE، نه یه‌طرفه DOWNTREND.
  2. CHOCH: به‌جای "هرجا SIDEWAYS بود CHOCH هم هست" (تعریف غلط)، الان با مقایسه‌ی
     ساختار فعلی با ساختار یه پنجره عقب‌تر تشخیص داده می‌شه - یعنی واقعاً یعنی
     "روند برعکس شده"، نه "روند نامشخصه".
  3. Order Block Strength: به‌جای فرمول خام (displacement*1000) که برای BTC همیشه
     ۱۰۰ و برای آلت‌کوین ارزون همیشه نزدیک صفر می‌شد، الان بر مبنای درصد تغییر
     نسبت به قیمت حساب می‌شه - قابل‌مقایسه بین همه دارایی‌ها.
  4. Liquidity Grab: به‌جای چک‌کردن روی کل تاریخچه‌ی داده (که باعث می‌شد این پرچم
     تقریباً همیشه True بمونه و بی‌فایده بشه)، فقط یه پنجره‌ی اخیر (پیش‌فرض ۳۰ کندل)
     رو چک می‌کنه.
  5. امتیازدهی یکپارچه: به‌جای ۳ لایه که نتیجه‌ی همدیگه رو دور می‌ریختن (باگ اصلی
     داشبورد)، الان فقط یه تابع امتیازدهی هست که هم Order Block هم Liquidity Grab
     رو جهت‌دار (bullish/bearish) در نظر می‌گیره، نه یک‌طرفه.
"""

from dataclasses import dataclass, field


def detect_swings(highs: list, lows: list, lookback: int = 3):
    """اندیس کندل‌هایی که swing high/low هستن رو برمی‌گردونه (fractal ساده)."""
    swing_highs, swing_lows = [], []
    n = len(highs)
    for i in range(lookback, n - lookback):
        window_highs = highs[i - lookback: i + lookback + 1]
        window_lows = lows[i - lookback: i + lookback + 1]
        if highs[i] == max(window_highs) and window_highs.count(highs[i]) == 1:
            swing_highs.append(i)
        if lows[i] == min(window_lows) and window_lows.count(lows[i]) == 1:
            swing_lows.append(i)
    return swing_highs, swing_lows


def _structure_from_pair(highs, lows, swing_highs, swing_lows, idx_high, idx_low):
    """با دو تا سوینگ متوالی (اندیس idx و idx-1)، ساختار اون لحظه رو تعیین می‌کنه."""
    higher_high = lower_high = higher_low = lower_low = None
    if idx_high is not None and idx_high >= 1 and len(swing_highs) > idx_high:
        cur = highs[swing_highs[idx_high]]
        prev = highs[swing_highs[idx_high - 1]]
        higher_high = cur > prev
        lower_high = not higher_high
    if idx_low is not None and idx_low >= 1 and len(swing_lows) > idx_low:
        cur = lows[swing_lows[idx_low]]
        prev = lows[swing_lows[idx_low - 1]]
        lower_low = cur < prev
        higher_low = not lower_low

    if higher_high and higher_low:
        return "UPTREND"
    if lower_low and lower_high:
        return "DOWNTREND"
    if higher_high and lower_low:
        return "VOLATILE"
    return "SIDEWAYS"


def analyze_structure(highs: list, lows: list, swing_highs: list, swing_lows: list):
    """
    Structure فعلی رو با مقایسه‌ی دو سوینگ آخر تعیین می‌کنه، و با مقایسه‌ش با
    ساختار یه پنجره عقب‌تر، BOS (ادامه‌ی روند) یا CHOCH (برگشت روند) رو تشخیص می‌ده.
    """
    current_structure = _structure_from_pair(
        highs, lows, swing_highs, swing_lows,
        idx_high=len(swing_highs) - 1, idx_low=len(swing_lows) - 1,
    )
    prev_structure = _structure_from_pair(
        highs, lows, swing_highs, swing_lows,
        idx_high=len(swing_highs) - 2, idx_low=len(swing_lows) - 2,
    )

    bos = False
    choch = False
    if current_structure in ("UPTREND", "DOWNTREND"):
        if current_structure == prev_structure:
            bos = True  # ادامه‌ی همون روند قبلی - تاییدیه
        elif prev_structure in ("UPTREND", "DOWNTREND"):
            choch = True  # روند برعکس شده نسبت به قبل - هشدار برگشت

    return {
        "structure": current_structure,
        "prev_structure": prev_structure,
        "bos": bos,
        "choch": choch,
    }


def analyze_liquidity(highs, lows, swing_highs, swing_lows, tolerance=0.001, recent_window=30):
    """
    Equal highs/lows (نقدینگی احتمالی) رو پیدا می‌کنه، و «Liquidity Grab» رو فقط
    توی یه پنجره‌ی اخیر چک می‌کنه (نه کل تاریخچه) تا این پرچم بامعنی بمونه.
    """
    equal_highs, equal_lows = [], []
    for i in range(1, len(swing_highs)):
        cur, prev = highs[swing_highs[i]], highs[swing_highs[i - 1]]
        if prev and abs(cur - prev) / prev <= tolerance:
            equal_highs.append(swing_highs[i])
    for i in range(1, len(swing_lows)):
        cur, prev = lows[swing_lows[i]], lows[swing_lows[i - 1]]
        if prev and abs(cur - prev) / prev <= tolerance:
            equal_lows.append(swing_lows[i])

    buy_side = len(equal_highs) > 0
    sell_side = len(equal_lows) > 0
    liquidity_grab = False
    grab_direction = None  # "buy_side" یا "sell_side"

    recent_highs = highs[-recent_window:] if len(highs) > recent_window else highs
    recent_lows = lows[-recent_window:] if len(lows) > recent_window else lows

    if buy_side:
        eq_level = highs[equal_highs[-1]]
        if recent_highs and max(recent_highs) > eq_level:
            liquidity_grab = True
            grab_direction = "buy_side"
    if sell_side:
        eq_level = lows[equal_lows[-1]]
        if recent_lows and min(recent_lows) < eq_level:
            liquidity_grab = True
            grab_direction = "sell_side" if grab_direction is None else "both"

    return {
        "equal_highs": equal_highs,
        "equal_lows": equal_lows,
        "buy_side_liquidity": buy_side,
        "sell_side_liquidity": sell_side,
        "liquidity_grab": liquidity_grab,
        "grab_direction": grab_direction,
    }


def analyze_order_block(opens, highs, lows, closes, structure):
    """
    آخرین Order Block رو (بر اساس جهت Structure) پیدا می‌کنه. قدرتش (ob_strength)
    بر مبنای درصد جابه‌جایی قیمت نسبت به خودش حساب می‌شه، نه عدد خام - این باعث
    می‌شه بین BTC (قیمت بالا) و یه آلت‌کوین ارزون قابل‌مقایسه باشه.
    """
    result = {
        "bullish_ob": False, "bearish_ob": False,
        "bullish_ob_price": 0.0, "bearish_ob_price": 0.0,
        "ob_strength": 0, "mitigated": False,
    }
    n = len(closes)
    if n < 4:
        return result

    if structure == "UPTREND":
        for i in range(n - 2, 1, -1):
            if closes[i] < opens[i]:  # آخرین کندل نزولی قبل از حرکت صعودی قوی
                result["bullish_ob"] = True
                result["bullish_ob_price"] = lows[i]
                ref_price = opens[i + 1] or 1e-9
                displacement_pct = abs(closes[i + 1] - opens[i + 1]) / ref_price * 100
                result["ob_strength"] = min(100, int(displacement_pct * 20))
                break
    elif structure == "DOWNTREND":
        for i in range(n - 2, 1, -1):
            if closes[i] > opens[i]:  # آخرین کندل صعودی قبل از حرکت نزولی قوی
                result["bearish_ob"] = True
                result["bearish_ob_price"] = highs[i]
                ref_price = opens[i + 1] or 1e-9
                displacement_pct = abs(opens[i + 1] - closes[i + 1]) / ref_price * 100
                result["ob_strength"] = min(100, int(displacement_pct * 20))
                break

    if result["bullish_ob"] and lows[-1] <= result["bullish_ob_price"]:
        result["mitigated"] = True
    if result["bearish_ob"] and highs[-1] >= result["bearish_ob_price"]:
        result["mitigated"] = True

    return result


def analyze_fvg(highs, lows):
    """آخرین Fair Value Gap (شکاف قیمتی ۳-کندلی) رو پیدا می‌کنه."""
    result = {
        "bullish_fvg": False, "bearish_fvg": False,
        "bullish_fvg_price": 0.0, "bearish_fvg_price": 0.0,
    }
    for i in range(2, len(highs)):
        if lows[i] > highs[i - 2]:
            result["bullish_fvg"] = True
            result["bullish_fvg_price"] = (lows[i] + highs[i - 2]) / 2
        elif highs[i] < lows[i - 2]:
            result["bearish_fvg"] = True
            result["bearish_fvg_price"] = (highs[i] + lows[i - 2]) / 2
    return result


def smc_score(structure_info, liquidity_info, ob_info, fvg_info, price, ema20, ema50, ema200):
    """
    امتیاز نهایی SMC - یه لایه‌ی واحد (نه ۳ لایه که همدیگه رو دور می‌ریزن مثل داشبورد
    اصلی)، و کاملاً جهت‌دار (هم برای bullish هم bearish وزن قرینه داره).
    """
    score = 0
    structure = structure_info["structure"]

    if structure == "UPTREND":
        score += 20
    elif structure == "DOWNTREND":
        score -= 20

    if structure_info["bos"]:
        score += 15 if structure == "UPTREND" else (-15 if structure == "DOWNTREND" else 0)

    if structure_info["choch"]:
        # CHOCH یعنی روند *جدید* که تازه شکل گرفته - هم‌جهت با structure فعلیه
        score += 12 if structure == "UPTREND" else (-12 if structure == "DOWNTREND" else 0)

    if liquidity_info["liquidity_grab"]:
        if liquidity_info["grab_direction"] == "buy_side":
            score += 8
        elif liquidity_info["grab_direction"] == "sell_side":
            score -= 8

    if ob_info["bullish_ob"] and not ob_info["mitigated"]:
        score += ob_info["ob_strength"] // 10
    if ob_info["bearish_ob"] and not ob_info["mitigated"]:
        score -= ob_info["ob_strength"] // 10

    if fvg_info["bullish_fvg"]:
        score += 8
    if fvg_info["bearish_fvg"]:
        score -= 8

    if price > ema20 > ema50 > ema200:
        score += 10
    elif price < ema20 < ema50 < ema200:
        score -= 10

    return score


def build_smc_analysis(opens, highs, lows, closes, ema20, ema50, ema200, lookback=3):
    """همه‌ی مراحل رو پشت سر هم اجرا می‌کنه و یه دیکشنری کامل برمی‌گردونه."""
    swing_highs, swing_lows = detect_swings(highs, lows, lookback=lookback)
    structure_info = analyze_structure(highs, lows, swing_highs, swing_lows)
    liquidity_info = analyze_liquidity(highs, lows, swing_highs, swing_lows)
    ob_info = analyze_order_block(opens, highs, lows, closes, structure_info["structure"])
    fvg_info = analyze_fvg(highs, lows)

    price = closes[-1]
    score = smc_score(structure_info, liquidity_info, ob_info, fvg_info, price, ema20, ema50, ema200)

    return {
        "structure": structure_info["structure"],
        "bos": structure_info["bos"],
        "choch": structure_info["choch"],
        "buy_side_liquidity": liquidity_info["buy_side_liquidity"],
        "sell_side_liquidity": liquidity_info["sell_side_liquidity"],
        "liquidity_grab": liquidity_info["liquidity_grab"],
        "bullish_ob": ob_info["bullish_ob"],
        "bearish_ob": ob_info["bearish_ob"],
        "ob_strength": ob_info["ob_strength"],
        "ob_mitigated": ob_info["mitigated"],
        "bullish_fvg": fvg_info["bullish_fvg"],
        "bearish_fvg": fvg_info["bearish_fvg"],
        "score": score,
    }
