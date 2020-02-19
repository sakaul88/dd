Install helm 3 (Why? because they have gotten rid of tiller)
 - https://helm.sh/docs/intro/install/

Install kind
kind web site: https://kind.sigs.k8s.io/

Note: have seen that a kind cluster will exist after a reboot, but may be partially incomplete - had to delete cluster and rerun playbook to create it

In the library section you may have to create a python program that uses the AnsibleModules module and calls other python programs that our team has written.

I had to run these pip installs:
pip install selinux
pip install ansible

I had to make a copy of the helm.py program in the lib-python-orchutils repo uner the orchutils directory.  This program had some specifi helm 2 syntax

you will need to cd to the lib-python-orchutils and run
 - sudo python3 setup.py build
 - sudo python3 setup.py install

When ever you make changes to a file in that orchutils area you need to run the build, install process

### For ansible
ansible localhost -m setup > facts.txt       <=  this command will capture the system facts to a filke so you can determine the structure of the variables you need

### For helm
run helm install elasticsearch stable/elasticsearch --namespace elasticsearch --version 1.30.0 --values p2paas-es-values.yaml --debug --dry-run

This will printout the k8s yamls and not do an actual install.  You can review this information if you are making changes to that p2pass-es-values.yaml
