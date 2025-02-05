def defineQueues(channel):

    # Declare exchanges
    channel.exchange_declare(
        exchange="audio_processing", exchange_type="direct", durable=True
    )

    channel.exchange_declare(
        exchange="audio_processing_dlx", exchange_type="direct", durable=True
    )

    # Declare primary queue with DLX configuration
    channel.queue_declare(
        queue="audio_processing_queue",
        durable=True,
        arguments={
            "x-dead-letter-exchange": "audio_processing_dlx",
            "x-dead-letter-routing-key": "expired_audio",
            "x-message-ttl": 60000,  # 1 minutes timeout
            "x-max-priority": 10,
            "x-consumer-timeout": 60000,  # 1 minutes ack timeout
            "delivery-limit": 1,  # Maximum number of delivery attempts before moving to DLQ
        },
    )
    # Declare DLQ (Dead Letter Queue) for fallback processing
    channel.queue_declare(queue="audio_processing_dlq", durable=True)

    # Bind queues to exchanges
    channel.queue_bind(
        exchange="audio_processing",
        queue="audio_processing_queue",
        routing_key="audio",
    )

    channel.queue_bind(
        exchange="audio_processing_dlx",
        queue="audio_processing_dlq",
        routing_key="expired_audio",
    )
