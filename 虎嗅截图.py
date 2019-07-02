#
#author:咕咕鸡
#

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
import time
import random
from PIL import Image
from io import BytesIO

class Huxiu_Login():
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option("excludeSwitches",["enable-automation"])
        self.browser = webdriver.Chrome(options=self.options)
        self.browser.set_window_size(1440,900)
        self.times = [1,1.2,1.1,1.09,0.9,0.8]

    def visit_url(self):
        self.browser.get("https://www.huxiu.com/")
        self.wait = WebDriverWait(self.browser,10)
        self.login_button = self.wait.until(EC.presence_of_all_elements_located((By.XPATH,"//li[@class='login-link-box']/a[@class='js-login']")))[0]
        self.login_button.click()
        time.sleep(random.choice(self.times))
        self.action()


    def get_screen(self):
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        screenshot.save("image3.png")
        return screenshot

    def get_position(self,xpath):
        img = self.wait.until(EC.presence_of_all_elements_located((By.XPATH,xpath)))[0]
        time.sleep(1)
        location = img.location
        size = img.size
        top,bottom,left,right=location["y"],location["y"]+size["height"],location["x"],location["x"]+size["width"]
        return top,bottom,left,right

    def get_image(self,xpath):
        top,bottom,left,right = self.get_position(xpath)
        screenhoot = self.get_screen()
        captcha = screenhoot.crop((1.25*left,1.25*top,1.25*right,1.25*bottom))
        return captcha

    def action(self):
        self.button = self.browser.find_element_by_xpath("//div[@class='gt_slider']/div[2]")
        ActionChains(self.browser).move_to_element(self.button).perform()
        origin_image= self.get_image("//div[@class='gt_cut_fullbg gt_show']")#得到原始图像
        time.sleep(1)
        self.button.click()

        time.sleep(2)
        cut_image = self.get_image("//div[@class='gt_cut_bg gt_show']")#得到带缺口图像
        time.sleep(1)

        origin_image.save("image6.png")#调试用
        cut_image.save("image7.png")

        time.sleep(1)
        distance = self.get_gap(origin_image,cut_image)#获取缺口与滑块距离
        print(distance)
        track = self.get_track(distance)#运行轨迹
        print(track)
        slider = self.browser.find_element_by_xpath("//div[@class='gt_slider']/div[2]")
        self.move_to_gap(slider,track)

    def get_gap(self,origin_image,cut_image):#获取两张图片滑块距缺口的距离
        distance = 77#从滑块右方开始计算距离,约为60包括滑块左侧的距离6
        for x in range(distance,origin_image.size[0]):#长
            for y in range(cut_image.size[1]):#高
                if not self.is_pixel_equal(origin_image,cut_image,x,y):#当滑块右侧两像素不一样时
                    distance = x
                    return distance
        return distance

    def is_pixel_equal(self,origin_image,cut_image,x,y):#判断像素点是否相同
        pixel_origin = origin_image.load()[x,y]#类似getpixel(x,y),内存释放,效率更快
        pixel_cut = cut_image.load()[x,y]
        threshold = 60#可随意设大小,只作为验证像素是否相同的基准
        if abs(pixel_origin[0]-pixel_cut[0]) < threshold and abs(pixel_origin[1]-pixel_cut[1]) < threshold and abs(pixel_origin[2]-pixel_cut[2]) < threshold:
            return True
        else:
            return False

    def get_track(self,distance):
        track = []#滑行轨迹
        current = 0#滑块滑行距离
        mid = distance * 4 / 5#回调阈值
        t = 0.2#计算间隔
        v = 0#初速度
        while current<distance:
            if current<mid:
                a = 2
            else:
                a = -5
            v0 = v
            v = v0 + a*t
            move = v0*t + 1/2*a*t*t
            current += move
            track.append(round(move,2))
        return track

    def move_to_gap(self,slider,track):
        ActionChains(self.browser).click_and_hold(slider).perform()
        for x in track:
            ActionChains(self.browser).move_by_offset(xoffset=x,yoffset=0).perform()
        time.sleep(0.3)
        ActionChains(self.browser).move_by_offset(xoffset=-7.5,yoffset=0).perform()#滑块左侧距图片边缘距离约为6
        time.sleep(1)
        ActionChains(self.browser).release().perform()


if __name__ == '__main__':
    image = Huxiu_Login()
    image.visit_url()
