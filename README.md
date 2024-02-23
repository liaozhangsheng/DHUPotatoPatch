<div align=center>
    <img src="./DHU.png" alt="DHU logo" width="50%">
</div>

<h4 align=center>上海某末流211教务处逆向API</h4>

---

### 简介

本项目是对上海某末流211教务处的逆向API，目前已经实现了简单的查询课程、选课、查成绩等功能。

### 示例

```python
from src.DHUPotatoPatch import DHUPotatoPatch
import csv

'''
查询某个学院（这里是体育部）的所有未满人的课程并写入csv文件
'''

with open("cookie", "r") as f:
    cookie = f.read()
bot = DHUPotatoPatch(cookie)

course_info = []

for co in bot.search_courses_by_collage(3):
    for cl in bot.search_courses_by_id(co["courseCode"], 81):
        if cl["maxNum"] > cl["admit"]:
            course_info.append(cl)

headers = ['courseName', 'collage', 'courseCode', 'maxNum', 'admit', 'campus', 'teacher', 'week', 'time', 'location']

with open('course_info.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()

    for info in course_info:
        writer.writerow(info)

print("done")

```