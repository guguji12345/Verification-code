#
#author:咕咕鸡
#

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from PIL import Image
import time
from io import BytesIO


def login():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches",["enable-automation"])#开发者模式
    browser = webdriver.Chrome(options=options)
    url = 'https://passport.bilibili.com/login'
    browser.get(url)
    wait = WebDriverWait(browser,10)
    input_email = wait.until(EC.presence_of_all_elements_located((By.ID,'login-username')))[0]
    input_email.send_keys("XXXXXXXXX")#账号
    input_password = wait.until(EC.presence_of_all_elements_located((By.ID,"login-passwd")))[0]
    input_password.send_keys("XXXXXXX")#密码
    time.sleep(0.8056)
    login_button = wait.until(EC.presence_of_all_elements_located((By.XPATH,"//a[@class='btn btn-login']")))[0]
    login_button.click()
    time.sleep(2)
    image1 = get_image(browser,wait,"//canvas[@class='geetest_canvas_slice geetest_absolute']")#xpath
    # image2 = get_image(browser,wait,"//canvas[@class='geetest_canvas_bg geetest_absolute']")#调试用
    image1.save("image6.png")#调试用
    # image2.save("image7.png")#调试用
    distance = get_gap(image1)
    time.sleep(0.3)
    distance = sorted(distance, key=lambda x: abs(x[1] - 51))#以横坐标及符合170像素点的长度与缺口长度比较进行排序
    result = {}
    results = []
    for each in distance:
        result.setdefault(each, 0)
        result[each] += 1
    for each in result.items():
        results.append(each)
    results.sort(key=lambda x: x[1], reverse=True)#以左边及长度的次数从大到小进行排序
    print(results)#调试长度
    distance = results[0][0][0]#横坐标
    print(distance)#调试坐标
    track = get_track(distance)#获取轨迹
    move_slider(browser,track)#开始滑动
    time.sleep(5)

def get_track(distance):#滑动轨迹,先加速后减速
    track = []
    mid = distance*4/5
    current = 0
    t=0.2
    v=0
    while current < distance:
        if current < mid:
            a = 2
        else:
            a = -3
        v0 = v
        v = v0 + a * t
        move = v0 * t + 1 / 2 * a * t * t
        current += move
        track.append(round(move,2))
    return track

def move_slider(browser,track):#滑动
    slider = browser.find_element_by_xpath("//div[@class='geetest_slider_button']")
    ActionChains(browser).click_and_hold(slider).perform()
    for x in track:
        ActionChains(browser).move_by_offset(xoffset=x,yoffset=0).perform()
        time.sleep(0.1)
    time.sleep(0.2)
    ActionChains(browser).move_by_offset(xoffset=-7,yoffset=0).perform()#滑块左边6-7个像素
    time.sleep(1)
    ActionChains(browser).release().perform()

def screen(browser):
    screenshot = browser.get_screenshot_as_png()
    screenshot = Image.open(BytesIO(screenshot))#读取二进制数据
    return screenshot

def inde_location(xpath,wait):
    image_ele = wait.until(EC.presence_of_element_located((By.XPATH,xpath)))
    location = image_ele.location
    size = image_ele.size
    top,bottom,left,right = location["y"],location["y"]+size["height"],location["x"],location["x"]+size["width"]
    return top,bottom,left,right#图片截图中的所在位置

def get_image(browser,wait,xpath):
    screenshot = screen(browser)
    time.sleep(0.5)
    top,bottom,left,right = inde_location(xpath,wait)
    time.sleep(0.5)
    image = screenshot.crop((left*1.25,top*1.25,right*1.25,bottom*1.25))#剪切适应屏幕尺寸
    return image

def get_gap(image):
    distance = []#
    # 缺口x轴坐标
    for i in range(image.size[1]):
    # x轴从x为65的像素点开始遍历，滑块占用的像素
        for j in range(65,image.size[0]):#从滑块右侧开始
            if is_pixel_equal(image, j, i, distance):
                break
    return distance


def is_pixel_equal(image, x, y, distance):
    pixel1 = image.load()[x, y]
    threshold = 170
    # count记录一次向右有多少个像素点R、G、B都是小于170的,可用ps软件分析像素特点
    #图片不用做灰度化处理,getpixel返回RGB值,本例中返回RGBA值
    count = 0
    # 如果该点的R、G、B都小于170，就开始向右遍历，记录向右有多少个像素点R、G、B都是小于170的
    if (pixel1[0] < threshold) and (pixel1[1] < threshold) and (pixel1[2] < threshold):
        for i in range(x + 1, image.size[0]):
            piexl = image.load()[i, y]
            if (piexl[0] < threshold) and (piexl[1] < threshold) and (piexl[2] < threshold):
                count += 1
            else:
                break
    if 49 < count < 52:#缺口长度为50-51,只保存该范围内的坐标
        distance.append((x, count))
        return True
    else:
        return False

if __name__ == '__main__':
    login()