# coding=utf-8
import random

import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017/')
client.drop_database('test')
db = client.test
coll = db.coll

# 插入单条信息
rs = coll.insert_one({'a': 1, 'b': 2})
object_id = rs.inserted_id
print rs.inserted_id  # 打印插入当对象ID

# 插入多条记录
rs = coll.insert_many([{'a': random.randint(1, 10), 'b': 10}
                       for _ in range(10)])

print rs.inserted_ids  # 打印插入的对象ID列表

# 查询单条（符合的第一条）记录
print coll.find_one({'a': 1, 'b': 2})

# 集合当前全部文件档数
print coll.count()

cursor = coll.find({'a': {'$lte': 1}})  # 查询结果是一个游标
print cursor.count()    # 符合查询当文档数

for r in cursor:
    print r, r['b']     # 打印符合查询当文档内容， 以及其中b键当值

# 注意，这个循环只能进行一次。如果想再获得查询结果，需要重新find或者使用list(cursor)把结果存起来

