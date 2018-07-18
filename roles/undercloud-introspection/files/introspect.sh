#!/bin/bash

set -eux

### --start_docs
## Prepare images for deploying the overcloud
## ==========================================

## Prepare Your Environment
## ------------------------

## * Source in the undercloud credentials.
## ::

source /home/stack/stackrc

## * Perform introspected check on nodes in manageable state.
##   Return 0 if all the nodes were introspected, 1 otherwise.
##   Set the nodes that have been introspected as available.
## ::
check_introspection_done()
{
    local failed=0

    for node in `openstack baremetal node list -f json | jq -r '.[]| select(.["Provisioning State"] == "manageable")| .["UUID"]'`; do
        local i_status=$(openstack baremetal introspection status $node --format value -c finished)
        echo "Introspection for $node: $i_status"
        if [ "$i_status" = "True" ]; then
            openstack baremetal node provide $node
        else
            echo "Introspection failed for $node" >&2
            failed=1
        fi
    done
    return $failed
}

## * Introspect all manageable nodes with a caller provided timeout.
##   then move all nodes that power off after a successful introspection
##   back to available so we don't introspect them again. This is useful
##   for large deployments (think 10+ nodes) where bulk introspection
##   can be troublesome. It's also useful in environments where connection
##   problems may spuriously fail a deployment. Related-Bug: #1651127
## ::
introspect()
{
    local tmout="${1:-15m}"	# introspection and cleaning timeout
    local bulk=20		# bulk of nodes to introspect at a time
    local clean_ret=0
    local i node

    clean $tmout || clean_ret=$?	# Cleaning failures are silently ignored here, but reported below.
    echo "Baremetal node cleaning finished: $clean_ret." >&2

    # Exclude the already available nodes
    set -- `openstack baremetal node list -f json | jq -r '.[]| select(.["Provisioning State"] == "manageable")| .["UUID"]'`

    while [ "${1-}" ] ; do
        i=$bulk
        while [ $i -gt 0 ] && [ "${1-}" ]; do
            node="$1"
            openstack baremetal introspection start $node
            ((i--))
            shift
            sleep 2
        done

        # Wait with a timeout for the introspection to finish on the last node where the introspection started
        set +e
        timeout $tmout bash -c -- "source $HOME/stackrc; \
            while [ \$(openstack baremetal introspection status $node --format value -c finished) = False ]; do \
                sleep 30; \
            done"
        set -e
    done

    # Make introspected nodes available for deployment
    check_introspection_done || return $?
}

clean_tmout()
{
    local tmout="${1:-15m}"	# cleaning and "clean wait" timeout

    set +e
    # Power State "power off" -> Provisioning State "cleaning";  Power State "power on" -> Provisioning State "clean wait"
    timeout $tmout bash -c -- \
        'source $HOME/stackrc; \
         while [ $(openstack baremetal node list -f json | jq -r ".[]| select((.[\"Provisioning State\"] == \"cleaning\") or (.[\"Provisioning State\"] == \"clean wait\" ))| .[\"UUID\"]" | wc -l) -gt 0 ]; do \
             sleep 30s; \
         done'
    set -e
}

clean_devices_metadata()
{
    openstack baremetal node clean $1 --clean-steps '[{"interface": "deploy", "step": "erase_devices_metadata"}]'
}

## * Attempt to correct hardware cleaning failures.
## ::
clean()
{
    local tmout="${1:-15m}"	# clean-wait timeout
    local failed=0

    for node in `openstack baremetal node list -f json | jq -r '.[]| select(.["Power State"] == "power off")| select(.["Provisioning State"] == "manageable")|.["UUID"]'`; do
       clean_devices_metadata $node
       sleep 10			# TODO: is this really necessary?
    done

    for try in 1 last; do
        # Getting nodes out of clean-wait is a real pain. Check if a longer timeout is justified on your hardware
        # but generally 15m is excessive.
        clean_tmout $tmout
        for node in `openstack baremetal node list -f json | jq -r '.[]| select(.["Provisioning State"] == "clean failed")| .["UUID"]'`; do
            openstack baremetal node maintenance unset $node
            openstack baremetal node manage $node
            if [ "$try" = "last" ]; then
                failed=1
                echo "Cleaning failed for $node" >&2
            else
                sleep 10	# TODO: is this really necessary?
                clean_devices_metadata $node
            fi
        done
        for node in `openstack baremetal node list -f json | jq -r '.[]| select(.["Provisioning State"] == "clean wait")| .["UUID"]'`; do
            openstack baremetal node maintenance set $node
            openstack baremetal node abort $node
            openstack baremetal node maintenance unset $node
            openstack baremetal node manage $node
            if [ "$try" = "last" ]; then
                failed=1
                echo "Cleaning aborted for $node" >&2
            else
                sleep 10	# TODO: is this really necessary?
                clean_devices_metadata $node
            fi
        done
    done

    return $failed
}

## * Introspect hardware attributes of nodes in a robust manner
##   retrying up to three times on any given node. This should
##   only be used in cases where deployment using bulk introspection
##   has reliability issues.
## ::

for node in `openstack baremetal node list -f json | jq -r '.[]| select(.["Provisioning State"] == "available")| .["UUID"]'`; do
    openstack baremetal node manage $node
done

introspect 15m || introspect 15m || introspect 15m

### --stop_docs
