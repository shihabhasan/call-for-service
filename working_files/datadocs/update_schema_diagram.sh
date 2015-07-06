#!/bin/bash

sc.sh -server=postgresql -host=freyja.rtp.rti.org -user=datascientist -password=1234thumbwar -database=cfs -command=graph -outputformat png -outputfile=cfs_relational_schema.png -infolevel=maxiumum -schemas=p.*\..* -tabletypes=TABLE
