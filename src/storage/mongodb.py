from mongoengine import connect


def init_mongo() -> None:
    connect(
        db="hw07db",
        host="mongodb://127.0.0.1:27017/hw07db",
        alias="default",
    )
