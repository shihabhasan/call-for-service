# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.hostname = "cfs"

  config.vm.provider "virtualbox" do |vb|
    # Customize the amount of memory on the VM:
    vb.memory = "2048"
  end

  config.vm.network "private_network", ip: "192.168.50.4"

  # Django dev server
  config.vm.network :forwarded_port, host: 8000, guest: 8000

  config.vm.provision :ansible do |ansible|
    ansible.playbook = "vagrant/playbook.yml"
  end

  config.vm.provider "virtualbox" do |v|
    v.name = "cfs"
  end

end
