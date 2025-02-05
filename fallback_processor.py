import pika
from datetime import datetime
import json

from define_queues import defineQueues


# Fallback Service Consumer
class FallbackAudioProcessor:
    def __init__(self):
        # Similar connection setup as primary processor
        connection_params = pika.ConnectionParameters(
            host="localhost",
            credentials=pika.PlainCredentials("guest", "guest"),
            heartbeat=600,
            blocked_connection_timeout=300,
        )
        self.connection = pika.BlockingConnection(connection_params)
        self.channel = self.connection.channel()
        defineQueues(self.channel)

    def process_dlq_message(self, ch, method, properties, body):
        try:
            # Process message from DLQ
            message = json.loads(body)
            print(message)

            # Implement fallback processing logic
            result = self.fallback_processing(message)

            # Notify backend about fallback processing
            if properties.reply_to:
                self.channel.basic_publish(
                    exchange="",
                    routing_key=properties.reply_to,
                    properties=pika.BasicProperties(
                        correlation_id=properties.correlation_id
                    ),
                    body=json.dumps(
                        {"status": "processed_by_fallback", "result": result}
                    ),
                )

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(e)
            # In fallback, we might want to log the error and not requeue
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def fallback_processing(self, message):
        # Implement fallback processing logic
        return {"fallback": "done"}

    def start_consuming(self):
        self.channel.basic_consume(
            queue="audio_processing_dlq", on_message_callback=self.process_dlq_message
        )
        print("Starting fallback consumer...")
        self.channel.start_consuming()


if __name__ == "__main__":
    processor = FallbackAudioProcessor()
    processor.start_consuming()
