"""Producer base-class providing common utilites and functionality"""
import logging
import time


from confluent_kafka import avro
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.avro import AvroProducer

SCHEMA_REGISTRY_URL = "http://localhost:8081"

BROKER_URL = "PLAINTEXT://localhost:9092"

logger = logging.getLogger(__name__)

class Producer:
    """Defines and provides common functionality amongst Producers"""

    # Tracks existing topics across all Producer instances
    existing_topics = set([])

    def __init__(
        self,
        topic_name,
        key_schema,
        value_schema=None,
        num_partitions=1,
        num_replicas=1,
    ):
        """Initializes a Producer object with basic settings"""
        self.topic_name = topic_name
        self.key_schema = key_schema
        self.value_schema = value_schema
        self.num_partitions = num_partitions
        self.num_replicas = num_replicas

        self.broker_properties = {
            "bootstrap.servers" : BROKER_URL,
            "schema.registry.url" : SCHEMA_REGISTRY_URL,
            "client.id" : "opt-producer"
            
        }
        
        self.client = AdminClient({"bootstrap.servers": BROKER_URL})

        # If the topic does not already exist, try to create it
        if self.topic_name not in Producer.existing_topics:
            self.create_topic()
            Producer.existing_topics.add(self.topic_name)

        self.producer = AvroProducer(self.broker_properties,
                                     default_key_schema = key_schema,
                                     default_value_schema = value_schema
                                    )

    def create_topic(self):
        """Creates the producer topic if it does not already exist"""
        
        futures = self.client.create_topics([
            NewTopic(topic=self.topic_name, 
                     num_partitions=self.num_partitions, 
                     replication_factor=self.num_replicas,
                     config={
                        'cleanup.policy' : 'delete',
#                         'compression.type' : 'lz4',
#                         'delete.retention.ms' : 2000,
#                         'file.delete.delay.ms' : 2000
                    }
            )
        ])
        for topic, future in futures.items():
            try:
                future.result()
                print(f"Topic '{topic}' is created")
            except Exception as e:
                print("Failed to create topic '{topic}' :")
                print(e)

    def time_millis(self):
        return int(round(time.time() * 1000))

    def close(self):
        """Prepares the producer for exit by cleaning up the producer"""
        if self.producer is not None:
            self.producer.flush()

            
    def time_millis(self):
        """Use this function to get the key for Kafka Events"""
        return int(round(time.time() * 1000))
