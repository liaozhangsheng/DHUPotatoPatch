import httpx
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

param = "vpn-12-o2-jwgl.dhu.edu.cn"
BASE_URL = "https://webproxy.dhu.edu.cn/https/446a5061214023323032323131446855152f7f4845a0b976a6a0aa1d0121c0/dhu"


class DHUPotatoPatch:

    def __init__(self, username: str = None, password: str = None, max_retries: int = 3, timeout: int = 10):
        self.username = username
        self.password = password
        self.headers = None
        self.current_semester = None
        self.is_first_login = True
        self.max_retries = max_retries
        self.timeout = timeout

    async def init(self):

        if not self.username or not self.password:
            raise Exception(
                "Please provide your username and password to login.")

        self.headers = {
            "Cookie": await self.login_and_get_cookie(),
        }

        self.current_semester = await self.get_current_semester()
        self.is_first_login = False

    async def __async_post_request__(self, url: str, headers: dict, payload: dict, params: str) -> dict:

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(url, headers=headers, data=payload, params=params, timeout=self.timeout)

                    if response.status_code != 200:
                        if not self.is_first_login:
                            print("Cookie expired, re-login...")
                            self.headers = {
                                "Cookie": await self.login_and_get_cookie(),
                            }
                            response = await client.post(url, headers=self.headers, data=payload, params=params, timeout=self.timeout)

                    return response.json()
            except httpx.TimeoutException:
                if attempt < self.max_retries - 1:
                    print(
                        f"Request timed out. Retrying {attempt + 1}/{self.max_retries}...")
                else:
                    raise httpx.TimeoutException(
                        f"Request failed after {self.max_retries} attempts due to timeout.")

    async def login_and_get_cookie(self) -> str:

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            try:
                await page.goto(BASE_URL)
                await page.wait_for_load_state("networkidle")
                await page.fill("#username", self.username)
                await page.fill("#password", self.password)
                await page.click(".auth_login_btn.primary.full_width")
                await page.wait_for_load_state("networkidle")
                await page.wait_for_load_state("load")
                await page.wait_for_load_state("domcontentloaded")
                await page.wait_for_load_state("networkidle")
                await page.wait_for_selector("#msg.auth_error", timeout=5000)
                login_success = False
            except:
                login_success = True

            if not login_success:
                await browser.close()
                raise Exception(
                    "Login failed, please check your username and password.")

            cookies = await page.context.cookies()
            await browser.close()
            cookie_str = "; ".join(
                [f"{cookie['name']}={cookie['value']}" for cookie in cookies])

            return cookie_str

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

    async def search_courses_by_id(self, courseCode: str, termId=None) -> list:

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

    async def get_current_semester(self) -> int:

        url = f"{BASE_URL}/common/semesterSS"
        payload = {
            "ordered": True,
            "sortType": "desc"
        }
        response = await self.__async_post_request__(url, self.headers, payload, param)

        for semester in response["semesterSS"]:
            if semester["current"]:
                return semester["id"]
