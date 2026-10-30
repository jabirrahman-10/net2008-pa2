# Name: Jabir Rahman
# Student ID: 101374024 (Carleton)

import sys
import json
import xml.etree.ElementTree as ET


def main():
    """Read the inventory file, count roles and interfaces, and write audit.json."""
    inventory_file = sys.argv[1]
    tree = ET.parse(inventory_file)
    root = tree.getroot()

    skipped = 0
    kept_ids = []
    roles = {}
    interfaces = {"up": 0, "down": 0, "other": 0}
    for device in root.findall("device"):
        if device.get("id") is None:
            skipped += 1
        else:
            kept_ids.append(device.get("id"))
            role = device.get("role")
            if role in roles:
                roles[role] += 1
            else:
                roles[role] = 1

            for interface in device.findall("interface"):
                status = interface.get("status")
                if status == "up":
                    interfaces["up"] += 1
                elif status == "down":
                    interfaces["down"] += 1
                else:
                    interfaces["other"] += 1

    report = {
        "site": root.get("site"),
        "total_devices": len(kept_ids),
        "skipped_devices": skipped,
        "roles": roles,
        "interfaces": interfaces,
        "violations": [],
        "compliant": sorted(kept_ids),
    }

    with open("audit.json", "w") as f:
        json.dump(report, f, indent=2)

    print("Audited", len(kept_ids), "devices, skipped", skipped)


if __name__ == "__main__":
    main()