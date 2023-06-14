import grpc
from concurrent import futures
import rating_pb2
import rating_pb2_grpc
import psycopg2

class RatingServicer(rating_pb2_grpc.RatingServicer):
    def __init__(self):
        self.connection_string = 'postgresql://postgres:20072004@localhost:5432/finalProject?sslmode=disable'
        self.connection = psycopg2.connect(self.connection_string)
        self.cursor = self.connection.cursor()

    def AddReview(self, request, context):
        # Access the request parameters using request.product_id, request.rating, request.review
        product_id = request.product_id
        rating = request.rating
        review = request.review

        # Insert the review into the database
        query = "INSERT INTO reviews (product_id, rating, review) VALUES (%s, %s, %s)"
        values = (product_id, rating, review)
        self.cursor.execute(query, values)
        self.connection.commit()

        # Example response
        response = rating_pb2.ReviewResponse(message="Review added successfully")
        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor())
    rating_pb2_grpc.add_RatingServicerServicer_to_server(RatingServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started. Listening on port 50051...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()