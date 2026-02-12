from django_redis import get_redis_connection

"""
    Ce file est pour la sauvegarde temporairement la presences des assistants
    en ligne dans une base de donnee redis (sur la ram de la machine)
"""


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

def assistant_joigned(group_name):
    r= redis_conn()
    r.sadd('chat_assistant',group_name )

def assistant_existed(group_name):
    r = redis_conn()
    return r.sismember('chat_assistant',group_name)

def remove_assistant_joigned(group_name):
    r = redis_conn()
    r.srem('chat_assistant', group_name)
