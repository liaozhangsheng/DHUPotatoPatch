import requests
import json
from bs4 import BeautifulSoup

param = "vpn-12-o2-jwgl.dhu.edu.cn"
BASE_URL = "https://webproxy.dhu.edu.cn/https/446a5061214023323032323131446855152f7f4845a0b976a6a0aa1d0121c0/dhu"

class DHUPotatoPatch:

    def __init__(self, cookie: str):

        self.headers = {
            "Cookie": cookie,
        }

        self.semester = self.get_current_semester()

    def search_courses_by_name(self, courseName: str, termId: int = None) -> list:

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

        response = requests.post(url, headers=self.headers, data=payload, params=param)
        data = response.json()

        courses = []
        for course in data["aaData"]:
            courses.append({
                "courseName": course["kcmc"],
                "courseID": course["kcbh"],
                "credit": course["xf"],
                "orgnName": course["orgname"]
            })

        return courses

    def search_courses_by_id(self, courseID: str, termId) -> list:

        url = f"{BASE_URL}/PublicQuery/getCourseTimeTableInfo"
        payload = {
            "kcbh": courseID,
            "termId": termId
        }

        response = requests.post(url, headers=self.headers, data=payload, params=param)

        html_doc = json.loads(response.text)["content"]
        soup = BeautifulSoup(html_doc, 'html.parser')
        rows = soup.find_all('tr')
        courseInfo = []
        for i, row in enumerate(rows):
            if i % 2 == 0:
                cols = row.find_all('td', style="text-align: center;vertical-align: inherit")
                # cols_text = []
                # for col in cols:
                #     cols_text.append(col.text)
                # courseInfo.append(cols_text)
                courseInfo.append({
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
                })

        return courseInfo
    
    def search_courses_by_collage(self, orgnId: int) -> list:
        url = f"{BASE_URL}/selectcourse/initSCByOrgn"
        payload = {
            "orgnId": orgnId,
        }

        response = requests.post(url, headers=self.headers, data=payload, params=param)
        data = response.json()

        courses = []
        for course in data["orgnCourses"]:
            courses.append({
                "credit": course["credit"],
                "courseCode": course["courseCode"],
                "courseName": course["courseName"]
            })

        return courses

    def select_course(self, classId: str, needMaterial: bool = False) -> bool:

        url = f"{BASE_URL}/selectcourse/scSubmit"
        payload = {
            "cttId": classId,
            "needMaterial": needMaterial
        }

        response = requests.post(url, headers=self.headers, data=payload, params=param)
        print(response.text)
        
        return json.loads(response.text)["success"]

    def remove_course(self, courseId: str, classNo: int) -> bool:
        
        url = f"{BASE_URL}/selectcourse/cancelSC"
        payload = {
            "courseCode": courseId,
            "classNo": classNo,
            "cancelType": 1
        }

        response = requests.post(url, headers=self.headers, data=payload, params=param)

        print(response.text)
        return json.loads(response.text)["success"]

    def get_grades(self, semester: int) -> list:
        
        url = f"{BASE_URL}/grade/gradeAnalysis/showPsersonalGrades"
        payload = {
            "semester": semester,
            "xh": "0"
        }

        response = requests.post(url, headers=self.headers, data=payload, params=param)

        return json.loads(response.text)["list"][0]["courseGrades"]

    def get_gpa(self) -> list:
        
        url = f"{BASE_URL}/grade/student/showGradePoint"
        payload = {
            "type": 1
        }

        response = requests.post(url, headers=self.headers, data=payload, params=param)
        
        return json.loads(response.text)["list"]

    def get_the_class_schedule(self):
        pass

    def get_current_semester(self) -> int:

        url = f"{BASE_URL}/common/semesterSS"
        payload = {
            "ordered": True,
            "sortType": "desc"
        }

        response = requests.post(url, headers=self.headers, data=payload, params=param)
        
        if response.text == "/dhu/casLogin" or json.loads(response.text)["success"] == False:
            raise Exception("Cookie无效，请检查或更新Cookie")
        
        for semester in json.loads(response.text)["semesterSS"]:
            if semester["current"]:
                return semester["id"]
