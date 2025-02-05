import pika
from datetime import datetime
import json
import time

from define_queues import defineQueues


class AudioProcessor:
    def __init__(self):
        # Connection parameters
        self.connection_params = pika.ConnectionParameters(
            host="localhost",
            credentials=pika.PlainCredentials("guest", "guest"),
            heartbeat=600,
            blocked_connection_timeout=300,
        )

        # Connect and create channel
        self.connection = pika.BlockingConnection(self.connection_params)
        self.channel = self.connection.channel()

        defineQueues(self.channel)

        # Set QoS
        self.channel.basic_qos(prefetch_count=1)

    def process_audio(self, ch, method, properties, body):
        try:
            # Start processing timer
            start_time = datetime.now()
            # Decode message
            message = json.loads(body)
            print(message, properties)
            audio_file = message["audio_file"]

            # Process audio file
            processed_result = {"file": audio_file}

            time.sleep(10)
            # Check if we're still within ack timeout
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            print("took time to process: ", processing_time)
            if processing_time >= 60000:  # 1 minutes in milliseconds
                # If processing took too long, let the ack timeout handle it
                return
            print("post processing check")
            # Send response back to backend
            if properties.reply_to:
                print("replying...", datetime.now())
                self.channel.basic_publish(
                    exchange="",
                    routing_key=properties.reply_to,
                    properties=pika.BasicProperties(
                        correlation_id=properties.correlation_id
                    ),
                    body=json.dumps({"status": "success", "result": processed_result}),
                )

            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print("in processor exception: ", e)
            # Check delivery attempts from message headers
            headers = properties.headers or {}
            delivery_count = headers.get("x-delivery-count", 0)
            print("delivery count: ", delivery_count)
            # Negative acknowledgment to requeue if processing fails
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def process_audio_file(self, audio_file):
        # Implement your audio processing logic here
        pass

    def start_consuming(self):
        self.channel.basic_consume(
            queue="audio_processing_queue", on_message_callback=self.process_audio
        )
        print("Starting to consume messages...")
        try:
            self.channel.start_consuming()
        except pika.exceptions.ChannelClosedByBroker:
            print("reconnecting...")
            self.reconnect()
        except Exception as e:
            print(f"didn't go to reconnect: {e}")

    def reconnect(self):
        """Reconnect to RabbitMQ if connection is lost"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()

            self.connection = pika.BlockingConnection(self.connection_params)
            self.channel = self.connection.channel()
            self.start_consuming()
        except Exception as e:
            print(f"Failed to reconnect: {e}")


if __name__ == "__main__":
    processor = AudioProcessor()
    processor.start_consuming()
