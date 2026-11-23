#!/usr/bin/env python3
"""抓國泰 CUBE 權益資料，存到 data/。

由 GitHub Actions 每小時執行（.github/workflows/update.yml），也可以在本機手動跑：
  python3 scripts/fetch.py

某個來源抓失敗時會保留上一次的檔案，並把錯誤記在 data/meta.json，頁面會顯示出來。
全部失敗才回傳非 0，讓 Actions 標示為失敗。
"""
import json
import pathlib
import sys
import urllib.request
from datetime import datetime, timezone

BASE = "https://www.cathay-cube.com.tw/content/cub-aem-cs/zh-tw/cathaybk/personal"
SOURCES = {
    # key: (網址, 用來確認內容沒走樣的關鍵字)
    "cube": (BASE + "/product/credit-card/cards/cube-list.model.json", "cub-cubelisttitle"),
    "googler": (BASE + "/event/overview/segment/2026/googler_package.model.json", "權益方案"),
}
DATA = pathlib.Path(__file__).resolve().parent.parent / "data"


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; CubeSearcher/1.0)",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def main():
    DATA.mkdir(exist_ok=True)
    meta = {"fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "sources": {}}
    ok = 0
    for key, (url, marker) in SOURCES.items():
        try:
            text = fetch(url)
            data = json.loads(text)  # 不是 JSON（例如被擋時的 HTML 頁）就會失敗
            if marker not in text:
                raise ValueError(f"內容裡找不到「{marker}」，網頁版型可能改了")
            # 排版後存檔，git diff 比較好讀
            out = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
            (DATA / f"{key}.json").write_text(out, encoding="utf-8")
            meta["sources"][key] = {"url": url, "ok": True}
            ok += 1
            print(f"[ok]   {key}: {len(out):,} bytes")
        except Exception as e:
            meta["sources"][key] = {"url": url, "ok": False, "error": f"{type(e).__name__}: {e}"}
            print(f"[fail] {key}: {type(e).__name__}: {e}", file=sys.stderr)
    (DATA / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
