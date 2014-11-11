#!/usr/bin/python
# -*- coding: utf-8 -*-

# Debug mode will be more verbose
debug = True

# A list of MySQL servers to dump.
mysql = {
    'enabled': True,
    'servers': [
        {
            'host': 'localhost',    # If no value is provided, we use 'localhost'
            'port': '3306',         # If no value is provided, we use 3306
            'user': 'root',         # If no value is provided, we use 'root'
            'password': ''
        }
    ]
}

# A list of directories to include into the backup archive
dirs_to_backup = [
    '/etc'
]

# A list of FTP to upload the archive to.
ftp = {
    'enabled': True,
    'servers': [
        {
            'host': '',
            'port': '21',
            'user': '',
            'password': '',
            'directory': ''
        }
    ]
}

# A list of Swift containers to upload the archive to.
swift = {
    'enabled': True,
    'servers': [
        {
            'name': '',             # The server name to display
            'authurl': '',          # OpenStack Keystone auth url (OS_AUTH_URL)
            'auth_version': '2.0',  # We use 2.0 authentication, do not change this line
            'user': '',             # Your OpenStack username (OS_USERNAME)
            'key': '',              # Your password (OS_PASSWORD_INPUT)
            'tenant_name': '',      # Your project number, also called tenant name (OS_TENANT_NAME)
            'container_name': '',   # The Swift container in which you want to store archives
            'autocreate': True      # Should we autocreate the container if it does not exist ?
        }
    ]
}

# Directory in which the .tar.gz backups will be saved
output_dir = '/var/backup'

# Time to keep the backup, in days
keeptime = 7

# Prefix in archive's filename
archive_prefix = ''