import string
import subprocess


def get_db_list(instance):
    if instance['port'] is '':
        instance['port'] = 3306

    query = string.join([
        'mysql',
        '--host=' + instance['host'],
        '--port=' + str(instance['port']),
        '--user=' + instance['user'],
        '--password=' + instance['password'],
        '-e "SHOW DATABASES;" | grep -Ev "(Database|information_schema)"'])

    process = subprocess.Popen(query, shell=True, stdout=subprocess.PIPE)

    db_list, stderr = process.communicate()
    
    db_list = string.split(str(db_list))

    # These databases can cause issues during backup
    db_list.remove('performance_schema')
    db_list.remove('mysql')

    return db_list


def save_dbs(instance, db_list, instance_dir):
    if instance['port'] is '':
        instance['port'] = 3306

    for db in db_list:
        print '\t\t' + db

        query = string.join([
            'mysqldump',
            '--force',
            '--opt',
            '--host=' + instance['host'],
            '--port=' + str(instance['port']),
            '--user=' + instance['user'],
            '--password=' + instance['password'],
            '--databases ' + db,
            '--result-file=' + instance_dir + db + '.sql'])
        
        subprocess.call(query, shell=True)