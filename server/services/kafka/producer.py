import os
import json
import logging
from typing import Any, Dict
import asyncio
from aiokafka import AIOKafkaProducer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_CELLS = os.getenv("KAFKA_TOPIC_CELLS", "hivedb-cells")
KAFKA_TOPIC_USERS = os.getenv("KAFKA_TOPIC_USERS", "hivedb-users")
KAFKA_TOPIC_AUDIT = os.getenv("KAFKA_TOPIC_AUDIT", "hivedb-audit")

logger = logging.getLogger(__name__)

class KafkaProducer:
    """Kafka producer for HiveDB events."""
    
    def __init__(self):
        self.producer = None
        self.is_ready = False
    
    async def start(self):
        """Start the Kafka producer."""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            await self.producer.start()
            self.is_ready = True
            logger.info("Kafka producer started successfully")
        except Exception as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            self.is_ready = False
    
    async def stop(self):
        """Stop the Kafka producer."""
        if self.producer:
            await self.producer.stop()
            self.is_ready = False
            logger.info("Kafka producer stopped")
    
    async def send_message(self, topic: str, data: Dict[str, Any], key: str = None):
        """Send a message to a Kafka topic."""
        if not self.is_ready:
            logger.warning("Kafka producer is not ready, message not sent")
            return False
        
        try:
            key_bytes = key.encode('utf-8') if key else None
            await self.producer.send_and_wait(topic, data, key=key_bytes)
            logger.debug(f"Message sent to topic {topic}: {data}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message to Kafka: {e}")
            return False
    
    async def send_cell_event(self, cell_key: str, event_type: str, data: Dict[str, Any]):
        """Send a cell-related event to Kafka."""
        message = {
            "cell_key": cell_key,
            "event_type": event_type,
            "timestamp": asyncio.get_event_loop().time(),
            "data": data
        }
        return await self.send_message(KAFKA_TOPIC_CELLS, message, key=cell_key)
    
    async def send_user_event(self, user_id: int, event_type: str, data: Dict[str, Any]):
        """Send a user-related event to Kafka."""
        message = {
            "user_id": user_id,
            "event_type": event_type,
            "timestamp": asyncio.get_event_loop().time(),
            "data": data
        }
        return await self.send_message(KAFKA_TOPIC_USERS, message, key=str(user_id))
    
    async def send_audit_event(self, actor_id: str, action: str, resource: str, details: Dict[str, Any]):
        """Send an audit event to Kafka."""
        message = {
            "actor_id": actor_id,
            "action": action,
            "resource": resource,
            "timestamp": asyncio.get_event_loop().time(),
            "details": details
        }
        return await self.send_message(KAFKA_TOPIC_AUDIT, message)

# Singleton instance
kafka_producer = KafkaProducer()
