"""SEO/social regression pack for the Periyapuranam reader.

Verifies every search + social-sharing element in
site/periya_puranam_index.html is present, consistent, and backed by a
real file: meta set, canonical, OG/Twitter cards (single-domain),
JSON-LD validity, icons + referenced PWA assets on disk.

    python scripts/check_seo.py

Exit 0 = all green, 1 = failures listed. Same style as check_reader.py.
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
PRODUCT = REPO / "site" / "periya_puranam_index.html"

fails = []
passes = []


def check(name, cond):
    (passes if cond else fails).append(name)


def meta(t, key):
    """Fetch <meta name|property=key content=...> value (first match)."""
    m = re.search(
        r'<meta\s+(?:name|property)="%s"\s+content="([^"]*)"' % re.escape(key),
        t)
    return m.group(1) if m else None


def repo_file(url):
    """Map a local URL (./x, /x, or absolute on our domain) to a repo path."""
    if url.startswith("./"):
        return REPO / "site" / url[2:]
    path = url
    if "://" in url:  # absolute: strip scheme + domain, resolve vs repo
        path = "/" + urlparse(url).path.lstrip("/")
    if path.startswith("/site/"):
        return REPO / path[1:]
    if path.startswith("/"):
        for base in (REPO, REPO / "dist"):
            p = base / path[1:]
            if p.is_file():
                return p
        site_src = REPO / "site" / path[1:]  # e.g. /sw.js served from dist root
        if site_src.is_file():
            return site_src
        return REPO / path[1:]
    return None


def main():
    t = PRODUCT.read_text(encoding="utf-8")

    # 1. Document basics.
    check("doctype first", t.lstrip().lower().startswith("<!doctype html>"))
    m = re.search(r'<html[^>]*\slang="([^"]+)"', t)
    check("html lang set", m is not None and bool(m.group(1)))
    check("charset utf-8", '<meta charset="UTF-8">' in t)
    m = re.search(r'<meta name="viewport" content="([^"]*)"', t)
    check("viewport mobile + safe-area",
          m is not None and "width=device-width" in m.group(1)
          and "viewport-fit=cover" in m.group(1))
    m = re.search(r"<title>([^<]+)</title>", t)
    check("title present (10-120 chars)",
          m is not None and 10 <= len(m.group(1).strip()) <= 120)
    title = m.group(1).strip() if m else ""

    # 2. Core meta set.
    desc = meta(t, "description")
    check("meta description (50-320 chars)",
          desc is not None and 50 <= len(desc) <= 320)
    check("meta keywords (tamil + english terms)",
          (meta(t, "keywords") or "").count(",") >= 5)
    check("meta robots index,follow",
          (meta(t, "robots") or "") == "index, follow")
    check("meta author", bool(meta(t, "author")))
    check("meta theme-color", bool(meta(t, "theme-color")))

    # 3. Canonical + single-domain consistency.
    m = re.search(r'<link rel="canonical" href="([^"]+)"', t)
    canon = m.group(1) if m else ""
    check("canonical absolute https",
          canon.startswith("https://"))
    dom = urlparse(canon).netloc
    urls = {"canonical": canon, "og:url": meta(t, "og:url") or "",
            "og:image": meta(t, "og:image") or "",
            "twitter:image": meta(t, "twitter:image") or ""}
    check("og:url matches canonical", urls["og:url"] == canon)
    check("one domain everywhere",
          all(urlparse(u).netloc == dom for u in urls.values() if u))

    # 4. Open Graph + Twitter cards.
    for key in ["og:type", "og:site_name", "og:title", "og:description",
                "og:url", "og:image", "og:image:alt"]:
        check(f"OG {key}", bool(meta(t, key)))
    check("OG type website", meta(t, "og:type") == "website")
    check("twitter card large image",
          meta(t, "twitter:card") == "summary_large_image")
    for key in ["twitter:title", "twitter:description", "twitter:image"]:
        check(f"Twitter {key}", bool(meta(t, key)))
    check("twitter:image matches og:image",
          meta(t, "twitter:image") == meta(t, "og:image"))
    check("og:title aligns with <title>",
          bool(meta(t, "og:title")) and
          (meta(t, "og:title") in title or title in meta(t, "og:title")))

    # 5. JSON-LD structured data.
    m = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
                  t, re.S)
    try:
        ld = json.loads(m.group(1)) if m else None
    except json.JSONDecodeError:
        ld = None
    check("JSON-LD valid JSON", ld is not None)
    if ld is not None:
        check("JSON-LD WebSite + name/url/lang/author",
              ld.get("@type") == "WebSite" and bool(ld.get("name"))
              and bool(ld.get("url")) and bool(ld.get("inLanguage"))
              and bool(ld.get("author")))
        about = ld.get("about", {})
        check("JSON-LD Book about",
              about.get("@type") == "Book" and bool(about.get("name")))

    # 6. Icons + social image exist on disk and are non-empty.
    m = re.search(r'<link rel="icon"[^>]*href="([^"]+)"', t)
    icon = m.group(1) if m else ""
    p = repo_file(icon) if icon else None
    check("svg favicon file on disk",
          p is not None and p.is_file() and p.stat().st_size > 0)
    m = re.search(r'<link rel="apple-touch-icon" href="([^"]+)"', t)
    touch = m.group(1) if m else ""
    p = repo_file(touch) if touch else None
    check("apple-touch-icon file on disk",
          p is not None and p.is_file() and p.stat().st_size > 0)
    p = repo_file(urls["og:image"]) if urls["og:image"] else None
    check("og:image file on disk",
          p is not None and p.is_file() and p.stat().st_size > 0)

    # 7. Referenced PWA assets exist (offline reader depends on them).
    m = re.search(r'<link rel="manifest" href="([^"]+)"', t)
    man = m.group(1) if m else ""
    p = repo_file(man) if man else None
    check("web manifest file on disk",
          p is not None and p.is_file() and p.stat().st_size > 0)
    sw_refs = re.findall(r"register\('([^']+)'\)", t)
    check("service-worker registration present", bool(sw_refs))
    for ref in sw_refs:
        p = repo_file(ref)
        check(f"service worker {ref} on disk",
              p is not None and p.is_file() and p.stat().st_size > 0)

    # 8. Web manifest content (installability requirements).
    man_path = REPO / "site" / "manifest.webmanifest"
    try:
        man = json.loads(man_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        man = None
    check("manifest valid JSON", man is not None)
    if man is not None:
        check("manifest name + start_url + standalone",
              bool(man.get("name")) and bool(man.get("start_url"))
              and man.get("display") == "standalone")
        sizes = {i.get("sizes") for i in man.get("icons", [])}
        check("manifest 192 + 512 icons", "192x192" in sizes
              and "512x512" in sizes)
        check("manifest maskable icon",
              any(i.get("purpose") == "maskable"
                  for i in man.get("icons", [])))
        for icon in man.get("icons", []):
            p = REPO / "site" / icon.get("src", "")
            check(f"manifest icon {icon.get('src')} on disk",
                  p.is_file() and p.stat().st_size > 0)

    print(f"check_seo: {len(passes)} passed, {len(fails)} failed")
    for f in fails:
        print(f"  FAIL: {f}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
