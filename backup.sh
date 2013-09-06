#!/bin/bash

START_TIME=$SECONDS

# System admin (any user that should be given access to the backups)
admin="";				# Any UNIX user on your machine
adminHomeDir=$(bash <<< "echo ~$admin");

# Temp folder location
tempDir='/tmp';				# /tmp as default; you can chose any folder $admin has full rights on

# Database credentials
host="";		# Any host should work but you will mainly choose localhost
user=""; 		# You must be root
password="";		# Password of MySQL root user

# Apache2 websites parameters
sitesLocation="/var/www/";

# Apache2 configuration files location
apache2configLocation="/etc/apache2/";

# Git repositories
gitReposLocation="/home/git/repositories/";

# Days before previous backups are deleted
daysBeforeDeletion="7";

# Remote FTP configuration
FTPHost="";
FTPPort="";
FTPUser="";
FTPPassword="";

# Archive password
backupPassword="";

if [ $# -ne 1 ]; then
        echo "Usage: $0 /path/to/backup/directory (without trailing slash)";
        exit 2;
fi

backupDirectory=$1;

echo "Backup starting on $(date)";
echo "";

########################################################################
# Creating the backup directory
cd $tempDir;
currentDate=$(date +"%Y-%m-%d");
dateDirectory=$currentDate"/";
mkdir $dateDirectory -m 705;


########################################################################
# Saving the databases

echo "[Databases ($host)]";
dbBackupDirectory=$dateDirectory"databases/";
mkdir -p $dbBackupDirectory;

# Get a list of databases
databases=`mysql --host=$host --user=$user --password=$password -e "SHOW DATABASES;" | grep -Ev "(Database|information_schema)"`

for db in $databases; do
	if [ "$db" != "mysql" -a "$db" != "performance_schema" ]; then
		echo -n "	$db... ";
		mysqldump --force --opt --host=$host --user=$user --password=$password --databases $db > $dbBackupDirectory$db".sql"; 
		echo "done.";
	fi
done
echo "	Databases backuped. Total size : $(du -s $dbBackupDirectory | cut -f1) kB.";


########################################################################
# Saving Apache2 websites

echo "[Websites ($sitesLocation)]";

sitesBackupDirectory=$dateDirectory"sites/";
mkdir -p $sitesBackupDirectory;

for site in $(ls $sitesLocation); do
	echo -n "	$site... ";
	cp -r $sitesLocation$site $sitesBackupDirectory$site;
	echo "done.";
done
echo "	Sites backuped. Total size : $(du -s $sitesBackupDirectory | cut -f1) kB.";


########################################################################
# Saving Apache2 configuration
echo "[Apache2 configuration ($apache2configLocation)]";

apache2configBackupDirectory=$dateDirectory"apache2/";
mkdir -p $apache2configBackupDirectory;

echo -n "	Backuping apache2 configuration... ";
cp -r $apache2configLocation $apache2configBackupDirectory;
echo "done.";


########################################################################
# Copying the admin's home dir
echo "[Admin home directory ($adminHomeDir)]";

echo -n "       Copying $admin's home directory... ";
cp -r $adminHomeDir $dateDirectory; 
echo "done.";


########################################################################
# Copying the Git repositories
echo "[Git repositories ($gitReposLocation)]";

echo -n "       Copying the Git repositories... ";
cp -r $gitReposLocation $dateDirectory; 
echo "done.";


########################################################################
# Zipping the backups and deleting the temporary one
echo "[Archive creation]";

echo -n "	Creating the archive... ";
zip -y -P $backupPassword -r $backupDirectory"/"$currentDate".zip" $dateDirectory > $backupDirectory"/"$currentDate".log";
echo "done.";

echo -n "	Deleting the temporary directory in $tempDir... ";
rm -rf $dateDirectory;
echo "done.";

cd $backupDirectory;


########################################################################
# Giving the rights to the admin to access the save

echo "[Permissions]";
echo -n "	Giving the right permissions to $admin... ";
chown -R $admin:$admin $backupDirectory;
chmod -R 700 $backupDirectory;
echo "done.";

########################################################################
# Uploading today's backup to the ftp repo

echo "[Remote upload]"
echo -n "	Uploading archive to $FTPHost...";

START_FTP_UPLOAD=$SECONDS;

ftp -i -n $FTPHost $FTPPort <<FTP_UPLOAD
user $FTPUser $FTPPassword
cd backups
cd vps
put $currentDate".zip"
put $currentDate".log"
quit
FTP_UPLOAD

echo "done ($(du -s $currentDate".zip" | cut -f1) kBs in $(($SECONDS-$START_FTP_UPLOAD))s).";

########################################################################
# Maintenance
echo "[Maintenance]";
echo "	Deleting previous backups that are at least $daysBeforeDeletion days old...";

for i in `find $backupDirectory -mtime +$daysBeforeDeletion -print`;
do

i=$(basename $i);
echo -n "		Deleting $i : local... ";
rm -rf $i;
echo "done; remote (FTP)... ";

# We also delete the file on our ftp
ftp -i -n $FTPHost $FTPPort <<FTP_DELETE
quote USER $FTPUser
quote PASS $FTPPassword
cd backups
cd vps
delete $i
quit
FTP_DELETE

echo "done.";

done;

echo "	Deletion of the previous backups terminated.";


########################################################################
# State, for monitoring
echo "[State of the backup folder]";
echo "	$backupDirectory	[$(du -hs $backupDirectory | cut -f1)]";

for backup in $(ls $backupDirectory); do
	echo "		$backup	[$(du -hs $backupDirectory/$backup | cut -f1)]";
done

echo "";

ELAPSED_TIME=$(($SECONDS-START_TIME));
echo "Backup terminated correctly on $(date) in $dateDirectory.";
echo "Backup duration : $(($ELAPSED_TIME/60)) min $(($ELAPSED_TIME%60)) s.";

