# su7.info maintenance stuff
Scripts and stuff I'm using to maintain my servers.

## Backup
This script backups the following :

* MySQL databases from multiple instances
* ... basically any directory you need on your filesystem !

All the data is `tar.gz`'d (so it keeps permissions, symbolic links and stuff) and uploaded to one or several FTP servers you can configure.

### Configuration :
Copy the `config.py.example` to `config.py` and fill it with your settings.  
This file has to remain located in the same directory `than backup.py`.

### Usage :
`python2 backup.py`

## Other scripts to come...
Maybe later ;-)

## Contact
The main repository for this is on [my Git server](http://git.quba.fr/su7_info/maintenance.git/). You can contact me by [email](mailto:quentin@quba.fr) if you have any question.  
Do not hesitate to contribute !
