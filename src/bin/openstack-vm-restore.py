#!/usr/bin/env python

import os
import sys
import json

from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client as keystone_client
from novaclient import client

def mk_auth():
    auth_url = os.environ['OS_AUTH_URL']
    ac_id = os.environ['OS_APPLICATION_CREDENTIAL_ID']
    ac_secret = os.environ['OS_APPLICATION_CREDENTIAL_SECRET']

    auth = v3.ApplicationCredential(
        auth_url=auth_url,
        application_credential_id=ac_id,
        application_credential_secret=ac_secret,
    )
    return(auth)

def main(input_file):
    server_json_list = []
    ks_auth = mk_auth()
    ks_session = session.Session(ks_auth)
    ks_client = keystone_client.Client(session=ks_session)
    nova_client = client.Client(version=2,session=ks_session)

    running_servers = {}
    saved_servers = {}
    with open(input_file,'r',encoding='utf-8') as f:
        json_data = json.load(f)
    for server in json_data:
        saved_servers[server['ID']] = server['Status']

    servers = nova_client.servers.list(search_opts={'all_tenants':1})
    for server in servers:
        result = "DELETED"
        os_cmd = ""
        if saved_servers.get(server.id):
            if saved_servers[server.id] == server.status:
                result = "MATCH"
            else:
                result = "CHANGE="+str(saved_servers[server.id]+ \
                        "->"+server.status)
                if saved_servers[server.id] == "ACTIVE" and \
                        server.status == "SHUTOFF":
                   os_cmd = "openstack server start "+server.id
        else:
            result = "NEW"
        running_servers[server.id]=server.status
        print("SERVER:"+server.id+" RESULT:"+result+" NAME:"+server.name)
        if os_cmd != "":
            print("    CMD:"+os_cmd)

    for srv_id,status in saved_servers.items():
        if not running_servers.get(srv_id):
            print("SERVER:"+srv_id+" MISSING="+status+"->NONE")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        print("Need to provide saved state file")
        exit(1)
    main(input_file)

