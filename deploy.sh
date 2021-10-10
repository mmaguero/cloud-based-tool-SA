# Up VM containers
#vagrant box add https://github.com/jose-lpa/packer-ubuntu_lts/releases/download/v3.1/ubuntu-16.04.box --name ubuntu16.04_docker
vagrant up
#vagrant provision #Si da problemas al provisionar
# Borrar tmp
vagrant ssh
docker rm $(sudo docker ps -a | grep Exit | cut -d ' ' -f 1)
docker rmi $(docker images | tail -n +2 | awk '$1 == "<none>" {print $'3'}')
docker volume rm $(docker volume ls -qf dangling=true)
exit
vagrant ssh -- -t docker images 
vagrant ssh -- -t docker ps -a 
