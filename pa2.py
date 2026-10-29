# Name: Jabir Rahman
# Student ID: 101374024 (Carleton)

import sys
import xml.etree.ElementTree as ET


def main():
    """Read the inventory file, skip devices with no id, and count the roles."""
    inventory_file = sys.argv[1]
    tree = ET.parse(inventory_file)
    root = tree.getroot()

    skipped = 0
    roles = {}
    for device in root.findall("device"):
        if device.get("id") is None:
            skipped += 1
        else:
            role = device.get("role")
            if role in roles:
                roles[role] += 1
            else:
                roles[role] = 1

    print("Skipped devices:", skipped)
    print("Roles:", roles)


if __name__ == "__main__":
    main()