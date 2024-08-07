import re
import requests
import json
import argparse
import os
import shutil
import time
import gzip
import base64

from urllib.parse import urlencode
import img2pdf
from PyPDF2 import PdfMerger, PdfReader

from json2pdf import save_pdf  # local
import my_tools  # local

import random

blackWords = ["股旁", "选股", "炒股", "股票", "赌博", "彩票", "福彩", "体彩", "赔率", "扑克", "视频教程", "操盘", "通达信", "源码", "赚钱", "云盘", "网盘",
              "迅雷", "360", "登录", "登陆", "入口", "下载", "港独", "微信", "转载", "身份证", "中国地图", "首页", "导航", "免费", "网易邮箱", "中文字幕",
              "秘方", "偏方", "好色", "电视剧", "视频全集", "纪录片", "影片", "目录", "官网", "网址", "软件", "网页", "网站", ".com", ".cn",
              ".net", "热血", "秘籍", "英雄无敌", "英雄联盟", "魔兽", "王者", "侠盗飞车", "侠盗猎车", "魔法门", "圣安地列", "荒岛求生", "三国群英", "幻世录",
              "僵尸岛", "地球帝国", "大话西游", "梦幻西游", "恶龙", "出轨", "肉蒲", "比基尼", "情妇", "mp3", "mp4", "电影", "在线", "视频", "壮阳", "约炮",
              "嫖", "小三", "脱光", "勿进", "勿看", "禁止观看", "羞羞", "人体油画", "情史", "动漫", "漫画", "灰太狼", "喜羊羊", "佩奇", "维尼", "阿狸",
              "罗小黑", "基督", "耶稣", "福音", "圣经", "天父", "灵歌", "书籍", "电子书", "巨著", "电子教材", "出版社", "电子课本", "丛书", "小说", "连载",
              "剧本", "GB", "党", "中央", "新疆", "西藏", "台湾", "共和国", "历任", "将领", "将军", "红军", "解放军", "八路军", "军工", "军功", "军人",
              "军长", "军队", "贪官", "高官", "市委书记", "国家领导", "政治局", "常委", "元帅", "总理", "国家部", "国防部长", "右派", "名单", "名录", "红色革命",
              "简历", "国税发", "号文", "红头文件", "发改", "印发", "人社发", "世联", "边检", "边防", "保密",

              "笔芯范文网", "阿扣范文网", "职场范文网", "好范文网", "考试院网", "香当网", "文档之家", "蚂蚁文库", "文档视界", "语文网", "工图网", "满分作文网", "学科网",
              "zxxk", "组卷网", "教育网", "查字典", "快文库", "青夏教育精英家教网", "快思网", "冰点", "幼儿园学习网", "21世纪", "万象文库", "写写帮", "相关文章专题",
              "二一教育", "21教育", "汇文网", "huiwenwangcn", "答案圈", "绿色圃中小学", "作文吧", "装配图网", "绿色作文网", "造句网", "出国留学网", "原上草网",
              "大文斗", "所有年代上下册", "中学历史教学园地", "第一文库", "baidu", "豆丁", "docin", "道客", "doc88", "原创力", "max",
              "book118", "文档赚钱", "投稿赚钱", "爱问文库", "大分享文库", "人人网", "知网", "金锄头", "文秘网", "天天文库", "投稿网", "第一课件", "第一模板网",
              "七彩学科网", "原上草网", "教育盘", "中学语文教学资源网", "360文档中心", "中国人才网", "作文网", "范文网", "xuexila", "学习啦", "ruiwen", "瑞文网",
              "118"]

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='WKS v0.2 \nBaidu Wenku Spider BY BoyInTheSun\nDo NOT use it to download VIP documents or for commercial purpose! \nONLY FOR easy to view and exchange spider technical.'
)
parser.add_argument(
    'url',
    nargs='?',
    default=None,
    help='A url of baiduwenku, seem like "https://wenku.baidu.com/view/abcd.html"'
)
parser.add_argument(
    '-c', '--cookies',
    help='Cookies of baiduwenku.'
)
parser.add_argument(
    '-C', '--cookies_filename',
    help='Filename of the cookies.'
)
parser.add_argument(
    '-t', '--temp',
    action='store_true',
    help='Save temporary files into folder'
)
parser.add_argument(
    '-o', '--output',
    help='Output filename.'
)
parser.add_argument(
    '-p', '--pagenums',
    help='For example, "2,6-8,10" means page numbers [2,6,7,8,10], start by 1'
)
parser.add_argument(
    '-u', '--useragent',
    help='User-Agent when request.'
)
parser.add_argument(
    '-F', '--filename',
    help='URLs in a file. One URL each line.'
)
parser.add_argument(
    '-l', '--listUrl',
    help='列表地址'
)

parser.add_argument(
    '-k', '--keyword',
    help='搜索的关键词, 多个词用 || 隔开'
)

parser.add_argument(
    '-P', '--page',
    help='当前页'
)

parser.add_argument(
    '-D', '--dir',
    help='导出的目录存放路径'
)

parser.add_argument(
    '-conv_file_path', '--conv_file_path',
    help='待转换的文件目录'
)

parser.add_argument(
    '-conv_save_path', '--conv_save_path',
    help='转换后保存的文件目录'
)

parser.add_argument(
    '-conv_file_type', '--conv_file_type',
    help='待转换的文件类型'
)

parser.add_argument(
    '-filter_file_type', '--filter_file_type',
    help='需要过滤的文件类型'
)

parser.add_argument(
    '-is_split_dir', '--is_split_dir',
    help='是否拆分目录'
)

parser.add_argument(
    '-cid', '--cid',
    help='分类ID 0:学前教育, 1:基础教育, 2:高校与高等教育, 3:语言/资格考试, 4:法律, 5:建筑, 6:互联网, 7:行业资料,'
         ' 8:政务民生, 9:说明书, 10:实用模板, 11:生活娱乐'
)

args = parser.parse_args()

# 处理word 转换
if args.conv_file_type == "word":
    args.conv_file_path = args.conv_file_path.rstrip("/") + "/"
    args.conv_save_path = args.conv_save_path.rstrip("/") + "/"
    if os.path.exists(args.conv_file_path) and os.path.exists(args.conv_save_path):
        for root, directories, files in os.walk(args.conv_file_path):
            for file in files:
                if 'word.pdf' in file:
                    docFileName = args.conv_save_path + file.rstrip(".pdf") + '.docx'
                    my_tools.convert_pdf_to_docx_with_style(args.conv_file_path + file, docFileName)
                    print(docFileName, "转换完成")
    else:
        print("目录不存在")

    exit(0)

pathDir = "./"
if args.dir:
    pathDir = args.dir.rstrip("/") + "/"

cookies = ''
if args.cookies:
    cookies = args.cookies
elif args.cookies_filename:
    with open(args.cookies_filename, 'r') as f:
        cookies = f.read()

useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
if args.useragent:
    useragent = args.useragent

headers = {
    'User-Agent': useragent,
    'Cookie': cookies,
    'Referer': 'https://wenku.baidu.com/'
}

isWord = False

fileTypeList = {
    1: 'doc',
    2: 'xls',
    3: 'PPT',
    4: 'doc',
    5: 'xls',
    6: 'ppt',
    7: 'PDF',
    8: 'txt',
}

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def fatch_urls(urls):
    for url in urls:
        sleepTime = random.randint(1, 6)
        print("开始等待:", sleepTime, " 秒")
        time.sleep(sleepTime)
        print("开始下载文档。。。")
        # url_original = url
        url = url.split('?')[0]
        print('Download from', url)
        url = url + '?edtMode=2'  # support vip account
        print('Download HTML...', end='')

        try:
            req = requests.get(url, headers=headers)
        except Exception:
            print("网络请求异常，休息10s")
            urls.append(url)
            time.sleep(10)
            continue

        html = req.text
        print("url: ", url)
        docId = temp_dir = url.split('?')[0].split('/')[-1]

        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

        print("temp_dir:", temp_dir)
        os.mkdir(temp_dir)
        # exit(0)
        print('Success. \nParse HTML...', end='')
        page_data = re.search(r'var pageData = (.*);', html)

        print("first:", page_data)

        try:
            data = json.loads(page_data.group(1))
            with open(os.path.join(temp_dir, 'pagedata.json'), 'w') as f:
                json.dump(data, f)
            # title = re.search( r'<title>(.*) - 百度文库</title>', html).group(1)
            if data['title'][-5:] == '-百度文库':
                title = data['title'][:-5]
            elif data['title'][-7:] == ' - 百度文库':
                title = data['title'][:-7]

            title = title.strip().replace(" ", "") + f"&&{docId}"
            # filetype = re.search(r'<div class="file-type-icon (.*)"></div>').group(1)
            filetype = data['viewBiz']['docInfo']['fileType']

            if url.split('/')[3] == 'view':
                docid = temp_dir
                aggid = ''
            elif url.split('/')[3] == 'aggs':
                docid = data['readerInfo']['docId']
                aggid = temp_dir

            if data['viewBiz']['docInfo']['fileType'] and data['viewBiz']['docInfo']['fileType'] != 'pdf':
                title = title + "_" + data['viewBiz']['docInfo']['fileType']
                if data['viewBiz']['docInfo']['fileType'] == 'word':
                    isWord = True
                else:
                    isWord = False
            print("===title===", title)
            if args.output:
                output = args.output
            else:
                output = tmpDir + title
        except:
            print('Error! It is not a Baidu Wenku document.')
            continue

        title = remove_html_tags(title)
        print('Success. ')
        print('title: ', title)
        if os.path.exists(output + '.pdf'):
            print("文件重复")
            continue

        # PPT
        if data['readerInfo']['tplKey'] == 'new_view' and filetype == 'ppt':
            print('Found ppt file 3333, prepare for download...', end='')

            print('Success.\nstart downloading jpg(s)...')
            imgs = data['readerInfo']['htmlUrls']
            if data['readerInfo']['page'] > len(imgs):
                print(
                    "It seems that you provided incorrect or Non-VIP cookies, only be able to download a part of the file ({} page), not the whole file ({} page).".format(
                        len(imgs), data['readerInfo']['page']))
            if args.pagenums:
                pagenums = my_tools.parse_pagenum(args.pagenums)
                pagenums = my_tools.under_by(pagenums, len(imgs))
            else:
                pagenums = list(range(1, len(imgs) + 1))
            print('page: ', my_tools.export_pagenum(pagenums))

            for i in range(len(pagenums)):
                # TODO: theading
                percentage = (i + 1) / len(pagenums) * 100
                print('\r|{}| {} / {} ({:.2f}%)'.format(
                    '=' * int(percentage // 2 - 1) + '>' + '-' * int((100 - percentage) // 2),
                    i + 1,
                    len(pagenums),
                    percentage
                ), end='')
                req = requests.get(imgs[pagenums[i] - 1], headers=headers)
                with open(os.path.join(temp_dir, str(pagenums[i]) + '.jpg'), 'wb') as f:
                    f.write(req.content)

            print('\nMerge images to a PDF...', end='')
            # imgs = [os.path.join(temp_dir, img) for img in os.listdir(temp_dir) if img[-4:] == '.jpg']
            file_imgs = [os.path.join(temp_dir, str(i) + '.jpg') for i in pagenums]

            try:
                with open(output + '.pdf', 'wb') as f:
                    f.write(img2pdf.convert(file_imgs))
            except:
                print("写文件异常")
                continue

            if not args.temp:
                shutil.rmtree(temp_dir)

            print('Success.')
            print('Saved to ' + output + '.pdf')

        # PDF WORD (EXCEL)
        elif data['readerInfo']['tplKey'] == 'html_view' and filetype in ['word', 'pdf', 'excel']:
            print('Found {} file 444, prepare for download...'.format(filetype), end='')
            jsons = {x['pageIndex']: x['pageLoadUrl'] for x in data['readerInfo']['htmlUrls']['json']}
            pngs = {x['pageIndex']: x['pageLoadUrl'] for x in data['readerInfo']['htmlUrls']['png']}
            fonts_csss = {x['pageIndex']: "https://wkretype.bdimg.com/retype/pipe/" + docid + "?pn=" + str(
                x['pageIndex']) + "&t=ttf&rn=1&v=6" + x['param'] for x in
                          data['readerInfo']['htmlUrls']['ttf']}  # temp_dir is doc ID in wenku.baidu.com
            print('Success.')

            if data['readerInfo']['page'] > 2:
                list_pn = list(range(3, data['readerInfo']['page'] + 1, 50))
                print("list_pn:", list_pn)
                for pn in list_pn:
                    url = "https://wenku.baidu.com/ndocview/readerinfo?doc_id={}&docId={}&type=html&clientType=10&pn={}&t={}&isFromBdSearch=0&srcRef=&rn=50&powerId=2".format(
                        docid, docid, pn, str(int(time.time())))
                    # aggs
                    if aggid:
                        url = "https://wenku.baidu.com/ndocview/readerinfo?doc_id={}&docId={}&type=html&clientType=1&pn={}&t={}&isFromBdSearch=0&rn=50".format(
                            temp_dir, temp_dir, pn, str(int(time.time())))
                    else:
                        # TODO: this url not work!
                        url = "https://wenku.baidu.com/ndocview/readerinfo?doc_id={}&docId={}&type=html&clientType=1&pn={}&t={}&isFromBdSearch=0&srcRef=&rn=50&powerId=2".format(
                            docid, docid, pn, str(int(time.time())))
                    try:
                        req = requests.get(
                            url,
                            headers=headers
                        )
                    except:
                        print("网络请求异常，休息10s")
                        time.sleep(10)
                        shutil.rmtree(temp_dir)
                        continue
                    print("url:", url)
                    data_temp = json.loads(req.text)['data'].get('htmlUrls')
                    # print("data_temp:", data_temp)
                    if data_temp:
                        jsons.update({x['pageIndex']: x['pageLoadUrl'] for x in data_temp['json']})
                        pngs.update({x['pageIndex']: x['pageLoadUrl'] for x in data_temp['png']})
                        fonts_csss.update(
                            {x['pageIndex']: "https://wkretype.bdimg.com/retype/pipe/" + docid + "?pn=" + str(
                                x['pageIndex']) + "&t=ttf&rn=1&v=6" + x['param'] for x in
                             data_temp['ttf']})  # temp_dir is doc ID in wenku.baidu.com

            if data['readerInfo']['page'] > len(jsons):
                print("页面未全部获取")
                continue
                print(
                    "It seems that you provided incorrect or Non-VIP cookies, only be able to download a part of the file ({} page), not the whole file ({} page).".format(
                        len(jsons), data['readerInfo']['page']))

            if args.pagenums:
                pagenums = my_tools.parse_pagenum(args.pagenums)
                pagenums = my_tools.under_by(pagenums, len(jsons))
                pagenums = [x for x in pagenums if x <= len(jsons)]
            else:
                pagenums = list(range(1, len(jsons) + 1))
            print('page: ', my_tools.export_pagenum(pagenums))

            print('Start downloading font(s)...')
            # for i in range(len(pagenums)):
            #     percentage = (i + 1) / len(pagenums) * 100
            #     if not fonts_csss.get(pagenums[i]):
            #         continue
            #     req = requests.get(fonts_csss[pagenums[i]], headers=headers)
            #     # status not 200?
            #     temp = re.findall(
            #         r'@font-face {src: url\(data:font/opentype;base64,(.*?)\)format\(\'truetype\'\);font-family: \'(.*?)\';',
            #         req.text)
            #     for each in temp:
            #         with open(os.path.join(temp_dir, str(each[1]) + '.ttf'), 'wb') as f:
            #             f.write(base64.b64decode(each[0]))
            #
            #     print('\r|{}| {} / {} ({:.2f}%)'.format(
            #         '=' * int(percentage // 2 - 1) + '>' + '-' * int(50 - percentage // 2),
            #         i + 1,
            #         len(pagenums),
            #         percentage
            #     ), end='')
            print()
            print('Start downloading json(s)...')
            for i in range(len(pagenums)):
                # TODO: theading
                if not jsons.get(pagenums[i]):
                    break
                try:
                    req = requests.get(jsons[pagenums[i]], headers=headers)
                    time.sleep(0.2)
                except:
                    print("获取json 数据异常")
                    break
                # status not 200?
                with open(os.path.join(temp_dir, str(pagenums[i]) + '.json'), 'w') as f:
                    try:
                        temp = re.search(r'wenku_[0-9]+\((.*)\)', req.text).group(1)
                    except:
                        # return
                        break
                    f.write(temp)
                percentage = (i + 1) / len(pagenums) * 100
                print('\r|{}| {} / {} ({:.2f}%)'.format(
                    '=' * int(percentage // 2 - 1) + '>' + '-' * int(50 - percentage // 2),
                    i + 1,
                    len(pagenums),
                    percentage
                ), end='')

            print()
            print('Start downloading png(s)...')
            for i in range(len(pagenums)):
                # TODO: theading
                if not pngs.get(pagenums[i]):
                    break
                req = requests.get(pngs[pagenums[i]], headers=headers)
                time.sleep(0.2)
                # status not 200?
                with open(os.path.join(temp_dir, str(pagenums[i]) + '.png'), 'wb') as f:
                    f.write(req.content)
                percentage = (i + 1) / len(pagenums) * 100
                print('\r|{}| {} / {} ({:.2f}%)'.format(
                    '=' * int(percentage // 2 - 1) + '>' + '-' * int(50 - percentage // 2),
                    i + 1,
                    len(pagenums),
                    percentage
                ), end='')

            print()
            print('Start generating pdf...')
            # jsons is right!
            font_replace = dict()
            # print("font_replace 1:", font_replace)
            for i in range(len(pagenums)):
                # TODO: theading
                try:
                    font_replace = save_pdf(temp_dir, pagenums[i], font_replace=font_replace)
                    # print("font_replace 2:", font_replace)
                except:
                    break
                percentage = (i + 1) / len(pagenums) * 100
                print('\r|{}| {} / {} ({:.2f}%)'.format(
                    '=' * int(percentage // 2 - 1) + '>' + '-' * int(50 - percentage // 2),
                    i + 1,
                    len(pagenums),
                    percentage
                ), end='')

            print()
            print('Start merging pdf...', end='')
            pdfs = {x[:-4]: os.path.join(temp_dir, x) for x in os.listdir(temp_dir) if x[-4:] == '.pdf'}
            file_merger = PdfMerger()
            for i in pagenums:
                # if i > len(pdfs):
                #     break
                try:
                    with open(pdfs[str(i)], 'rb') as f_pdf:
                        file_merger.append(PdfReader(f_pdf))
                except:
                    print("字体不全，跳过")
                    break
            if os.path.exists(output + '.pdf'):
                print("文件重复")
                continue
                # output = output + "_" + str(int(time.time() * 1000))
            file_merger.write(output + '.pdf')

            print('Success.')
            print('Saved to ' + output + '.pdf')

            # convert pdf to word
            # if isWord:
            #     try:
            #         my_tools.convert_pdf_to_docx_with_style(output + ".pdf", output + ".docx")
            #         if os.path.exists(output+'.pdf'):
            #             os.remove(output+'.pdf')
            #     except:
            #         print("pdf转word失败")

            if not args.temp and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

        # TXT
        elif data['readerInfo']['tplKey'] == 'txt_view' and filetype == 'txt':
            print('Found txt file, parse text from HTML...', end='')
            lines = re.findall(r'<p class="p-txt">(.*)</p>', html)

            print('Success.')
            if args.pagenums:
                print('Do not support argument "-p" or "--pagenums".')
            print('Download other(s) text...', end='')
            temp_dir = url.split('?')[0].split('/')[-1][:-5]
            req = requests.get(
                'https://wkretype.bdimg.com/retype/text/' + temp_dir + data['readerInfo']['md5sum'] + "&pn=2&rn=" + str(
                    int(data['viewBiz']['docInfo']['page']) - 1) + '&type=txt&rsign=' + data['readerInfo'][
                    'rsign'] + '&callback=cb&_=' + str(int(time.time())),
                headers=headers
            )
            try:
                lines_others_json = json.loads(req.text[3: -1])
            except:
                print("解释json异常，json数据事：")
                continue
            lines_others = [x['parags'][0]['c'][:-2] for x in lines_others_json]
            lines = [line for line in lines if line]
            lines[-1] = lines[-1][:-1]
            lines = lines + lines_others
            print('Success.')
            with open(output + '.txt', 'w', encoding='utf-8') as f:
                for line in lines:
                    f.write(line.replace('\r\n', '\r'))
            print('Saved to ' + output + '.txt')

            if not args.temp and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

        else:
            print('Do NOT support this document. File type:', filetype)


def fetch_search_url(listUrl, keyword, current_timestamp_ms, page):
    urlsList = []
    postData = {"requests": [{"sceneID": "PCSearch",
                              "params": {"word": keyword, "searchType": 0, "lm": "0", "od": "0", "fr": "search",
                                         "ie": "utf-8", "_wkts_": current_timestamp_ms, "wkQuery": "计划",
                                         "pn": page,
                                         "fd": 0, "curLogId": "1253665579"}},
                             {"sceneID": "PCSearchRec",
                              "params": {"word": "总结",
                                         "searchType": 0,
                                         "lm": "0", "od": "0",
                                         "fr": "search",
                                         "ie": "utf-8",
                                         "_wkts_": current_timestamp_ms,
                                         "wkQuery": "计划",
                                         "pn": page, "fd": 0}},
                             {"sceneID": "PCSearchVipcard"}]}

    res = requests.post(listUrl,
                        json=postData,
                        headers=headers)
    print("res:", res)
    resData = json.loads(res.text)
    if resData['status']['code'] != 0:
        print("获取搜索结果数据异常：", resData['status']['msg'])
        exit(0)

    itemList = resData['data']['items']['PCSearch']
    if itemList['error']:
        print("解析数据异常：", itemList['error'])
        exit(0)

    # print(itemList)

    for tmpUrl in itemList['result']['items']:
        print("标题：", tmpUrl['data']['title'])
        try:
            if args.filter_file_type is not None:
                filterFileType = args.filter_file_type.split(",")
                matching_indices = [value for i, value in enumerate(fileTypeList) if
                                    fileTypeList[value].upper() in filterFileType or fileTypeList[
                                        value].lower() in filterFileType]
                if tmpUrl['data']['fileType'] in matching_indices:
                    print("文件类型不能是=====", filterFileType)
                    # 1:doc ,2:xls ,3:PPT ,4: doc , 5:xls  6: ppt, 7: PDF, 8: txt
                    continue
        except:
            print("fileType 不存在")
            continue

        notExistKeyword = True
        for bk in blackWords:
            if bk in tmpUrl['data']['title'] or bk in tmpUrl['data']['content']:
                print("包含关键字：", bk, tmpUrl['data']['title'])
                notExistKeyword = False
                break

        if tmpUrl['data']['pageNum'] < 91 and notExistKeyword:
            # print("url:", tmpUrl['data']['url'])
            urlsList.append(tmpUrl['data']['url'].replace(".html", ""))

    return urlsList


# listUrl 请求地址
# keyword 关键字
# page 页码
# cid 分ID 0:学前教育, 1:基础教育, 2:高校与高等教育, 3:语言/资格考试, 4:法律, 5:建筑, 6:互联网, 7:行业资料,
# 8:政务民生, 9:说明书, 10:实用模板, 11:生活娱乐
def fetch_cate_search(listUrl, keyword, pageNum, cid=0):
    urlList = []
    pageNum = pageNum - 1
    if pageNum < 0:
        pageNum = 0
    goodsType = [2, 3]
    sortType = [2, 3, 4]
    docIds = []

    for gt in goodsType:
        for st in sortType:
            params = {
                "cid1": cid,
                "goodsType": gt,  # 2:vip, 3:付费
                "sortType": st,  # 1:综合排序,2:销量优先, 3:新品优先, 4:人气优先
                "tag": keyword,
                "rn": 24,
                "pn": pageNum
            }
            query_string = urlencode(params)
            queryUrl = listUrl + f'?{query_string}'
            print("listUrl", queryUrl)

            res = requests.get(queryUrl)
            if res.status_code != 200:
                print("获取列表数据一次, http_code:", res.status_code)
                return []

            resData = res.json()
            if 'data' not in resData:
                continue

            resData = resData['data']

            if 'docList' not in resData:
                continue

            resData = resData['docList']

            for item in resData:
                docId = item['docId']  # id
                if docId in docIds:
                    continue
                docIds.append(docId)

                filterFileType = []
                if args.filter_file_type != '':
                    filterFileType = args.filter_file_type.split(",")

                docTitle = item['docTitle']  # 标题
                docType = item['docType']  # 文件类型
                downCount = item['downCount']  # 下载次数
                viewCount = item['viewCount']  # 浏览次数
                if docType != '' and docType in filterFileType:
                    print(f"过滤{docTitle},文件类型：{docType}")
                    continue
                urlList.append(f'https://wenku.baidu.com/view/{docId}?fr=hp_sub')

            time.sleep(0.3)
    docIds = []
    return urlList


urls = []
tmpDir = ''
if args.listUrl:
    listUrl = args.listUrl
    keywordList = args.keyword.strip(" ").strip("||").strip(" ").split("||")
    for keyword in keywordList:
        print(f"current fetch {keyword}")
        if args.is_split_dir is not None and int(args.is_split_dir) == 1:
            tmpDir = pathDir + "{}/".format(keyword)
        else:
            tmpDir = pathDir

        print("tmpDir", tmpDir)

        if not os.path.exists(tmpDir):
            os.mkdir(tmpDir)

        pageList = args.page.split("-")
        if len(pageList) == 1:
            pages = [int(args.page[0])]
        else:
            pages = list(range(int(pageList[0]), int(pageList[1]) + 1))

        print("pages:", pages)

        for page in pages:
            print("current_page =", page)
            current_timestamp_ms = int(time.time() * 1000)
            # 判断是 //wenku.baidu.com/ghome/secpage/secfilterres 还是//wenku.baidu.com/gsula/sula/syncmrecall
            if "syncmrecall" in args.listUrl:
                # 文档搜索
                urls = fetch_search_url(args.listUrl, keyword, current_timestamp_ms, page)
            else:
                # 分类中搜索
                if args.cid is None:
                    args.cid = 0
                urls = fetch_cate_search(args.listUrl, keyword, page, args.cid)

            print("urls:", urls)

            if len(urls) > 0:
                fatch_urls(urls)

            urls.clear()
            if current_timestamp_ms - int(time.time() * 1000) < 60000:
                time.sleep(random.randint(8, 16))

        # urls = ["https://wenku.baidu.com/view/4c4eb0e1a7c30c22590102020740be1e640ecc62?fr=income7-doc-search"]

    exit(0)

if args.url:
    urls = [args.url]
elif args.filename:
    with open(args.filename) as f:
        urls = f.read().split('\n')
elif len(urls) == 0:
    parser.parse_args(['-h'])

fatch_urls(urls)
