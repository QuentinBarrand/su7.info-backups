import datetime
import os
import shutil
import sys
import tarfile
import time

from tempfile import mkdtemp

import ftp
import mysql

try:
    from config import *
except:
    print 'Could not import settings ! Please check config.py.'
    sys.exit(2)

print 'Backup starting on ' + str(datetime.datetime.now())

# Start the counter
start = int(time.time())

# Create temporary directory
temp_dir = mkdtemp()

# MySQL

print '\n[MySQL]'

i = 0

for instance in MYSQL:
    db_list = mysql.get_db_list(instance)

    # If instance is not empty
    if db_list:
        print '\tInstance #' + str(i)

        instance_dir = temp_dir + '/db/mysql/instance' + str(i) + '/'
        os.makedirs(instance_dir)
        mysql.save_dbs(instance, db_list, instance_dir)

    i += 1

# ... the rest

print '\n[Archiving]'

# Create OUTPUT_DIR if it does not exist
if not os.path.isdir(OUTPUT_DIR):
    try:
        os.makedirs(OUTPUT_DIR)
    except:
        print 'The backup directory ' + OUTPUT_DIR + ' does not exist ' + \
              'and could not be created. Exiting.'
        sys.exit(1)

# Create the tar archive
print '\tCreating directory'
tar_file = OUTPUT_DIR + '/' + ARCHIVE_PREFIX + str(datetime.date.today()) + '.tar.gz'
tar = tarfile.open(tar_file, 'w:gz')

# Add databases into the archive
print '\tAdding database dumps'
tar.add(temp_dir)

# Add all the directories from config into the archive
print '\tAdding directories from configuration'
for directory in DIRS_TO_BACKUP:
    print '\t\t' + directory
    tar.add(directory)

tar.close()

shutil.rmtree(temp_dir)

print '\n\tArchive : ' + os.path.basename(tar_file) + ', size ' + str(os.path.getsize(tar_file) / 1000000) + ' MB.'

print '\n[Upload]'

for instance in FTP:
    ftp.upload(instance, tar_file)

print '\n[Delete old backups]'

archives_deleted = False

for archive in os.listdir(OUTPUT_DIR):
    archive_info = os.stat(OUTPUT_DIR + '/' + archive)
    
    # If archive is older than keeptime (in days)...
    if time.mktime(time.gmtime()) - archive_info.st_mtime > (KEEPTIME * 24 * 60 * 60):
        print '\tDeleting ' + archive
        
        print '\t\tLocal...'
        os.remove(OUTPUT_DIR + '/' + archive)

        for instance in FTP:
            ftp.delete_remote(instance, archive)
        
        archives_deleted = True

if not archives_deleted:
    print '\tNo archives were deleted.'

# Stop the counter
end = int(time.time())

print '\nBackup ending on ' + str(datetime.datetime.now())

minutes = (end - start) / 60
seconds = (end - start) - minutes * 60
print 'Time elapsed : ' + str(minutes) + ' min ' + str(seconds) + ' s.'