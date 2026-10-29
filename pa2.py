# Name: Jabir Rahman
# Student ID: 101374024 (Carleton)

import sys
import xml.etree.ElementTree as ET


def main():
    """Read the inventory file, skip devices with no id, count roles and interfaces."""
    inventory_file = sys.argv[1]
    tree = ET.parse(inventory_file)
    root = tree.getroot()

    skipped = 0
    roles = {}
    interfaces = {"up": 0, "down": 0, "other": 0}
    for device in root.findall("device"):
        if device.get("id") is None:
            skipped += 1
        else:
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

    print("Skipped devices:", skipped)
    print("Roles:", roles)
    print("Interfaces:", interfaces)


if __name__ == "__main__":
    main()