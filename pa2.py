# Name: Jabir Rahman
# Student ID: 101374024 (Carleton)

import sys
import json
import yaml
import xml.etree.ElementTree as ET


class InputError(Exception):
    """Raised when an input file is missing or invalid."""


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


def version_parts(text):
    """Turn a version like '15.10' into a list of numbers [15, 10]."""
    parts = []
    for piece in str(text).split("."):
        parts.append(int(piece))
    return parts


def is_older(found, required):
    """Return True if version 'found' is lower than version 'required'."""
    a = version_parts(found)
    b = version_parts(required)
    # pad the shorter list with zeros so 9.1.0 equals 9.1
    while len(a) < len(b):
        a.append(0)
    while len(b) < len(a):
        b.append(0)
    return a < b


def load_inventory(path):
    """Read the XML file and return its root element."""
    try:
        return ET.parse(path).getroot()
    except FileNotFoundError:
        raise InputError(path + ": file not found")
    except ET.ParseError:
        raise InputError(path + ": not valid XML")
    except OSError:
        raise InputError(path + ": cannot be read")


def load_policy(path):
    """Read the YAML file and return the policy as a dictionary."""
    try:
        with open(path) as f:
            policy = yaml.safe_load(f)
    except FileNotFoundError:
        raise InputError(path + ": file not found")
    except yaml.YAMLError:
        raise InputError(path + ": not valid YAML")
    except OSError:
        raise InputError(path + ": cannot be read")

    if policy is None:
        policy = {}
    if not isinstance(policy, dict):
        raise InputError(path + ": policy must be a mapping")
    return policy


def run(inventory_file, policy_file):
    """Read both files, check the policy, and write audit.json."""
    root = load_inventory(inventory_file)
    policy = load_policy(policy_file)

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

    min_os = policy.get("min_os")
    violations = []
    for device in devices:
        known_role = True

        # unknown_role: role is not a key of min_os (no OS check then)
        if isinstance(min_os, dict) and device.role not in min_os:
            known_role = False
            violations.append(
                {"device": device.id, "type": "unknown_role", "role": device.role}
            )

        # os_outdated: version lower than the minimum for its role
        if isinstance(min_os, dict) and known_role:
            required = str(min_os[device.role])
            try:
                if is_older(device.os, required):
                    violations.append(
                        {
                            "device": device.id,
                            "type": "os_outdated",
                            "found": device.os,
                            "required": required,
                        }
                    )
            except ValueError:
                raise InputError("bad version number for device " + device.id)

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


def main():
    """Check the arguments, run the audit, and handle errors."""
    if len(sys.argv) != 3:
        print("usage: python pa2.py DEVICES.xml POLICY.yaml")
        sys.exit(2)

    try:
        run(sys.argv[1], sys.argv[2])
    except InputError as error:
        print("Error:", error)
        sys.exit(1)


if __name__ == "__main__":
    main()