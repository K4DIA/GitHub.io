#!/usr/bin/env python3
"""Regenerate sitemap.xml and robots.txt for k4dia.com.

Walks every .html file in the repository, skips the ones that should not be
indexed, and writes the sitemap with each page's last commit date. Run it
after adding or removing pages:

    python3 build-sitemap.py
"""
import os, re, subprocess, datetime

BASE = "https://k4dia.com"
SKIP_FILES = {"404.html"}
SKIP_DIRS = {".git", "fonts", "brand"}

def url_for(path):
    if path == "index.html":
        return BASE + "/"
    if path.endswith("/index.html"):
        return BASE + "/" + path[:-len("index.html")]
    return BASE + "/" + path

def lastmod(path):
    """Date of the file's last commit. Anything edited since then counts as today,
    so the sitemap is honest whether it is regenerated before or after a commit."""
    try:
        dirty = subprocess.run(["git", "diff", "--quiet", "--", path],
                               capture_output=True, timeout=10).returncode != 0
        if dirty:
            return datetime.date.today().isoformat()
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", path],
                             capture_output=True, text=True, timeout=10).stdout.strip()
        if out:
            return out
    except Exception:
        pass
    return datetime.date.today().isoformat()

def priority(path):
    if path == "index.html":            return "1.0"
    if path == "learn/index.html":      return "0.9"
    if re.match(r"learn/hub-", path):   return "0.8"
    if path.endswith("/index.html"):    return "0.7"
    return "0.6"

pages = []
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
    for f in sorted(files):
        if not f.endswith(".html") or f in SKIP_FILES:
            continue
        rel = os.path.normpath(os.path.join(root, f)).replace(os.sep, "/")
        if rel.startswith("./"):
            rel = rel[2:]
        pages.append(rel)
pages.sort()

lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for p in pages:
    lines += ["  <url>",
              f"    <loc>{url_for(p)}</loc>",
              f"    <lastmod>{lastmod(p)}</lastmod>",
              f"    <priority>{priority(p)}</priority>",
              "  </url>"]
lines.append("</urlset>")
open("sitemap.xml", "w", encoding="utf-8").write("\n".join(lines) + "\n")

open("robots.txt", "w", encoding="utf-8").write(
    "User-agent: *\n"
    "Allow: /\n"
    "\n"
    f"Sitemap: {BASE}/sitemap.xml\n")

print(f"sitemap.xml: {len(pages)} pages")
print("robots.txt: written")
