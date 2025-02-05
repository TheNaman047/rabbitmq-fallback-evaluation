# Primary Service Consumer
import pika
from datetime import datetime
import json

connection_params = pika.ConnectionParameters(
    host="localhost",
    credentials=pika.PlainCredentials("guest", "guest"),
    heartbeat=600,
    blocked_connection_timeout=300,
)
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()
# Ensure callback queue exists
result = channel.queue_declare(
    queue="backend_callback_queue",
    durable=True,
    exclusive=False,
    auto_delete=False,
    arguments={"x-message-ttl": 600000},  # 10 minutes timeout for replies
)
callback_queue = result.method.queue


# Backend Publisher Example
def publish_audio_task(audio_file, priority=0):

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
            reply_to=callback_queue,  # Queue for receiving processing results
        ),
        body=json.dumps(
            {"audio_file": audio_file, "timestamp": str(datetime.utcnow())}
        ),
    )

    # connection.close()


def handle_callback(ch, method, properties, body):
    try:
        # Decode message
        message = json.loads(body)
        print(message, properties)

        # Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(e)
        # Negative acknowledgment to requeue if processing fails
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_consuming():
    channel.basic_consume(queue=callback_queue, on_message_callback=handle_callback)
    print("Starting to consume messages...")
    channel.start_consuming()


if __name__ == "__main__":
    print("producing")
    publish_audio_task("some text", 1)
    start_consuming()
