#!/usr/bin/python
# -*- coding: utf-8 -*-

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
    print 'Backup starting on %s' % str(datetime.datetime.now())

    # Start the counter
    start = int(time.time())

    # Create temporary directory
    temp_dir = mkdtemp()

    # MySQL
    if config.mysql['enabled']:
        print '\n[MySQL]'

        i = 0

        for settings in config.mysql['servers']:
            instance = mysql.Mysql(settings)

            instance_dir = os.path.join(temp_dir, 'db/mysql/instance', str(i))
            dump_filepath = os.path.join(instance_dir, 'all_databases.sql')

            os.makedirs(instance_dir)

            print '\tInstance %s' % str(i)

            for db in instance.get_db_list():
                print '\t\t%s' % db

            instance.save(dump_filepath)

            print '\n\tDump : %s (%s MB)' % (os.path.basename(dump_filepath), str(os.path.getsize(dump_filepath) / 1000000))

            i += 1

    # ... the rest

    print '\n[Archiving]'

    # Create output_dir if it does not exist
    if not os.path.isdir(config.output_dir):
        try:
            os.makedirs(config.output_dir)
        except:
            print 'The backup directory %s does not exist and could not be created. Exiting.' % config.output_dir
            sys.exit(1)

    # Create the tar archive
    print '\tCreating directory'
    tar_file = os.path.join(config.output_dir, config.archive_prefix + str(datetime.date.today()) + ".tar.gz")
    tar = tarfile.open(tar_file, 'w:gz')

    # Add databases into the archive
    if config.mysql['enabled']:
        print '\tAdding database dumps'
        tar.add(temp_dir)

    # Add all the directories from config into the archive
    if len(config.dirs_to_backup) > 0:
        print '\tAdding directories from configuration'
        for directory in config.dirs_to_backup:
            print '\t\t%s' % directory
            tar.add(directory)

    tar.close()

    shutil.rmtree(temp_dir)

    print '\n\tArchive : %s, size %s MB.' % (os.path.basename(tar_file), str(os.path.getsize(tar_file) / 1000000))

    print '\n[Upload]'

    # FTP
    if config.ftp['enabled']:
        for instance in config.ftp['servers']:
            try:
                print '\tUploading to %s' % instance['host']
                upload_time = ftp.upload(instance, tar_file)

                minutes = upload_time / 60
                seconds = upload_time - minutes * 60
                
                print '\t\tUpload completed in %s min %s s.' % (str(minutes), str(seconds))
            except Exception as e:
                print 'Error during upload : %s\n' % e.message

    # Swift
    if config.swift['enabled']:
        for server in config.swift['servers']:
            try:
                container = swift.SwiftContainer(
                    server['authurl'],
                    server['auth_version'],
                    server['user'],
                    server['key'],
                    server['tenant_name'],
                    server['container_name'],
                    server['autocreate'])

                print '\tUploading to Swift server %s' % server['name']
                swift_upload_start = int(time.time())

                container.upload(tar_file)

                swift_upload_end = int(time.time())

                minutes = (swift_upload_end - swift_upload_start) / 60
                seconds = (swift_upload_end - swift_upload_start) - minutes * 60
                print '\t\tUpload completed in %s min %s s.' % (str(minutes), str(seconds))
                
            except Exception as e:
                print 'Error during upload : %s\n' % e.message


    print '\n[Delete old backups]'

    archives_deleted = False

    for archive in os.listdir(config.output_dir):
        archive_info = os.stat(os.path.join(config.output_dir, archive))
        
        # If archive is older than keeptime (in days)...
        if time.mktime(time.gmtime()) - archive_info.st_mtime > (config.keeptime * 24 * 60 * 60):
            print '\tDeleting %s' % archive
            
            # Remove local copy
            print '\t\tLocal copy'
            try:
                os.remove(config.output_dir + '/' + archive)
            except Exception as e:
                print 'Error during removal : %s\n' % e.message

            # Remove FTP copy
            if config.ftp['enabled']:
                for instance in config.ftp['servers']:
                    try:
                        print '\t\tFrom FTP server %s' % instance['host']
                        ftp.delete_remote(instance, archive)
                    except Exception as e:
                        print 'Error during deletion : %s\n' % e.message
            
            if config.swift['enabled']:
                for server in config.swift['servers']:
                    try:
                        print '\t\tFrom Swift server %s' % server['name']
                        container = swift.SwiftContainer(
                            server['authurl'],
                            server['auth_version'],
                            server['user'],
                            server['key'],
                            server['tenant_name'],
                            server['container_name'])

                        container.delete(archive)
                    except Exception as e:
                        print 'Error during deletion : %s\n' % e.message


            archives_deleted = True

    if not archives_deleted:
        print '\tNo archives were deleted.'

    # Stop the counter
    end = int(time.time())

    print '\nBackup ending on %s' % str(datetime.datetime.now())

    minutes = (end - start) / 60
    seconds = (end - start) - minutes * 60
    print 'Time elapsed : %s min %s s.' % (str(minutes), str(seconds))


if __name__ == "__main__":
    try:
        import config
    except Exception as e:
        print 'Could not import settings ! Please check config.py (%s).' % e.message
        sys.exit(2)

    if config.swift['enabled']:
        import swift

    main()