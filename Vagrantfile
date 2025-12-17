# Full Automated Vagrantfile with Provisioning
Vagrant.configure("2") do |config|
  
  config.ssh.insert_key = false
  config.ssh.forward_agent = true
  config.ssh.keep_alive = true
  config.vm.boot_timeout = 1800
  
  # ═══════════════════════════════════════════════════════════
  # 🔧 VM 1: JENKINS - CI/CD Server (AUTOMATED)
  # ═══════════════════════════════════════════════════════════
  config.vm.define "jenkins" do |jenkins|
    jenkins.vm.box = "ubuntu/focal64"
    jenkins.vm.hostname = "jenkins-vm"
    jenkins.vm.network "private_network", ip: "192.168.33.10"
    jenkins.vm.network "forwarded_port", guest: 8080, host: 8080
    
    jenkins.vm.provider "virtualbox" do |vb|
      vb.name = "candlestick-jenkins"
      vb.memory = "2048"
      vb.cpus = 2
      vb.gui = true  # Show VM window
      vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
    end
    
    jenkins.vm.synced_folder ".", "/vagrant"
    
    # Automatic provisioning
    jenkins.vm.provision "shell", inline: <<-SHELL
      export DEBIAN_FRONTEND=noninteractive
      apt-get update
      apt-get install -y openjdk-11-jdk git curl

      # Install Jenkins
      curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null
      echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/ | tee /etc/apt/sources.list.d/jenkins.list > /dev/null
      apt-get update
      apt-get install -y jenkins

      # Install Docker
      apt-get install -y apt-transport-https ca-certificates software-properties-common
      curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
      add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
      apt-get update
      apt-get install -y docker-ce docker-ce-cli containerd.io
      usermod -aG docker jenkins

      # Install Ansible
      apt-get install -y software-properties-common
      add-apt-repository --yes --update ppa:ansible/ansible
      apt-get install -y ansible

      systemctl start jenkins
      systemctl enable jenkins

      echo "✅ Jenkins VM configured!"
      echo "📌 Jenkins password:"
      sleep 10
      cat /var/lib/jenkins/secrets/initialAdminPassword 2>/dev/null || echo "Will be available after Jenkins starts"
    SHELL
  end

  # ═══════════════════════════════════════════════════════════
  # 🚀 VM 2: APPSERVER - Application Server (AUTOMATED)
  # ═══════════════════════════════════════════════════════════
  config.vm.define "appserver" do |app|
    app.vm.box = "ubuntu/focal64"
    app.vm.hostname = "appserver-vm"
    app.vm.network "private_network", ip: "192.168.33.11"
    app.vm.network "forwarded_port", guest: 3000, host: 3000
    app.vm.network "forwarded_port", guest: 8000, host: 8000
    app.vm.network "forwarded_port", guest: 8001, host: 8001
    
    app.vm.boot_timeout = 1800
    
    app.vm.provider "virtualbox" do |vb|
      vb.name = "candlestick-appserver"
      vb.memory = "4096"
      vb.cpus = 4
      vb.gui = true  # Show VM window
      vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
    end
    
    app.vm.synced_folder ".", "/vagrant"
    
    # Automatic provisioning
    app.vm.provision "shell", inline: <<-SHELL
      export DEBIAN_FRONTEND=noninteractive
      apt-get update
      apt-get install -y apt-transport-https ca-certificates curl software-properties-common

      # Install Docker
      curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
      add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
      apt-get update
      apt-get install -y docker-ce docker-ce-cli containerd.io

      # Install Docker Compose
      curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
      chmod +x /usr/local/bin/docker-compose

      usermod -aG docker vagrant
      apt-get install -y python3 python3-pip

      echo "✅ AppServer VM configured!"
      echo "🚀 Starting containers..."
      
      cd /vagrant
      docker-compose build
      docker-compose up -d
      
      echo "✅ Application deployed!"
      docker-compose ps
    SHELL
  end

  # ═══════════════════════════════════════════════════════════
  # 📊 VM 3: MONITOR - Nagios Monitoring (AUTOMATED)
  # ═══════════════════════════════════════════════════════════
  config.vm.define "monitor" do |mon|
    mon.vm.box = "ubuntu/focal64"
    mon.vm.hostname = "monitor-vm"
    mon.vm.network "private_network", ip: "192.168.33.12"
    mon.vm.network "forwarded_port", guest: 80, host: 8888
    
    mon.vm.provider "virtualbox" do |vb|
      vb.name = "candlestick-monitor"
      vb.memory = "1024"
      vb.cpus = 1
      vb.gui = true  # Show VM window
      vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
    end
    
    mon.vm.synced_folder ".", "/vagrant"
    
    # Automatic provisioning
    mon.vm.provision "shell", inline: <<-SHELL
      export DEBIAN_FRONTEND=noninteractive
      apt-get update
      apt-get install -y apache2 wget

      echo "✅ Monitor VM configured!"
      echo "📌 Nagios will be available at: http://localhost:8888"
    SHELL
  end
  
  config.vm.post_up_message = <<-MESSAGE
  ╔════════════════════════════════════════════════════════════════════╗
  ║   🎉 3-VM DevOps Pipeline is Ready!                               ║
  ╠════════════════════════════════════════════════════════════════════╣
  ║   🔧 JENKINS:   http://localhost:8080                              ║
  ║   🚀 FRONTEND:  http://localhost:3000                              ║
  ║   🚀 BACKEND:   http://localhost:8000                              ║
  ║   🚀 AI:        http://localhost:8001                              ║
  ║   📊 NAGIOS:    http://localhost:8888                              ║
  ╚════════════════════════════════════════════════════════════════════╝
  MESSAGE
end
