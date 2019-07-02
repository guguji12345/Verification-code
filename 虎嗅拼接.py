#
#author:咕咕鸡
#

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
import re
import time
import random
from PIL import Image
from urllib import request

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
        self.button = self.browser.find_element_by_xpath("//div[@class='gt_slider']/div[2]")
        ActionChains(self.browser).move_to_element(self.button).perform()
        time.sleep(2.2)
        self.action()

    def action(self):
        origin_image_url,origin_location = self.get_image("//div[@class='gt_cut_fullbg_slice']")#得到原始图像
        cut_image_url,cut_location = self.get_image("//div[@class='gt_cut_bg_slice']")#得到带缺口图像

        origin_image = self.splice_image(origin_image_url,origin_location)#拼接原始图像
        cut_image = self.splice_image(cut_image_url,cut_location)#拼接缺口图像
        origin_image.save("image1.png")#调试用
        cut_image.save("image2.png")

        distance = self.get_gap(origin_image,cut_image)#获取缺口与滑块距离
        track = self.get_track(distance)#运行轨迹
        time.sleep(2)
        slider = self.browser.find_element_by_xpath("//div[@class='gt_slider']/div[2]")
        self.move_to_gap(slider,track)
        # self.if_eat_error()
        # self.if_error()

    # def if_eat_error(self):
    #     while True:
    #         try:
    #             print(0)
    #             text = self.browser.find_element_by_xpath("//div[@class='gt_info_tip gt_forbidden']")
    #             print(1)
    #             close_button = self.browser.find_element_by_xpath("//div[@class='modal-body modal-body-alert']/i[@class='icon-modal icon-alert-close']")
    #             print(2)
    #             close_button.click()
    #             time.sleep(1)
    #             self.login_button = self.wait.until(EC.presence_of_all_elements_located(
    #                 (By.XPATH, "//li[@class='login-link-box']/a[@class='js-login']")))[0]
    #             print(3)
    #             self.login_button.click()
    #             time.sleep(random.choice(self.times))
    #             self.action()
    #         except:
    #             break

    # def if_error(self):
    #     while True:
    #         try:
    #             print("000")
    #             text = self.browser.find_element_by_xpath("//div[@class='gt_info_tip gt_fail']")
    #             print("111")
    #             close_button = self.browser.find_element_by_xpath("//div[@class='modal-body modal-body-alert']/i[@class='icon-modal icon-alert-close']")
    #             print("222")
    #             close_button.click()
    #             time.sleep(1)
    #             self.login_button = self.wait.until(EC.presence_of_all_elements_located(
    #                 (By.XPATH, "//li[@class='login-link-box']/a[@class='js-login']")))[0]
    #             print("333")
    #             self.login_button.click()
    #             time.sleep(random.choice(self.times))
    #             self.action()
    #         except:
    #             break

    def get_gap(self,origin_image,cut_image):#获取两张图片滑块距缺口的距离
        distance = 60#从滑块右方开始计算距离,约为60包括滑块左侧的距离6
        for x in range(distance,origin_image.size[0]):#长
            for y in range(cut_image.size[1]):#宽
                if not self.is_pixel_equal(origin_image,cut_image,x,y):#当两像素不一样时
                    distance = x
                    return distance
        return distance

    def is_pixel_equal(self,origin_image,cut_image,x,y):#判断像素点是否相同
        pixel_origin = origin_image.load()[x,y]#类似getpixel(x,y),内存释放,效率更快
        pixel_cut = cut_image.load()[x,y]
        threshold = 160#可随意设大小,只作为验证像素是否相同的基准
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
                a = 1.5
            else:
                a = -8
            v0 = v
            v = v0 + a*t
            move = v0*t + 1/2*a*t*t
            current += move
            track.append(round(move))
        return track

    def move_to_gap(self,slider,track):
        ActionChains(self.browser).click_and_hold(slider).perform()
        for x in track:
            ActionChains(self.browser).move_by_offset(xoffset=x,yoffset=0).perform()
        # time.sleep(0.2)
        ActionChains(self.browser).move_by_offset(xoffset=-6,yoffset=0).perform()#滑块左侧距图片边缘距离约为6
        time.sleep(1)
        ActionChains(self.browser).release().perform()

    def get_image(self,xpath):#获取两张图片的url及分割后每张的位置
        text = re.compile(r'background-image: url\("(.*?)"\); background-position: (.*?)px (.*?)px;')
        image_elements = self.browser.find_elements_by_xpath(xpath)
        image_url = None
        location = []
        for image_element in image_elements:
            style = image_element.get_attribute("style")
            groups = text.search(style)
            image_url = groups[1]
            x_pos = groups[2]
            y_pos = groups[3]
            pos = (int(x_pos),int(y_pos))
            location.append(pos)
        return image_url,location

    def splice_image(self,image_url,location):
        image_url = image_url.split(".")
        image_url[-1] = "jpg"
        image_url = ".".join(image_url)
        request.urlretrieve(image_url,"image.jpg")
        image = Image.open("image.jpg")
        image_up = []
        image_down = []
        for pos in location:
            if pos[1]==0:#y==0在上半段
                image_up.append(image.crop((abs(pos[0]),0,abs(pos[0])+10,58)))#左上角到右下角进行剪切图片
            else:#y==58在下半段
                image_down.append(image.crop((abs(pos[0]),58,abs(pos[0])+10,image.height)))

        x_offset = 0
        #创建新图画布,用于拼接图片
        new_image = Image.new("RGB",(260,image.height))
        for img in image_up:#拼接图片上半段
            new_image.paste(img,(x_offset,58))#上半部分高度(0,58)开始粘贴
            x_offset+=img.width

        x_offset = 0
        for img in image_down:#拼接图片下半段
            new_image.paste(img,(x_offset,0))#下半部分高度(0,0)开始粘贴
            x_offset+=img.width

        return new_image

if __name__ == '__main__':
    image = Huxiu_Login()
    image.visit_url()
