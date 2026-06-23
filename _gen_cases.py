#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批次生成接案作品案子頁。資料來源：images/work/<dir>/
版型：右欄頂端 banner → 兩段亮點文字 → 各區塊（標題＋一行說明）。"""
import os, re, glob
from urllib.parse import quote
from PIL import Image as PILImage

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(ROOT, "images", "work")
VER = "20260623a"

def natkey(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]

IMG_EXT = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.mp4')
def list_imgs(folder):
    out = []
    for f in os.listdir(folder):
        if f.startswith('.') or f.lower().startswith('cover'):
            continue
        if not f.lower().endswith(IMG_EXT):  # 排除 .ai／.mov 等非網頁圖檔
            continue
        out.append(f)
    return sorted(out, key=natkey)

def subdirs(folder):
    return [d for d in os.listdir(folder)
            if os.path.isdir(os.path.join(folder, d)) and not d.startswith('.')]

def src(d, *parts):
    rel = "/".join(["./images/work", d] + list(parts))
    return quote(rel, safe="/.")

def is_wide(d, *parts, ratio=1.5):
    """寬圖（橫式）→ 在磚牆中橫跨整排"""
    p = os.path.join(WORK, d, *parts)
    try:
        w, h = PILImage.open(p).size
        return (w / h) >= ratio
    except Exception:
        return False

def img(d, *parts):
    cls = ' class="wide"' if is_wide(d, *parts) else ''
    return f'<img loading="lazy"{cls} src="{src(d, *parts)}" alt="">'

def hero(d, files, sub=None):
    inner = "\n".join("    " + img(d, *([sub, f] if sub else [f])) for f in files)
    return f'<div class="proj-hero">\n{inner}\n  </div>'

def gallery(d, files, sub=None, seam=False):
    cls = "proj-gallery proj-gallery--seam" if seam else "proj-gallery"
    inner = "\n".join("    " + img(d, *([sub, f] if sub else [f])) for f in files)
    return f'<div class="{cls}">\n{inner}\n  </div>'

def grid(d, files, sub=None):
    inner = "\n".join("    " + img(d, *([sub, f] if sub else [f])) for f in files)
    return f'<div class="proj-grid2">\n{inner}\n  </div>'

def lp_grid(d, files, sub=None):
    """募資頁：左右兩欄磚牆（左高右低）＋白底"""
    inner = "\n".join("    " + img(d, *([sub, f] if sub else [f])) for f in files)
    return f'<div class="proj-lp">\n{inner}\n  </div>'

def video_tag(d, f):
    return f'<div class="proj-video"><video controls preload="metadata" src="{src(d, f)}"></video></div>'

def section(label, desc, body):
    p = f'<p class="proj-sec-desc">{desc}</p>' if desc else ''
    return f'<div class="proj-text"><h2>{label}</h2>{p}</div>\n  {body}'

def lead_block(p1, p2):
    return f'<div class="proj-lead"><p>{p1}</p><p>{p2}</p></div>'

# 子資料夾 → 標籤 / 版型 / 說明（banner 另外拉到 hero）
LABELS = {'廣告': '廣告素材', 'lp': '募資頁 Landing Page',
          '貼文': '社群貼文', '貼文2': '社群貼文', '體驗卷': '體驗券'}
LAYOUT = {'廣告': 'grid', 'lp': 'seam', '貼文': 'grid', '貼文2': 'grid', '體驗卷': 'grid'}
SEC_DESC = {
    '廣告': '因應預熱、開跑、倒數等不同檔期節點，延伸多版位廣告素材，維持整檔的聲量與調性一致。',
    'lp': '完整的募資長頁，從使用痛點、產品賣點到信任背書，一路鋪陳引導到下單。',
    '貼文': '延續品牌語氣與視覺風格的社群經營貼文。',
    '貼文2': '',
    '體驗卷': '線下通路使用的體驗券設計。',
}
SEC_ORDER = ['廣告', 'lp', '貼文', '貼文2', '體驗卷']

def norm(s):
    s = s.lower()
    if s == 'banner':
        return 'banner'
    return s if s in LABELS else None

def build_auto(d):
    """回傳 (hero_html, sections_html)"""
    folder = os.path.join(WORK, d)
    subs = {norm(s): s for s in subdirs(folder) if norm(s)}
    hero_html = ''
    if 'banner' in subs:
        bfiles = list_imgs(os.path.join(folder, subs['banner']))
        if bfiles:
            hero_html = hero(d, bfiles, subs['banner'])
    secs = []
    for key in SEC_ORDER:
        if key not in subs:
            continue
        files = list_imgs(os.path.join(folder, subs[key]))
        if not files:
            continue
        if LAYOUT[key] == 'seam':
            body = lp_grid(d, files, subs[key])
        else:
            body = grid(d, files, subs[key])
        secs.append(section(LABELS[key], SEC_DESC.get(key, ''), body))
    return hero_html, "\n\n  ".join(secs)

PAGE = '''<!DOCTYPE html>
<html lang="zh-Hant-TW">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{desc}" />
    <link rel="shortcut icon" href="./images/index/link.png">

    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{desc}" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="https://vera-design3.github.io/{out}" />
    <meta property="og:image" content="https://vera-design3.github.io/{ogimg}" />
    <link href="./images/index/apple.png" rel="apple-touch-icon" />

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Noto+Sans+TC:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="./css/style-new.css?v={VER}">
    <script src="./js/layout-new.js?v={VER}"></script>
</head>

<body>
    <main class="wrap project">
        <div class="proj-layout">
            <aside class="proj-side">
                <p class="eyebrow">{eyebrow}</p>
                <h1>{h1}</h1>
                <p class="proj-intro">{intro}</p>
                <div class="proj-side-meta">
                    <div><span>Date</span><p>{date}</p></div>
                    <div><span>Client</span><p>{client}</p></div>
                    <div><span>Role</span><p>{role}</p></div>
                    <div><span>Type</span><p>{type_label}</p></div>
                </div>
            </aside>

            <div class="proj-main">
  {herohtml}
  {leadhtml}

  {main}
            </div>
        </div>

        <nav class="proj-nav">
            <a href="{prev}"><span>Previous</span>{prev_t}</a>
            <a class="next" href="{next}"><span>Next project</span>{next_t} →</a>
        </nav>
    </main>
</body>

</html>
'''

def cover_path(d):
    cs = sorted(glob.glob(os.path.join(WORK, d, "cover*")))
    return src(d, os.path.basename(cs[0]))[2:] if cs else f"images/work/{d}/"

CAMP_ROLE = "設計"
PROD_ROLE = "企劃 ＆ 設計"
CASES = []

# ---------- A. 活動類型（MARAIS，flat） ----------
def flat_marais(d, out, title_zh, date, intro, p1, p2, video=False):
    files = list_imgs(os.path.join(WORK, d))
    banners = [f for f in files if 'banner' in f.lower()]
    ads = [f for f in files if ('廣告' in f or f.lower().endswith('.gif')) and not f.lower().endswith('.mp4')]
    vids = [f for f in files if f.lower().endswith('.mp4')]
    hero_html = hero(d, banners) if banners else ''
    secs = []
    if ads:
        secs.append(section('廣告素材', '延伸到社群的多版位廣告，搭配檔期節奏投放。', gallery(d, ads)))
    if video and vids:
        secs.append(section('活動影片', '動態廣告，強化檔期的節奏與渲染力。',
                            "\n  ".join(video_tag(d, f) for f in vids)))
    return dict(d=d, out=out, eyebrow="Campaign",
                title=f"{title_zh}｜MARAIS 活動視覺 | Vera", h1=title_zh,
                desc=intro, intro=intro, lead=lead_block(p1, p2), date=date, client="MARAIS",
                role=CAMP_ROLE, type_label="活動視覺", hero=hero_html,
                main="\n\n  ".join(secs))

CASES.append(flat_marais("marais-618", "project-marais-618.html", "MARAIS 618 理想生活提案", "2026.04",
    "以「理想生活」為題的 618 年中慶檔期，從主視覺、官網 banner 到社群廣告，營造溫暖的居家提案氛圍。",
    "618 年中慶是電商一年裡最關鍵的檔期之一。這次以「理想生活」為主軸，用溫暖的復古插畫把居家情境視覺化，讓促購訊息不只是折扣數字，而是一種生活提案。",
    "整檔視覺從主視覺定調，延伸到官網 banner 與系列社群廣告，確保不同版位之間的風格、色調與訊息層級維持一致，讓整檔的視覺體驗從第一眼到結帳都連貫。"))
CASES.append(flat_marais("marais-summer", "project-marais-summer.html", "MARAIS 夏日生活節", "2026.05",
    "MARAIS 夏日生活節檔期視覺，以清爽色調帶出季節感，延伸多種版位素材。",
    "夏日生活節主打季節感與輕鬆氛圍。以清爽的色調與插畫風格重新包裝檔期，讓品牌在夏季維持鮮明而一致的視覺記憶。",
    "從主視覺 KV 出發，延伸成官網與社群的多種版位素材，讓夏季檔期在各個觸點都有統一而清爽的視覺印象，也方便行銷團隊快速套用。"))
CASES.append(flat_marais("queen-day", "project-queen-day.html", "MARAIS 38 購物女王節", "2024.03",
    "38 購物女王節檔期，以「姐的時代」為訴求描繪自信女性形象，產出多尺寸 banner 與動態廣告。",
    "38 女王節以「姐的時代」為核心，把女性的自信與態度放到主視覺中央，讓檔期不只是促購，更傳遞品牌想對女性說的話。",
    "除了製作 web 與 mobile 多尺寸的 banner，也設計了動態廣告，用節奏感強化檔期在社群上的曝光與點擊。", video=True))
CASES.append(flat_marais("newyear", "project-newyear.html", "MARAIS 團圓年菜大賞", "2024.12",
    "農曆春節「團圓年菜大賞」檔期主視覺，以豐盛年菜傳達團圓圍爐的氛圍。",
    "農曆春節是食品電商的兵家必爭之地。「團圓年菜大賞」以豐盛的年菜插畫傳達圍爐團圓的溫度，把「買年菜」的功能訴求包裝成有情感、有記憶點的節慶主視覺。",
    "從主視覺延伸到各版位的促購素材，在傳遞節慶溫度的同時，也讓年菜的賣點與優惠訊息清楚易讀，兼顧氛圍與轉換。"))

# MARS（flat，全廣告，無 banner；依檔名數字分三類）
mars_files = list_imgs(os.path.join(WORK, "mars"))
def mars_grp(*prefixes):
    return [f for f in mars_files if any(f.startswith(p) for p in prefixes)]
mars_main = "\n\n  ".join([
    section('乳清蛋白・牛奶系列', '水解乳清蛋白牛奶系列，從各口味款到系列主視覺，建立一致的產品識別。',
            grid("mars", mars_grp('廣告1', '廣告2'))),
    section('米蛋白・植物蛋白飲', '全台首創的素食米蛋白，訴求 100% 純素、無麩質與低過敏性。',
            grid("mars", mars_grp('廣告3'))),
    section('乳清蛋白・品牌形象', '以生活情境與品牌語氣切入的形象廣告，強化「為人生加點蛋白」的訴求。',
            grid("mars", mars_grp('廣告4', '廣告5'))),
])
CASES.append(dict(d="mars", out="project-mars.html", eyebrow="Social",
    title="MARS 高蛋白粉 社群廣告 | Vera", h1="MARS 高蛋白粉",
    desc="MARS 高蛋白粉的社群圖文與限動廣告設計。",
    intro="MARS 高蛋白粉的社群圖文與限時動態廣告，橫跨乳清蛋白、米蛋白等產品線，從產品賣點切入帶動轉換。",
    lead=lead_block(
        "高蛋白粉的市場競爭激烈，視覺要在三秒內讓人記住賣點。MARS 的社群圖文與限動廣告從「為什麼選這款」切入，用清楚的版面層級與一致的品牌調性，把產品優勢轉化成好懂、好分享的素材。",
        "橫跨乳清蛋白牛奶系列、素食米蛋白到品牌形象廣告，針對不同產品線與訴求設計系列素材，統一品牌的版面語言與色彩系統，讓每一張廣告都能被快速辨識，也方便延展到更多版位。"),
    date="2024–2025", client="MARS", role=PROD_ROLE, type_label="社群廣告",
    hero='', main=mars_main))

# gym mars（子資料夾，無 banner）
gym_hero, gym_secs = build_auto("gym-mars")
CASES.append(dict(d="gym-mars", out="project-gym-mars.html", eyebrow="Social",
    title="gym mars 健身房 社群行銷 | Vera", h1="gym mars 健身房",
    desc="gym mars 健身房的社群行銷素材設計。",
    intro="gym mars 健身房的長期包月合作，每月固定產出教練課、體驗券、社群貼文等多元素材，橫跨大直店與核心基地。",
    lead=lead_block(
        "gym mars 是長期合作的包月客戶。從教練課招生、體驗券到社群貼文，每月固定產出多種類型的行銷素材，橫跨大直店與核心基地兩個據點，需求多元、節奏緊湊。",
        "長期合作最大的好處，是設計能穩定維持品牌的調性與視覺一致性；也因為彼此熟悉、默契到位，省去每次重新說明品牌背景的來回溝通，讓每一檔都能更快、更順地交付，合作起來格外愉快。"),
    date="2024.08–2025.08", client="gym mars", role=PROD_ROLE, type_label="社群廣告",
    hero=gym_hero, main=gym_secs))

# Legin 皮拉提斯（flat，無 banner；方圖並排、橫式獨立在下）
legin_files = list_imgs(os.path.join(WORK, "legin 皮拉提斯"))
legin_ordered = ([f for f in legin_files if not is_wide("legin 皮拉提斯", f)]
                 + [f for f in legin_files if is_wide("legin 皮拉提斯", f)])
CASES.append(dict(d="legin 皮拉提斯", out="project-legin.html", eyebrow="Social",
    title="Legin 皮拉提斯 社群廣告 | Vera", h1="Legin 皮拉提斯",
    desc="Legin 皮拉提斯的社群廣告與招生視覺設計。",
    intro="Legin 皮拉提斯的社群廣告與招生視覺，以乾淨俐落的版面、沉穩的色調，傳達課程的專業與身體的優雅。",
    lead=lead_block(
        "皮拉提斯賣的不只是課程，而是一種對身體的講究。Legin 的社群廣告從這個核心出發，用大量留白、俐落的線條與沉穩的色調，把「精準、優雅、專業」的品牌氣質視覺化，吸引重視生活品質的客群。",
        "從體態雕塑的課程主視覺，到教練招募的形象廣告，每一張都維持一致的版面語言與調性；即使素材精煉，也讓品牌在競爭激烈的健身與身心市場中，建立起辨識度高、質感統一的形象。"),
    date="2024.08–2025.08", client="Legin", role=PROD_ROLE, type_label="社群廣告",
    hero='', main=section('廣告素材', '涵蓋課程招生、體態雕塑與教練招募的系列社群廣告，以一致的視覺語言維持品牌調性。',
                          gallery("legin 皮拉提斯", legin_ordered))))

# ---------- B. 產品上線（群眾集資，子資料夾，banner→hero） ----------
def prod(d, out, title_zh, client, date, intro, p1, p2):
    h, s = build_auto(d)
    return dict(d=d, out=out, eyebrow="Crowdfunding",
        title=f"{title_zh} | Vera", h1=title_zh, desc=intro, intro=intro,
        lead=lead_block(p1, p2),
        date=date, client=client, role=PROD_ROLE, type_label="群眾集資",
        hero=h, main=s)

CASES.append(prod("belkin", "project-belkin.html", "Belkin SOUNDFORM Immerse 降噪耳機",
    "Belkin", "2022",
    "Belkin SOUNDFORM Immerse 主動降噪耳機的群眾集資專案，從募資頁、廣告素材到社群經營，將「聲音」做視覺化呈現。",
    "群眾集資的成敗，往往在募資頁的第一屏就決定了。Belkin SOUNDFORM Immerse 主動降噪耳機的專案，從「聲音視覺化」的概念出發，把抽象的降噪與音質做成看得見的設計語言。",
    "企劃與設計一手包辦，從募資頁的架構鋪陳、廣告素材到社群經營，從預熱、開跑到封館倒數，把產品優勢轉化成有節奏、有記憶點的集資內容。"))
CASES.append(prod("sharp-hairdryer", "project-sharp-hairdryer.html", "SHARP 雙氣流智慧吹風機",
    "SHARP", "2021",
    "SHARP 雙氣流智慧吹風機 IB-WX1T 群眾集資專案，以「以水護髮」為核心訴求，規劃募資頁與全套廣告素材。",
    "「以水護髮」是 SHARP 雙氣流智慧吹風機 IB-WX1T 的核心訴求。專案從這個情感切點延伸，把「科技」與「溫柔護髮」兩個看似衝突的概念，整合成有說服力的產品故事。",
    "從募資頁到全套廣告素材，圍繞核心訴求一路鋪陳，把技術規格翻譯成消費者能感受到的好處與使用情境。"))
CASES.append(prod("sharp-allday", "project-sharp-allday.html", "SHARP all day",
    "SHARP", "2021–2022",
    "SHARP all day 系列群眾集資專案，從產品生活情境出發，產出募資頁與社群廣告素材。",
    "SHARP all day 系列訴求的是一整天的生活陪伴。視覺從真實的生活情境出發，用溫暖自然的調性，讓家電不只是功能，而是日常的一部分。",
    "以生活情境貫穿募資頁與社群廣告，讓產品的功能訴求融入日常畫面，拉近與消費者的距離、也強化品牌的溫度。"))
CASES.append(prod("niconico-skewer", "project-niconico-skewer.html", "NICONICO 旋轉吧！串串",
    "NICONICO", "2021–2023",
    "NICONICO 旋轉吧！串串（電烤串烤機）群眾集資專案，募資頁與系列廣告素材設計。",
    "NICONICO 旋轉吧！串串把「在家也能輕鬆烤串」的樂趣視覺化，讓產品的使用情境一看就懂、也讓人想擁有。",
    "募資頁從使用情境、產品特色到優惠方案層層鋪陳，搭配一系列倒數與開跑廣告，維持整個集資期間的聲量與節奏。"))
CASES.append(prod("niconico-snack", "project-niconico-snack.html", "NICONICO 小食曆",
    "NICONICO", "2021–2023",
    "NICONICO 小食曆 掀蓋式火烤兩用爐的群眾集資專案，募資頁與系列廣告素材設計。",
    "NICONICO 小食曆掀蓋式火烤兩用爐，主打一機多用的生活想像。以「一日三餐、一年四季」的生活敘事貫穿整個專案。",
    "從募資頁延伸出系列廣告，把一機多用的特色變成能想像的日常場景，讓規格說明變成有畫面、有溫度的生活提案。"))
CASES.append(prod("baby", "project-baby.html", "寶寶吹風機",
    "BLAUPUNKT", "2021–2023",
    "寶寶吹風機群眾集資專案，以安全與安心訴求設計募資頁與系列廣告素材。",
    "寶寶吹風機主打的是「安心」。專案以柔和的色調與清楚的安全訴求，讓家長一眼就能感受到品牌的用心與專業。",
    "從預熱、開跑到倒數，設計完整的募資頁與系列廣告，以一致的視覺語言與清楚的安全訴求，建立家長對品牌的信任感。"))
CASES.append(prod("FURIMORI 咖啡機", "project-furimori.html", "FURIMORI 咖啡機",
    "FURIMORI", "2022",
    "FURIMORI 咖啡機的群眾集資專案，募資頁與系列廣告素材設計。",
    "咖啡機要打動的，是「在家也能喝杯好咖啡」的渴望。FURIMORI 的群眾集資從生活情境切入，把產品的便利與儀式感視覺化，讓人一看就想擁有。",
    "從募資頁到系列廣告，圍繞核心訴求一路鋪陳；從預熱、開跑到好評延長，維持整個集資期間的聲量與節奏。"))

# ---------- 導覽鏈（對齊首頁排序；含沿用的 PHILIPS 與 UI/UX 兩頁） ----------
NAV = [
    ("project-gym-mars.html", "gym mars 健身房"),
    ("project-mars.html", "MARS 高蛋白粉"),
    ("project-legin.html", "Legin 皮拉提斯"),
    ("project-marais-618.html", "MARAIS 618"),
    ("project-newyear.html", "團圓年菜大賞"),
    ("project-PHILIPS.html", "PHILIPS 白小奈"),
    ("project-sharp-hairdryer.html", "SHARP 雙氣流吹風機"),
    ("project-belkin.html", "Belkin Immerse"),
    ("project-sharp-allday.html", "SHARP all day"),
    ("project-niconico-snack.html", "NICONICO 小食曆"),
    ("project-niconico-skewer.html", "NICONICO 旋轉吧！串串"),
    ("project-baby.html", "寶寶吹風機"),
    ("project-furimori.html", "FURIMORI 咖啡機"),
    ("project-queen-day.html", "38 購物女王節"),
    ("project-marais-summer.html", "MARAIS 夏日生活節"),
    ("project-MYFEEL%20UIUX.html", "MYFEEL 集資平台"),
    ("project-zangan.html", "蘵感美學補習班"),
]
navidx = {out: i for i, (out, _) in enumerate(NAV)}

for c in CASES:
    i = navidx[c['out']]
    prev = NAV[i-1] if i > 0 else ("index.html", "所有作品")
    nxt = NAV[i+1] if i < len(NAV)-1 else ("index.html", "所有作品")
    html = PAGE.format(
        title=c['title'], desc=c['desc'], out=c['out'], ogimg=cover_path(c['d']),
        eyebrow=c['eyebrow'], h1=c['h1'], intro=c['intro'], leadhtml=c['lead'], date=c['date'],
        client=c['client'], role=c['role'], type_label=c['type_label'],
        herohtml=c['hero'], main=c['main'], prev=f"./{prev[0]}", prev_t=prev[1],
        next=f"./{nxt[0]}", next_t=nxt[1], VER=VER)
    with open(os.path.join(ROOT, c['out']), "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", c['out'])

print("done:", len(CASES), "pages")
