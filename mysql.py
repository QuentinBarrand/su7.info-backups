#!/usr/bin/python
# -*- coding: utf-8 -*-

import string
import subprocess

class Mysql:

    def __init__(self, settings):
        self.host = settings['host'] if settings['host'] != '' else 'localhost'
        self.port = settings['port'] if settings['port'] != '' else 3306
        self.user = settings['user'] if settings['user'] != '' else 'root'
        self.password = settings['password']


    def get_db_list(self):
        query = string.join([
            'mysql',
            '--host=%s' % self.host,
            '--port=%s' % str(self.port),
            '--user=%s' % self.user,
            '--password=%s' % self.password,
            '-e "SHOW DATABASES;" | grep -Ev "(Database|information_schema)"'])

        process = subprocess.Popen(query, shell=True, stdout=subprocess.PIPE)

        db_list, stderr = process.communicate()
        
        db_list = string.split(str(db_list))

        return db_list


    def save(self, dump_filename):

        query = string.join([
            'mysqldump',
            '--force',
            '--opt',
            '--host=%s' % self.host,
            '--port=%s' % str(self.port),
            '--user=%s' % self.user,
            '--password=%s' % self.password,
            '--ignore-table=mysql.event',
            '--all-databases',
            '--result-file=%s' % dump_filename])
                
        subprocess.call(query, shell=True)