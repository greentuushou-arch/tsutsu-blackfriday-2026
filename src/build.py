"""元ページ(orig/index.html)にデザイン層を重ねて dist/index.html(納品用)と index.html(確認用)を作る。
python -I src/build.py で実行。元ファイルは書き換えない。"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"


def must_replace(html: str, old: str, new: str, label: str) -> str:
    if html.count(old) != 1:
        sys.exit(f"[build] '{label}' が {html.count(old)} 件見つかりました（1件のはず）")
    return html.replace(old, new)


def main() -> None:
    html = (ROOT / "orig" / "index.html").read_text(encoding="utf-8")
    css = (SRC / "redesign.css").read_text(encoding="utf-8")
    cal = (SRC / "calendar.html").read_text(encoding="utf-8")
    js = (SRC / "redesign.js").read_text(encoding="utf-8")

    fonts = (
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Jost:wght@500;600;700'
        '&family=Noto+Sans+JP:wght@500;700&display=swap" rel="stylesheet">\n'
    )
    html = must_replace(html, "</head>", f"{fonts}<style id=\"bf-redesign\">\n{css}\n</style>\n</head>", "head")
    html = must_replace(html, "<body>", '<body class="bf-rd">', "body")

    # 見出し・文言の変更（11/12 ユーザー指示）
    html = must_replace(
        html,
        '<h2 id="schedule-title" class="event-bubble">当店クーポンは<b>10</b>日間！</h2>',
        '<h2 id="schedule-title" class="event-bubble"><b>10</b>日間カレンダー</h2>',
        "calendar title",
    )
    html = must_replace(html, "<span>初めてご利用のお客様には</span>", "<span>初めてご利用のお客様は</span>", "entry lead")

    # 毎日15時クーポン：日付を「11/20」と「（金）」に分けて横並びの枠にする
    import re as _re0
    html, n = _re0.subn(
        r'<span class="daily-date">(\d+/\d+)（(.)）</span>',
        r'<span class="daily-date"><b>\1</b><small>（\2）</small></span>',
        html,
    )
    if n != 5:
        sys.exit(f"[build] daily-date が {n} 件（5件のはず）")

    # ロゴは透過PNG（生成りの文字＋ピンクのハート）に差し替え
    html = must_replace(
        html,
        '<img class="festival-copy-image" src="image/logo-001.png" alt="">',
        '<img class="festival-copy-image rd-logo" src="image/logo-dai-white.png" alt="にっぽん津々浦々" width="720" height="393">',
        "logo",
    )

    # メインコピー「年に一度のチャンス！ いつもの「好き」を まとめてストック！」はFV看板に一体化
    hero_catch = (
        '<div class="rd-hero-catch"><p class="rd-chance">年に一度のチャンス！</p>'
        '<p class="rd-catch"><span>いつもの「好き」を</span><strong><b>まとめて</b><b>ストック</b></strong></p></div>'
    )
    html = must_replace(
        html,
        "<h1>BLACK<span>FRIDAY</span></h1>",
        "<h1>BLACK<span>FRIDAY</span></h1>\n          " + hero_catch,
        "hero catch",
    )
    # 元の「年に一度のチャンス」枠（BLACK FRIDAY ブラックフライデー特別企画の文字も）は外す。P10倍だけ残す
    html = must_replace(
        html,
        '<p class="unified-promo-eyebrow">BLACK FRIDAY <span aria-hidden="true">｜</span> ブラックフライデー特別企画</p>\n'
        '          <h2 id="unified-benefits-title">年に一度のチャンス！</h2>\n'
        '          <p class="unified-promo-lead">いつもの「好き」を、<wbr>まとめてストック。</p>\n',
        "",
        "unified texts",
    )

    # 初めての方P10倍は「年に一度のチャンス」の枠から出して独立させる
    import re as _re
    entry_re = _re.compile(r'\n\s*<a class="unified-entry".*?</a>', _re.S)
    entry = entry_re.search(html)
    if not entry:
        sys.exit("[build] unified-entry が見つかりません")
    html = html[: entry.start()] + html[entry.end():]
    entry_html = entry.group(0).strip().replace('class="unified-entry"', 'class="rd-entry"', 1)
    # 中身が空になった枠ごと P10倍ブロックに置き換える
    unified_re = _re.compile(r'<section class="lead-benefits unified-benefits"[^>]*>\s*</section>', _re.S)
    if len(unified_re.findall(html)) != 1:
        sys.exit("[build] 空の unified-benefits が見つかりません")
    html = unified_re.sub(lambda _m: entry_html, html)

    # ポイント5倍の商品は黒い期間欄から出して、明るい地に置く
    p5_re = _re.compile(r'\s*<section class="point5-recommendations".*?</section>', _re.S)
    p5 = p5_re.search(html)
    if not p5:
        sys.exit("[build] point5-recommendations が見つかりません")
    html = html[: p5.start()] + html[p5.end():]
    html = must_replace(
        html,
        '\n      <div class="container">\n        <div class="nav-section-surface surface-ivory">\n<section id="coupons"',
        '\n      <div class="container rd-p5">' + p5.group(0).strip() + '</div>'
        '\n      <div class="container">\n        <div class="nav-section-surface surface-ivory">\n<section id="coupons"',
        "point5 move",
    )

    promise = (
        '<div class="rd-promise">'
        '<div class="rd-gold"><small>当店クーポン 最大</small><strong>2,000<i>円OFF</i></strong></div>'
        '<div class="rd-pink"><small>新規の方はエントリーで</small><strong>P10<i>倍</i></strong></div>'
        "</div>"
    )
    html = must_replace(
        html,
        '23:59</p>\n        </div>\n        <div class="hero-product-marquee"',
        f'23:59</p>\n          {promise}\n        </div>\n        <div class="hero-product-marquee"',
        "hero promise",
    )
    # 元の期間表は楽天BFの日時を含むため丸ごと外し、10日間カレンダーに置き換える
    import re as _re
    table_re = _re.compile(
        r'<h3 class="timeline-table-title".*?</h3>\s*<div class="timeline-table-scroll".*?</table>\s*</div>', _re.S
    )
    if len(table_re.findall(html)) != 1:
        sys.exit("[build] 期間表が見つかりません")
    html = table_re.sub(lambda _m: cal, html)

    # 楽天BFの日時を書かない（CSSコメント内も）
    html = must_replace(html, "終了表示は前分の23:59/01:59。", "終了表示は前分の23:59。", "comment 1")
    html = must_replace(html, "当店18日0時〜27日末、楽天市場19日20時〜25日1:59。", "当店18日0時〜27日末。", "comment 2")
    html = html.replace("当店クーポンと楽天市場の開催期間", "当店クーポンの開催期間")

    daily_head = (
        '<div class="rd-daily-head rd-shine"><div><small>5,900円以上の</small><small>お買い物で</small>'
        "<small>各日15:00〜 先着20件</small></div><strong>500<i>円OFF</i></strong></div>"
    )
    html = must_replace(
        html,
        '<p class="daily-coupon-intro">11/20（金）〜24（火）</p>',
        '<p class="daily-coupon-intro">11/20（金）〜24（火）</p>\n          ' + daily_head,
        "daily head",
    )
    pokkiri_head = 'id="pokkiri-title">買いまわりのあと一品に！1,000円ポッキリ</h2></header>'
    html = must_replace(
        html,
        pokkiri_head,
        pokkiri_head + '\n            <p class="rd-pokkiri-big"><span>全品</span><b>1,000</b><span>円ポッキリ</span><em>すべて送料無料</em></p>',
        "pokkiri big",
    )
    html = html.replace("人気商品をチェック🔍", "人気商品をチェック")

    rat = '<script type="text/javascript" src="https://r.r10s.jp/com/js/d/pa/pa3.min.js"'
    html = must_replace(html, rat, js + rat, "redesign js")

    # 納品用（楽天GOLDにアップするもの）：dist/index.html
    (ROOT / "dist").mkdir(exist_ok=True)
    (ROOT / "dist" / "index.html").write_text(html, encoding="utf-8")

    # 確認用（GitHub Pages / ローカル）：楽天の計測タグを外し noindex を付けたもの
    import re
    preview = re.sub(r'<script type="text/javascript" src="https://r\.r10s\.jp[^>]*></script>', "", html)
    preview = re.sub(r'<script type="text/template" name="rat"[^>]*></script>\s*', "", preview)
    preview = preview.replace(
        "<head>",
        '<head>\n<meta name="robots" content="noindex, nofollow, noarchive">'
        '\n<meta name="googlebot" content="noindex, nofollow">',
        1,
    )
    # デモ表示（納品用には入れない）
    preview = preview.replace(
        '<body class="bf-rd">',
        '<body class="bf-rd">\n<p class="rd-demo">デモページです。</p>',
        1,
    )
    (ROOT / "index.html").write_text(preview, encoding="utf-8")
    (ROOT / "preview.html").write_text(preview, encoding="utf-8")
    print("[build] dist/index.html（納品用）/ index.html（確認用）を作成しました")


if __name__ == "__main__":
    main()


def build_artifact() -> None:
    """Claude Artifact 共有用：doctype/head/body の外枠を外した版"""
    import re
    html = (ROOT / "preview.html").read_text(encoding="utf-8")
    head = re.search(r"<head>(.*?)</head>", html, re.S).group(1)
    head = re.sub(r'<meta[^>]*(charset|viewport)[^>]*>', "", head)
    head = re.sub(r'<script type="text/template"[^>]*></script>', "", head)
    body = re.search(r'<body class="bf-rd">(.*)</body>', html, re.S).group(1)
    out = head + '\n<script>document.body.classList.add("bf-rd")</script>\n' + body
    out = out.replace(
        "<title>BLACK FRIDAY｜BLACK × GOLD｜にっぽん津々浦々</title>",
        '<title>津々浦々 BF特集 改修案</title>',
    )
    # 楽天の画像はArtifactでは読めないので ext/ のコピーに差し替え（map.tsv）
    map_file = ROOT / "map.tsv"
    if map_file.exists():
        for line in map_file.read_text(encoding="utf-8").splitlines():
            url, local = line.split("\t")
            out = out.replace(url, local)
    (ROOT / "artifact.html").write_text(out, encoding="utf-8")
    print("[build] artifact.html")


build_artifact()
