#!/bin/bash

host="";
user="";
password="";

# MySQL maintenance
mysqlcheck -h $host -u $user -p$password --auto-repair --optimize --all-databases;

# Restarting services
service apache2 restart;
service mysql restart;
