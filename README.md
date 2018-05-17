# tripleo-quickstart-scalelab

Playbook to deploy Tripleo OpenStack on ScaleLab for OpenShift on OpenStack performance and scale testing.


## Deploy-scalelab.yaml

To be filled in

## Install Browbeat Monitoring

From CLI

```
$ cp hosts.example hosts
$ # Add Undercloud host to hosts
$ # Edit vars in install-browbeat.yaml or set Environment vars
$ ansible-playbook -i hosts install-browbeat.yaml
```

If as a Jenkins Job, define the following parameters:

```
DNS_SERVER
GRAPHITE
GRAPHITE_PREFIX
BROWBEAT_COLLECTD_COMPUTE
BROWBEAT_COLLECTD_RABBITMQ
BROWBEAT_COLLECTD_CEPH
```
