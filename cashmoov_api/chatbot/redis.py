from django_redis import get_redis_connection

def redis_conn():
    return get_redis_connection("default")

def add_online_user(username):
    r = redis_conn()
    r.sadd("online_users", username)

def remove_online_user(username):
    r = redis_conn()
    r.srem("online_users", username)

def get_online_users():
    r = redis_conn()
    return [u.decode() for u in r.smembers("online_users")]

def count_online_users():
    r = redis_conn()
    return r.scard("online_users")
