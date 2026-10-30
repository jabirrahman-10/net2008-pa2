# Name: Jabir Rahman
# Student ID: 101374024 (Carleton)

import sys
import json
import yaml
import xml.etree.ElementTree as ET


class Device:
    """One network device from the inventory file."""

    def __init__(self, element):
        """Read the id, role, os, owner and interface statuses from an XML element."""
        self.id = element.get("id")
        self.role = element.get("role")
        self.os = element.get("os")

        owner = element.find("owner")
        if owner is None or owner.text is None:
            self.owner = ""
        else:
            self.owner = owner.text.strip()

        self.statuses = []
        for interface in element.findall("interface"):
            self.statuses.append(interface.get("status"))

    def count_status(self, wanted):
        """Return how many interfaces have the wanted status."""
        count = 0
        for status in self.statuses:
            if status == wanted:
                count += 1
        return count


def main():
    """Read both files, check the policy, and write audit.json."""
    inventory_file = sys.argv[1]
    policy_file = sys.argv[2]
    root = ET.parse(inventory_file).getroot()

    with open(policy_file) as f:
        policy = yaml.safe_load(f)
    if policy is None:
        policy = {}

    skipped = 0
    devices = []
    for element in root.findall("device"):
        if element.get("id") is None:
            skipped += 1
        else:
            devices.append(Device(element))

    roles = {}
    interfaces = {"up": 0, "down": 0, "other": 0}
    for device in devices:
        if device.role in roles:
            roles[device.role] += 1
        else:
            roles[device.role] = 1

        up = device.count_status("up")
        down = device.count_status("down")
        interfaces["up"] += up
        interfaces["down"] += down
        interfaces["other"] += len(device.statuses) - up - down

    violations = []
    for device in devices:
        # unknown_role: role is not a key of min_os
        if "min_os" in policy:
            if device.role not in policy["min_os"]:
                violations.append(
                    {"device": device.id, "type": "unknown_role", "role": device.role}
                )

        # missing_owner: owner required but empty
        if policy.get("require_owner") is True and device.owner == "":
            violations.append({"device": device.id, "type": "missing_owner"})

        # too_many_down: more down interfaces than allowed
        if "max_down_interfaces" in policy:
            down = device.count_status("down")
            if down > policy["max_down_interfaces"]:
                violations.append(
                    {"device": device.id, "type": "too_many_down", "down": down}
                )

    bad_ids = []
    for violation in violations:
        bad_ids.append(violation["device"])

    compliant_ids = []
    for device in devices:
        if device.id not in bad_ids:
            compliant_ids.append(device.id)

    report = {
        "site": root.get("site"),
        "total_devices": len(devices),
        "skipped_devices": skipped,
        "roles": roles,
        "interfaces": interfaces,
        "violations": violations,
        "compliant": sorted(compliant_ids),
    }

    with open("audit.json", "w") as f:
        json.dump(report, f, indent=2)

    print("Audited", len(devices), "devices, skipped", skipped)
    print("Violations found:", len(violations))

if __name__ == "__main__":
    main()