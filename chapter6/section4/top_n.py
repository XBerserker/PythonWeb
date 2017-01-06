# coding=utf-8
import string
import random

import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)

GAME_BOARD_KEY = 'game.board'

#插入1000条随机用户名和分数组成的记录。zadd方法表示我们操作的时一个有序列表
for _ in range(1000):
    score = round((random.random() * 100), 2)
    user_id = ''.join(random.sample(string.ascii_letters, 6))
    r.zadd(GAME_BOARD_KEY, score, user_id)

# 随机获得一个用户和他的得分，zrevrange表示从高到低对列表排序
user_id, score = r.zrevrange(GAME_BOARD_KEY, 0, -1, withscores=True)[random.randint(0, 200)]
print user_id, score

# 获取全部记录条目数
board_count = r.zcount(GAME_BOARD_KEY, 0, 100)

# 这个用户分数超过吕多少用户
current_count = r.zcount(GAME_BOARD_KEY, 0, score)

print current_count, board_count

print 'TOP 10'
print '-' * 20

# 获取排行榜前10位当用户名和得分
for user_id, score in r.zrevrangebyscore(GAME_BOARD_KEY, 100, 0, start=0, num=10, withscores=True):
    print user_id, score