#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time

from ftplib import FTP

## Uploads an archive to a FTP instance.
#
# @param instance the FTP instance to upload the archive to.
# @param archive the archive to be uploaded.
# @return the time taken to upload the archive.
# @throws Error
#
def upload(instance, archive):
    start = int(time.time())

    connection = FTP()
    connection.connect(instance['host'], instance['port'])
    connection.login(instance['user'], instance['password'])
    connection.cwd(instance['directory'])

    connection.storbinary('STOR ' + os.path.basename(archive), open(archive, 'rb'))

    connection.quit()

    end = int(time.time())

    return (end - start)

## Deletes an archive on the remote instance.
#
# @param instance the instance on which the archive should be deleted.
# @param archive the archive to be deleted.
#
def delete_remote(instance, archive):
    connection = FTP()
    connection.connect(instance['host'], instance['port'])
    connection.login(instance['user'], instance['password'])

    connection.delete(instance['directory'] + '/' + archive)

    connection.quit()
