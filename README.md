# openstack-api-backup

Uses python-openstackclient to periodicailly export json versions of resources
in OpenStack APIs (e.g. servers, volumes, networks, etc,). Backups are
compressed and shipped to S3-compatible storage.
