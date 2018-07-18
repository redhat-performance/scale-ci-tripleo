#!/usr/bin/env python
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import argparse
import os
import sys
import time

from ironicclient import client

"""
Script to pin nodes based on a hint within the ipmi hostname.

Examples:
pin.py -n 3 -p controller --hint 1029p -c
pin.py -n 39 -p novacompute --hint 1029p
pin.py -n 5 -p cephstorage --hint 1029u

Example pins 3 1029p nodes as controllers, 39 as compute nodes, and 5 1029u as ceph storage nodes.
"""


def set_capablities(ironic, uuid, capabilities):
    """Sets or Capabilities on OpenStack Ironic Node"""
    patch = [
        {
            "op": "replace",
            "path": "/properties/capabilities",
            "value": capabilities,
        }
    ]
    ironic.node.update(uuid, patch=patch)

start_time = time.time()

parser = argparse.ArgumentParser(
        description="Pin nodes to node type based on hint", prog="pin.py")
parser.add_argument("-n", "--nodes", type=int, required=True, help="Number of Nodes to pin")
parser.add_argument("--hint", type=str, required=True, help="Hint in ironic node properties")
parser.add_argument("-p", "--pin", type=str, required=True, help="Role to pin nodes")
parser.add_argument("-c", "--clear", action="store_true", default=False, help="Clear existing pins")

cliargs = parser.parse_args()

print "INFO :: pin.py node count: {}".format(cliargs.nodes)
print "INFO :: pin.py hint: {}".format(cliargs.hint)
print "INFO :: pin.py pin: {}".format(cliargs.pin)
print "INFO :: pin.py clear: {}".format(cliargs.clear)

if "OS_PROJECT_NAME" in os.environ:
    project_name = os.environ["OS_PROJECT_NAME"]
elif "OS_TENANT_NAME" in os.environ:
    project_name = os.environ["OS_TENANT_NAME"]
else:
    print "ERROR :: Missing OS_PROJECT_NAME or OS_TENANT_NAME in rc file"
    exit(1)

user_domain_name = None
if "OS_USER_DOMAIN_NAME" in os.environ:
    user_domain_name = os.environ["OS_USER_DOMAIN_NAME"]
project_domain_name = None
if "OS_PROJECT_DOMAIN_NAME" in os.environ:
    project_domain_name = os.environ["OS_PROJECT_DOMAIN_NAME"]

# Establish Ironic API Connection
ironic = client.get_client(
        1, os_username=os.environ["OS_USERNAME"], os_password=os.environ["OS_PASSWORD"],
        os_auth_url=os.environ["OS_AUTH_URL"], os_project_name=project_name,
        os_user_domain_name=user_domain_name, os_project_domain_name=project_domain_name)

# Get Ironic nodes (once)
nodes = ironic.node.list()

# Clear Ironic Node Pinning
if cliargs.clear:
    print "INFO :: Clearing existing pins"
    for node in nodes:
        properties = ironic.node.get(node.uuid).properties
        if "node" in str(properties["capabilities"]):
            ipmi_addr = ironic.node.get(node.uuid).to_dict()["driver_info"]["ipmi_address"]
            print "INFO :: Node {} ({}) with pin: {}".format(
                    ipmi_addr, node.uuid, properties["capabilities"])
            data = properties["capabilities"].split(",")
            new_cap = ",".join([item for item in data if "node" not in item])
            print "INFO :: Setting capabilities: {} for node {} ({})".format(
                    new_cap, ipmi_addr, node.uuid)
            set_capablities(ironic, node.uuid, new_cap)
    print "INFO :: Finished Clearing existing pins"

# Perform requested pinning based on a hint
for node_idx in range(cliargs.nodes):
    node_pinned = False
    print "INFO :: Pinning Node: {}".format(node_idx)
    for node in nodes:
        properties = ironic.node.get(node.uuid).properties
        if "node" not in str(properties["capabilities"]):
            ipmi_addr = ironic.node.get(node.uuid).to_dict()["driver_info"]["ipmi_address"]
            if cliargs.hint in ipmi_addr:
                print "INFO :: Node {} ({}) pinning to: {}".format(
                        ipmi_addr, node.uuid, properties["capabilities"])
                data = properties["capabilities"].split(",")
                data.append("node:{}-{}".format(cliargs.pin, node_idx))
                new_cap = ",".join(data)
                print "INFO :: Setting capabilities: {} for node {} ({})".format(
                        new_cap, ipmi_addr, node.uuid)
                set_capablities(ironic, node.uuid, new_cap)
                node_pinned = True
                break
    # Exit/Fail if we can not pin a node
    if not node_pinned:
        print "ERROR :: Could not pin: {} to hint: {}".format(node_idx, cliargs.hint)
        exit(1)

print "INFO :: Took {} to pin nodes.".format(round(time.time() - start_time, 2))
exit(0)
