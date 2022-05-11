import base64
import time
import requests
from Crypto.Cipher import AES
from AES import AEScryptor


# 读取cookies
with open("cookies.txt", "r") as file:
    COOKIES = file.read()

# 课程secret码列表
with open("id.txt", "r") as file:
    recruitAndCourseIdList = []
    rid = file.read()
    if rid != "":
        recruitAndCourseIdList = rid.split("\n")

# recruitId
recruitId: str = ""

# courseId
courseId: str = ""

# 存储当前课程所有视频信息
videoInformationList: list = list()

# 获取当前时间戳 毫秒级
timestamp: time = time.time()
dateFormate: int = int(round(timestamp * 1000) / 1000)

# 课程recruitAndCourseId码
recruitAndCourseId: str = ""

# 设置请求头 带上Cookie
headers: dict = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1185.39',
    "Cookie": COOKIES
}

# 初始化 AES加密器 key：密钥 iv：偏移量
key: bytes = b"qz632524n86i7fk9"
iv: bytes = b"1g3qqdh4jvbskb9x"
aesCryptor: AEScryptor = AEScryptor(key, AES.MODE_CBC, iv, paddingMode="PKCS7Padding", characterSet='utf-8')

_a = "AgrcepndtslzyohCia0uS@"
_b = "A0ilndhga@usreztoSCpyc"
_c = "d0@yorAtlhzSCeunpcagis"
_d = "zzpttjd"


def X(t):
    e = ""
    for i in range(0, len(t)):
        n = ord(t[i]) ^ ord(_d[i % len(_d)])
        e += Y(n)
    return e


def Y(t):
    e = hex(int(t)).replace('0x', '')
    if len(e) < 2:
        e = _b[1] + e
    return e[-4: -1] + e[-1]


def Z(t):
    e = ""
    for i in range(0, len(t)):
        e += str(t[i]) + ";"
    e = e[0: len(e) - 1]
    return X(e)


# 获取总时间 转换成H:M:S格式
def getTolTime(tolTime: int) -> str:
    minute, second = divmod(tolTime, 60)
    hour, minute = divmod(minute, 60)
    tolTime: str = "%02d:%02d:%02d" % (hour, minute, second)
    return tolTime


# learningTimeRecord、generateWatchPoint 通过这两个方法，生成 为/learning/saveDatabaseIntervalTime中的watchPoint参数
# 此参数的作用是验证是否完整观看
def learningTimeRecord(tolStudyTime: int, watchPointPost: str) -> tuple:
    t: int = int(tolStudyTime / 5) + 2
    if watchPointPost is None or watchPointPost == "":
        e: str = "0,1,"
    else:
        e: str = watchPointPost + ","
    return t, e


def generateWatchPoint(videoSec: int) -> str:
    tolStudyTime: int = 0
    watchPointPost: str = ""
    for i in range(0, videoSec):
        if i % 2 == 0:
            t, e = learningTimeRecord(tolStudyTime, watchPointPost)
            watchPointPost = e + str(t)
        if i % 5 == 0:
            tolStudyTime += 5
    return watchPointPost


# 提交数据 实现刷课
def submitData(lesson_Information: dict, chapterId: str, studyTotalTime: int) -> dict:
    params: dict = {
        "ccCourseId": courseId,
        "isApply": 1,
        "recruitId": recruitId,
        "videoId": lesson_Information["videoId"],
        "dateFormate": dateFormate
    }

    if chapterId == "":
        params["chapterId"] = lesson_Information["chapterId"]
        params["lessonId"] = lesson_Information["id"]

        lessonData: list = [recruitId, lesson_Information["id"], 0, lesson_Information["videoId"],
                      lesson_Information["chapterId"], "0", lesson_Information["videoSec"] - studyTotalTime,
                            lesson_Information["videoSec"], getTolTime(lesson_Information["videoSec"])]
    else:
        params["chapterId"] = chapterId
        params["lessonVideoId"] = lesson_Information["id"]
        params["lessonId"] = lesson_Information["lessonId"]

        lessonData: list = [recruitId, lesson_Information["lessonId"], lesson_Information["id"],
                      lesson_Information["videoId"], chapterId, "0", lesson_Information["videoSec"] - studyTotalTime,
                      lesson_Information["videoSec"], getTolTime(lesson_Information["videoSec"])]

    resp: requests = requests.post("https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/prelearningNote", {
        "secretStr": aesCryptor.encryptFromString(str(params))
    }, headers=headers)

    learningTokenId: str = str(resp.json()["data"]["studiedLessonDto"]["id"])
    learningTokenId: str = base64.encodebytes(learningTokenId.encode("utf8")).decode()

    params: dict = {
        "watchPoint": generateWatchPoint(lesson_Information["videoSec"]),
        "ev": Z(lessonData),
        "learningTokenId": learningTokenId,
        "courseId": courseId,
        "dateFormate": dateFormate
    }

    resp: requests = requests.post("https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/saveDatabaseIntervalTime", {
        "secretStr": aesCryptor.encryptFromString(str(params))
    }, headers=headers)
    return resp.json()


if __name__ == "__main__":
    if COOKIES == "":
        print("请在cookies.txt中填入播放页面的cookies")
        exit(1)

    if len(recruitAndCourseIdList) == 0:
        print("请在id.txt中填入需要刷的课程id")
        exit(1)

    # 登录
    resp = requests.get(
        "https://studyservice.zhihuishu.com/login/getLoginUserInfo?dateFormate=" + str(dateFormate) + "000"
        , headers=headers)
    # 读取返回数据
    data = resp.json()
    if data["code"] == 200:
        uuid = data["data"]["uuid"]
        print("             用户信息            ")
        print("realName：" + data["data"]["realName"])
        print("uuid：" + data["data"]["uuid"])
        print("username：" + data["data"]["username"])
        print("登录成功！")

        choose = input("是否默认刷未完成的课时(Y/N)? : ")
        for recruitAndCourseId in recruitAndCourseIdList:
            print("--> 当前id: ", recruitAndCourseId)
            time.sleep(3)

            if recruitAndCourseId is None or recruitAndCourseId == "":
                print("获取失败！停止运行")
                quit()
            else:
                # 获取当前课程所有视频信息
                data = {
                    "recruitAndCourseId": recruitAndCourseId,
                    "dateFormate": dateFormate
                }
                resp = requests.post("https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/videolist", {
                    "secretStr": aesCryptor.encryptFromString(str(data))
                }, headers=headers)
                if resp.json()["code"] == 0:
                    content = resp.json()["data"]
                    recruitId = content["recruitId"]
                    courseId = content["courseId"]
                    videoInformationList = content["videoChapterDtos"]
                    print("获取课程所有视频信息成功！")
                    print()
                else:
                    print("获取课程所有视频信息失败！停止运行")
                    quit()

            print("正在查询当前视频学习情况。。。。")
            data = {}
            videoLessonsIds = []
            for i in videoInformationList:
                videoLessons = i["videoLessons"]
                for j in videoLessons:
                    videoLessonsIds.append(j["id"])
            data["lessonIds"] = videoLessonsIds

            videoSmallLessonsIds = []
            for i in videoInformationList:
                videoLessons = i["videoLessons"]
                for k in videoLessons:
                    if len(k) == 9:
                        videoSmallLessons = k["videoSmallLessons"]
                        for l in videoSmallLessons:
                            videoSmallLessonsIds.append(l["id"])
            data["lessonVideoIds"] = videoSmallLessonsIds
            data["recruitId"] = recruitId
            data["dateFormate"] = dateFormate

            resp = requests.post("https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/queryStuyInfo", {
                "secretStr": aesCryptor.encryptFromString(str(data))
            }, headers=headers)

            if resp.json()["code"] == 0:
                print("开始检测。。。。")
                print()
                queryStuyInfoData = resp.json()["data"]
                lessonList = {}
                lvList = {}
                if len(queryStuyInfoData) == 2:
                    lessonList = resp.json()["data"]["lesson"]
                    lvList = resp.json()["data"]["lv"]
                else:
                    lessonList = resp.json()["data"]["lesson"]
                for m in videoInformationList:
                    videoLessons = m["videoLessons"]
                    for n in videoLessons:
                        if len(n) == 10:
                            lessonInformation = lessonList[str(n["id"])]
                            print("视频名称：" + n["name"])
                            print("视频总时长：" + getTolTime(n["videoSec"]))
                            print("学习总时长：" + str(lessonInformation["studyTotalTime"]) + "s")
                            if n["videoSec"] - lessonInformation["studyTotalTime"] < 50:
                                print("状态：已完成")
                                print()
                            else:
                                print("状态：未完成")
                                if choose == "Y" or choose == "y":
                                    result = submitData(n, "", lessonInformation["studyTotalTime"])
                                    print("----submitData1------")
                                    if result["code"] == 0:
                                        if result["data"]["submitSuccess"]:
                                            print("提交数据成功！")
                                            print()
                                        else:
                                            print("提交数据失败！")
                                    else:
                                        print(result)
                                        exit(1)
                        else:
                            chapterId = n["chapterId"]
                            videoSmallLessons = n["videoSmallLessons"]
                            for p in videoSmallLessons:
                                lvInformation = lvList[str(p["id"])]
                                print("视频名称：" + p["name"])
                                print("视频总时长：" + getTolTime(p["videoSec"]))
                                print("学习总时长：" + str(lvInformation["studyTotalTime"]) + "s")
                                if p["videoSec"] - lvInformation["studyTotalTime"] < 50:
                                    print("状态：已完成")
                                    print()
                                else:
                                    print("状态：未完成")
                                    if choose == "Y" or choose == "y":
                                        result = submitData(p, chapterId, lvInformation["studyTotalTime"])
                                        print("----submitData2------")
                                        if result["code"] == 0:
                                            if result["data"]["submitSuccess"]:
                                                print("提交数据成功！")
                                                print()
                                            else:
                                                print("提交数据失败！")
                                        else:
                                            print(result)
                                            exit(1)
                        time.sleep(1)

        print("全部刷取完成！感谢使用")
    else:
        print("登录失败！停止运行")
        exit(1)
