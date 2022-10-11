#!/usr/bin/env python

import os
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

def main():
    server_json_list = []
    ks_auth = mk_auth()
    ks_session = session.Session(ks_auth)
    ks_client = keystone_client.Client(session=ks_session)
    nova_client = client.Client(version=2,session=ks_session)

    servers = nova_client.servers.list(search_opts={'all_tenants':1})
    for server in servers:
        networks = nova_client.servers.ips(server.id)
        server_json = { "ID": server.id,
                        "Name": server.name,
                        "Status": server.status,
                        "Networks": networks,
                        "Image": server.image,
                        "Flavor": server.flavor }
        server_json_list.append(server_json)
    server_json_str = json.dumps(server_json_list)
    print(server_json_str)

if __name__ == "__main__":
    main()
