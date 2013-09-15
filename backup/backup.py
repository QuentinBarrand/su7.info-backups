#!/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import getopt
import subprocess
import string
import pwd
import grp

from shutil import copytree, rmtree
from json import loads
from datetime import date, datetime
from ftplib import FTP
from zipfile import ZipFile


def usage():
	print "Usage : python backup.py -c <path_to_config.json> [-s]"
	sys.exit(2)


def get_db_list():
	global config

	mysql_settings = config['mysql']

	mysql_query = string.join(['mysql',
		' --host=', mysql_settings['host'],
		' --user=', mysql_settings['user'],
		' --password=', mysql_settings['password'],
		' -e "SHOW DATABASES;" | grep -Ev "(Database|information_schema)"'], '')

	process = subprocess.Popen(mysql_query, shell=True, stdout=subprocess.PIPE)

	db_list, stderr = process.communicate()
	
	db_list = string.split(str(db_list))
	db_list.pop()

	# These databases can cause issues during backup
	db_list.remove('performance_schema')
	db_list.remove('mysql')


	return db_list


def save_db():
	global config

	mysql_settings = config['mysql']

	for db in config['db_list']:
		print"\t" + db + "...",

		mysql_query = string.join(['mysqldump',
			' --force',
			' --opt',
			' --host=' + mysql_settings['host'],
			' --user=' + mysql_settings['user'],
			' --password=' + mysql_settings['password'],
			' --databases '+ db,
			' > ' + config['db_directory'] + db + '.sql'])

		process = subprocess.Popen(mysql_query, shell=True)

		print 'done.'


def save_apache2():
	global config

	os.mkdir(config['date_directory'] + 'apache2/')
	
	print "debug : " + config['date_directory'] + 'apache2/sites'

	print "\tWebsites...",
	copytree(config['apache']['sites'], config['date_directory'] + 'apache2/sites', symlinks=True, ignore=None)
	print "done."

	print "\tConfig...",
	copytree(config['apache']['conf'], config['date_directory'] + 'apache2/config', symlinks=True, ignore=None)
	print "done."


def save_homedirs():
	global config

	os.mkdir(config['date_directory'] + 'homedirs/')

	for home in config['users_home']:
		print "\t" + home + "...",

		try:
			copytree(home, config['date_directory'] + 'homedirs/' + home, symlinks=True, ignore=None)
			print "done."
		except OSError:
			print "There is a problem with " + home + ". It could not be backuped."


def zip_directory():
	global config

	zip_file = ZipFile(config['zip_archive'], 'w')
	zip_file.setpassword(config['backup_password'])
	
	for root, dirs, files in os.walk(config['date_directory']):
		for file in files:
			# An OSError exception can be thrown due to ZipFile following symlinks :-(
			try:
				zip_file.write(os.path.join(root, file))
			except OSError:
				pass

	zip_file.close()


def upload_remote():
	global config

	for server in config['ftp']:
		print "\tUploading to " + server['host'] + "...",

		try:
			connection = FTP()
			connection.connect(server['host'], server['port'])
			connection.login(server['user'], server['password'])
			connection.cwd(server['path_to_backup_dir'])

			connection.storbinary("STOR " + config['zip_archive'], open(config['zip_archive'], 'rb'))

			connection.quit()
			print "done."
		except error as e:
			print "Something went wrong during the upload. Here's the error message :\n" + e.message


def delete_remote(zip_archive):
	global config

	for server in config['ftp']:
		print "\t\tDeleting on " + server['host'] + "...",

		try:
			connection = FTP()
			connection.connect(server['host'], server['port'])
			connection.login(server['user'], server['password'])

			connection.delete(server['path_to_backup_dir'] + '/' + zip_archive)

			connection.quit()
			print "done."
		except error as e:
			print "Something went wrong during the removal. Here's the error message :\n" + e.message


def maintenance():
	global config

	print "\tDeleting temporary folder...",
	rmtree(config['date_directory'])
	print "done."

	# Removing old archives
	os.chdir(config['backup_dir'])

	now = time.mktime(time.gmtime())
	archives_deleted = 0

	for archive in os.listdir(config['backup_dir']):
		archive_info = os.stat(config['backup_dir'] + '/' + archive)
		
		# If archive is older than keeptime (in days)...
		if now - archive_info.st_mtime > now - (config['keeptime'] * 24 * 60 * 60):
			print "\tDeleting " + archive + "...",
			
			print "\t\tLocal...",
			os.remove(archive)
			print "done."

			delete_remote(archive)
			archives_deleted = 1

	if archives_deleted == 0:
		print "\tNo archives were deleted."

	# Give permissions to the directory containing the zip archives to the admin only
	print "\tGiving permissions to " + config['admin'] + "...",
	os.chown(config['backup_dir'], pwd.getpwnam(config['admin']).pw_uid, grp.getgrnam(config['admin']).gr_gid)
	os.chmod(config['backup_dir'], 700)
	print "done."


def main():
	global config

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hc:s", ["help", "config_path=", "cronjob"])
	except getopt.GetoptError as err:
		print str(err) 
		usage()

	# Default configuration
	config_path = 'config.json'

	# Silent = nothing to the standard output
	silent = False

	# Arguments handling
	for o, a in opts:
		if o in ("-c", "--config_path"):
			config_path = a
		elif o in ("-h", "--help"):
			usage()
		elif o in ("-s", "--silent"):
			silent = True
		else:
			assert False, "unhandled option"

	# Starting the script
	start_time = int(time.mktime(time.gmtime()))

	print "Backup starting on " + str(datetime.now())

	# Import configuration from config file
	config = loads(open(config_path).read())

	# A double trailing slash does not matter so let's be sure there's at least one
	config['backup_dir'] += '/'

	# Create backup directory
	date_directory = config['temp_dir'] + '/backup_' + str(date.today()) + '/'

	config['date_directory'] = date_directory

	os.mkdir(date_directory)

	# Save db
	print "\n[MySQL]"
	os.mkdir(date_directory + 'db/')

	config['db_directory'] = date_directory + 'db/'
	config['db_list'] = get_db_list()

	save_db()

	# Save apache2 sites and config
	print "\n[Apache 2]"
	save_apache2()

	# Save Git repos
	print "\n[Git]"

	print "\tRepositories...",
	copytree(config['git'], date_directory + "git", symlinks=True, ignore=None)
	print "done."

	# Save the users' home directories
	print "\n[Users home directories]"
	
	save_homedirs()

	# ZIP
	print "\n[Archives]"

	os.chdir(config['backup_dir'])

	config['zip_archive'] = config['archive_prefix'] + str(date.today()) + ".zip"

	print "\tCreating backup archive (" + config['zip_archive'] + ")...", 
	zip_directory()
	print "done."

	# Upload the archive to ftp repos
	print "\n[Upload to remote servers]"
	upload_remote()

	# Run maintenance
	print "\n[Maintenance]"
	maintenance()

	end_time = int(time.mktime(time.gmtime()))

	minutes = (end_time - start_time) / 60
	seconds = (end_time - start_time) - minutes * 60

	print "\nBackup terminating on " + str(datetime.now())
	print "Time elapsed : " + str(minutes) + "min " + str(seconds) + "s."


if __name__ == "__main__":
	main()
