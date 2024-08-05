import os
import sys
import time
import random
import base64
import requests
import io
from io import BytesIO
from PIL import Image, ImageDraw
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver import FirefoxOptions

# 用户的key
key = '9vMU6EzIgmtfEuZe8iIw'


# PIL图片保存为base64编码
def PIL_base64(img, coding='utf-8'):
    img_format = img.format
    if img_format == None:
        img_format = 'JPEG'

    format_str = 'JPEG'
    if 'png' == img_format.lower():
        format_str = 'PNG'
    if 'gif' == img_format.lower():
        format_str = 'gif'

    if img.mode == "P":
        img = img.convert('RGB')
    if img.mode == "RGBA":
        format_str = 'PNG'
        img_format = 'PNG'

    output_buffer = BytesIO()
    # img.save(output_buffer, format=format_str)
    img.save(output_buffer, quality=100, format=format_str)
    byte_data = output_buffer.getvalue()
    base64_str = 'data:image/' + img_format.lower() + ';base64,' + base64.b64encode(byte_data).decode(coding)

    return base64_str


# 接口识别
def shibie(img):
    # 图片转base64
    img_base64 = PIL_base64(img)
    # 验证码识别接口
    url = "http://www.detayun.cn/openapi/verify_code_identify/"
    data = {
        # 用户的key
        "key": key,
        # 验证码类型
        "verify_idf_id": "44",
        # 样例图片
        "img_base64": img_base64,
    }
    header = {"Content-Type": "application/json"}

    # 发送请求调用接口
    response = requests.post(url=url, json=data, headers=header)
    # 判断是否正确请求
    if response.json()['code'] == 200:
        print(response.json())
        return response.json()['data']['angle']
    else:
        print('参数错误，请前往得塔云了解详情：https://www.detayun.cn/tool/verifyCodeHomePage2/?_=1714093687434')
        print('错误参数：', response.json())
        return None


# 浏览器配置
option = FirefoxOptions()
# option.add_argument('--headless')
driver = webdriver.Firefox(executable_path=r'webdriver\geckodriver.exe', options=option)

# 记录成功次数
t = 0
# 记录失败次数
f = 0

for i in range(200):
    # 打开验证码页面
    driver.get(
        'https://seccaptcha.baidu.com/v1/webapi/verint/svcp.html?ak=M7bcdh2k6uqtYV5miaRiI8m8x6LIaONq&backurl=https%3A%2F%2Fwenku.baidu.com%2F%3F_wkts_%3D1705066238641&ext=ih2lW9VV3PmxmO%2B%2Bx8wZgk9i1xGx9WH05J9hI74kTEVkpokzRQ8QxLB082MG2VoQUUT15llYBwsC%2BAaysNoPxpuKg0Hkpo4qMzBjXDEGhuQ%3D&subid=pc_home&ts=1705066239&sign=1cebe634245cd92fc9eca10d0850a36b')
    time.sleep(3)

    html_str = driver.page_source
    if 'canvas' in html_str:
        if '曲线' in html_str:
            print('曲线验证码')

        elif '数值' in html_str or '数字' in html_str:
            print('数值验证码')
    else:
        print('旋转验证码')
        # 等待图片出现
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_xpath('//img[@class="passMod_spin-background"]'))
        img = driver.find_element_by_xpath('//img[@class="passMod_spin-background"]')
        img_url = img.get_attribute('src')

        # 下载图片
        header = {
            "Host": "passport.baidu.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
            "Accept": "image/webp,*/*",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://seccaptcha.baidu.com/v1/webapi/verint/svcp.html?ak=M7bcdh2k6uqtYV5miaRiI8m8x6LIaONq&backurl=https%3A%2F%2Fwenku.baidu.com%2F%3F_wkts_%3D1705066238641&ext=ih2lW9VV3PmxmO%2B%2Bx8wZgk9i1xGx9WH05J9hI74kTEVkpokzRQ8QxLB082MG2VoQUUT15llYBwsC%2BAaysNoPxpuKg0Hkpo4qMzBjXDEGhuQ%3D&subid=pc_home&ts=1705066239&sign=1cebe634245cd92fc9eca10d0850a36b",
            "Cookie": "BAIDUID=A0621DC238F4D936B38F699B70A7E41F:SL=0:NR=10:FG=1; BIDUPSID=A0621DC238F4D9360CD42C9C31352635; PSTM=1667351865; HOSUPPORT=1; UBI=fi_PncwhpxZ%7ETaKAanh2ue0vFk6vHMY02DgvigILJIFul8Z1nzMr9do3SYLtjAUqHSpUz7LvOKV27cIr18-YJryP0Q8j92oo93%7E6hGa0CLdraAlaHUZG-0PW9QrpZkW7MTyUn-yrAq7OmSRBIJ7%7E8gM9pv-; HISTORY=0ece87e30ec8ecccd52ff3d5c42f98002a893bfb73ff358893; BDUSS_BFESS=kwTVdpeFNORXlWVEozbW1kcFhBeHo0ZWQwbVlJNlBvcFhEWWpRZVJQWGhzbnBsSUFBQUFBJCQAAAAAAAAAAAEAAAC13Mct0KHQwl9keHkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOElU2XhJVNld1; H_WISE_SIDS=219946_216846_213346_219942_213039_230178_204909_230288_110085_236307_243888_244730_245412_243706_232281_249910_247148_250889_249892_252577_234296_253427_253705_240590_254471_179345_254689_254884_254864_253213_255713_254765_255939_255959_255982_107317_256062_256093_256083_255803_253993_256257_255661_256025_256223_256439_256446_254831_253151_256252_256196_256726_256739_251973_256230_256611_256996_257068_257079_257047_254075_257110_257208_251196_254144_257290_251068_256095_257287_254317_251059_251133_254299_257454_257302_255317_255907_255324_257481_244258_257582_257542_257503_255177_257745_257786_257937_257167_257904_197096_257586_257402_255231_257790_258193_258248_258165_8000084_8000115_8000114_8000126_8000140_8000149_8000166_8000172_8000178_8000181_8000185_8000204; Hm_lvt_90056b3f84f90da57dc0f40150f005d5=1700546200; MAWEBCUID=web_VYfxPuQDaKjEzVgXMFgoHouACkpXyjcDpcWwhATKqELuuwEtNy; BAIDUID_BFESS=A0621DC238F4D936B38F699B70A7E41F:SL=0:NR=10:FG=1; H_PS_PSSID=40206_40215_40080_40352_40379_40416_40300_40466_40471_40317; ZFY=j0lpzcgUac2hW5oc8GUPbnW9ug8zMx:B7VJa:AnxqPUaQ:C; BDRCVFR[gltLrB7qNCt]=mk3SLVN4HKm; delPer=0; PSINO=6",

        }
        response = requests.get(url=img_url, headers=header)
        img = Image.open(BytesIO(response.content))
        # 识别角度  360度对应238像素
        angle = shibie(img)

        # 计算滑动距离
        move_x = int(angle * (238 / 360))
        if move_x >= 238:
            move_x = 237
        elif move_x < 10:
            move_x = 10

        print(angle, move_x)
        # 获取滑块
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_xpath('//div[@class="passMod_slide-btn "]'))
        tag = driver.find_element_by_xpath('//div[@class="passMod_slide-btn "]')

        # 滑动滑块
        action = ActionChains(driver)
        action.click_and_hold(tag).perform()
        # 计算实际滑动距离 = 像素距离 + 前面空白距离
        if move_x + 11 < 238:
            action.move_by_offset(move_x + 11, 5)
            action.move_by_offset(-15, -2)
            action.move_by_offset(4, 3)
        else:
            action.move_by_offset(move_x - 11, 5)
            action.move_by_offset(7, -2)
            action.move_by_offset(4, 3)
        action.release().perform()

        # 判断是否成功 app
        try:
            WebDriverWait(driver, 5).until(lambda x: x.find_element_by_xpath('//div[@id="app"]'))
            t += 1
            print('成功')
        except:
            f += 1
            print('失败')
            time.sleep(2)
        print('总次数：{}，成功：{}，失败：{}，正确率：{}'.format(t + f, t, f, t / (t + f)))