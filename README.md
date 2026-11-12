# にっぽん津々浦々 ブラックフライデー特集 改修案

先方作成の楽天GOLDページ（`orig/index.html`）に、デザイン層（`src/`）を重ねて作り直したもの。

- `index.html` … 確認用（GitHub Pages。楽天の計測タグなし・noindex）
- `dist/index.html` … 楽天GOLDに上げる納品用（`python -I src/build.py` で生成、リポジトリには含めない）
- `src/redesign.css` … 黒×ピンクゴールドの見た目
- `src/calendar.html` … 10日間タイムライン（期間は %(1日=10%) で配置）
- `src/redesign.js` … FVの紙吹雪・カレンダー・もっと見る・価格の円
- `src/build.py` … 元ページに上の3つを差し込む

楽天ブラックフライデーの開催日時はページに載せない。
