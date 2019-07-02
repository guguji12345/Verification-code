#
#知网为例
#author:咕咕鸡
#自行获取图片
#

from PIL import Image
import os


def get_image_table(image):#转为二值化图片
    threshold = 140
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    return table

def show_table(image):#调试观察table点
    image = image.convert("L")  # 转为灰度图像
    table = get_image_table(image)
    image = image.point(table,"1")
    for h in range(image.height):
        for w in range(image.width):
            print(image.getpixel((w, h)), end='')
        print("")

def count_isolated(image,x,y):#找出噪点位置
    cur_pixel = image.getpixel((x,y))   #当前像素的点对应0(黑)/1(白)
    width = image.width
    height = image.height

    if cur_pixel == 1:
        return 0
    if y == 0:#第一行
        if x == 0:#左上角点
            sum = cur_pixel + image.getpixel((x,y+1)) + image.getpixel((x+1,y)) + image.getpixel((x+1,y+1))
            #分别对应左上角起始点 + 起始点下方的点 + 起始点右边的点 + 起始点对立的点
            return 4 - sum

        elif x == width-1:#右上角点
            sum = cur_pixel + image.getpixel((x-1,y)) + image.getpixel((x,y+1)) + image.getpixel((x-1,y+1))
            #分别对应右上角起始点 + 起始点下方的点 + 起始点左边的点 + 起始点对立的点
            return 4 - sum

        else:#非顶点,最上面一行邻域有六个的点
            sum = image.getpixel((x-1,y)) + image.getpixel((x-1,y+1)) + cur_pixel + image.getpixel((x,y+1)) + image.getpixel((x+1,y)) + image.getpixel((x+1,y+1))
            #分别对应基准点左边的点 + 左下方的点 + 基准点 + 下方的点 + 右边的点 + 右下方的点
            return 6 - sum

    elif y == height - 1:#最下面一行
        if x == 0:#左下角
            sum = cur_pixel + image.getpixel((x,y-1)) + image.getpixel((x+1,y)) + image.getpixel((x+1,y-1))
            #分别对应基准点 + 上方的点 + 右方的点 + 对立点
            return 4 - sum

        elif x == width-1:#右下角
            sum = cur_pixel + image.getpixel((x-1,y)) + image.getpixel((x-1,y-1)) + image.getpixel((x,y-1))
            #分别对应基准点 + 左边的点 + 对立点 + 上方的点
            return 4 - sum

        else:#非顶点,最下面一行邻域有六个的点
            sum = image.getpixel((x-1,y)) + image.getpixel((x-1,y-1)) + cur_pixel + image.getpixel((x,y-1)) + image.getpixel((x+1,y)) + image.getpixel((x+1,y-1))
            #分别对应基准点左边的点 + 左上方的点 + 基准点 + 上方的点 + 右方的点 + 右上方的点
            return 6 - sum
    else:#像素点不在上下两行
        if x == 0:#左边行非顶点
            sum = image.getpixel((x,y-1)) + image.getpixel((x+1,y-1)) + cur_pixel + image.getpixel((x+1,y)) + image.getpixel((x,y+1)) + image.getpixel((x+1,y+1))
            #分别对应基准点上方的点 + 右上方点 + 基准点 + 右边点 + 下方点 + 右下方点
            return 6 - sum

        elif x == width-1:#右边行非顶点
            sum = image.getpixel((x,y-1)) + image.getpixel((x-1,y-1)) + cur_pixel + image.getpixel((x-1,y)) + image.getpixel((x,y+1)) + image.getpixel((x-1,y+1))
            #分别对应基准点上方点 + 左上方点 + 基准点 + 左边点 + 下方点 + 左下方点
            return 6 - sum

        else:#中间邻域为9的点
            sum = image.getpixel((x-1,y-1)) + image.getpixel((x,y-1)) + image.getpixel((x+1,y-1)) + image.getpixel((x-1,y)) + cur_pixel + image.getpixel((x+1,y)) + image.getpixel((x-1,y+1)) + image.getpixel((x,y+1)) + image.getpixel((x+1,y+1))
            #分别对应基准点左上方点 + 上方点 + 右上方点 + 左方点 + 基准点 + 右方点 + 左下方点 + 下方点 + 右下方点
            return 9 - sum

def remove_noise_pixel(image,noise_pixel_list):#除去噪点
    for item in noise_pixel_list:
        image.putpixel((item[0],item[1]),1)#value像素为1的点

def get_clear_image(image):#转灰->二值化->除燥
    img = image.convert("L")#转为灰度图像
    table = get_image_table(img)
    out_img = img.point(table,"1")#转为二值化图像
    noise_pixel_list = []#噪点列表
    for x in range(out_img.width):
        for y in range(out_img.height):
            noise_pixel = count_isolated(out_img,x,y)#找出噪点位置个数
            if (0 < noise_pixel < 3) and out_img.getpixel((x,y)) == 0:#当前像素为黑色0时且周围黑色像素数少于3个则该点为噪点
                pos = (x,y) #噪点坐标
                noise_pixel_list.append(pos)
    remove_noise_pixel(out_img,noise_pixel_list)#移除噪点
    return out_img

def get_crop_image(out_image):#每张二值化图像切割成4个子图
    child_image_list = []
    for i in range(4):#ps切割查找规律
        x = 7 + (10+1)*i
        y = 7
        child_image = out_image.crop((x,y,x+10,y+15))#左上右下剪切
        child_image_list.append(child_image)
    return child_image_list

def print_line(image,x):#打印图片某一行,调试用
    print("图片第%s行:"%x)
    for w in range(image.width):
        print(image.getpixel((w,x)),end = '')
    print('')

def batch_get_clear_images():#批量转灰->二值化->除燥
    bin_clear_folder = r"C:\Users\骨头\.PyCharm2018.3\config\爬虫\验证码\四位数字\all_cut_images"
    origin_pic = r'C:\Users\骨头\.PyCharm2018.3\config\爬虫\验证码\四位数字\origin_images'
    Image_path = r'C:\Users\骨头\.PyCharm2018.3\config\爬虫\验证码\四位数字\all_Images'
    file_list = os.listdir(origin_pic)
    for file_name in file_list:
        file_full_path = os.path.join(origin_pic,file_name)
        image = Image.open(file_full_path)
        out_image = get_clear_image(image)
        out_image.save(bin_clear_folder+"\\"+file_name)#将转灰->二值化->除燥后的图存在bin_clear文件夹内
    batch_cut_images(bin_clear_folder)#批量分割除燥后的图片


def batch_cut_images(bin_clear_folder):
    file_list = os.listdir(bin_clear_folder)#遍历每个out_img
    for file_name in file_list:
        clear_image_path = os.path.join(bin_clear_folder,file_name)
        image = Image.open(clear_image_path)
        child_image_list = get_crop_image(image)#切割后的4个单字符
        save_crop_images(clear_image_path,child_image_list)#保存切割后的图


def save_crop_images(fill_full_path,child_image_list):
    full_file_name = os.path.basename(fill_full_path)#只显示文件名称
    full_file_name_split = full_file_name.split(".")#0.png分割文件名
    file_name = full_file_name_split[0]
    cut_pic_folder =os.path.join(r"C:\Users\骨头\.PyCharm2018.3\config\爬虫\验证码\四位数字","cut_pic")
    i = 0
    for child_image in child_image_list:
        cut_image_file_name = str(file_name) + "-" + ("%s.png"%i)
        child_image.save(os.path.join(cut_pic_folder,cut_image_file_name))
        i+=1

def demo_cut_pic():#调试用,分割成四个单字符
    image = "image4.png"
    image = Image.open(image)
    cut_save = "C:/Users/骨头/.PyCharm2018.3/config/爬虫/验证码/四位数字"
    child_img_list = get_crop_image(image)
    index = 0
    for child_img in child_img_list:
        child_img.save(cut_save+"/cut-%d.png"%index)
        index+=1

# def batch_crop_images():
#     file_list = os.listdir()

if __name__ == '__main__':
    # image = Image.open("image1.png")
    # out_img = get_clear_image(image)
    # out_img.save("image4.png")
    # out_img.show()
    # show_table(image)##调试table
    # demo_cut_pic()
    batch_get_clear_images()