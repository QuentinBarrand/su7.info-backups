#!/usr/bin/python

import datetime
import os
import shutil
import sys
import tarfile
import time

from tempfile import mkdtemp

import ftp
import mysql

## Application's entry point.
def main():
    print 'Backup starting on ' + str(datetime.datetime.now())

    # Start the counter
    start = int(time.time())

    # Create temporary directory
    temp_dir = mkdtemp()

    # MySQL

    print '\n[MySQL]'

    i = 0

    for instance in MYSQL:
        instance_dir = temp_dir + '/db/mysql/instance' + str(i) + '/'
        os.makedirs(instance_dir)

        db_list = []

        print '\tInstance #' + str(i)

        try:
            db_list = mysql.get_db_list(instance)
            mysql.save_dbs(instance, instance_dir, all_dbs = False, db_list = db_list)
        except Exception as e:
            print "Could not get databases list. Dumping all databases now."
            mysql.save_dbs(instance, instance_dir, all_dbs = True)

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
        try:
            print '\tUploading to ' + instance['host']
            upload_time = ftp.upload(instance, tar_file)

            minutes = upload_time / 60
            seconds = upload_time - minutes * 60
            
            print '\tUpload completed in ' + str(minutes) + ' min ' + str(seconds) + ' s.'
        except Exception as e:
            print 'Error during upload :\n' + e.message


    print '\n[Delete old backups]'

    archives_deleted = False

    for archive in os.listdir(OUTPUT_DIR):
        archive_info = os.stat(OUTPUT_DIR + '/' + archive)
        
        # If archive is older than keeptime (in days)...
        if time.mktime(time.gmtime()) - archive_info.st_mtime > (KEEPTIME * 24 * 60 * 60):
            print '\tDeleting ' + archive
            
            print '\t\tLocal...'
            try:
                os.remove(OUTPUT_DIR + '/' + archive)
            except Exception as e:
                print 'Error during removal : '

            for instance in FTP:
                try:
                    print '\t\tFrom host ' + instance['host']
                    ftp.delete_remote(instance, archive)
                except Exception as e:
                    print 'Error during deletion :\n' + e.message
            
            archives_deleted = True

    if not archives_deleted:
        print '\tNo archives were deleted.'

    # Stop the counter
    end = int(time.time())

    print '\nBackup ending on ' + str(datetime.datetime.now())

    minutes = (end - start) / 60
    seconds = (end - start) - minutes * 60
    print 'Time elapsed : ' + str(minutes) + ' min ' + str(seconds) + ' s.'

if __name__ == "__main__":
    try:
        from config import *
    except:
        print 'Could not import settings ! Please check config.py.'
        sys.exit(2)

    main()