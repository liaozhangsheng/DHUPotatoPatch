from src.DHUPotatoPatch import DHUPotatoPatch
import asyncio
import csv
import random

async def main():
    # 83 for the second semester of the 2024-2025 academic year, and so on
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
