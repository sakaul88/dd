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

### Example run
This implementation of elasticsearch uses one playbook that can be called with install or uninstall_chart
Here is how to run the install:
 - ansible-playbook elasticsearch-run.yaml --extra-vars "role_name=elasticsearch run_option=install" --module-path roles/elasticsearch/library
   -- the --module-path is being used as it appears that using an include or an importcauses the implied path to the library to be unavailable
Here is how to run the uninstall:
 - ansible-playbook elasticsearch-run.yaml --extra-vars "role_name=elasticsearch run_option=uninstall" --module-path roles/elasticsearch/library
   -- the --module-path is not required for the uninstall, but am leaving it for consistency

Now, wait until es is running and ready: kubectl get pods -n elasticsearch
Then we can install kibana:
 - ansible-playbook kibana-run.yaml --extra-vars "role_name=kibana run_option=install" --module-path roles/elasticsearch/library

To uninstall:
 - ansible-playbook kibana-run.yaml --extra-vars "role_name=kibana run_option=uninstall" --module-path roles/elasticsearch/library

#### elasticsearch notes
Elasticsearch can be accessed:

  * Within your cluster, at the following DNS name at port 9200:

    elasticsearch-client.elasticsearch.svc

  * From outside the cluster, run these commands in the same shell:

    export POD_NAME=$(kubectl get pods --namespace elasticsearch -l "app=elasticsearch,component=client,release=elasticsearch" -o jsonpath="{.items[0].metadata.name}")
    echo "Visit http://127.0.0.1:9200 to use Elasticsearch"
    kubectl port-forward --namespace elasticsearch $POD_NAME 9200:9200

#### kibana notes
Kibana can be accessed:

  * From outside the cluster, run these commands in the same shell:

    export POD_NAME=$(kubectl get pods --namespace elasticsearch -l "app=kibana,release=kibana" -o jsonpath="{.items[0].metadata.name}")
    echo "Visit http://127.0.0.1:5601 to use Kibana"
    kubectl port-forward --namespace elasticsearch $POD_NAME 5601:5601
