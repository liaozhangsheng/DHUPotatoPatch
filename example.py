from src.DHUPotatoPatch import DHUPotatoPatch
import asyncio
import csv
import random

async def main():
    # 83 表示 2024-2025 学年第二学期
    bot = DHUPotatoPatch(username="username", password="password",
                         current_semester=83, max_retries=5, timeout=10)

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
    # course_info = []
    # tasks = []
    # for course in await bot.search_courses_by_collage(3):
    #     tasks.append(bot.search_courses_by_id(course["courseCode"]))

    # results = await asyncio.gather(*tasks)
    # for result in results:
    #     for course in result:
    #         if course["maxNum"] > course["admit"]:
    #             course_info.append(course)

    # headers = ["courseName", "collage", "courseCode", "maxNum",
    #            "admit", "campus", "teacher", "week", "time", "location"]

    # with open("course_info.csv", "w", newline="") as f:
    #     writer = csv.DictWriter(f, fieldnames=headers)
    #     writer.writeheader()
    #     for course in course_info:
    #         writer.writerow(course)

    '''
    循环选课（不验证是否满人会触发验证码）
    '''
    # 课程编号: [选课序号1, 选课序号2, ...]
    selected_courses = {
        "039701": ["278361", "278362"],
        "039681": ["278364", "278365"],
        "039661": ["278368"],
    }
    rounds = 1
    while rounds != 0:
        print(f"第 {rounds} 轮选课")
        rounds += 1
        for courseCode in selected_courses:
            courses = await bot.search_courses_by_id(courseCode)
            for course in courses:
                if course["courseCode"] in selected_courses[courseCode] and course["maxNum"] > course["admit"]:
                    print(await bot.select_course(course["courseCode"]))
                    rounds = 0
                    break
            else:
                continue
            break
        await asyncio.sleep(random.randint(5, 7))

asyncio.run(main())
