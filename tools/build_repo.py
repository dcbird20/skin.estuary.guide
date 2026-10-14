#!/usr/bin/env python3
"""Build the Kodi repository under docs/ (served by GitHub Pages).

Run from the repo root:  python3 tools/build_repo.py
Bump the version in addon.xml first; old zips are kept so Kodi can roll back.
"""
import hashlib, os, re, zipfile
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs")
SKIN_ID = "skin.estuary.guide"
REPO_ID = "repository.dcbird20"
EXCLUDE = {".git", "docs", "tools"}


def zip_dir(src_dir, addon_id, version, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, f"{addon_id}-{version}.zip")
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for base, dirs, files in os.walk(src_dir):
            dirs[:] = sorted(d for d in dirs if not (base == src_dir and d in EXCLUDE))
            for f in sorted(files):
                full = os.path.join(base, f)
                rel = os.path.relpath(full, src_dir)
                z.write(full, os.path.join(addon_id, rel))
    return dest


def version_of(addon_xml):
    return ET.parse(addon_xml).getroot().get("version")


def body(addon_xml):
    text = open(addon_xml, encoding="utf-8").read()
    return re.sub(r"^<\?xml[^>]*\?>\s*", "", text).strip()


def listing(dirpath, title):
    items = sorted(n for n in os.listdir(dirpath) if n != "index.html")
    links = "\n".join(f'<a href="{n}{"/" if os.path.isdir(os.path.join(dirpath, n)) else ""}">{n}</a><br>' for n in items)
    with open(os.path.join(dirpath, "index.html"), "w") as f:
        f.write(f"<!doctype html><html><head><meta charset=\"utf-8\"><title>{title}</title></head><body>\n{links}\n</body></html>\n")


repo_src = os.path.join(ROOT, "tools", REPO_ID)
skin_ver = version_of(os.path.join(ROOT, "addon.xml"))
repo_ver = version_of(os.path.join(repo_src, "addon.xml"))

os.makedirs(OUT, exist_ok=True)
zip_dir(ROOT, SKIN_ID, skin_ver, os.path.join(OUT, SKIN_ID))
zip_dir(repo_src, REPO_ID, repo_ver, os.path.join(OUT, REPO_ID))

xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n'
xml += body(os.path.join(ROOT, "addon.xml")) + "\n"
xml += body(os.path.join(repo_src, "addon.xml")) + "\n</addons>\n"
with open(os.path.join(OUT, "addons.xml"), "w", encoding="utf-8") as f:
    f.write(xml)
with open(os.path.join(OUT, "addons.xml.md5"), "w") as f:
    f.write(hashlib.md5(xml.encode("utf-8")).hexdigest())

for d in (OUT, os.path.join(OUT, SKIN_ID), os.path.join(OUT, REPO_ID)):
    listing(d, "Kodi repository")
print("built", SKIN_ID, skin_ver, "and", REPO_ID, repo_ver)
