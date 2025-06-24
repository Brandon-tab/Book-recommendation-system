import jieba
from matplotlib import pyplot as plt
from wordcloud import WordCloud
import numpy as np
from PIL import Image
from pymysql import *

def get_img(field,targetImageSrc,resImageSrc):
    conn = connect(host="localhost",user="root",password="123456",database="dbbook",port=3306,charset='utf8mb4')
    cursor = conn.cursor()
    sql = f"select {field} from booklist"
    cursor.execute(sql)
    data = cursor.fetchall()

    text = ''
    for i in data:
        if i[0] != '':
            tarArr = i
            for j in tarArr:
                text += j
    cursor.close()
    conn.close()
    data_cut = jieba.cut(text,cut_all=False)
    string = ' '.join(data_cut)

    #wordcloud
    img = Image.open(targetImageSrc)
    ima_arr = np.array(img)
    wc = WordCloud(
        background_color='#fff',
        font_path='STHUPO.TTF',
        mask=ima_arr
    )
    wc.generate_from_text(string)

    fig = plt.figure(1)
    plt.imshow(wc)
    plt.axis('off')

    plt.savefig(resImageSrc,dpi=800,bbox_inches='tight',pad_inches=-0.1)

get_img('title','./static/start.jpg','./static/cloudImg/titleCloud')