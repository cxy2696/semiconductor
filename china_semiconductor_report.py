import ast
import concurrent.futures
import json
import math
import os
import re
import shutil
import time
import webbrowser
from datetime import datetime
from zoneinfo import ZoneInfo

import akshare as ak
import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup
from jinja2 import Template

print("正在生成中国半导体行业报告 v5.4（GitHub 持续更新版）")

# ====================== 您的公司元数据（v5.3 已全面更新） ======================
# 32家核心半导体上市公司（设备/材料/晶圆代工/设计/IDM/存储/AI芯片/封测全覆盖）
_base_dir = os.path.dirname(os.path.abspath(__file__))
_docs_dir = os.path.join(_base_dir, "docs")
_config_dir = os.path.join(_base_dir, "config")
_meta_path_candidates = [
    os.path.join(_config_dir, "company_metadata.py"),
    os.path.join(_base_dir, "company_metadata"),
]
_template_path_candidates = [
    os.path.join(_config_dir, "html_template.html"),
    os.path.join(_base_dir, "html_template.html"),
]


def pick_first_existing(candidates):
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(f"No existing path found in candidates: {candidates}")


_meta_path = pick_first_existing(_meta_path_candidates)

def load_company_metadata(path):
    with open(path, encoding="utf-8") as meta_file:
        raw = meta_file.read()
    tree = ast.parse(raw, filename="company_metadata", mode="exec")
    metadata = None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "company_metadata":
                metadata = ast.literal_eval(node.value)
                break
        if metadata is not None:
            break
    if not isinstance(metadata, list) or not metadata:
        raise ValueError("company_metadata must define a non-empty list named `company_metadata`.")
    return metadata

company_metadata = load_company_metadata(_meta_path)

total_companies = len(company_metadata)
print(f"已加载 {total_companies} 条公司数据（最新名单）")


def ensure_dirs():
    os.makedirs(_docs_dir, exist_ok=True)


def sanitize_for_json(value):
    """Recursively convert NaN/Infinity-like values into JSON-safe values."""
    if isinstance(value, dict):
        return {k: sanitize_for_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize_for_json(v) for v in value]
    if isinstance(value, tuple):
        return [sanitize_for_json(v) for v in value]
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if hasattr(value, "item"):
        try:
            return sanitize_for_json(value.item())
        except Exception:
            return value
    return value


ensure_dirs()

# ====================== 新闻抓取 ======================
def get_dramx_news(display_items=8, pool_size=24):
    def parse_date_from_link(link):
        m = re.search(r"/(\d{8})-", link or "")
        if not m:
            return datetime.now().strftime("%Y-%m-%d")
        raw = m.group(1)
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get("https://www.dramx.com/News/", headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        items = soup.select("h3 a")
        news_all = []
        seen = set()

        for a in items:
            href = a.get("href") or "#"
            link = href if href.startswith("http") else f"https://www.dramx.com{href}"
            title = a.get_text(strip=True)
            if not title or link in seen:
                continue
            seen.add(link)
            news_all.append({
                "title": title,
                "link": link,
                "date": parse_date_from_link(link),
            })

        if not news_all:
            fallback = [{"title": "暂无最新新闻", "link": "#", "date": datetime.now().strftime("%Y-%m-%d")}]
            return fallback, fallback

        # 保证“最新”：先按日期降序，截取最新池，再随机抽样用于“换一批”
        news_all = sorted(news_all, key=lambda x: x.get("date", ""), reverse=True)
        latest_pool = news_all[: max(pool_size, display_items)]

        # 首页默认严格展示“最新”的前N条；前端可在最新池内再做“换一批”
        news_display = latest_pool[:display_items]

        return news_display, latest_pool
    except Exception:
        fallback = [{"title": "暂无最新新闻（网络或站点更新中）", "link": "#", "date": datetime.now().strftime("%Y-%m-%d")}]
        return fallback, fallback

news_data, news_pool = get_dramx_news()
print(f"已抓取 {len(news_pool)} 条最新新闻候选，当前展示 {len(news_data)} 条")

# ====================== 行业简介 ======================
def get_industry_intro():
    """从实时网页抓取行业简介，失败时再使用本地兜底。"""

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    def clean_text(text):
        text = re.sub(r"\[[^\]]*\]", "", text or "")
        text = re.sub(r"\s+", " ", text).strip(" \n\t\r。")
        return text

    def normalize_sentence(text, max_len=120):
        text = clean_text(text)
        if len(text) < 24:
            return None
        if len(text) > max_len:
            text = text[:max_len].rstrip("，,；; ") + "..."
        return text + ("" if text.endswith(("。", "！", "？", "...")) else "。")

    def format_intro(lines):
        return [f"{idx + 1}. {line}" for idx, line in enumerate(lines[:3])]

    def collect_from_baike(session):
        r = session.get("https://baike.baidu.com/item/%E5%8D%8A%E5%AF%BC%E4%BD%93", timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        summary = soup.select_one("div.lemma-summary") or soup.select_one("div.J-summary")
        if not summary:
            return []

        items = []
        for p in summary.find_all("p"):
            sentence = normalize_sentence(p.get_text(" ", strip=True))
            if sentence:
                items.append(sentence)
            if len(items) >= 3:
                break
        return items

    def collect_from_wiki_api(session):
        # 使用维基摘要API，结构稳定，适合提取“最新可读简介”
        r = session.get(
            "https://zh.wikipedia.org/api/rest_v1/page/summary/%E5%8D%8A%E5%AF%BC%E4%BD%93",
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        extract = clean_text(data.get("extract", ""))
        if len(extract) < 24:
            return []

        pieces = re.split(r"[。！？]", extract)
        items = [normalize_sentence(p) for p in pieces if normalize_sentence(p)]
        return items[:3]

    def collect_from_wiki_html(session):
        r = session.get("https://zh.wikipedia.org/wiki/%E5%8D%8A%E5%AF%BC%E4%BD%93", timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        content = soup.select_one("div.mw-parser-output")
        if not content:
            return []

        items = []
        for p in content.find_all("p", recursive=False):
            sentence = normalize_sentence(p.get_text(" ", strip=True))
            if sentence and "维基百科" not in sentence:
                items.append(sentence)
            if len(items) >= 3:
                break
        return items

    with requests.Session() as session:
        session.headers.update(headers)

        sources = [
            ("百度百科", collect_from_baike),
            ("Wikipedia API", collect_from_wiki_api),
            ("中文维基网页", collect_from_wiki_html),
        ]

        for source_name, collector in sources:
            try:
                items = collector(session)
                if len(items) >= 3:
                    return format_intro(items), source_name
            except Exception:
                continue

    # 仅在全部网页源失败时使用兜底
    return [
        "1. 半导体是现代电子系统核心基础，材料导电性介于导体与绝缘体之间，广泛用于计算、通信与电力控制。",
        "2. 行业链路可分为上游设备/材料、中游设计与制造、下游封测与应用，技术与资本门槛均较高。",
        "3. 中国半导体正围绕先进制造、关键设备与高端芯片持续投入，重点服务AI、汽车电子与工业数字化。",
    ], "本地兜底"

industry_intro, industry_intro_source = get_industry_intro()

def get_industry_daily_terms():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    def clean_text(text):
        text = re.sub(r"\[[^\]]*\]", "", text or "")
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def split_sentences(text):
        pieces = re.split(r"[。！？]", clean_text(text))
        out = []
        for p in pieces:
            p = p.strip(" \n\t\r，,；;")
            if len(p) < 16:
                continue
            if len(p) > 100:
                p = p[:100].rstrip("，,；; ") + "..."
            out.append(p + ("。" if not p.endswith("...") else ""))
        return out

    scraped_sentences = []
    with requests.Session() as session:
        session.headers.update(headers)
        try:
            resp = session.get("https://zh.wikipedia.org/api/rest_v1/page/summary/%E5%8D%8A%E5%AF%BC%E4%BD%93", timeout=10)
            resp.raise_for_status()
            data = resp.json()
            scraped_sentences.extend(split_sentences(data.get("extract", "")))
        except Exception:
            pass
        try:
            resp = session.get("https://baike.baidu.com/item/%E5%8D%8A%E5%AF%BC%E4%BD%93", timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            summary = soup.select_one("div.lemma-summary") or soup.select_one("div.J-summary")
            if summary:
                for p in summary.find_all("p"):
                    scraped_sentences.extend(split_sentences(p.get_text(" ", strip=True)))
        except Exception:
            pass

    dedup = []
    seen = set()
    for sentence in scraped_sentences:
        if sentence in seen:
            continue
        seen.add(sentence)
        dedup.append(sentence)
        if len(dedup) >= 12:
            break

    if dedup:
        default_pad = [
            "半导体产业链通常拆分为上游设备材料、中游设计制造、下游封测与应用。",
            "先进制程主要服务高性能计算与AI，成熟制程广泛用于车规和工业控制。",
            "封装测试直接影响芯片良率、功耗表现与交付稳定性。",
            "国产替代关注关键设备、材料与核心芯片的本土化能力。",
            "行业景气观察通常结合订单、库存周期、资本开支和终端需求。",
            "估值与波动结合观察可帮助识别潜在风险和机会窗口。"
        ]
        merged = dedup[:]
        for item in default_pad:
            if len(merged) >= 9:
                break
            if item not in merged:
                merged.append(item)
        return [{"term": f"每日术语 {idx + 1}", "desc": text} for idx, text in enumerate(merged[:9])]

    return [
        {"term": "每日术语 1", "desc": "半导体是现代电子系统基础材料，导电性介于绝缘体与导体之间。"},
        {"term": "每日术语 2", "desc": "行业链路分为上游设备材料、中游设计制造、下游封测应用。"},
        {"term": "每日术语 3", "desc": "国产替代聚焦设备、材料与关键芯片能力建设。"},
        {"term": "每日术语 4", "desc": "先进制程偏向高性能计算与AI场景，成熟制程服务工业与车规。"},
        {"term": "每日术语 5", "desc": "封测直接影响芯片良率、稳定性与交付质量。"},
    ]

industry_basics = get_industry_daily_terms()

industry_source_refs = [
    {"name": "百度百科（半导体）", "url": "https://baike.baidu.com/item/%E5%8D%8A%E5%AF%BC%E4%BD%93"},
    {"name": "Wikipedia 摘要 API", "url": "https://zh.wikipedia.org/api/rest_v1/page/summary/%E5%8D%8A%E5%AF%BC%E4%BD%93"},
    {"name": "中文维基页面", "url": "https://zh.wikipedia.org/wiki/%E5%8D%8A%E5%AF%BC%E4%BD%93"},
]

# ====================== 行情数据 ======================
print(f"正在抓取 {total_companies} 家公司实时行情")
spot_df = None
for _ in range(3):
    try:
        spot_df = ak.stock_zh_a_spot_em()
        break
    except Exception:
        time.sleep(2)

def get_yahoo_ticker(code):
    code = str(code).strip()
    if ".HK" in code:
        return code

    clean = code.replace(".HK", "")
    if clean.startswith(("6", "688")):
        return f"{clean}.SS"
    return f"{clean}.SZ"

results = []
for idx, comp in enumerate(company_metadata):
    code = comp["code"]
    print(f"[{idx+1:03d}/{total_companies}] {comp['name']}", end="\r")
    data = None
    if spot_df is not None and ".HK" not in code:
        row = spot_df[spot_df["代码"] == code]
        if not row.empty:
            try:
                data = {
                    "price": float(row["最新价"].iloc[0]),
                    "pe_trailing": round(float(row["市盈率-动态"].iloc[0]), 2) if pd.notna(row["市盈率-动态"].iloc[0]) else "N/A",
                    "pe_forward": "N/A",
                    "volume": int(row["成交量"].iloc[0]),
                    "market_cap": round(float(row["总市值"].iloc[0]) / 100000000, 2),
                    "high52": "N/A",
                    "low52": "N/A",
                    "change_pct": float(row.get("涨跌幅", pd.Series([0])).iloc[0])
                }
            except Exception:
                data = None
    if data is None:
        try:
            info = yf.Ticker(get_yahoo_ticker(code)).info
            data = {
                "price": info.get("currentPrice") or "N/A",
                "pe_trailing": round(float(info.get("trailingPE") or 0), 2) if info.get("trailingPE") else "N/A",
                "pe_forward": round(float(info.get("forwardPE") or 0), 2) if info.get("forwardPE") else "N/A",
                "volume": info.get("volume") or "N/A",
                "market_cap": round((info.get("marketCap") or 0) / 100000000, 2) if info.get("marketCap") else "N/A",
                "high52": info.get("fiftyTwoWeekHigh") or "N/A",
                "low52": info.get("fiftyTwoWeekLow") or "N/A",
                "change_pct": round(float(info.get("regularMarketChangePercent") or 0), 2)
            }
        except Exception:
            data = {
                "price": "N/A",
                "pe_trailing": "N/A",
                "pe_forward": "N/A",
                "volume": "N/A",
                "market_cap": "N/A",
                "high52": "N/A",
                "low52": "N/A",
                "change_pct": 0.0,
            }
    results.append({**comp, **data, "data_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    # Keep a light delay to avoid aggressive upstream throttling.
    time.sleep(0.15)

df = pd.DataFrame(results)
df['market_cap'] = pd.to_numeric(df['market_cap'], errors='coerce')
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['change_pct'] = pd.to_numeric(df['change_pct'], errors='coerce')

def get_board(code):
    if ".HK" in code:
        return "H股"
    if code.startswith("688"):
        return "科创板"
    if code.startswith("300"):
        return "创业板"
    if code.startswith("002"):
        return "中小板"
    return "主板"

df["board"] = df["code"].apply(get_board)

chain_map = {
    "设备": "上游", "材料": "上游", "Fabless": "中游", "IDM": "中游", "晶圆代工": "中游",
    "存储": "中游", "AI芯片": "中游", "CPU": "中游", "封测": "下游", "功率": "下游",
    "模拟": "下游", "传感器": "下游", "RF": "下游", "FPGA": "下游"
}
df['chain_segment'] = df['business_type'].map(chain_map).fillna("其他")
chain_dist = df['chain_segment'].value_counts().to_dict()

# ====================== 投资筛选逻辑（评分模型） ======================
for col in ["pe_trailing", "pe_forward", "volume", "high52", "low52"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

market_cap_p40 = df["market_cap"].quantile(0.40)
market_cap_p70 = df["market_cap"].quantile(0.70)
volume_median = df["volume"].median()

strategic_types = {"设备", "材料", "晶圆代工", "CPU", "AI芯片", "存储", "Fabless", "IDM"}

def score_stock(row):
    score = 0
    reasons = []
    tags = []

    # 1) 规模（流动性和抗风险）
    cap = row.get("market_cap")
    if pd.notna(cap):
        if cap >= market_cap_p70:
            score += 20
            tags.append("龙头规模")
            reasons.append("市值处于样本前30%，抗波动能力较强")
        elif cap >= market_cap_p40:
            score += 12
            reasons.append("市值处于样本中上区间")

    # 2) 估值（优先看 forward PE）
    fpe = row.get("pe_forward")
    tpe = row.get("pe_trailing")
    if pd.notna(fpe) and fpe > 0:
        if fpe <= 30:
            score += 20
            tags.append("估值友好")
            reasons.append("Forward PE处于较低区间")
        elif fpe <= 45:
            score += 12
            reasons.append("Forward PE处于中性区间")
    elif pd.notna(tpe) and tpe > 0:
        if tpe <= 35:
            score += 14
            reasons.append("Trailing PE处于相对合理区间")
        elif tpe <= 55:
            score += 8

    # 3) 短期动量（避免过热）
    change = row.get("change_pct")
    if pd.notna(change):
        if -3 <= change <= 6:
            score += 15
            reasons.append("短期涨跌幅温和，风险收益比相对均衡")
        elif 6 < change <= 12:
            score += 8
            tags.append("强势动量")
            reasons.append("存在强势趋势但需关注回撤")

    # 4) 战略赛道
    btype = row.get("business_type")
    if btype in strategic_types:
        score += 20
        tags.append("战略赛道")
        reasons.append("属于国产替代与高景气相关赛道")

    # 5) 板块偏好
    board = row.get("board")
    if board in {"科创板", "创业板"}:
        score += 8
        tags.append("成长属性")

    # 6) 成交活跃度
    vol = row.get("volume")
    if pd.notna(vol) and pd.notna(volume_median) and vol >= volume_median:
        score += 10
        reasons.append("成交量高于样本中位数，交易活跃")

    # 7) 52周位置（避免高位追涨）
    price = row.get("price")
    high52 = row.get("high52")
    low52 = row.get("low52")
    if pd.notna(price) and pd.notna(high52) and pd.notna(low52) and high52 > low52:
        pos = (high52 - price) / (high52 - low52)
        if 0.2 <= pos <= 0.7:
            score += 7
            reasons.append("股价位于52周区间中段，追高风险相对可控")

    score = max(0, min(100, int(round(score))))
    if score >= 80:
        grade = "A"
    elif score >= 65:
        grade = "B"
    elif score >= 50:
        grade = "C"
    else:
        grade = "D"

    tags = list(dict.fromkeys(tags))
    reason_text = "；".join(reasons[:3]) if reasons else "基础面/估值信息不足，建议结合财报进一步验证"
    is_pick = score >= 70

    return pd.Series({
        "invest_score": score,
        "invest_grade": grade,
        "invest_tags": ",".join(tags) if tags else "观察",
        "invest_reason": reason_text,
        "is_pick": is_pick
    })

df[["invest_score", "invest_grade", "invest_tags", "invest_reason", "is_pick"]] = df.apply(score_stock, axis=1)

# ====================== 生成Excel（唯一数据源） ======================
excel_file = os.path.join(_base_dir, "中国半导体行业报告.xlsx")
with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name="半导体公司数据")

print(f"Excel 已生成（唯一数据源）→ {excel_file}")

# ====================== 从Excel重新读取（保证HTML与Excel 100%一致） ======================
df = pd.read_excel(excel_file)   # 关键：从Excel读取

# Top6 K线（30天）：扩大候选池，尽量稳定凑齐6家公司
candidate_cols = ['code', 'name', 'market_cap', 'business_type', 'chain_segment']
top_candidates = (
    df.dropna(subset=['market_cap'])
      .sort_values('market_cap', ascending=False)
      .head(72)[candidate_cols]
      .to_dict(orient='records')
)

kline_data = {}


def fetch_kline_entry(comp):
    try:
        code_str = str(comp["code"]).strip()
        ticker = yf.Ticker(get_yahoo_ticker(code_str))
        hist = ticker.history(period="30d")
        if hist.empty:
            return None

        hist = hist.dropna(subset=["Open", "High", "Low", "Close"])
        if len(hist) < 10:
            return None

        close_list = hist["Close"].round(2).tolist()
        start_price = float(close_list[0]) if close_list else 0.0
        end_price = float(close_list[-1]) if close_list else 0.0
        change_30d = round(((end_price - start_price) / start_price) * 100, 2) if start_price > 0 else 0.0

        key = f"{comp['name']}（{code_str}）"
        return key, {
            "code": code_str,
            "market_cap": float(comp.get("market_cap") or 0),
            "business_type": comp.get("business_type", "其他"),
            "chain_segment": comp.get("chain_segment", "其他"),
            "date": hist.index.strftime("%Y-%m-%d").tolist(),
            "open": hist["Open"].round(2).tolist(),
            "high": hist["High"].round(2).tolist(),
            "low": hist["Low"].round(2).tolist(),
            "close": close_list,
            "change_30d": change_30d,
        }
    except Exception:
        return None


with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(fetch_kline_entry, comp) for comp in top_candidates]
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if not result:
            continue
        key, payload = result
        if key not in kline_data:
            kline_data[key] = payload

with open(pick_first_existing(_template_path_candidates), encoding="utf-8") as _tpl_file:
    html_template = _tpl_file.read()

template = Template(html_template)

_data_generated_cn = datetime.now(ZoneInfo("Asia/Shanghai"))
data_records = sanitize_for_json(df.to_dict(orient="records"))
safe_news_pool = sanitize_for_json(news_pool)
safe_kline_data = sanitize_for_json(kline_data)

html_content = template.render(
    data=data_records,
    data_time=_data_generated_cn.strftime("%Y-%m-%d %H:%M:%S"),
    data_time_iso=_data_generated_cn.isoformat(),
    news_data=news_data,
    news_pool=safe_news_pool,
    industry_intro=industry_intro,
    industry_basics=industry_basics,
    industry_source_refs=industry_source_refs,
    industry_intro_source=industry_intro_source,
    industry_updated_time=_data_generated_cn.strftime("%Y-%m-%d %H:%M:%S"),
    kline_data=safe_kline_data,
    page_mode="all",
    page_title="中国半导体投资学习课"
)

page_render_specs = [
    ("index.html", "all", "中国半导体投资学习课"),
    ("overview.html", "overview", "模块A｜市场快照 - 中国半导体投资学习课"),
    ("charts.html", "charts", "模块B｜图谱与K线 - 中国半导体投资学习课"),
    ("knowledge.html", "knowledge", "模块C｜知识课堂 - 中国半导体投资学习课"),
    ("risk-news.html", "risk-news", "模块D/E｜风险与新闻 - 中国半导体投资学习课"),
    ("data-center.html", "data-center", "数据中心 - 中国半导体投资学习课"),
]

latest_payload = {
    "data": data_records,
    "news_pool": safe_news_pool,
    "kline_data": safe_kline_data,
    "industry_intro": sanitize_for_json(industry_intro),
    "industry_basics": sanitize_for_json(industry_basics),
    "industry_source_refs": sanitize_for_json(industry_source_refs),
    "industry_intro_source": industry_intro_source,
    "data_time": _data_generated_cn.strftime("%Y-%m-%d %H:%M:%S"),
    "data_time_iso": _data_generated_cn.isoformat(),
}

html_file = os.path.join(_base_dir, "中国半导体行业报告.html")
with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

latest_payload_file = os.path.join(_base_dir, "latest_data.json")
with open(latest_payload_file, "w", encoding="utf-8") as f:
    json.dump(latest_payload, f, ensure_ascii=False, allow_nan=False)

# GitHub Pages 输出（docs/*.html）
docs_html_outputs = []
for file_name, page_mode, page_title in page_render_specs:
    docs_html_content = template.render(
        data=data_records,
        data_time=_data_generated_cn.strftime("%Y-%m-%d %H:%M:%S"),
        data_time_iso=_data_generated_cn.isoformat(),
        news_data=news_data,
        news_pool=safe_news_pool,
        industry_intro=industry_intro,
        industry_basics=industry_basics,
        industry_source_refs=industry_source_refs,
        industry_intro_source=industry_intro_source,
        industry_updated_time=_data_generated_cn.strftime("%Y-%m-%d %H:%M:%S"),
        kline_data=safe_kline_data,
        page_mode=page_mode,
        page_title=page_title,
    )
    docs_html_file = os.path.join(_docs_dir, file_name)
    with open(docs_html_file, "w", encoding="utf-8") as f:
        f.write(docs_html_content)
    docs_html_outputs.append(docs_html_file)

docs_payload_file = os.path.join(_docs_dir, "latest_data.json")
with open(docs_payload_file, "w", encoding="utf-8") as f:
    json.dump(latest_payload, f, ensure_ascii=False, allow_nan=False)

# 前端脚本同步到 docs，确保 GitHub Pages 可直接加载
frontend_js_file = os.path.join(_base_dir, "app.js")
docs_js_file = os.path.join(_docs_dir, "app.js")
if os.path.exists(frontend_js_file):
    shutil.copyfile(frontend_js_file, docs_js_file)

dashboard_js_file = os.path.join(_base_dir, "dashboard.js")
docs_dashboard_js_file = os.path.join(_docs_dir, "dashboard.js")
if os.path.exists(dashboard_js_file):
    shutil.copyfile(dashboard_js_file, docs_dashboard_js_file)

# 样式文件同步到 docs
frontend_css_file = os.path.join(_base_dir, "styles.css")
docs_css_file = os.path.join(_docs_dir, "styles.css")
if os.path.exists(frontend_css_file):
    shutil.copyfile(frontend_css_file, docs_css_file)

# 禁用 Jekyll，确保静态文件按原样发布
nojekyll_file = os.path.join(_docs_dir, ".nojekyll")
with open(nojekyll_file, "w", encoding="utf-8") as f:
    f.write("")

print("\nv5.4 生成完成（GitHub 持续更新）")
print(f"Excel（唯一数据源）→ {excel_file}")
print(f"HTML（完全基于Excel）→ {html_file}")
print(f"GitHub Pages 输出 → {', '.join(docs_html_outputs)}")
print(f"实时刷新数据输出 → {docs_payload_file}")

# 默认在本地打开报告场景下保留产物，其余场景清理根目录本地产物以减少仓库噪音。
ci_mode = os.environ.get("CI", "").lower() == "true"
open_report_enabled = os.environ.get("OPEN_REPORT", "1") == "1"
keep_local_artifacts = os.environ.get("KEEP_LOCAL_ARTIFACTS", "0") == "1" or (not ci_mode and open_report_enabled)
if not keep_local_artifacts:
    for local_file in [excel_file, html_file, latest_payload_file]:
        try:
            if os.path.exists(local_file):
                os.remove(local_file)
        except Exception:
            pass

# CI / workflow 环境默认不弹浏览器，本地可通过 OPEN_REPORT=1 启用自动打开
if not ci_mode and open_report_enabled and keep_local_artifacts:
    webbrowser.open(f"file://{os.path.abspath(html_file)}")