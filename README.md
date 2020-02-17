# p2pass-iks-containerization
This repo is meant for Migration of current supported apps to IKS where appropriate

### Git Use
make a branch of this repo

### Step 1 Install helm 3 
(Why? because they have gotten rid of tiller)
  - helm web site: https://helm.sh/docs/intro/install/
  - make sure to set HELM_HOME to the directory where the p2paas-values.yaml file is

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
