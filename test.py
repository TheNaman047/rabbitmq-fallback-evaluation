# Primary Service Consumer
import pika
from datetime import datetime
import json


# Backend Publisher Example
def publish_audio_task(audio_file, priority=0):
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    # Generate correlation ID
    correlation_id = str(datetime.utcnow().timestamp())

    # Publish message
    channel.basic_publish(
        exchange="audio_processing",
        routing_key="audio",
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
            priority=priority,  # Set message priority
            correlation_id=correlation_id,
            reply_to="backend_callback_queue",  # Queue for receiving processing results
        ),
        body=json.dumps(
            {"audio_file": audio_file, "timestamp": str(datetime.utcnow())}
        ),
    )

    connection.close()


if __name__ == "__main__":
    publish_audio_task("some text", 1)
