import os
import json
import logging
import asyncio
from typing import Dict, Any, Callable, List
from aiokafka import AIOKafkaConsumer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_CELLS = os.getenv("KAFKA_TOPIC_CELLS", "hivedb-cells")
KAFKA_TOPIC_USERS = os.getenv("KAFKA_TOPIC_USERS", "hivedb-users")
KAFKA_TOPIC_AUDIT = os.getenv("KAFKA_TOPIC_AUDIT", "hivedb-audit")

logger = logging.getLogger(__name__)

class KafkaConsumer:
    """Kafka consumer for HiveDB events."""
    
    def __init__(self):
        self.consumers = {}
        self.handlers = {}
        self.running = False
    
    async def start(self, topics: List[str]):
        """Start the Kafka consumer for the specified topics."""
        try:
            for topic in topics:
                if topic in self.consumers:
                    continue
                
                consumer = AIOKafkaConsumer(
                    topic,
                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                    group_id=f"hivedb-{topic}-consumer",
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    auto_offset_reset="latest"
                )
                
                await consumer.start()
                self.consumers[topic] = consumer
                self.handlers[topic] = []
                
                # Start consumer task
                asyncio.create_task(self._consume_messages(topic))
            
            self.running = True
            logger.info(f"Kafka consumer started for topics: {topics}")
        except Exception as e:
            logger.error(f"Failed to start Kafka consumer: {e}")
            await self.stop()
    
    async def stop(self):
        """Stop all Kafka consumers."""
        for topic, consumer in self.consumers.items():
            await consumer.stop()
            logger.info(f"Kafka consumer stopped for topic: {topic}")
        
        self.consumers = {}
        self.handlers = {}
        self.running = False
    
    async def _consume_messages(self, topic: str):
        """Consume messages from a Kafka topic."""
        consumer = self.consumers.get(topic)
        if not consumer:
            return
        
        try:
            async for message in consumer:
                logger.debug(f"Received message from topic {topic}: {message.value}")
                
                # Call all registered handlers for this topic
                for handler in self.handlers.get(topic, []):
                    try:
                        await handler(message.value, message.key.decode('utf-8') if message.key else None)
                    except Exception as e:
                        logger.error(f"Error in message handler: {e}")
        except Exception as e:
            logger.error(f"Error consuming messages from topic {topic}: {e}")
            if self.running:
                # Try to restart the consumer
                await asyncio.sleep(5)
                asyncio.create_task(self._consume_messages(topic))
    
    def register_handler(self, topic: str, handler: Callable[[Dict[str, Any], str], None]):
        """Register a handler for a specific topic."""
        if topic not in self.handlers:
            self.handlers[topic] = []
        
        self.handlers[topic].append(handler)
        logger.info(f"Registered handler for topic {topic}")
        
        # Start consumer for this topic if not already started
        if topic not in self.consumers and self.running:
            asyncio.create_task(self.start([topic]))

# Singleton instance
kafka_consumer = KafkaConsumer()
