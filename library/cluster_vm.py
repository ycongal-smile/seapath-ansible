#!/usr/bin/env python3

# Copyright (C) 2021, RTE (http://www.rte-france.com)
# SPDX-License-Identifier: Apache-2.0

ANSIBLE_METADATA = {
    "metadata_version": "1.0",
    "status": ["preview"],
    "supported_by": "seapath",
}


__metaclass__ = type

DOCUMENTATION = r"""
---
module: cluster_vm

short_description: Manages virtual machines on a SEAPATH cluster

version_added: "2.9"

author:
    - "Mathieu Dupré (mathieu.dupre@savoirfairelinux.com)"
    - "Albert Babí Oller (albert.babi@savoirfairelinux.com)"

supported_by: seapath

description: This module manages virtual machines on a SEAPATH cluster.

options:
  name:
    description:
      - Name of the guest VM being managed
      - This option is required unless I(command) is C(list_vms)
      - Name must be composed of letters and numbers only
    type: str
    aliases:
      - guest
  command:
    description:
      - The action to perform
      - C(create)  Create and start a new VM. Require arguments I(name), I(xml)
        , I(system_image)
      - C(remove)  Remove a VM with its data. Require arguments I(name)
      - C(list_vms)  List all the defined VMs in the cluster
      - C(start)  Start or resume a VM. Require arguments I(name)
      - C(status) Get the status of a VM. Require arguments I(name)
      - C(stop)  Gracefully stop a VM. Require arguments I(name)
      - C(clone) Create a VM based on other VM. Require arguments I(name),
        I(src_name), I(xml)
      - C(enable)  Enable a VM. Require arguments I(name)
      - C(disable)  Disable a VM. Require arguments I(name)
      - C(list_snapshots)  List all snapshots of a VM. Require arguments
        I(name)
      - C(create_snapshot) Create a snapshot of a VM. Require arguments I(name)
        , I(snapshot_name)
      - C(remove_snapshot) Delete a snapshot of a VM. Require arguments I(name)
        , I(snapshot_name)
      - C(purge_image) Delete all snapshots (or optionally the ones filtered by
        number or date) of a VM. Require arguments I(name)
      - C(rollback_snapshot) Restore the VM in its previous state using a
        snapshot. Require arguments I(name), I(snapshot_name)
      - C(list_metadata) List all metadatas associated to a VM. Require
        arguments I(name)
      - C(get_metadata) Get the given metadata associated to a VM. Require
        arguments I(name), I(metadata_name)
    choices: [ create, remove, list_vms, start, status, stop, clone,
    list_snapshots, create_snapshot,remove_snapshot, rollback_snapshot,
    purge_image, list_metadata, get_metadata, disable, enable]
    type: str
  xml:
    description:
      - Libvirt XML config used if I(command) is C(create) or C(clone)
      - It will be used by the Libvirt define command
      - It must be raw XML content (that can be obtained by using C(lookup))
        and not a reference to a file
    type: str
  system_image:
    description:
      The VM system image disk in qcow2 format to import if I(command) is C(
      create)
    type: path
  force:
    description:
      - Force an action to be performed
      - Relevant if I(command) is C(create), C(clone), C(snapshot_create)
        or C(stop)
    type: bool
    default: false
  src_name:
    description:
      - Name of the VM to clone
      - This option is required if I(command) is C(clone)
    type: str
  snapshot_name:
    description:
      - Name of the snapshot
      - This option is required if I(command) is C(create_snapshot),
        C(remove_snapshot) or C(rollback_snapshot)
    type: str
  preferred_host:
    description:
      - Deploy the VM on the given host in priority
      - Optional parameter relevant only if I(command) is C(create) or C(clone)
    type: str
  pinned_host:
    description:
      - Pin the VM on the given host
      - Optional parameter relevant only if I(command) is C(create) or C(clone)
    type: str
  clear_constraint:
    description:
      - Do not keep source location constraint
      - Optional parameter relevant only if I(command) is C(clone)
    type: bool
    default: false
  metadata_name:
    description:
      - Name of a metadata key
      - This option is required if I(command) is C(get_metadata)
    type: str
  metadata:
    description:
      - Metadata in format key, value to store in the VM
      - This parameter is optional if the I(command) is C(create) or
        C(clone)
      - Metadata key must be composed of letters and numbers only
    type: dict
  purge_date:
    description:
      - Date until the snapshots must be removed
      - This parameter is optional if I(command) is C(purge)
      - It cannot be used if I(purge_number) is set
    type: dict
    suboptions:
      date:
        description:
          - Date in format YYYY-MM-DD
        type: str
      iso_8601:
        description:
          - Date and time represented in international ISO 8601 format. Time
            zone information is ignored
        type: str
      posix:
        description:
          - Number of milliseconds that have elapsed since 00,00,00, 1 January
            1970
        type: int
      time:
        description:
          - Time in format HH:MM
        type: str
  purge_number:
    description:
      - Number of snapshots to delete starting with the oldest
      - This parameter is optional if I(command) is C(purge)
      - Cannot be used if I(purge_date) is set
    type: int

requirements:
    - python >= 3.7
    - librbd
    - libvirt
    - vm_manager
"""


EXAMPLES = r"""
# Create and start a VM
- name: Create and start guest0
  cluster_vm:
    name: guest0
    command: create
    system_image: my_disk.qcow2
    xml: "{{ lookup('file', 'my_vm_config.xml', errors='strict') }}"
    metadata:
        myMetadata: value
        anotherMetadata: value

# Remove a VM
- name: Remove guest0
  cluster_vm:
    name: guest0
    command: remove

# List VM
- name: List all VMs
  cluster_vm:
    command: list_vms

# Start a VM
- name: Start guest0
  cluster_vm:
    name: guest0
    command: start

# Stop a VM
- name: Stop guest0
  cluster_vm:
    name: guest0
    command: stop

# Force stopping (power off) a VM
- name: Stop guest0
  cluster_vm:
    name: guest0
    command: stop
    force: true

# Enable a VM
- name: Enable guest0
  cluster_vm:
    name: guest0
    command: enable

# Disable a VM
- name: Disable guest0
  cluster_vm:
    name: guest0
    command: disable

# Clone a VM
- name: Clone guest0 into guest1
  cluster_vm:
    name: guest1
    src_name: guest0
    command: clone
    xml: "{{ lookup('template', 'my_vm_config.xml', errors='strict') }}"

# Create a VM snapshot
- name: Create a snapshot of guest0
  cluster_vm:
    name: guest0
    command: create_snapshot
    snapshot_name: snap1

# Delete a VM snapshot
- name: Remove snap1 snapshot of guest0
  cluster_vm:
    name: guest0
    command: remove_snapshot
    snapshot_name: snap1

# Remove all snapshots
- name: Remove all snapshots of guest0
  cluster_vm:
    name: guest0
    command: purge_image

# Remove old snapshots
- name: Remove snapshots of guest0 older than January 24th 2021 8:00 AM
  cluster_vm:
    name: guest0
    command: purge_image
    purge_date:
        date: '2021-01-24'
        time: '08:00'

# Restore a VM from a snapshot
- name: Rollback guest0 into snapshot snap1
  cluster_vm:
    name: guest0
    command: rollback_snapshot
    snapshot_name: snap1

# List all snapshots stored in a VM
- name: List snapshots of guest0
  cluster_vm:
    name: guest0
    command: list_snapshots

# List metadata stored in a VM
- name: List guest0 metadata
  cluster_vm:
    name: guest0
    command: list_metadata

# Get the value of a metadata field
- name: Get metadata test_metadata stored on guest0
  cluster_vm:
    name: guest0
    command: get_metadata
    metadata_name: test_metadata
"""

RETURN = """
# For list_vms command
list_vms:
    description: The list of VMs defined on the remote cluster returned by the
                 list_vms command
    type: list
    sample: [
        "guest0",
        "guest1"
    ]
    returned: success
# For status command
status:
    description: The status of the VM, among Starting, Started, Paused,
                 Stopped,Stopping, FAILED, Disabled and Undefined return by the
                 status command
    type: str
    sample: "started"
    returned: success
# For get_metadata command
metadata_value:
    description: The metadata returned by the get_metadata command
    type: str
    sample: "my metadata value"
    returned: success
# For list_metadata command
list_metadata:
    description: The metadata list returned by the list_metadata command
    type: list
    sample: [
        "name",
        "xml",
        "other metadata"
    ]
    returned: success
# for list_snapshots command
list_snapshots:
    description: The napshots list returned by the list_snapshots command
    type: list
    sample: [
        "snapshot1",
        "snapshot2",
    ]
    returned: success
"""

import os
import traceback
import datetime
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native

try:
    import vm_manager
except ImportError:
    HAS_VM_MANAGER = False
else:
    HAS_VM_MANAGER = True

commands_list = [
    "create",
    "remove",
    "start",
    "stop",
    "list_vms",
    "enable",
    "disable",
    "status",
    "clone",
    "create_snapshot",
    "remove_snapshot",
    "list_snapshots",
    "rollback_snapshot",
    "purge_image",
    "list_metadata",
    "get_metadata",
]


def run_module():
    def check_parameters(parameters, commands_list):
        if command in commands_list:
            for var_name, value in parameters.items():
                if not value:
                    module.fail_json(
                        msg="`{}` is required when `command` is `{}`".format(
                            var_name, command
                        )
                    )

    module_args = dict(
        command=dict(type="str", required=True, choices=commands_list),
        name=dict(type="str", required=False, aliases=["guest"]),
        xml=dict(type="str", required=False),
        data_disk=dict(type="str", required=False),
        force=dict(type="bool", required=False, default=False),
        enable=dict(type="bool", required=False, default=True),
        system_image=dict(type="str", required=False),
        src_name=dict(type="str", required=False),
        metadata_name=dict(type="str", required=False),
        snapshot_name=dict(type="str", required=False),
        metadata=dict(type="dict", require=False),
        purge_date=dict(
            type=dict,
            require=False,
            options=dict(
                date=dict(type="str"),
                iso_8601=dict(type="str"),
                posix=dict(type="int"),
                time=dict(type="str"),
            ),
        ),
        purge_number=dict(type="int", require=False),
        preferred_host=dict(type="str", require=False),
        pinned_host=dict(type="str", require=False),
        clear_constraint=dict(type="bool", required=False, default=False),
    )
    result = {}
    required = [
        ("command", "create", ("name", "xml", "system_image")),
        ("command", "clone", ("name", "src_name")),
        ("command", "remove", ("name",)),
        ("command", "start", ("name",)),
        ("command", "stop", ("name",)),
        ("command", "status", ("name",)),
        ("command", "enable", ("name",)),
        ("command", "disable", ("name",)),
        ("command", "list_metadata", ("name",)),
        ("command", "get_metadata", ("name", "metadata_name")),
        ("command", "purge_image", ("name",)),
        ("command", "create_snapshot", ("name", "snapshot_name")),
        ("command", "remove_snapshot", ("name", "snapshot_name")),
        ("command", "rollback_snapshot", ("name", "snapshot_name")),
        ("command", "list_snapshots", ("name",)),
    ]
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=required,
        mutually_exclusive=[("purge_date", "purge_number")],
    )
    if not HAS_VM_MANAGER:
        module.fail_json(
            msg="The `vm_manager` module is not importable. Check the "
            "requirements."
        )
    args = module.params
    command = args.get("command", None)
    vm_name = args.get("name", None)
    vm_config = args.get("xml", None)
    system_image = args.get("system_image", None)
    force = args.get("force", False)
    enable = args.get("enable", True)
    src_name = args.get("src_name", None)
    metadata_name = args.get("metadata_name", None)
    metadata = args.get("metadata", {})
    snapshot_name = args.get("snapshot_name", None)
    purge_date = args.get("purge_date", None)
    purge_number = args.get("purge_number", None)
    preferred_host = args.get("preferred_host", None)
    pinned_host = args.get("pinned_host", None)
    clear_constraint = args.get("clear_constraint", False)

    vm_name_command_list = commands_list.copy()
    vm_name_command_list.remove("list_vms")
    check_parameters({"name": vm_name}, vm_name_command_list)
    check_parameters(
        {"system_image": system_image, "vm_config": vm_config}, ["create"]
    )
    check_parameters({"src_name": src_name}, ["clone"])
    check_parameters({"metadata_name": metadata_name}, ["get_metadata"])
    check_parameters(
        {"snapshot_name": snapshot_name},
        ["create_snapshot", "remove_snapshot", "rollback_snapshot"],
    )
    try:
        if command == "list_vms":
            result["list_vms"] = vm_manager.list_vms()
        elif command == "create":
            if not os.path.isfile(system_image):
                module.fail_json(
                    msg="`system_image` doesn't exist or is not a file`"
                )
            vm_manager.create(
                vm_name,
                vm_config,
                system_image,
                force=force,
                enable=enable,
                metadata=metadata,
                preferred_host=preferred_host,
                pinned_host=pinned_host,
            )
        elif command == "clone":
            vm_manager.clone(
                src_name,
                vm_name,
                base_xml=vm_config,
                force=force,
                enable=enable,
                metadata=metadata,
                preferred_host=preferred_host,
                pinned_host=pinned_host,
                clear_constraint=clear_constraint,
            )
        elif command == "remove":
            vm_manager.remove(vm_name)
        elif command == "start":
            vm_manager.start(vm_name)
        elif command == "stop":
            vm_manager.stop(vm_name)
        elif command == "disable":
            vm_manager.disable_vm(vm_name)
        elif command == "status":
            result["status"] = vm_manager.status(vm_name)
        elif command == "enable":
            vm_manager.enable_vm(vm_name)
        elif command == "status":
            result["status"] = vm_manager.status(vm_name)
        elif command == "create_snapshot":
            vm_manager.create_snapshot(vm_name, snapshot_name)
        elif command == "purge_image":
            date_time = None
            if purge_date:
                if (
                    ("date" in purge_date and "time" not in purge_date)
                    or "time" in purge_date
                    and "date" not in purge_date
                ):
                    module.fail_json(
                        msg="purge_date argument error: date and time must be"
                        "set together"
                    )
                if (
                    "date" in purge_date
                    and ("posix" in purge_date or "iso_8601" in purge_date)
                    or "posix" in purge_date
                    and "iso_8601" in purge_date
                ):
                    module.fail_json(
                        msg="purge_date argument error: date/time, iso_8601"
                        " and posix and mutually exclusive"
                    )
                if "date" in purge_date:
                    date = purge_date["date"]
                    time = purge_date["time"]
                    date_time = datetime.datetime.combine(
                        datetime.date.fromisoformat(date),
                        datetime.time.fromisoformat(time),
                    )
                elif "iso_8601" in purge_date:
                    date_time = datetime.datetime.fromisoformat(
                        purge_date["iso_8601"]
                    )
                elif "posix" in purge_date:
                    date_time = datetime.datetime.fromtimestamp(
                        purge_date["posix"]
                    )
            vm_manager.purge_image(
                vm_name, date=date_time, number=purge_number
            )
        elif command == "remove_snapshot":
            vm_manager.remove_snapshot(vm_name, snapshot_name)
        elif command == "list_snapshots":
            result["list_snapshot"] = vm_manager.list_snapshots(vm_name)
        elif command == "rollback_snapshot":
            vm_manager.rollback_snapshot(vm_name, snapshot_name)
        elif command == "list_metadata":
            result["list_metadata"] = vm_manager.list_metadata(vm_name)
        elif command == "get_metadata":
            result["metadata_value"] = vm_manager.get_metadata(
                vm_name, metadata_name
            )
        else:
            module.fail_json(
                msg="{} `command` is not implemented yet".format(command)
            )
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=traceback.format_exc())

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
