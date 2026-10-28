# Name: Jabir Rahman
# Student ID: 101374024 (Carleton)

import sys
import xml.etree.ElementTree as ET


def main():
    """Read the inventory file and print every device id."""
    inventory_file = sys.argv[1]
    tree = ET.parse(inventory_file)
    root = tree.getroot()

    for device in root.findall("device"):
        print(device.get("id"))


if __name__ == "__main__":
    main()