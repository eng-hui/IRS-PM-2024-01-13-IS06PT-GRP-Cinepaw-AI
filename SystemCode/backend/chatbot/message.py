from kombu import Connection, Exchange, Queue
REDIS_URL = 'redis://localhost:6379//'
chat_exchange = Exchange('chat', 'direct', durable=True)

def produce_chat_message(message, session_key):
    chat = Queue(session_key, exchange=chat_exchange, routing_key=session_key)
    with Connection(REDIS_URL) as conn:
        # produce
        producer = conn.Producer(serializer='json')
        producer.publish(message,
                        exchange=chat_exchange, routing_key=session_key,
                        declare=[chat])

def consume_chat_message(session_key):
    tmp = {}
    def fetch_message(body, message):
        tmp["result"] = body
        message.ack()
        return tmp
        
    chat = Queue(session_key, exchange=chat_exchange, routing_key=session_key)
    with Connection(REDIS_URL) as conn:
        with conn.Consumer(chat, callbacks=[fetch_message]) as consumer:
            try:
                conn.drain_events(timeout=1)
            except Exception as e:
                pass
    return tmp.get("result")

