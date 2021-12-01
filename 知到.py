import execjs
import requests
import time
import base64

# recruitId
recruitId = ""
# courseId
courseId = ""
# 存储当前课程所有视频信息
videoInformationList = []
# 时间戳 毫秒级
t = time.time()
dateFormate = int(round(t * 1000) / 1000)
# 课程secret码
recruitAndCourseId = ""
# session
SESSION = input("请输入session登录：")
# 请求头
headers = {
    "Cookie": "SESSION=" + SESSION + ";"
}
# 用户id
uuid = ""
# 判断类型
typeNumbers = 0


ctx = execjs.compile("""
var _a = "AgrcepndtslzyohCia0uS@",
_b = "A0ilndhga@usreztoSCpyc",
_c = "d0@yorAtlhzSCeunpcagis",
_d = "zzpttjd";

function X(t) {
    for (var e = "", i = 0; i < t[_c[8] + _a[4] + _c[15] + _a[1] + _a[8] + _b[6]]; i++) {
        var n = t[_a[3] + _a[14] + _c[18] + _a[2] + _b[18] + _b[16] + _c[0] + _a[4] + _b[0] + _b[15]](i) ^ 
        _d[_b[21] + _b[6] + _a[17] + _c[5] + _b[18] + _c[4] + _a[7] + _a[4] + _a[0] + _c[7]]
        (i % _d[_a[10] + _b[13] + _b[4] + _a[1] + _c[7] + _a[14]]);
        e += Y(n)
    }
    return e
}

function Y(t) {
    var e = t[_c[7] + _a[13] + _a[20] + _b[15] + _a[2] + _b[2] + _c[15] + _c[19]](16);
    return e = e[_b[3] + _a[4] + _b[4] + _a[1] + _c[7] + _c[9]] < 2 ? _b[1] + e : e,
    e[_a[9] + _b[3] + _c[20] + _c[17] + _c[13]](-4)
}

function Z(t) {
    for (var e = "", i = 0; i < t.length; i++) {
        e += t[i] + ";";
    }
    return e = e.substring(0, e.length - 1), X(e);
}
""")


def getTolTime(tolTime):
    m, s = divmod(tolTime, 60)
    h, m = divmod(m, 60)
    tolTime = "%02d:%02d:%02d" % (h, m, s)
    return tolTime


def learningTimeRecord(tolStudyTime, watchPointPost):
    t = int(tolStudyTime / 5) + 2
    if watchPointPost is None or watchPointPost == "":
        e = "0,1,"
    else:
        e = watchPointPost + ","
    return t, e


def generateWatchPoint(videoSec):
    tolStudyTime = 0
    watchPointPost = ""
    for i in range(0, videoSec):
        if i % 2 == 0:
            t, e = learningTimeRecord(tolStudyTime, watchPointPost)
            watchPointPost = e + str(t)
        if i % 5 == 0:
            tolStudyTime += 5
    return watchPointPost


def submitData(k, studyTotalTime):
    resp = requests.post("https://studyservice.zhihuishu.com/learning/prelearningNote", {
        "ccCourseId": courseId,
        "chapterId": k["chapterId"],
        "isApply": 1,
        "lessonId": k["id"],
        "recruitId": recruitId,
        "videoId": k["videoId"],
        "uuid": uuid,
        "dateFormate": dateFormate
    }, headers=headers)
    learningTokenId = str(resp.json()["data"]["studiedLessonDto"]["id"])
    learningTokenId = base64.encodebytes(learningTokenId.encode("utf8")).decode()

    s = [recruitId, k["id"], 0, k["videoId"], k["chapterId"], "0", k["videoSec"] - studyTotalTime,
         k["videoSec"], getTolTime(k["videoSec"])]
    resp = requests.post("https://studyservice.zhihuishu.com/learning/saveDatabaseIntervalTime", {
        "watchPoint": generateWatchPoint(k["videoSec"]),
        "ev": ctx.call("Z", s),
        "learningTokenId": learningTokenId,
        "courseId": courseId,
        "uuid": uuid,
        "dateFormate": dateFormate
    }, headers=headers)
    return resp.json()


def submitData2(k, chapterId, studyTotalTime):
    resp = requests.post("https://studyservice.zhihuishu.com/learning/prelearningNote", {
        "ccCourseId": courseId,
        "chapterId": chapterId,
        "isApply": 1,
        "lessonId": k["lessonId"],
        "lessonVideoId": k["id"],
        "recruitId": recruitId,
        "videoId": k["videoId"],
        "uuid": uuid,
        "dateFormate": dateFormate
    }, headers=headers)
    learningTokenId = str(resp.json()["data"]["studiedLessonDto"]["id"])
    learningTokenId = base64.encodebytes(learningTokenId.encode("utf8")).decode()

    s = [recruitId, k["lessonId"], k["id"], k["videoId"], chapterId, "0", k["videoSec"] - studyTotalTime,
         k["videoSec"], getTolTime(k["videoSec"])]
    resp = requests.post("https://studyservice.zhihuishu.com/learning/saveDatabaseIntervalTime", {
        "watchPoint": generateWatchPoint(k["videoSec"]),
        "ev": ctx.call("Z", s),
        "learningTokenId": learningTokenId,
        "courseId": courseId,
        "uuid": uuid,
        "dateFormate": dateFormate
    }, headers=headers)
    return resp.json()


# 登录
resp = requests.get("https://studyservice.zhihuishu.com/login/getLoginUserInfo?dateFormate=" + str(dateFormate) + "000"
                    , headers=headers)
# 读取返回数据
data = resp.json()
if data["code"] == 200:
    # 赋值
    uuid = data["data"]["uuid"]
    print("             用户信息            ")
    print("realName：" + data["data"]["realName"])
    print("uuid：" + data["data"]["uuid"])
    print("username：" + data["data"]["username"])
    print("登录成功！")
    print()
else:
    print("登录失败！停止运行")
    quit()

recruitAndCourseId = input("请输入课程secret码：")
if recruitAndCourseId is None or recruitAndCourseId == "":
    print("获取失败！停止运行")
    quit()
else:
    # 获取当前课程所有视频信息
    resp = requests.post("https://studyservice.zhihuishu.com/learning/videolist", {
        "recruitAndCourseId": recruitAndCourseId,
        "uuid": uuid,
        "dateFormate": dateFormate
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
count = 0
for i in videoInformationList:
    videoLessons = i["videoLessons"]
    for j in videoLessons:
        data["lessonIds[" + str(count) + "]"] = j["id"]
        count += 1
count = 0
for i in videoInformationList:
    videoLessons = i["videoLessons"]
    for k in videoLessons:
        if len(k) == 9:
            videoSmallLessons = k["videoSmallLessons"]
            for l in videoSmallLessons:
                data["lessonVideoIds[" + str(count) + "]"] = l["id"]
                count += 1
data["recruitId"] = recruitId
data["uuid"] = uuid
data["dateFormate"] = dateFormate

resp = requests.post("https://studyservice.zhihuishu.com/learning/queryStuyInfo", data=data, headers=headers)
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
                    choose = input("是否刷取该节视频？（Y/N）：")
                    if choose == "Y" or choose == "y":
                        result = submitData(n, lessonInformation["studyTotalTime"])
                        if result["code"] == 0:
                            if result["data"]["submitSuccess"]:
                                print("提交数据成功！")
                                print()
                            else:
                                print("提交数据失败！")
                        else:
                            print("请求失败！停止运行")
                    else:
                        print("刷取完成！停止运行")
                        quit()
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
                        choose = input("是否刷取该节视频？（Y/N）：")
                        if choose == "Y" or choose == "y":
                            result = submitData2(p, chapterId, lvInformation["studyTotalTime"])
                            if result["code"] == 0:
                                if result["data"]["submitSuccess"]:
                                    print("提交数据成功！")
                                    print()
                                else:
                                    print("提交数据失败！")
                            else:
                                print("刷取完成！停止运行")
                                quit()
            time.sleep(1)
    print("全部刷取完成！感谢使用")
