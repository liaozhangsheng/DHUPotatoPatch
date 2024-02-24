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