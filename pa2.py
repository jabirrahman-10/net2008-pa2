# Name: Jabir Rahman
# Student ID: 101374024 (Carleton)

import sys
import xml.etree.ElementTree as ET


def main():
    """Read the inventory file, skip devices with no id, and print the ids."""
    inventory_file = sys.argv[1]
    tree = ET.parse(inventory_file)
    root = tree.getroot()

    skipped = 0
    for device in root.findall("device"):
        if device.get("id") is None:
            skipped += 1
        else:
            print(device.get("id"))

    print("Skipped devices:", skipped)


if __name__ == "__main__":
    main()