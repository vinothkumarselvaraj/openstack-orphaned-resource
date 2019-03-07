#!/usr/bin/env python
"""openstack_orphaned_resource.py: This script will list the resources that are allocated to non-existing Project IDs."""
__author__      = "Vinoth Kumar Selvaraj"

import os
import sys
from keystoneauth1 import identity
from keystoneauth1 import session
from keystoneclient.v3 import client
from neutronclient.v2_0 import client as nclient
from novaclient import client as novaclient

def usage():
    print "listorphans.py <object> where object is one or more of",
    print "'networks', 'routers', 'subnets', 'floatingips', 'ports', 'servers', 'secgroup' or 'all'"

username=os.environ['OS_USERNAME']
password=os.environ['OS_PASSWORD']
project_name=os.environ['OS_PROJECT_NAME']
project_domain_id='default'
user_domain_id='default'
auth_url=os.environ['OS_AUTH_URL']
auth = identity.Password(auth_url=auth_url, username=username, password=password, project_name=project_name, project_domain_id=project_domain_id, user_domain_id=user_domain_id)

sess = session.Session(auth=auth)
keystone = client.Client(session=sess)
neutron = nclient.Client(session=sess)
nova = novaclient.Client(2.0, session=sess)

def get_projectids():
    return [project.id for project in keystone.projects.list()]

def get_orphaned_neutron_objects(object):
    projectids = get_projectids()
    projectids.append("")
    objects = getattr(neutron, 'list_' + object)()
    orphans = []
    for object in objects.get(object):
        if object['tenant_id'] not in projectids:
            orphans.append(object['id'])
    return orphans

def get_orphaned_nova_objects():
    projectids = get_projectids()
    projectids.append("")
    orphans = []
    for server in nova.servers.list(search_opts={'all_tenants': 1}):
        if server.tenant_id not in projectids:
           orphans.append(server.id)
    return orphans

def get_orphaned_security_group_objects():
    projectids = get_projectids()
    projectids.append("")
    orphans = []
    for secgroup in nova.security_groups.list(search_opts={'all_tenants': 1}):
        if secgroup.tenant_id not in projectids:
           orphans.append(secgroup.id)
    return orphans

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'all':
            objects = [ 'networks', 'routers', 'subnets', 'floatingips', 'ports', 'servers', 'secgroup' ]
        else:
            objects = sys.argv[1:]
        for object in objects:
            if object=="servers":
              orphans = get_orphaned_nova_objects()
              print len(orphans), 'orphan(s) found of type', object
              print '\n'.join(map(str, orphans))
            elif object=="secgroup":
              orphans = get_orphaned_security_group_objects()
              print len(orphans), 'orphan(s) found of type', object
              print '\n'.join(map(str, orphans))
            else:
              orphans = get_orphaned_neutron_objects(object)
              print len(orphans), 'orphan(s) found of type', object
              print '\n'.join(map(str, orphans))
    else:
        usage()
        sys.exit(1)
