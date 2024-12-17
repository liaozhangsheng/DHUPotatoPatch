<div align=center>
    <img src="./DHU.png" alt="DHU logo" width="50%">
</div>

<h1 align=center>这个库什么也不能做，请不要盯着我</h1>

---

<div style="background-color: #fff3cd; border-left: 4px solid #ffeeba; padding: 10px; margin: 20px 0;">
  <strong>⚠️ 注意:</strong> 此代码需要 <a href="https://nodejs.org/zh-cn/">nodejs</a> 环境（用于运行加密脚本）。
</div>

### 示例

```python
from src.DHUPotatoPatch import DHUPotatoPatch
import asyncio
import csv
import random

async def main():
    # 83 代表 2024-2025第二学期，依此类推
    bot = DHUPotatoPatch(username="username", password="password", current_semester="83")

    '''
    查课程
    '''
    # print(await bot.search_courses_by_name("微积分"))
    # print(await bot.search_courses_by_id("010761"))
    # print(await bot.search_courses_by_collage(1))

    '''
    选课退课
    '''
    # print(await bot.select_course("273731"))
    # print(await bot.remove_course("273731", 3))

    '''
    查成绩、绩点
    '''
    # print(await bot.get_grades())
    # print(await bot.get_gpa())

    '''
    查询未满人体育课
    '''
    course_info = []
    tasks = []
    for course in await bot.search_courses_by_collage(3):
        tasks.append(bot.search_courses_by_id(course["courseCode"]))

    results = await asyncio.gather(*tasks)
    for result in results:
        for course in result:
            if course["maxNum"] > course["admit"]:
                course_info.append(course)

    headers = ["courseName", "collage", "courseCode", "maxNum",
               "admit", "campus", "teacher", "week", "time", "location"]

    with open("course_info.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for course in course_info:
            writer.writerow(course)

    '''
    循环选课
    '''
    # selected_courses = ["273933", "273934"]
    # while True:
    #     for course in selected_courses:
    #         print(await bot.select_course(course))
    #     await asyncio.sleep(random.randint(20, 30))

asyncio.run(main())
```

### 仅供学习交流使用，请勿用于商业用途，否则后果自负。
