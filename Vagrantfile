# -*- mode: ruby -*-
# vi: set ft=ruby :

# How to create your own box for Vagrant
# https://scotch.io/tutorials/how-to-create-a-vagrant-base-box-from-an-existing-one

Vagrant.configure(2) do |config|
  #config.ssh.insert_key = false

  # The box is private and available to logged in members of the Center for Data Science
  # https://atlas.hashicorp.com/rtidatascience/boxes/cfs_analytics
  config.vm.box = "rtidatascience/cfs_analytics"

  config.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
    vb.gui = false
  
    # Customize the amount of memory on the VM:
    vb.memory = "2048"
  end

  config.vm.define "cfs_backend" do |web_config|
    
    web_config.vm.box = "rtidatascience/cfs_analytics"
    web_config.vm.network :forwarded_port, host: 8887, guest: 8888
    
    # Provisioning every time
    web_config.vm.provision :shell, run: "always", path: "always_provisioning.sh"
    
    # Provisioning just the first time
    web_config.vm.provision :shell, path: "bootstrap_provisioning.sh"
  end

  config.vm.define "cfs_database" do |db_config|
    
    db_config.vm.box = "ubuntu/trusty64"
    db_config.omnibus.chef_version = :latest
    db_config.vm.network :forwarded_port, host: 5433, guest: 5432
    db_config.vm.provision :chef_solo do |chef|
     chef.node_name = 'cfs_database' 
     chef.cookbooks_path = "chef/cookbooks"
     chef.roles_path = "chef/roles"
     chef.add_role "cfs_database"
    end
  end


end
