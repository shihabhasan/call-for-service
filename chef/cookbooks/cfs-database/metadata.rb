name             'cfs-database'
maintainer       'Research Triangle Institute'
maintainer_email 'apreston@rti.org'
license          'All rights reserved'
description      'Installs/Configures cfs_database'
long_description IO.read(File.join(File.dirname(__FILE__), 'README.md'))
version          '0.1.0'

depends 'apt', '>= 1.9.0'
depends 'openssl'
depends 'postgresql'
	