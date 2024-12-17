import httpx
import requests
import re
import subprocess
from bs4 import BeautifulSoup

param = "vpn-12-o2-jwgl.dhu.edu.cn"
BASE_URL = "https://webproxy.dhu.edu.cn/https/446a5061214023323032323131446855152f7f4845a0b976a6a0aa1d0121c0/dhu"


class DHUPotatoPatch:

    def __init__(self, username: str, password: str, current_semester: int, max_retries: int = 3, timeout: int = 10):
        
        self.client = httpx.AsyncClient()
        self.username = username
        self.password = password
        self.timeout = timeout
        self.is_first_login = False
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
                    if not self.is_first_login:
                        print("Cookie expired, re-login...")
                        self.headers = {
                            "Cookie": await self.login_and_get_cookie(),
                        }
                        response = await self.client.post(url, headers=self.headers, data=payload, params=params, timeout=self.timeout)

                return response.json()
            except httpx.TimeoutException:
                if attempt < self.max_retries - 1:
                    print(
                        f"Request timed out. Retrying {attempt + 1}/{self.max_retries}...")
                else:
                    self.client.close()
                    raise httpx.TimeoutException(
                        f"Request failed after {self.max_retries} attempts due to timeout.")

    def __call_encrypt_aes__(self, salt):

        result = subprocess.run(
            ['node', './js/encryptAESWrapper.js', self.password, salt], capture_output=True, text=True)
        
        return result.stdout.strip()

    # TODO: Replacing requests with httpx
    def login_and_get_cookie(self) -> str:
        LOGIN_URL = "https://webproxy.dhu.edu.cn/https/446a50612140233230323231314468551c396b0a0faca42deda1bb464c2c/authserver/login"
        PARAM = "service=http://jwgl.dhu.edu.cn/dhu/casLogin"

        session = requests.Session()

        response = session.get(url=LOGIN_URL, params=PARAM)
        cookie = response.headers.get('Set-Cookie')
        result = response.text
        pwd_default_encrypt_salt = re.search(
            r'var pwdDefaultEncryptSalt = "(.*?)";', result).group(1)
        lt = re.search(r'name="lt" value="(.*?)"', result).group(1)
        execution = re.search(r'name="execution" value="(.*?)"', result).group(1)
        route = re.search(r'route=(.*?);', cookie).group(1)
        wengine_vpn_ticket = re.search(
            r'wengine_vpn_ticketwebproxy_dhu_edu_cn=(.*?);', cookie).group(1)

        encrypted_password = self.__call_encrypt_aes__(pwd_default_encrypt_salt)
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,ja;q=0.8",
            "cache-control": "max-age=0",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "cookie": f"route={route}; wengine_vpn_ticketwebproxy_dhu_edu_cn={wengine_vpn_ticket}",
            "Referer": f"{LOGIN_URL}?{PARAM}",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        data = {
            "username": self.username,
            "password": encrypted_password,
            "lt": lt,
            "dllt": "userNamePasswordLogin",
            "execution": execution,
            "_eventId": "submit",
            "rmShown": "1"
        }
        response = session.post(url=LOGIN_URL, params=PARAM,
                                headers=headers, data=data, allow_redirects=False)
        location = response.headers.get('Location')
        session.get(location, headers={
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1"
        })

        cookies_str = "; ".join(
            [f"{key}={value}" for key, value in session.cookies.items()])
        return cookies_str

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
