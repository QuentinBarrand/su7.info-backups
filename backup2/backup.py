import datetime
import os
import shutil
import sys
import tarfile

from tempfile import mkdtemp

import mysql
import ftp

try:
    from config import *
except:
    print 'Could not import settings ! Please check config.py.'
    sys.exit(2)

# Create temporary directory
temp_dir = mkdtemp()

print temp_dir

# MySQL

print '[MySQL]'

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

print '[Archiving]'

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

print '[Upload]'

for instance in FTP:
    ftp.upload(instance, tar_file)
