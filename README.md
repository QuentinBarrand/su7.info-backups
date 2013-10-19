# su7.info maintenance stuff
Scripts and stuff I'm using to maintain my servers.

## Backup
This script backups the following :

* MySQL databases
* websites and apache2 configuration
* Git repositories
* users' home directories

All the data is zipped you can set up any number of remote FTP locations you want.
You must configure your installation's details in `config.json`.

Usage :
`python backup.py`

Options :

* `-c    --config_path <path>` : path to config.json when it's not located in the same directory
* `-d    --debug` : debug mode, data isn't sent to any FTP repo and maintenance operations on old archives are not permformed
* `-h    --help` : display this usage.
* `-s    --silent` : no output in stdout (experimental)

## MySQL
I face issues with MySQL, with the process sometimes using to much RAM and crashing. This script permits to restart and check non-critical databases.

You must configure your installation's details in the file. 

Usage :
`./maintenance.sh`

# Contact
The main repository for this is on [my Git server](http://git.quentinbarrand.com/?p=su7_info/maintenance.git;a=summary). You can contact me by [email](mailto:quentin.barrand@mail.com) if you have any question.

Do not hesitate to contribute !
