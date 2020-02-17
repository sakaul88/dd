# kind - kubernetes in docker

### Install kind
 - kind web site: https://kind.sigs.k8s.io/
 - the default in this repo is to create kind/bin directory in the users's home and install kind there
 - create a cluster see example cluster configs in kind subdir
   -- ~/kind/bin/kind create cluster --name=cluster1 --config=p2paas-kind.yaml
 - create the namespace you will be using
   -- kubectl create namespace kafka

### Multiple nodes
 - See the file named p2paas-kind.yaml
 - this file created the control-plane node (this node is always required) and three worker nodes
 - once the cluster is created you need to label the nodes
 - first display node label info
  -- kubectl get nodes --show-labels
  -- NAME                     STATUS   ROLES    AGE   VERSION   LABELS
cluster1-control-plane   Ready    master   58m   v1.17.0   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,ingress-ready=true,kubernetes.io/arch=amd64,kubernetes.io/hostname=cluster1-control-plane,kubernetes.io/os=linux,node-role.kubernetes.io/master=
cluster1-worker          Ready    <none>   58m   v1.17.0   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=cluster1-worker,kubernetes.io/os=linux
cluster1-worker2         Ready    <none>   58m   v1.17.0   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=cluster1-worker2,kubernetes.io/os=linux
cluster1-worker3         Ready    <none>   58m   v1.17.0   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=cluster1-worker3,kubernetes.io/os=linux
  -- Label the nodes
  -- kubectl label node cluster1-worker "name=worker1"
  -- kubectl label node cluster1-worker2 "name=worker2"
  -- kubectl label node cluster1-worker3 "name=worker3"

 - Now we can apply affinity rules to keep like containers deployed to different nodes for fault tolerance
>
  ## Pod affinity
  ## ref: https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#affinity-and-anti-affinity
  ##
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: name
            operator: In
            values:
            - worker1
            - worker2
            - worker3
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 1
        preference:
          matchExpressions:
          - key: another-node-label-key
            operator: In
            values:
            - another-node-label-value
>

#### Note: 
have seen that a kind cluster will exist after a reboot, but may be partially incomplete - had to delete cluster and rerun playbook to create it

