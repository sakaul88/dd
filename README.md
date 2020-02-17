# p2pass-iks-containerization
This repo is meant for Migration of current supported apps to IKS where appropriate

### Git Use
 - make a branch of this repo

### get a repo clone
 - git clone git@github.ibm.com:WCE-SaaS-Ops/p2pass-iks-containerization.git
 
### create a new branch
 - git checkout -b my-new-branch-name

### put back changes
 - edit files and/or add files/directories
 - git add -A (or the specific files or directories)
 - git commit -a -m "comments..."
 - git checkout master
 - git pull
 - git checkout my-new-branch-name
 - git merge master (or rebase)


### Step 1 Install helm 3 
(Why? because they have gotten rid of tiller)
  - helm web site: https://helm.sh/docs/intro/install/
  - make sure to set HELM_HOME to the directory where the p2paas-values.yaml file is
  - The p2paas-values.yaml file is a copy pof the chart values.yaml file and it is the place where we make changes to the chart values

### Step 2 Install kind
 - kind web site: https://kind.sigs.k8s.io/
 - the default in this repo is to create kind/bin directory in the users's honme and install kind there
 - create a cluster see example cluster configs in kind subdir
   -- ~/kind/bin/kind create cluster --name=cluster1 --config=p2paas-kind.yaml
 - create the namespace you will be using
   -- kubectl create namespace kafka

#### Note: 
have seen that a kind cluster will exist after a reboot, but may be partially incomplete - had to delete cluster and rerun playbook to create it

In the library section you may have to create a python program that uses the AnsibleModules module and calls other python programs that our team has written.

### Step 3 Fix Python3
I had to run these pip installs:
 - pip install selinux
 - pip install ansible

I had to make a copy of the helm.py program in the lib-python-orchutils repo uner the orchutils directory.  This proigram had some specifi helm 2 syntax

Node networking article:
https://www.magalix.com/blog/kubernetes-cluster-networking-101

## Work Around
### No uninstall playbook
 - TODO
 - for now you just run
  -- helm uninstall <release> --namespace <namespace>
  -- i.e.,helm uninstall elasticsearch --namespace elasticsearch

### No Services exposed for performiung production like operatons
 - TODO
 - I have exposed services by setting service typoe to NodePort, but it needs more work
   -- may need an ingress.  I have an ingress install process and I have tested it
   
### Persistent Volume Claims
 - TODO
 - Have not done anything with this as far as Ansible/Helm is concerned
 - Need to find out how far we have gotten with Cloud Object Store as it has encryption

## Docs
### Ansible
 - https://docs.ansible.com/ansible/latest/user_guide/quickstart.html

### Helm
 - https://helm.sh/docs/intro/install/

### kind
 - https://kind.sigs.k8s.io/
