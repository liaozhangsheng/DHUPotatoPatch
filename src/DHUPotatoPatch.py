import httpx
from bs4 import BeautifulSoup

param = "vpn-12-o2-jwgl.dhu.edu.cn"
BASE_URL = "https://webproxy.dhu.edu.cn/https/446a5061214023323032323131446855152f7f4845a0b976a6a0aa1d0121c0/dhu"


async def post_request(url: str, headers: dict, payload: dict, params: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload, params=params)
        return response.json()


class DHUPotatoPatch:

    def __init__(self, cookie: str):

        self.headers = {
            "Cookie": cookie,
        }

        self.semester = self.get_current_semester()

    async def search_courses_by_name(self, courseName: str, termId: int = None) -> list:

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
                "week": cols[10].text if len(cols) > 10 else "",
                "time": cols[11].text if len(cols) > 10 else "",
                "location": cols[12].text if len(cols) > 10 else "",
            }
            for row in rows if len(row) > 4
            for cols in [row.find_all('td', style="text-align: center;vertical-align: inherit")]
        ]

        return courseInfo

    async def search_courses_by_collage(self, orgnId: int) -> list:

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

        url = f"{BASE_URL}/selectcourse/scSubmit"
        payload = {
            "cttId": courseId,
            "needMaterial": needMaterial
        }

        return await post_request(url, self.headers, payload, param)

    async def remove_course(self, courseCode: str, classNo: int) -> dict:

        url = f"{BASE_URL}/selectcourse/cancelSC"
        payload = {
            "courseCode": courseCode,
            "classNo": classNo,
            "cancelType": 1
        }

        return await post_request(url, self.headers, payload, param)

    def get_grades(self, semester: int = None) -> list:

        url = f"{BASE_URL}/grade/gradeAnalysis/showPsersonalGrades"
        payload = {
            "semester": self.semester if semester == None else semester,
            "xh": "0"
        }

        response = httpx.post(url, headers=self.headers,
                              data=payload, params=param).json()
        response_list = response["list"][0]["courseGrades"]

        return [{"courseName": item["KCMC"], "credit": item["XF"], "grade": item["CJ"]} for item in response_list]

    def get_gpa(self) -> list:

        url = f"{BASE_URL}/grade/student/showGradePoint"
        payload = {
            "type": 1
        }

        response = httpx.post(url, headers=self.headers,
                              data=payload, params=param).json()

        response_list = response["list"]

        return [{"averageGpa": item["ptjd"], "semester": item["xqbh"]} for item in response_list]

    def get_the_class_schedule(self):

        pass

    def get_current_semester(self) -> int:

        url = f"{BASE_URL}/common/semesterSS"
        payload = {
            "ordered": True,
            "sortType": "desc"
        }

        try:
            response = httpx.post(
                url=url, headers=self.headers, data=payload, params=param).json()
        except:
            print("Invalid cookie! Please check that the cookie is correct.")
            exit(1)

        if 'semesterSS' in response:
            for semester in response["semesterSS"]:
                if semester["current"]:
                    return semester["id"]
