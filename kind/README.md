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

#### Different releases
I have found that there are some charts that were built on older versions of kubernetes.  Kind has the ability to run older versions of kubernetes.  For the available versions, see https://github.com/kubernetes-sigs/kind/releases.

You can add the release image to the config yaml, here is the p2paas-kind-v1.15.yaml example:
> kind: Cluster
> apiVersion: kind.x-k8s.io/v1alpha4
> # networking:
> #   apiServerAddress: "10.96.0.5"
> nodes:
> - role: control-plane
>   image: kindest/node:v1.15.7@sha256:e2df133f80ef633c53c0200114fce2ed5e1f6947477dbc83261a6a921169488d
>   kubeadmConfigPatches:
>     - |
>      kind: InitConfiguration
>       nodeRegistration:
>         kubeletExtraArgs:
>           node-labels: "ingress-ready=true"
>           authorization-mode: "AlwaysAllow"

#### Note:
have seen that a kind cluster will exist after a reboot, but may be partially incomplete - had to delete cluster and rerun playbook to create it
