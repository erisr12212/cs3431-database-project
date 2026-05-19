"""
teamlambda.py

Reads Yelp JSON files and inserts their contents into our PostgreSQL schema
(see teamlambda.sql). Run teamlambda.sql first to create the tables, then run this.

Requires: psycopg2 (or psycopg2-binary), python-dotenv

Create a .env next to this file with:
    POSTGRES_USER=your_user
    POSTGRES_PASSWORD=your_password
    POSTGRES_DB=yelp
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    YELP_DATA_DIR=/absolute/path/to/yelpdata_CS3431
"""

import json
import os
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

DB_PARAMS = {
    "dbname":   os.getenv("POSTGRES_DB", "yelp"),
    "user":     os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host":     os.getenv("POSTGRES_HOST", "localhost"),
    "port":     os.getenv("POSTGRES_PORT", "5432"),
}

_data_dir = os.getenv("YELP_DATA_DIR")
if not _data_dir:
    raise SystemExit(
        "YELP_DATA_DIR is not set. Add YELP_DATA_DIR=/path/to/yelpdata_CS3431 to .env."
    )
DATA_DIR = Path(_data_dir).expanduser()
BATCH = 5000

def clean(s):
    """Strip characters that would break SQL statements."""
    if s is None:
        return None
    return s.replace("\x00", "").replace("\n", " ")


def flatten_attributes(attrs):
    """Yelp attributes can be nested one level deep (e.g. Ambience.romantic).
    Flatten to a list of (name, value) pairs using just the leaf key."""
    out = []
    for name, value in attrs.items():
        if isinstance(value, dict):
            out.extend(flatten_attributes(value))
        else:
            out.append((name, value))
    return out


def parse_time(t):
    """Standarize time strings from yelp data. Return 'HH:MM:00'."""
    h, m = t.split(":")
    return f"{int(h):02d}:{int(m):02d}:00"


def batched(iterable, n):
    """Yield lists of size n from iterable."""
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= n:
            yield batch
            batch = []
    if batch:
        yield batch


def iter_json_lines(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def stream_insert(cur, sql, rows):
    """Batch-insert rows through execute_values. Returns total count."""
    count = 0
    for batch in batched(rows, BATCH):
        execute_values(cur, sql, batch)
        count += len(batch)
    return count


# ---------------------------------------------------------------------------
# Insert functions. Each reads a JSON file and inserts into the tables.
# ---------------------------------------------------------------------------

def insert_businesses(cur):
    """Insert business rows and collect rows for the dependent tables.

    We do a first pass over yelp_business.JSON to accumulate rows for
    the main columns and then flush them in dependency order.
    """
    print("Inserting businesses...")

    business_rows = []
    category_names = set()
    business_category_rows = []
    attribute_names = set()
    business_attribute_rows = []
    schedule_rows = []

    for data in iter_json_lines(DATA_DIR / "yelp_business.JSON"):
        bid = data["business_id"]
        business_rows.append((
            bid,
            clean(data["name"]),
            clean(data["address"]),
            clean(data["city"]),
            data["state"],
            data["postal_code"] or None,
            data["latitude"],
            data["longitude"],
            data["stars"],
            0,  # num_tips, we'll take care of it in task 2
            data["is_open"],
        ))

        if data.get("categories"):
            for cat in data["categories"].split(", "):
                cat = cat.strip()
                if cat:
                    category_names.add(cat)
                    business_category_rows.append((cat, bid))

        if data.get("attributes"):
            for name, value in flatten_attributes(data["attributes"]):
                attribute_names.add(name)
                business_attribute_rows.append((name, str(value), bid))

        if data.get("hours"):
            for day, span in data["hours"].items():
                open_t, close_t = span.split("-")
                schedule_rows.append((bid, day, parse_time(open_t), parse_time(close_t)))

    execute_values(cur,
        """INSERT INTO business
           (BusinessId, Name, StreetAddress, City, State, ZIP,
            Latitude, Longitude, Stars, num_tips, IsOpen)
           VALUES %s""",
        business_rows, page_size=BATCH)
    print(f"  business: {len(business_rows)}")

    execute_values(cur,
        "INSERT INTO category (CategoryName) VALUES %s",
        [(c,) for c in category_names], page_size=BATCH)
    print(f"  category: {len(category_names)}")

    execute_values(cur,
        "INSERT INTO business_category (CategoryName, BusinessId) VALUES %s",
        business_category_rows, page_size=BATCH)
    print(f"  business_category: {len(business_category_rows)}")

    execute_values(cur,
        "INSERT INTO attribute (AttributeName) VALUES %s",
        [(a,) for a in attribute_names], page_size=BATCH)
    print(f"  attribute: {len(attribute_names)}")

    seen = set()
    deduped = []
    for name, value, bid in business_attribute_rows:
        key = (name, bid)
        if key in seen:
            continue
        seen.add(key)
        deduped.append((name, value, bid))
    execute_values(cur,
        "INSERT INTO business_attribute (AttributeName, Value, BusinessId) VALUES %s",
        deduped, page_size=BATCH)
    print(f"  business_attribute: {len(deduped)}")

    execute_values(cur,
        "INSERT INTO schedule (BusinessId, Day, Open, Close) VALUES %s",
        schedule_rows, page_size=BATCH)
    print(f"  schedule: {len(schedule_rows)}")


def insert_users_and_friends(cur):
    """Insert users first, then the friendships. We keep a set of valid user
    IDs so we can drop any friend references that point outside the dataset
    (would otherwise violate the FK)."""
    print("Inserting users...")

    user_ids = set()

    def user_rows():
        for data in iter_json_lines(DATA_DIR / "yelp_user.JSON"):
            uid = data["user_id"]
            user_ids.add(uid)
            yield (
                uid,
                clean(data["name"]),
                data["average_stars"],
                data["funny"], data["cool"], data["useful"], data["fans"],
                0,  # tip_count, we'll do it in task 2
                data["yelping_since"],
            )

    n = stream_insert(cur,
        """INSERT INTO users
           (UserId, Name, Stars, Funny, Cool, Useful, Fans, tip_count, CreatedAt)
           VALUES %s""", user_rows())
    print(f"  users: {n}")

    print("Inserting friends...")
    # Second pass so we don't cache like around 1M friend pairs at the same time as everything else.
    def friend_rows():
        for data in iter_json_lines(DATA_DIR / "yelp_user.JSON"):
            u1 = data["user_id"]
            for u2 in data.get("friends", []):
                if u2 in user_ids and u1 != u2:
                    yield (u1, u2)

    n = stream_insert(cur,
        "INSERT INTO friends (UserId1, UserId2) VALUES %s ON CONFLICT DO NOTHING",
        friend_rows())
    print(f"  friends: {n}")


def insert_tips(cur):
    print("Inserting tips...")
    rows = (
        (d["user_id"], d["business_id"], d["date"], d["likes"], clean(d["text"]))
        for d in iter_json_lines(DATA_DIR / "yelp_tip.JSON")
    )
    n = stream_insert(cur,
        """INSERT INTO tip (UserId, BusinessId, tip_date, Likes, tip_Text)
           VALUES %s ON CONFLICT DO NOTHING""", rows)
    print(f"  tip: {n}")


def insert_checkins(cur):
    print("Inserting checkins...")
    def rows():
        for data in iter_json_lines(DATA_DIR / "yelp_checkin.JSON"):
            bid = data["business_id"]
            for ts in data["date"].split(","):
                ts = ts.strip()
                if ts:
                    yield (bid, ts)
    n = stream_insert(cur,
        "INSERT INTO checkin (BusinessId, timestamp) VALUES %s ON CONFLICT DO NOTHING",
        rows())
    print(f"  checkin: {n}")


def main():
    with psycopg2.connect(**DB_PARAMS) as conn:
        with conn.cursor() as cur:
            insert_businesses(cur)
            insert_users_and_friends(cur)
            insert_tips(cur)
            insert_checkins(cur)
        conn.commit()
    print("Done.")


if __name__ == "__main__":
    main()
