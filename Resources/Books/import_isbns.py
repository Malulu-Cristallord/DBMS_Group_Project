from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    # webb: Allow this seed script to import Backend modules when run directly.
    sys.path.insert(0, str(ROOT))

from Backend.DB_Stuff.db_connect import execute_query_fetch
from Backend.Functions import book_request


DEFAULT_ISBNS = [
    "9780007264179",
    "9780060747480",
    "9780141355429",
    "9780312984854",
    "9780373110629",
    "9780439362139",
    "9780545082174",
    "9780545948869",
    "9780573702419",
    "9780671823795",
    "9781410499707",
    "9781471250811",
    "9781566199094",
    "9787500129851",
    "9787544804196",
]


def clean_isbn(value: str) -> str:
    return value.strip().replace("-", "")


def get_existing_book(isbn: str) -> dict | None:
    # webb: Check the local database first to avoid duplicate book inserts.
    rows = execute_query_fetch(
        """
        SELECT ISBN, Title
        FROM books
        WHERE ISBN = %s
        LIMIT 1
        """,
        (isbn,),
    )
    if rows is None:
        raise RuntimeError(f"Could not check books table for ISBN {isbn}")
    return rows[0] if rows else None


def import_isbns(isbns: list[str] | None = None) -> dict[str, list[dict[str, str]]]:
    # webb: Reuse the existing Open Library import flow for this fixed ISBN seed list.
    results: dict[str, list[dict[str, str]]] = {
        "imported": [],
        "skipped": [],
        "failed": [],
    }

    for raw_isbn in isbns or DEFAULT_ISBNS:
        isbn = clean_isbn(raw_isbn)
        if not isbn.isdigit():
            results["failed"].append(
                {"isbn": raw_isbn, "reason": "ISBN contains non-digit characters"}
            )
            continue

        existing = get_existing_book(isbn)
        if existing:
            results["skipped"].append(
                {"isbn": isbn, "title": existing.get("Title") or ""}
            )
            print(f"ISBN already exists, skipped: {isbn}")
            continue

        result = book_request.request_book_data(isbn)
        if result == -1:
            existing = get_existing_book(isbn)
            results["skipped"].append(
                {"isbn": isbn, "title": (existing or {}).get("Title", "")}
            )
            continue

        if result == "error":
            results["failed"].append(
                {"isbn": isbn, "reason": "Open Library request failed"}
            )
            continue

        inserted = get_existing_book(isbn)
        if not inserted:
            results["failed"].append(
                {"isbn": isbn, "reason": "Open Library returned data, but no row was inserted"}
            )
            continue

        results["imported"].append(
            {"isbn": isbn, "title": inserted.get("Title") or ""}
        )
        print(f"ISBN imported: {isbn}")

    print_summary(results)
    return results


def print_summary(results: dict[str, list[dict[str, str]]]) -> None:
    print("\nISBN import summary")
    for key in ("imported", "skipped", "failed"):
        print(f"{key}: {len(results[key])}")
        for item in results[key]:
            detail = item.get("title") or item.get("reason") or ""
            print(f"  - {item['isbn']}: {detail}")


if __name__ == "__main__":
    import_isbns()
