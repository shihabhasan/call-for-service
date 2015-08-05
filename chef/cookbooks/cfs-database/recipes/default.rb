#
# Cookbook Name:: cfs_database
# Recipe:: default
#
# Copyright 2015, RTI
#
# All rights reserved - Do Not Redistribute
#

node.set['postgresql']['enable_pgdg_apt']     = true
node.set['postgresql']['password']['postgres'] =  'md509bc7ef3583c9b8be81c0f156b8f25d7'
node.set['postgresql']['config']['listen_addresses'] = '*'
node.set['postgresql']['pg_hba']			   = [{:comment => '# Backdoor for postgres ',:type => 'host', :db => 'all', :user => 'postgres', :addr => "0.0.0.0/0", :method => 'md5'}]

include_recipe "openssl"
include_recipe "postgresql::apt_pgdg_postgresql"
include_recipe "postgresql::server"

