"""A local delivery tracker. All example addresses are fictional."""
import csv
from datetime import datetime, timezone
from copy import deepcopy
from html import escape
import json
from pathlib import Path

DATA = Path(__file__).with_name("packages.json")
def timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


STATUSES = ("Pending", "Out for delivery", "Delivered", "Failed")


def validate(packages):
    """Reject malformed data rather than silently replacing someone's file."""
    if not isinstance(packages, dict):
        raise ValueError("Expected a dictionary of packages.")
    for key, package in packages.items():
        if not isinstance(package, dict) or not isinstance(key, str) or not key.strip():
            raise ValueError("Invalid package record.")
        if not isinstance(package.get("address"), str) or not package["address"].strip():
            raise ValueError("Each package needs an address.")
        if package.get("status") not in STATUSES:
            raise ValueError("Unknown package status.")
        history = package.get("history", [])
        if not isinstance(history, list):
            raise ValueError("History must be a list.")
        for event in history:
            if (not isinstance(event, dict) or event.get("status") not in STATUSES
                    or not isinstance(event.get("time"), str)):
                raise ValueError("Invalid history event.")
            datetime.fromisoformat(event["time"])
    return packages


def load(path=DATA):
    if not path.exists():
        return {}
    return validate(json.loads(path.read_text(encoding="utf-8")))


def save(packages, path=DATA):
    validate(packages)
    # Write a temporary file first, then replace the old file.
    temporary = path.with_suffix(".tmp")
    if path.exists():
        # Keep one previous on-disk version before replacing it.
        path.with_suffix(".backup.json").write_bytes(path.read_bytes())
    temporary.write_text(json.dumps(packages, indent=2), encoding="utf-8")
    temporary.replace(path)


def add_package(packages, package_id, address):
    package_id, address = package_id.strip(), address.strip()
    if not package_id or not address:
        raise ValueError("ID and address cannot be blank.")
    if package_id in packages:
        raise ValueError("That ID already exists.")
    packages[package_id] = {"address": address, "status": "Pending",
                            "history": [{"time": timestamp(), "status": "Pending"}]}


def update_status(packages, package_id, status):
    if package_id not in packages:
        raise ValueError("Package not found.")
    if status not in STATUSES:
        raise ValueError("Invalid status.")
    if packages[package_id]["status"] == status:
        raise ValueError("Package already has that status.")
    packages[package_id]["status"] = status
    packages[package_id].setdefault("history", []).append({"time": timestamp(), "status": status})


def statistics(packages):
    counts = {status: 0 for status in STATUSES}
    for package in packages.values():
        counts[package["status"]] += 1
    rate = 100 * counts["Delivered"] / len(packages) if packages else 0
    return counts, rate


def export_csv(packages, path):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Address", "Status"])
        for key, package in sorted(packages.items()):
            writer.writerow([key, package["address"], package["status"]])


def show(packages):
    if not packages:
        print("No matching packages.")
    for key, package in sorted(packages.items()):
        print(f"{key}: {package['address']} | {package['status']}")


def html_report(packages, path):
    counts, rate = statistics(packages)
    cards = "".join(f"<div><strong>{count}</strong><br>{escape(status)}</div>" for status, count in counts.items())
    rows = "".join(f"<tr><td>{escape(key)}</td><td>{escape(p['address'])}</td><td>{escape(p['status'])}</td><td>{len(p.get('history', []))}</td></tr>" for key, p in sorted(packages.items()))
    path.write_text(f"""<!doctype html><meta charset="utf-8"><title>Delivery report</title>
<style>body{{font:17px system-ui;background:#f1f5fb;color:#17243b;max-width:1000px;margin:40px auto;padding:20px}}.cards{{display:flex;gap:16px;flex-wrap:wrap}}.cards div{{background:white;padding:22px;border-radius:12px}}strong{{font-size:30px}}table{{width:100%;background:white;border-collapse:collapse}}td,th{{padding:14px;border-bottom:1px solid #ddd;text-align:left}}</style>
<h1>Delivery Operations Report</h1><p>Generated {escape(timestamp())} | Fictional demo data</p>
<div class="cards">{cards}</div><p>Delivered: {rate:.1f}% of {len(packages)} packages</p>
<table><tr><th>ID</th><th>Address</th><th>Status</th><th>Recorded events</th></tr>{rows}</table>""", encoding="utf-8")


def main():
    try:
        packages = load()
    except (OSError, ValueError) as error:
        print(f"Cannot load data: {error}. Repair or back up packages.json first.")
        return
    while True:
        print("\nDELIVERY TRACKER\n1 Add  2 View  3 Search  4 Update  5 Summary  6 Export CSV  7 History  8 HTML report  9 Filter  0 Exit")
        choice = input("Choose: ").strip()
        previous = deepcopy(packages)
        try:
            if choice == "0":
                break
            elif choice == "1":
                add_package(packages, input("ID: "), input("Address: "))
                save(packages)
                print("Added and saved.")
            elif choice == "2":
                show(packages)
            elif choice == "3":
                term = input("ID or address text: ").lower().strip()
                show({key: value for key, value in packages.items()
                      if term in key.lower() or term in value["address"].lower()})
            elif choice == "4":
                key = input("ID: ").strip()
                for index, status in enumerate(STATUSES, 1):
                    print(index, status)
                number = int(input("Status number: "))
                if not 1 <= number <= len(STATUSES):
                    raise ValueError("Choose a listed status.")
                update_status(packages, key, STATUSES[number - 1])
                save(packages)
                print("Updated and saved.")
            elif choice == "5":
                counts, rate = statistics(packages)
                for status, count in counts.items():
                    print(f"{status}: {count}")
                print(f"Delivered: {rate:.1f}% of {len(packages)} packages")
            elif choice == "6":
                path = DATA.with_name("delivery_report.csv")
                export_csv(packages, path)
                print(f"Exported {path.name}")
            elif choice == "7":
                key = input("ID: ").strip()
                if key not in packages:
                    raise ValueError("Package not found.")
                for event in packages[key].get("history", []):
                    print(event["time"], event["status"])
            elif choice == "8":
                path = DATA.with_name("delivery_report.html")
                html_report(packages, path)
                print(f"Open {path.name} in a browser.")
            elif choice == "9":
                status = input("Status (Pending, Out for delivery, Delivered, Failed): ").strip()
                if status not in STATUSES:
                    raise ValueError("Unknown status.")
                show({key: p for key, p in packages.items() if p["status"] == status})
            else:
                print("Choose a listed option.")
        except (ValueError, OSError) as error:
            print(f"Error: {error}")
            packages = previous
            print("The attempted change was rolled back in memory.")


if __name__ == "__main__":
    main()
