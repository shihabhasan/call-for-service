#!/usr/bin/env bash

apt-get install -y build-essential
apt-get install -y postgresql-server-dev-9.4
apt-get install -y libpq-dev
pip3 install psycopg2
pip3 install djangorestframework

curl --silent --location https://deb.nodesource.com/setup_0.12 | sudo bash -
sudo apt-get install -y nodejs
sudo apt-get autoremove

cat >> /home/vagrant/.bashrc << END
# Make the python command invoke python3
alias python=python3
# Make the pip command invoke pip3
alias pip=pip3
END