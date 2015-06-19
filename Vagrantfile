# -*- mode: ruby -*-
# vi: set ft=ruby :

# How to create your own box for Vagrant
# https://scotch.io/tutorials/how-to-create-a-vagrant-base-box-from-an-existing-one

Vagrant.configure(2) do |config|
  # config.ssh.insert_key = false

  # The box is private and available to logged in members of the Center for Data Science
  # https://atlas.hashicorp.com/rtidatascience/boxes/cfs_analytics
  config.vm.box = "rtidatascience/cfs_analytics"
  config.vm.define "cfs_backend"

  config.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
    vb.gui = false
  
    # Customize the amount of memory on the VM:
    vb.memory = "2048"
  end

  # Provisioning every time
  # This basically looks for 
  config.vm.provision :shell, run: "always", path: "always_provisioning.sh"

  # Provisioning just the first time
  config.vm.provision :shell, path: "bootstrap_provisioning.sh"

  # Port forwarding
  config.vm.network :forwarded_port, host: 8887, guest: 8888
end
