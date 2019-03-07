# openstack-orphaned-resource
This script will list the resources that are allocated to non-existing Project IDs.

$ python openstack_orphaned_resource.py <object> 

where object is one or more of "'networks', 'routers', 'subnets', 'floatingips', 'servers' or 'all'"
