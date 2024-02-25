import httpx
import asyncio
from bs4 import BeautifulSoup

param = "vpn-12-o2-jwgl.dhu.edu.cn"
BASE_URL = "https://webproxy.dhu.edu.cn/https/446a5061214023323032323131446855152f7f4845a0b976a6a0aa1d0121c0/dhu"


async def post_request(url: str, headers: dict, payload: dict, params: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload, params=params)
        return response.json()


class DHUPotatoPatch:
    """
    A class representing a DHU Potato Patch, which provides various methods for searching courses, selecting courses,
    removing courses, and retrieving grades.

    Attributes:
        headers (dict): The headers to be included in the HTTP requests.
        semester (int): The current semester ID.

    Methods:
        search_courses_by_name: Search courses by name.
        search_courses_by_id: Search courses by ID.
        search_courses_by_collage: Search courses by collage.
        select_course: Select a course.
        remove_course: Remove a course.
        get_grades: Get grades for a specific semester.
        get_gpa: Get the GPA (Grade Point Average).
        get_the_class_schedule: Get the class schedule.
        get_current_semester: Get the current semester ID.
    """

    def __init__(self, cookie: str):
        """
        Initializes a new instance of the DHUPotatoPatch class.

        Args:
            cookie (str): The cookie string used for authentication.
        """

        self.headers = {
            "Cookie": cookie,
        }

        self.semester = self.get_current_semester()

    async def search_courses_by_name(self, courseName: str, termId: int = None) -> list:
        """
        Search courses by name.

        Args:
            courseName (str): The name of the course to search for.
            termId (int, optional): The ID of the term to search in. Defaults to None.

        Returns:
            list: A list of dictionaries representing the search results, each containing the course name, course ID,
                  credit, and organization name.
        
        Example:
            ```python
            DHUPotatoPatch.search_courses_by_name("计算机")
            DHUPotatoPatch.search_courses_by_name("计算机", 81)
            ```
        """

        url = f"{BASE_URL}/PublicQuery/getSelectCourseTermList"
        payload = {
            "sEcho": 2,
            "iColumns": 6,
            "sColumns": "",
            "iDisplayStart": 0,
            "iDisplayLength": 100,
            "mDataProp_0": "kcmc",
            "mDataProp_1": "kcbh",
            "mDataProp_2": "xf",
            "mDataProp_3": "jxdg_url",
            "mDataProp_4": "jxrl_url",
            "mDataProp_5": "orgname",
            "iSortCol_0": 0,
            "sSortDir_0": "asc",
            "iSortingCols": 1,
            "bSortable_0": "false",
            "bSortable_1": "false",
            "bSortable_2": "false",
            "bSortable_3": "false",
            "bSortable_4": "false",
            "bSortable_5": "false",
            "termId": self.semester if termId == None else termId,
            "course": courseName,
        }

        response = await post_request(url, self.headers, payload, param)

        courses = []
        for course in response["aaData"]:
            courses.append({
                "courseName": course["kcmc"],
                "courseCode": course["kcbh"],
                "credit": course["xf"],
                "orgnName": course["orgname"]
            })

        return courses

    async def search_courses_by_id(self, courseCode: str, termId=None) -> list:
        """
        Search courses by ID.

        Args:
            courseCode (str): The ID of the course to search for.
            termId (int, optional): The ID of the term to search in. Defaults to None.

        Returns:
            list: A list of dictionaries representing the search results, each containing the course name, collage,
                  course code, maximum number of students, admission number, campus, teacher, week, time, and location.

        Example:
            ```python
            DHUPotatoPatch.search_courses_by_id("039981")
            DHUPotatoPatch.search_courses_by_id("039981", 81)
            ```
        """

        url = f"{BASE_URL}/PublicQuery/getCourseTimeTableInfo"
        payload = {
            "kcbh": courseCode,
            "termId": self.semester if termId == None else termId,
        }

        response = await post_request(url, self.headers, payload, param)
        soup = BeautifulSoup(response["content"], 'html.parser')
        rows = soup.find_all('tr')

        courseInfo = [
            {
                "courseName": cols[1].text,
                "collage": cols[2].text,
                "courseCode": cols[3].text,
                "maxNum": cols[5].text,
                "admit": cols[7].text,
                "campus": cols[8].text,
                "teacher": cols[9].text,
                "week": cols[10].text,
                "time": cols[11].text,
                "location": cols[12].text,
            }
            for i, row in enumerate(rows) if i % 2 == 0
            for cols in [row.find_all('td', style="text-align: center;vertical-align: inherit")]
        ]

        return courseInfo

    async def search_courses_by_collage(self, orgnId: int) -> list:
        """
        Search courses by collage.

        Args:
            orgnId (int): The ID of the collage to search for.

        Returns:
            list: A list of dictionaries representing the search results, each containing the credit, course code,
                  and course name.

        Example:
            ```python
            DHUPotatoPatch.search_courses_by_collage(3)
            ```
        """

        url = f"{BASE_URL}/selectcourse/initSCByOrgn"
        payload = {
            "orgnId": orgnId,
        }

        response = await post_request(url, self.headers, payload, param)

        courses = []
        for course in response["orgnCourses"]:
            courses.append({
                "credit": course["credit"],
                "courseCode": course["courseCode"],
                "courseName": course["courseName"]
            })

        return courses

    async def select_course(self, courseId: str, needMaterial: bool = False) -> dict:
        """
        Select a course.

        Args:
            courseId (str): The ID of the class to select.
            needMaterial (bool, optional): Whether materials are needed for the course. async Defaults to False.

        Returns:
            bool: True if the course selection is successful, False otherwise.

        Example:
            ```python
            DHUPotatoPatch.select_course("269663")
            DHUPotatoPatch.select_course("269663", True)
            ```
        """

        url = f"{BASE_URL}/selectcourse/scSubmit"
        payload = {
            "cttId": courseId,
            "needMaterial": needMaterial
        }

        return await post_request(url, self.headers, payload, param)

    async def remove_course(self, courseCode: str, classNo: int) -> dict:
        """
        Remove a course.

        Args:
            courseCode (str): The ID of the course to remove.
            classNo (int): The class number of the course to remove.

        Returns:
            bool: True if the course removal is successful, False otherwise.

        Example:
            ```python
            DHUPotatoPatch.remove_course("039981", 1)
            ```
        """

        url = f"{BASE_URL}/selectcourse/cancelSC"
        payload = {
            "courseCode": courseCode,
            "classNo": classNo,
            "cancelType": 1
        }

        return await post_request(url, self.headers, payload, param)

    def get_grades(self, semester: int = None) -> list:
        """
        Get grades for a specific semester.

        Args:
            semester (int): The ID of the semester to retrieve grades for.

        Returns:
            list: A list of dictionaries representing the grades for each course, including the course name,
                  course ID, credit, grade, and GPA.

        Example:
            ```python
            DHUPotatoPatch.get_grades()
            DHUPotatoPatch.get_grades(81)
            ```
        """

        url = f"{BASE_URL}/grade/gradeAnalysis/showPsersonalGrades"
        payload = {
            "semester": self.semester if semester == None else semester,
            "xh": "0"
        }

        response = httpx.post(url, headers=self.headers, data=payload, params=param).json()
        response_list = response["list"][0]["courseGrades"]

        return [{"courseName": item["KCMC"], "credit": item["XF"], "grade": item["CJ"]} for item in response_list]
    
    def get_gpa(self) -> list:
        """
        Get the GPA (Grade Point Average).

        Returns:
            list: A list of dictionaries representing the GPA for each semester, including the semester name
                and GPA value.

        Example:
            ```python
            DHUPotatoPatch.get_gpa()
            ```
        """

        url = f"{BASE_URL}/grade/student/showGradePoint"
        payload = {
            "type": 1
        }

        response = httpx.post(url, headers=self.headers, data=payload, params=param).json()

        response_list = response["list"]

        return [{"averageGpa": item["ptjd"], "semester": item["xqbh"]} for item in response_list]

    def get_the_class_schedule(self):
        """
        Get the class schedule.

        TODO: Add documentation for this method.
        """

        pass

    def get_current_semester(self) -> int:
        """
        Get the current semester ID.

        Returns:
            int: The ID of the current semester.

        Example:
            ```python
            DHUPotatoPatch.get_current_semester()
            ```
        """

        url = f"{BASE_URL}/common/semesterSS"
        payload = {
            "ordered": True,
            "sortType": "desc"
        }

        try:
            response = httpx.post(url=url, headers=self.headers, data=payload, params=param).json()
        except:
            print("Invalid cookie! Please check that the cookie is correct.")
            exit(1)

        if 'semesterSS' in response:
            for semester in response["semesterSS"]:
                if semester["current"]:
                    return semester["id"]
