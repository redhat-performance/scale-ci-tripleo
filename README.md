# tripleo-quickstart-scalelab

Playbook to deploy Tripleo OpenStack on ScaleLab for OpenShift on OpenStack performance and scale testing.

## Deploying Undercloud and Overcloud

From CLI

```
$ cp hosts.example hosts
$ # Add Undercloud host to hosts
$ # Edit vars in vars/deploy.yml or define Environment vars
$ ansible-playbook -i hosts deploy-scalelab.yaml
```

If using environment variables (Ex Jenkins Job Parameters), define the following:

```
#
# OpenStack Version/Build Variables:
#
OSP_RHOS_RELEASE_URL
OSP_RHOS_VERSION
OSP_RHOS_RHEL_VERSION
OSP_RHOS_RELEASE_VERSION
OSP_RHOS_BUILD
#
# Undercloud Variables:
#
OSP_REBUILD_UNDERCLOUD
OSP_UNDERCLOUD_HOSTNAME
OSP_QUADS_TICKET_NUMBER
OSP_QUADS_FOREMAN_URL
OSP_STACK_PASSWORD
OSP_INSTACKENV_NO_INTROSPECTION
OSP_NODE_PROVIDE_TIMEOUT
OSP_INTROSPECTION
OSP_BULK_INTROSPECTION_TIMEOUT
OSP_INTROSPECTION_SCRIPT
OSP_NODE_CLEANING
#
# Overcloud Variables
#
OSP_INSTACKENV_JSON
OSP_CONTROLLER_TYPE
OSP_CEPHSTORAGE_TYPE
OSP_COMPUTE_TYPE
OSP_NUM_CONTROLLERS
OSP_NUM_CEPHSTORAGE
OSP_NUM_COMPUTE
#
# Undercloud and Overcloud Network Setup:
#
OSP_UNDERCLOUD_LOCAL_INTERFACE
OSP_NTP_SERVER
OSP_EXTERNAL_NETWORK_SETUP
OSP_DNS_SERVER
OSP_EXTERNAL_VLAN
OSP_EXTERNAL_NET_POOL_START
OSP_EXTERNAL_NET_POOL_END
OSP_EXTERNAL_NET_GATEWAY
OSP_EXTERNAL_NET_CIDR
OSP_EXTERNAL_NETWORK_VIP
OSP_FIP_POOL_START
OSP_FIP_POOL_END
OSP_UNDERCLOUD_PUBLIC_INTERFACE
OSP_UNDERCLOUD_PRIVATE_EXTERNAL_INTERFACE
OSP_PRIVATE_EXTERNAL_ADDRESS
OSP_PRIVATE_EXTERNAL_NETMASK
```

## Install Browbeat Monitoring

From CLI

```
$ cp hosts.example hosts
$ # Add Undercloud host to hosts
$ # Edit vars in vars/browbeat.yml or define Environment vars
$ ansible-playbook -i hosts install-browbeat.yaml
```

If as a Jenkins Job, define the following parameters:

```
BROWBEAT_DNS_SERVER
BROWBEAT_GRAPHITE_HOST
BROWBEAT_GRAPHITE_PREFIX
BROWBEAT_GRAFANA_HOST
BROWBEAT_GRAFANA_APIKEY
BROWBEAT_COLLECTD_COMPUTE
BROWBEAT_COLLECTD_RABBITMQ
BROWBEAT_COLLECTD_CEPH
```
