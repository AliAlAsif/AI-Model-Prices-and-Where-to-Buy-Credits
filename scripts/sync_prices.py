#!/usr/bin/env python3
"""Sync model prices and context sizes in index.html from OpenRouter's public catalog.

OpenRouter passes provider list prices through without markup and needs no API key:
    GET https://openrouter.ai/api/v1/models   (pricing.prompt / pricing.completion are USD per token)

How it works
- index.html holds its data in <script type="application/json" id="data">.
- A model with an "or" list (candidate OpenRouter IDs) is AUTO: the first candidate found in the
  catalog is used, its prices (per 1M tokens) and context size are written back, and "oid" records
  the match. A model with no "or" list, or no match, stays MANUAL and is never touched.
- Safety: a price that would move by more than 4x either way is NOT applied (it is reported),
  and the run fails if the catalog looks broken. Standard library only.
"""
import datetime
import difflib
import json
import os
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "index.html"
API = "https://openrouter.ai/api/v1/models"
BLOCK = re.compile(r'(<script type="application/json" id="data">)(.*?)(</script>)', re.S)
MAX_RATIO = 4.0      # refuse to apply a price change bigger than this factor (either direction)
HEARTBEAT_DAYS = 7   # bump "synced" at least this often, even if nothing changed


def fetch_catalog():
    req = urllib.request.Request(API, headers={"User-Agent": "price-sync (GitHub Actions)"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))["data"]


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def strip_date(s):
    return re.sub(r"[-_.]?(\d{4}-\d{2}-\d{2}|\d{8}|\d{6}|\d{4})$", "", s)


def build_index(catalog):
    ids = {m["id"]: m for m in catalog if ":" not in m["id"]}  # skip :batch, :free, :thinking variants
    exact = {norm(i): i for i in ids}
    loose = {}
    for i in ids:
        loose.setdefault(norm(strip_date(i)), []).append(i)
    return ids, exact, loose


def find(cands, exact, loose):
    for c in cands:
        if norm(c) in exact:
            return exact[norm(c)]
    for c in cands:
        hit = loose.get(norm(strip_date(c)))
        if hit:
            return sorted(hit, key=len)[0]
    return None


def per_million(x):
    try:
        return round(float(x) * 1e6, 6)
    except (TypeError, ValueError):
        return None


def fmt_ctx(n):
    if not n:
        return None
    return "1M" if n >= 900_000 else f"{round(n / 1000)}K"


def dump(d):
    one = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    return ('{"updated":%s,"synced":%s,\n"providers":[\n%s\n],\n"models":[\n%s\n]}'
            % (one(d["updated"]), one(d["synced"]),
               ",\n".join(one(p) for p in d["providers"]),
               ",\n".join(one(m) for m in d["models"])))


def main():
    text = PAGE.read_text(encoding="utf-8")
    match = BLOCK.search(text)
    if not match:
        sys.exit("ERROR: data block not found in index.html")
    data = json.loads(match.group(2))

    catalog = fetch_catalog()
    if len(catalog) < 50:
        sys.exit(f"ERROR: catalog has only {len(catalog)} models, refusing to continue")
    ids, exact, loose = build_index(catalog)

    changes, blocked, unmatched, matched = [], [], [], 0
    for m in data["models"]:
        cands = m.get("or")
        if not cands:
            continue
        oid = find(cands, exact, loose)
        if not oid:
            near = difflib.get_close_matches(cands[0], list(ids), n=3, cutoff=0.5)
            unmatched.append((m["m"], cands[0], near))
            m.pop("oid", None)  # no longer matched: show as MANUAL
            continue
        entry = ids[oid]
        pricing = entry.get("pricing") or {}
        new = {"i": per_million(pricing.get("prompt")), "o": per_million(pricing.get("completion"))}
        if not new["i"] or not new["o"] or new["i"] <= 0 or new["o"] <= 0:
            blocked.append((m["m"], oid, "catalog price missing or zero"))
            continue
        matched += 1
        m["oid"] = oid
        for key, label in (("i", "input"), ("o", "output")):
            old = m.get(key)
            if old and not (1 / MAX_RATIO <= new[key] / old <= MAX_RATIO):
                blocked.append((m["m"], oid, f"{label} ${old} -> ${new[key]} is more than {MAX_RATIO:g}x, not applied"))
            elif old != new[key]:
                changes.append((m["m"], label, old, new[key]))
                m[key] = new[key]
        ctx = fmt_ctx(entry.get("context_length") or (entry.get("top_provider") or {}).get("context_length"))
        if ctx and ctx != m.get("c"):
            changes.append((m["m"], "context", m.get("c"), ctx))
            m["c"] = ctx

    if matched == 0:
        sys.exit("ERROR: no models matched the catalog, so the IDs or the API format may have changed")

    today = datetime.datetime.now(datetime.timezone.utc).date()
    if changes:
        data["updated"] = today.isoformat()
    last = datetime.date.fromisoformat(data.get("synced", "1970-01-01"))
    if changes or (today - last).days >= HEARTBEAT_DAYS:
        data["synced"] = today.isoformat()

    new_text = text[:match.start(2)] + dump(data) + text[match.end(2):]
    if new_text != text:
        PAGE.write_text(new_text, encoding="utf-8")

    lines = [f"### Price sync {today}", f"{matched} auto models matched, {len(changes)} change(s).", ""]
    if changes:
        lines += ["| Model | Field | Old | New |", "|---|---|---|---|"]
        lines += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in changes]
        lines += ["", "Review the notes beside changed rows, because notes are written by hand.", ""]
    if blocked:
        lines += ["**Not applied**", ""] + [f"- {a} ({b}): {c}" for a, b, c in blocked] + [""]
    if unmatched:
        lines += ["**Not found in the catalog (these rows stay MANUAL). Fix the `or` list in index.html:**", ""]
        lines += [f"- {a}: tried `{b}`; closest IDs: {', '.join(n) or 'none'}" for a, b, n in unmatched] + [""]
    report = "\n".join(lines)
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(report + "\n")


if __name__ == "__main__":
    main()
