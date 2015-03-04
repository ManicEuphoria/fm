import redis


r_cli = redis.StrictRedis(host="localhost", port=6379, db=0)

waiting_user_set = "waitingUserSet"
