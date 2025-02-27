import httpx
from bs4 import BeautifulSoup

from .encryptAES import encryptAES

param = "vpn-12-o2-jwgl.dhu.edu.cn"
BASE_URL = "https://webproxy.dhu.edu.cn/https/446a5061214023323032323131446855152f7f4845a0b976a6a0aa1d0121c0/dhu"


class DHUPotatoPatch:

    def __init__(self, username: str, password: str, current_semester: int, max_retries: int = 5, timeout: int = 10):

        self.client = httpx.AsyncClient()
        self.username = username
        self.password = password
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = {
            "Cookie": self.login_and_get_cookie(),
        }

        self.current_semester = current_semester

    async def __async_post_request__(self, url: str, headers: dict, payload: dict, params: str) -> dict:

        for attempt in range(self.max_retries):
            try:
                response = await self.client.post(url, headers=headers, data=payload, params=params, timeout=self.timeout)

                if response.status_code != 200:
                    print("Login error, re-login...")
                    self.headers["Cookie"] = self.login_and_get_cookie()
                else:
                    return response.json()

            except (httpx.TimeoutException, httpx.RequestError) as e:
                if attempt < self.max_retries:
                    print(
                        f"Request timed out. Retrying {attempt + 1}/{self.max_retries}...")
                else:
                    self.client.aclose()
                    raise Exception(
                        f"Request failed after {self.max_retries} attempts due to timeout.") from e

    def login_and_get_cookie(self) -> str:
        LOGIN_URL = "https://webproxy.dhu.edu.cn/https/446a50612140233230323231314468551c396b0a0faca42deda1bb464c2c/authserver/login"
        PARAM = "service=http://jwgl.dhu.edu.cn/dhu/casLogin"

        with httpx.Client() as client:
            for attempt in range(self.max_retries):
                try:
                    response = client.get(
                        url=LOGIN_URL, params=PARAM, timeout=self.timeout)

                    if response.status_code == 200:
                        result = response.text

                    login_data = {"username": self.username, }

                    for hidden_input in BeautifulSoup(result, 'html.parser').find('form', id='casLoginForm').find_all('input', type='hidden'):
                        name = hidden_input.get('name')
                        value = hidden_input.get('value')
                        if not name:
                            login_data["password"] = encryptAES(
                                self.password, value)
                            continue
                        login_data[name] = value

                    response = client.post(
                        url=LOGIN_URL, params=PARAM, data=login_data, follow_redirects=True, timeout=self.timeout)

                    cookies_str = "; ".join(
                        [f"{key}={value}" for key, value in client.cookies.items()])

                    response = client.post(
                        url=f"{BASE_URL}/studentui/initstudinfo", params=param, timeout=self.timeout)

                    if response.status_code != 200:
                        if response.status_code == 302:
                            raise ValueError(
                                "Login failed, please check your username and password.")
                        else:
                            raise httpx.RequestError(
                                f"Internal server error, please try again later. status code: {response.status_code}")

                    return cookies_str

                except (httpx.TimeoutException, AttributeError) as e:
                    if attempt < self.max_retries:
                        print(
                            f"Login failed. Retrying {attempt + 1}/{self.max_retries}...")
                    else:
                        raise Exception(
                            f"Login failed after {self.max_retries} attempts.") from e

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
            "termId": self.current_semester if not termId else termId,
            "course": courseName,
        }

        response = await self.__async_post_request__(url, self.headers, payload, param)

        courses = []
        for course in response["aaData"]:
            courses.append({
                "courseName": course["kcmc"],
                "courseCode": course["kcbh"],
                "credit": course["xf"],
                "orgnName": course["orgname"]
            })

        return courses

    async def search_courses_by_code(self, courseCode: str, termId=None) -> list:

        url = f"{BASE_URL}/PublicQuery/getCourseTimeTableInfo"
        payload = {
            "kcbh": courseCode,
            "termId": self.current_semester if not termId else termId,
        }

        response = await self.__async_post_request__(url, self.headers, payload, param)

        soup = BeautifulSoup(response["content"], "html.parser")
        rows = soup.find_all("tr")

        courseInfo = [
            {
                "courseCode": cols[0].text,
                "courseName": cols[1].text,
                "collage": cols[2].text,
                "courseNo": cols[3].text,
                "classNo": cols[4].text,
                "maxNum": cols[5].text,
                "admit": cols[7].text,
                "campus": cols[8].text,
                "teacher": cols[9].text,
                "week": cols[10].text if len(cols) > 10 else "",
                "time": cols[11].text if len(cols) > 10 else "",
                "location": cols[12].text if len(cols) > 10 else "",
            }
            for row in rows if len(row) > 4
            for cols in [row.find_all("td", style="text-align: center;vertical-align: inherit")]
        ]

        return courseInfo

    async def search_courses_by_collage(self, orgnId: int) -> list:

        url = f"{BASE_URL}/selectcourse/initSCByOrgn"
        payload = {
            "orgnId": orgnId,
        }

        response = await self.__async_post_request__(url, self.headers, payload, param)
        if not response["success"] or not response["orgnCourses"]:
            return []

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

        return await self.__async_post_request__(url, self.headers, payload, param)

    async def remove_course(self, courseCode: str, classNo: int) -> dict:

        url = f"{BASE_URL}/selectcourse/cancelSC"
        payload = {
            "courseCode": courseCode,
            "classNo": classNo,
            "cancelType": 1
        }

        return await self.__async_post_request__(url, self.headers, payload, param)

    async def get_grades(self, semester: int = None) -> list:

        url = f"{BASE_URL}/grade/gradeAnalysis/showPsersonalGrades"
        payload = {
            "semester": self.current_semester if not semester else semester,
            "xh": "0"
        }

        response = await self.__async_post_request__(url, self.headers, payload, param)

        return [{"courseName": item["KCMC"], "credit": item["XF"], "grade": item["CJ"]} for item in response["list"][0]["courseGrades"]]

    async def get_gpa(self) -> list:

        url = f"{BASE_URL}/grade/student/showGradePoint"
        payload = {
            "type": 1
        }

        response = await self.__async_post_request__(url, self.headers, payload, param)

        response_list = response["list"]

        return [{"averageGpa": item["ptjd"], "semester": item["xqbh"]} for item in response_list]

    async def get_class_schedule(self) -> list:

        pass
