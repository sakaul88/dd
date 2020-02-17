kafka

Kafka can be accessed via port 9092 on the following DNS name from within your cluster:

    my-release-kafka.default.svc.cluster.local

To create a topic run the following command:

    export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=kafka,app.kubernetes.io/instance=my-release,app.kubernetes.io/component=kafka" -o jsonpath="{.items[0].metadata.name}")
    kubectl --namespace default exec -it $POD_NAME -- kafka-topics.sh --create --zookeeper my-release-zookeeper:2181 --replication-factor 1 --partitions 1 --topic test

***** for Jeff's install
export POD_NAME=$(kubectl get pods --namespace kafka -l "app.kubernetes.io/component=kafka,app.kubernetes.io/instance=kafka" -o jsonpath="{.items[0].metadata.name}")

kubectl --namespace kafka exec -it $POD_NAME -- kafka-topics.sh --create --zookeeper kafka-zookeeper:2181 --replication-factor 1 --partitions 1 --topic test

To list all the topics run the following command:

***** for Jeff's install
kubectl --namespace kafka exec -it $POD_NAME -- kafka-topics.sh --list --zookeeper kafka-zookeeper:2181

    export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=kafka,app.kubernetes.io/instance=my-release,app.kubernetes.io/component=kafka" -o jsonpath="{.items[0].metadata.name}")
    kubectl --namespace default exec -it $POD_NAME -- kafka-topics.sh --list --zookeeper my-release-zookeeper:2181

To start a kafka producer run the following command:

    export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=kafka,app.kubernetes.io/instance=my-release,app.kubernetes.io/component=kafka" -o jsonpath="{.items[0].metadata.name}")
    kubectl --namespace default exec -it $POD_NAME -- kafka-console-producer.sh --broker-list localhost:9092 --topic test

To start a kafka consumer run the following command:

    export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=kafka,app.kubernetes.io/instance=my-release,app.kubernetes.io/component=kafka" -o jsonpath="{.items[0].metadata.name}")
    kubectl --namespace default exec -it $POD_NAME -- kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test --from-beginning

    PRODUCER:
        kafka-console-producer.sh --broker-list 127.0.0.1:9092 --topic test
    CONSUMER:
        kafka-console-consumer.sh --bootstrap-server 127.0.0.1:9092 --topic test --from-beginning

