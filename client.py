import grpc
import rating_pb2
import rating_pb2_grpc

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = rating_pb2_grpc.RatingServiceStub(channel)

    product_id = input("Введите идентификатор товара: ")
    rating = int(input("Введите рейтинг (от 1 до 5): "))
    review = input("Введите обзор: ")

    request = rating_pb2.Review(product_id=product_id, rating=rating, review=review)
    response = stub.AddReview(request)

    print("Рейтинг и обзор успешно добавлены.")

if __name__ == '__main__':
    run()