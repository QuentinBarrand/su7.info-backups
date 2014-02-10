import os

from ftplib import FTP

def upload(instance, archive):
    try:
        print '\tUploading to ' + instance['host']

        connection = FTP()
        connection.connect(instance['host'], instance['port'])
        connection.login(instance['user'], instance['password'])
        connection.cwd(instance['directory'])

        connection.storbinary('STOR ' + os.path.basename(archive), open(archive, 'rb'))

        connection.quit()
    except Exception as e:
        print 'Error during upload :\n' + e.message


def delete_remote(instance, archive):
    try:
        print '\t\tFrom host ' + instance['host']
        
        connection = FTP()
        connection.connect(instance['host'], instance['port'])
        connection.login(instance['user'], instance['password'])

        connection.delete(instance['directory'] + '/' + archive)

        connection.quit()
    except Exception as e:
        print 'Error during deletion :\n' + e.message
