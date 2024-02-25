<div align=center>
    <img src="./DHU.png" alt="DHU logo" width="50%">
</div>

<h4 align=center>上海某末流本科教务系统的逆向API</h4>

---

### 简介

本项目是对上海某末流本科教务系统的逆向API，目前已经实现了简单的查询课程、选课、查成绩等功能。

### 示例

```python
from src.DHUPotatoPatch import DHUPotatoPatch

# 初始化
with open("cookie", "r") as f:
    cookie = f.read()
bot = DHUPotatoPatch(cookie)

'''
查询课程
'''
# 通过课程代码搜索课程
print(bot.search_courses_by_id("039981"))

# 通过学院搜索课程
print(bot.search_courses_by_collage(3))

# 通过课程名搜索课程
print(bot.search_courses_by_name("篮球"))

'''
选课、退课
'''
# 退课
print(bot.remove_course("039981", 1))

# 选课
print(bot.select_course("269663")) # 填课程序号

'''
查成绩、绩点
'''
# 查询绩点
print(bot.get_gpa())

# 查询成绩
print(bot.get_grades())

```

#### 小例子：查询体育部未满人的课并保存为csv文件

```python
from src.DHUPotatoPatch import DHUPotatoPatch
import csv

course_info = []

for co in bot.search_courses_by_collage(3):
    for cl in bot.search_courses_by_id(co["courseCode"], 81):
        if cl["maxNum"] > cl["admit"]:
            course_info.append(cl)

headers = ['courseName', 'collage', 'courseCode', 'maxNum',
           'admit', 'campus', 'teacher', 'week', 'time', 'location']

with open('course_info.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()

    for info in course_info:
        writer.writerow(info)

print("done")

```