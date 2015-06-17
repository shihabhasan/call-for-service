#!/usr/bin/env bash

apt-get install -y postgresql-server-dev-9.4
apt-get install -y libpq-dev
pip3 install psycopg2

cat >> /home/vagrant/.bashrc << END
# Make the python command invoke python3
alias python=python3
# Make the pip command invoke pip3
alias pip=pip3
END