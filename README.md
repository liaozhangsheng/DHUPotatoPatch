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
with open("cookie", "r") as f: # 从教务系统获取cookie存入文件中再读取，或者直接填入也行
    cookie = f.read()
bot = DHUPotatoPatch(cookie)

'''
查询课程
'''
# 通过课程代码搜索课程
print(await bot.search_courses_by_id("092161"))

# 通过学院搜索课程
print(await bot.search_courses_by_collage(3))

# 通过课程名搜索课程
print(await bot.search_courses_by_name("篮球"))

'''
选课、退课
'''
# 退课
print(await bot.remove_course("039981", 1))

# 选课
print(await bot.select_course("269663")) # 填课程序号

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
import csv
import asyncio

with open("cookie", "r") as file:
    cookie = file.read().strip()
patch = DHUPotatoPatch(cookie=cookie)

course_info = []

tasks = []
for co in await patch.search_courses_by_collage(3):
    tasks.append(patch.search_courses_by_id(co["courseCode"], 81))

results = await asyncio.gather(*tasks)

for result in results:
    for cl in result:
        if cl["maxNum"] > cl["admit"]:
            course_info.append(cl)

headers = ['courseName', 'collage', 'courseCode', 'maxNum',
            'admit', 'campus', 'teacher', 'week', 'time', 'location']

with open('course_info.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, headers)
    writer.writeheader()
    for cl in course_info:
        writer.writerow(cl)

df = pd.read_csv('course_info.csv')

print("done")

```