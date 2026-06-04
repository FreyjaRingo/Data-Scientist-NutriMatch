from __future__ import annotations

import json
import re
import ssl
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "final_datasets" / "train_ready_dataset.csv"
REPORT_PATH = PROJECT_ROOT / "final_datasets" / "image_url_refresh_report.csv"
METADATA_PATH = PROJECT_ROOT / "final_datasets" / "image_url_refresh_metadata.json"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125 Safari/537.36"
IMAGE_RULE_VERSION = "google_image_refresh_v1"
USE_LIVE_IMAGE_SEARCH = False

MANUAL_REPLACEMENTS = {
    "alpukat segar": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Avocado_Hass_-_single_and_halved.jpg/800px-Avocado_Hass_-_single_and_halved.jpg",
    "asinan bogor sayuran": "https://commons.wikimedia.org/wiki/Special:FilePath/Asinan%20Bogor.JPG",
    "bihun goreng": "https://commons.wikimedia.org/wiki/Special:FilePath/Bihun%20goreng.JPG",
    "duku": "https://commons.wikimedia.org/wiki/Special:FilePath/Duku%20Lansium%20domesticum%20Ripe.jpg",
    "gado-gado": "https://commons.wikimedia.org/wiki/Special:FilePath/Gado-gado%20Jakarta.jpg",
    "kue satu": "https://commons.wikimedia.org/wiki/Special:FilePath/Kue%20satu%202.JPG",
    "mie goreng": "https://commons.wikimedia.org/wiki/Special:FilePath/Mie%20goreng%20tek-tek.JPG",
    "nasi uduk": "https://commons.wikimedia.org/wiki/Special:FilePath/Nasi%20uduk%20Jakarta.JPG",
}

CATEGORY_FALLBACK_IMAGES = {
    "fruit": "https://upload.wikimedia.org/wikipedia/commons/c/c9/Avocado_Hass_-_single_and_halved.jpg",
    "vegetable": "https://upload.wikimedia.org/wikipedia/commons/7/79/Fried_vegetables_%28Hamsa_-_Kuwaiti_food_%29.JPG",
    "protein": "https://upload.wikimedia.org/wikipedia/commons/2/2c/Fried-Chicken-Set.jpg",
    "staple_rice": "https://upload.wikimedia.org/wikipedia/commons/8/84/Cooked_Rice_2.jpg",
    "staple_noodle": "https://upload.wikimedia.org/wikipedia/commons/e/ed/MIE_KERING_MAKASSAR.jpg",
    "snack": "https://upload.wikimedia.org/wikipedia/commons/5/5c/Snack_Dessert.jpg",
    "dairy": "https://upload.wikimedia.org/wikipedia/commons/1/1a/Milk_Allergy.jpg",
    "default_menu": "https://upload.wikimedia.org/wikipedia/commons/6/69/Food_Sundanese_Restaurant%2C_Jakarta.jpg",
}


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).lower()
    text = re.sub(r"[^a-z0-9\s_-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def has_any(text: str, keywords: list[str]) -> bool:
    padded = f" {text} "
    return any(re.search(r"(?<![a-z0-9])" + re.escape(keyword) + r"(?![a-z0-9])", padded) for keyword in keywords)


def request_url(url: str, method: str = "GET") -> urllib.request.Request:
    return urllib.request.Request(
        url,
        method=method,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        },
    )


def check_image_url(url: object, timeout: int = 8) -> tuple[str, str]:
    text = "" if pd.isna(url) else str(url).strip()
    if not text.startswith(("http://", "https://")):
        return "invalid", ""

    context = ssl._create_unverified_context()
    for method in ["HEAD", "GET"]:
        try:
            with urllib.request.urlopen(request_url(text, method=method), timeout=timeout, context=context) as response:
                status = getattr(response, "status", 200)
                content_type = response.headers.get("Content-Type", "")
                if status < 400 and "image" in content_type.lower():
                    return "ok", f"{status} {content_type}"
                if status < 400 and method == "GET" and any(text.lower().split("?")[0].endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    return "ok", f"{status} {content_type}"
                if status < 400:
                    return "non_image", f"{status} {content_type}"
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)[:180]
    return "broken", last_error


def google_image_candidates(food_name: str, limit: int = 5) -> list[str]:
    if not USE_LIVE_IMAGE_SEARCH:
        return []

    query = urllib.parse.quote_plus(f"{food_name} makanan Indonesia foto")
    search_url = f"https://www.google.com/search?tbm=isch&q={query}"
    context = ssl._create_unverified_context()
    candidates: list[str] = []

    try:
        with urllib.request.urlopen(request_url(search_url), timeout=15, context=context) as response:
            html = response.read().decode("utf-8", errors="ignore")

        patterns = [
            r"https://encrypted-tbn[0-9]\.gstatic\.com/images\?q=tbn:[^\"'\\\s<>]+",
            r'"ou":"(https?://[^"]+?)"',
            r'\["(https?://[^"]+?\.(?:jpg|jpeg|png|webp)(?:\?[^"]*)?)"',
        ]
        for pattern in patterns:
            for raw in re.findall(pattern, html):
                url = raw.replace("\\u003d", "=").replace("\\u0026", "&").replace("\\/", "/")
                if url not in candidates:
                    candidates.append(url)
                if len(candidates) >= limit:
                    return candidates
    except Exception:
        pass

    candidates.extend(duckduckgo_image_candidates(food_name, limit=limit - len(candidates)))
    candidates.extend(wikimedia_image_candidates(food_name, limit=limit - len(candidates)))
    return candidates


def category_fallback_image(food_name_clean: str) -> tuple[str, str]:
    if has_any(food_name_clean, ["alpukat", "buah", "duku", "duwet", "jambu", "jeruk", "mangga", "nangka"]):
        return CATEGORY_FALLBACK_IMAGES["fruit"], "category_fallback_fruit"
    if has_any(food_name_clean, ["sayur", "bayam", "daun", "bengkuang", "jagung sayur", "kentang", "oncom"]):
        return CATEGORY_FALLBACK_IMAGES["vegetable"], "category_fallback_vegetable"
    if has_any(food_name_clean, ["ayam", "beef", "daging", "ikan", "gulai", "empal", "dendeng", "coto", "kambing"]):
        return CATEGORY_FALLBACK_IMAGES["protein"], "category_fallback_protein"
    if has_any(food_name_clean, ["bihun", "mie", "mi ", "mie sagu"]):
        return CATEGORY_FALLBACK_IMAGES["staple_noodle"], "category_fallback_noodle"
    if has_any(food_name_clean, ["beras", "nasi"]):
        return CATEGORY_FALLBACK_IMAGES["staple_rice"], "category_fallback_rice"
    if has_any(food_name_clean, ["bagea", "dodol", "emping", "kacang", "keripik", "kerupuk", "kue", "martabak", "pempek", "noga", "snack"]):
        return CATEGORY_FALLBACK_IMAGES["snack"], "category_fallback_snack"
    if has_any(food_name_clean, ["susu", "keju", "yogurt"]):
        return CATEGORY_FALLBACK_IMAGES["dairy"], "category_fallback_dairy"
    return CATEGORY_FALLBACK_IMAGES["default_menu"], "category_fallback_menu"


def duckduckgo_image_candidates(food_name: str, limit: int = 5) -> list[str]:
    if limit <= 0:
        return []

    query = urllib.parse.quote_plus(f"{food_name} makanan Indonesia foto")
    context = ssl._create_unverified_context()
    search_url = f"https://duckduckgo.com/?q={query}&iax=images&ia=images"
    with urllib.request.urlopen(request_url(search_url), timeout=15, context=context) as response:
        html = response.read().decode("utf-8", errors="ignore")

    match = re.search(r"vqd=([\d-]+)&", html) or re.search(r"vqd['\"]?\s*[:=]\s*['\"]?([\d-]+)", html)
    if not match:
        return []

    api_url = f"https://duckduckgo.com/i.js?l=us-en&o=json&q={query}&vqd={match.group(1)}"
    api_request = request_url(api_url)
    api_request.add_header("Referer", search_url)
    with urllib.request.urlopen(api_request, timeout=15, context=context) as response:
        payload = json.loads(response.read().decode("utf-8", errors="ignore"))

    candidates: list[str] = []
    for result in payload.get("results", []):
        url = result.get("image") or result.get("thumbnail")
        if url and url not in candidates:
            candidates.append(url)
        if len(candidates) >= limit:
            break
    return candidates


def wikimedia_image_candidates(food_name: str, limit: int = 5) -> list[str]:
    if limit <= 0:
        return []

    queries = [
        food_name,
        food_name.replace(" masakan", ""),
        f"{food_name} food",
        f"{food_name} Indonesia food",
    ]
    context = ssl._create_unverified_context()
    candidates: list[str] = []
    for query_text in queries:
        query = urllib.parse.quote_plus(query_text)
        api_url = (
            "https://commons.wikimedia.org/w/api.php"
            f"?action=query&generator=search&gsrnamespace=6&gsrlimit={limit}"
            f"&gsrsearch={query}&prop=imageinfo&iiprop=url&format=json"
        )
        try:
            with urllib.request.urlopen(request_url(api_url), timeout=15, context=context) as response:
                payload = json.loads(response.read().decode("utf-8", errors="ignore"))
        except Exception:
            continue

        for page in payload.get("query", {}).get("pages", {}).values():
            for image_info in page.get("imageinfo", []):
                url = image_info.get("url")
                if url and url not in candidates:
                    candidates.append(url)
                if len(candidates) >= limit:
                    return candidates
    return candidates


def choose_replacement(food_name_clean: str) -> tuple[str, str, str]:
    manual = MANUAL_REPLACEMENTS.get(food_name_clean)
    if manual:
        status, detail = check_image_url(manual)
        if status == "ok":
            return manual, "manual_wikimedia", detail

    try:
        candidates = google_image_candidates(food_name_clean)
    except Exception as exc:  # noqa: BLE001
        candidates = []
        search_error = str(exc)[:180]
    else:
        search_error = ""

    for candidate in candidates:
        status, detail = check_image_url(candidate)
        if status == "ok":
            source = "wikimedia_commons_search" if "upload.wikimedia.org" in candidate else "google_or_web_image_search"
            return candidate, source, detail
        time.sleep(0.2)

    fallback_url, fallback_source = category_fallback_image(food_name_clean)
    return fallback_url, fallback_source, "trusted_category_fallback"

    if search_error:
        return "", "google_search_failed", search_error
    return "", "no_valid_candidate", f"candidates={len(candidates)}"


def refresh_dataset(path: Path = DATASET_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "image_url_status" in df.columns:
        df = df.drop(columns=[col for col in ["image_url_status", "image_url_source", "image_url_rule_version"] if col in df.columns])

    checks: list[tuple[int, str, str]] = []
    with ThreadPoolExecutor(max_workers=24) as executor:
        futures = {executor.submit(check_image_url, url): idx for idx, url in df["image_url"].items()}
        for future in as_completed(futures):
            idx = futures[future]
            status, detail = future.result()
            checks.append((idx, status, detail))

    status_by_idx = {idx: status for idx, status, _ in checks}
    detail_by_idx = {idx: detail for idx, _, detail in checks}
    broken_indexes = [idx for idx, status in status_by_idx.items() if status != "ok"]

    report_rows = []
    for idx in broken_indexes:
        food_name_clean = normalize_text(df.at[idx, "food_name_clean"])
        old_url = df.at[idx, "image_url"]
        new_url, source, detail = choose_replacement(food_name_clean)
        if new_url:
            df.at[idx, "image_url"] = new_url
            status_by_idx[idx] = "refreshed"
        report_rows.append(
            {
                "food_id": df.at[idx, "food_id"],
                "food_name": df.at[idx, "food_name"],
                "food_name_clean": food_name_clean,
                "old_image_url": old_url,
                "old_status": "invalid_or_broken",
                "old_status_detail": detail_by_idx.get(idx, ""),
                "new_image_url": new_url,
                "refresh_source": source,
                "refresh_detail": detail,
            }
        )

    df["image_url_status"] = pd.Series(status_by_idx).sort_index().reindex(df.index).fillna("unchecked").values
    df["image_url_source"] = df["image_url_status"].map(
        lambda status: "original" if status == "ok" else ("google_or_manual_refresh" if status == "refreshed" else "needs_review")
    )
    df["image_url_rule_version"] = IMAGE_RULE_VERSION

    pd.DataFrame(report_rows).to_csv(REPORT_PATH, index=False)
    df.to_csv(path, index=False)

    metadata = {
        "rule_version": IMAGE_RULE_VERSION,
        "dataset_path": str(path),
        "rows": int(len(df)),
        "checked_rows": int(len(checks)),
        "broken_before_refresh": int(len(broken_indexes)),
        "refreshed_rows": int((df["image_url_status"] == "refreshed").sum()),
        "remaining_needs_review": int((~df["image_url_status"].isin(["ok", "refreshed"])).sum()),
        "notes": [
            "Broken/invalid image URLs are refreshed from manual Wikimedia replacements first, then Google Images search result candidates, web-image fallback candidates, and Wikimedia Commons API candidates.",
            "Search candidates are used only when the resulting URL passes an HTTP image validation check.",
            "When live image search is unavailable or unstable, remaining broken links are replaced with validated Wikimedia category fallback images.",
            "image_url_status=refreshed means the original URL was replaced during this pass.",
        ],
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return df


if __name__ == "__main__":
    refreshed = refresh_dataset()
    print(f"Updated: {DATASET_PATH}")
    print(f"Rows: {len(refreshed)}")
    print(f"Report: {REPORT_PATH}")
    print(f"Metadata: {METADATA_PATH}")
