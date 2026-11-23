# CubeSearcher

查詢國泰世華 CUBE 信用卡各權益方案的優惠商家。可以模糊搜尋，結果依回饋率排序，並建議要切換哪個方案。

純靜態網頁，部署在 GitHub Pages；資料由 GitHub Actions 每小時從官網抓一次。

## 運作方式

```
GitHub Actions（每小時）
  └─ scripts/fetch.py ──抓──> 國泰官網 .model.json
        └─ 存到 data/cube.json、data/googler.json（有變動才 commit）
              └─ 和 index.html 一起部署到 GitHub Pages
```

國泰官網沒有開放 CORS，瀏覽器不能直接讀它的資料，所以改成先抓下來，和頁面放在同一個網站。

## 第一次設定

1. 把這個資料夾推到 GitHub（免費帳號需設為 public 才能用 Pages）
2. repo 的 **Settings → Pages → Source** 選 **GitHub Actions**
3. 到 **Actions** 頁面手動執行一次「Update data & deploy」

## 本機預覽

```bash
python3 scripts/fetch.py      # 抓最新資料到 data/
python3 -m http.server 8000   # 打開 http://localhost:8000
```

（直接雙擊 index.html 用 file:// 開啟會讀不到 data/。）

## 檔案

- `index.html`：頁面，資料解析、搜尋、畫面都在這裡
- `scripts/fetch.py`：抓官網資料；某個來源失敗時保留上一次的資料，錯誤記在 `data/meta.json`，頁面會顯示
- `.github/workflows/update.yml`：每小時排程、commit 資料、部署 Pages

## 注意

- Googler 頁的網址含年份（`/segment/2026/`），換年要更新 `scripts/fetch.py` 和 `index.html` 裡的網址。
- GitHub 會在 public repo **60 天沒有任何活動**時自動停用排程。資料有變動時的自動 commit 會算活動；如果被停用，到 Actions 頁面按「Enable workflow」即可。頁面上若資料超過 6 小時沒更新會顯示提醒。
