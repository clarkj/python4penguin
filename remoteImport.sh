#!/bin/sh
mongoimport --host ds015953.mlab.com --port 15953 --username clarkj --password penguin --db oesolardb --collection josh1 --type csv --headerline --file dataout/2016-05-29T21\:15.csv
