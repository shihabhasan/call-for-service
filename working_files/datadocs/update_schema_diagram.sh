#!/bin/bash

sc.sh -server=postgresql -host=freyja.rtp.rti.org -user=datascientist -password=1234thumbwar -database=cfs_v3 -command=graph -outputformat png -outputfile=cfs_relational_schemav3.png -infolevel=maxiumum -schemas=p.*\..* -tabletypes=TABLE
