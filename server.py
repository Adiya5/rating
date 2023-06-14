import grpc
from concurrent import futures
import rating_pb2
import rating_pb2_grpc
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import pika

# Создание базового класса модели с использованием SQLAlchemy
Base = declarative_base()

# Определение модели для хранения рейтинга и обзора
class RatingReview(Base):
    __tablename__ = 'ratings_reviews'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    rating = Column(Float)
    review = Column(String)

# Создание соединения с базой данных PostgreSQL
engine = create_engine('postgresql://postgres:20072004@localhost:5432/finalProject?sslmode=disable')
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

# Реализация сервиса для обработки запросов о рейтингах и обзорах
class RatingReviewService(rating_pb2_grpc.RatingReviewServicer):
    def __init__(self):
        # Создание соединения с RabbitMQ
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        # Определение имени очереди
        self.queue_name = 'rating_reviews'

        # Создание очереди, если она не существует
        self.channel.queue_declare(queue=self.queue_name)

    def AddRatingReview(self, request, context):
        product_id = request.product_id
        rating = request.rating
        review = request.review

        # Сохранение рейтинга и обзора в базе данных
        session = Session()
        rating_review = RatingReview(product_id=product_id, rating=rating, review=review)
        session.add(rating_review)
        session.commit()
        session.close()

        # Отправка сообщения в очередь RabbitMQ
        message = f"Product ID: {product_id}, Rating: {rating}, Review: {review}"
        self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=message)

        # Отправка подтверждения клиенту
        response = rating_pb2.AddRatingReviewResponse(message="Rating and review added successfully")
        return response

    def serve(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        rating_pb2_grpc.add_RatingReviewServicer_to_server(self, server)
        server.add_insecure_port('[::]:50051')
        server.start()
        server.wait_for_termination()

    def start_consuming(self):
        def callback(ch, method, properties, body):
            # Обработка сообщения из очереди RabbitMQ
            print("Received message:", body)

        # Установка callback-функции для обработки сообщений
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=True)

        # Начать прослушивание очереди
        self.channel.start_consuming()

if __name__ == '__main__':
    rating_service = RatingReviewService()
    rating_service.start_consuming()
    rating_service.serve()