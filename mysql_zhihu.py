# -*- coding:utf-8 -*-

#coding=utf-8
import MySQLdb

conn= MySQLdb.connect(
        host='localhost',
        port = 3306,
        user='test',
        passwd='!qazzaq1',
        db ='zhihuDB',
        )
cur = conn.cursor()

#创建数据表
#cur.execute("create table student(id int ,name varchar(20),class varchar(30),age varchar(10))")

#插入一条数据
sql_i = "insert into zhihu_user values(%s,%s,%s,%s,%)"
cur.execute("insert into zhihu_user values(null,'user_test','Nick Name','互联网','本科','female')")


#修改查询条件的数据
#cur.execute("update student set class='3 year 1 class' where name = 'Tom'")

#删除查询条件的数据
#cur.execute("delete from student where age='9'")

num = cur.execute("select * from zhihu_user")
print num
students = cur.fetchmany(num)
for student in students:
    print student
    print student[3]

cur.close()
conn.commit()
conn.close()
