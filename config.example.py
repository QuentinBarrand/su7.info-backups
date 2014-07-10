debug = False

# Array of MySQL instances that should be savec
mysql_servers = [{
    'host': '',
    'port': '',
    'user': '',
    'password': ''
}]

# List of directories to save
dirs_to_backup = [
    ''
]

# Directory in which the .tar.gz backups will be saved
output_dir = '/var/backup/'

# List of FTP repositories where backups should be copied
ftp_servers = [{
    'host': '',
    'port': '',
    'user': '',
    'password': '',
    'directory': ''
}]

# Time to keep the backup, in days
keeptime = 7

# Prefix in archive's filename
archive_prefix = ''