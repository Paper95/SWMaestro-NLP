from gensim import models
import psycopg2 as pg2
import re
import pandas as pd
import csv
import numpy as np
from scipy import spatial
from sklearn import neighbors
from scipy.spatial import distance

# ## 추가 학습 시키는 소스
# # IP = "ec2-13-124-107-195.ap-northeast-2.compute.amazonaws.com"
# # video_keyword = pd.read_csv(r'D:\createtrend_public_video_keyword.csv')
# ko_model = models.fasttext.load_facebook_model(r'D:\share\wiki.ko.bin')
# def pre(text):
#     text = text.strip().lower()
#     # text = re.sub('[^ 0-9ㄱ-ㅣ가-힣a-z:/_.\'\",~!?`#%^&*{}()]+', '', text)
#     text = re.sub('http.*', '', text)
#     text = re.sub('[0-9]{1,3}:[0-9]{1,2}', ' ', text)
#     # text = re.sub('[^ 0-9ㄱ-ㅣ가-힣a-z!?.,\'\"~`#%^&*(){}]+', ' ', text)
#     text = re.sub('[^ 0-9ㄱ-ㅣ가-힣a-z]', ' ', text)
#     text = re.sub('\n', ' ', text)
#     text = re.sub(' {2,}', ' ', text)
#     return text.strip()
# new_data = []
#
# f = open(r'D:\createtrend_public_video.csv', 'r', encoding='utf-8')
# rdr = csv.reader(f)
# for line in rdr:
#     new_data.append(pre(line[1]).split())
#     new_data.append(pre(line[2]).split())
#
# f = open(r'D:\Result_11.csv', 'r', encoding='utf-8')
# rdr = csv.reader(f)
# for line in rdr:
#     new_data.append([kk.strip() for kk in line[1].split(',')])
#
# ko_model.build_vocab(new_data, update=True)
# ko_model.train(new_data, total_examples=len(new_data), epochs=ko_model.epochs)
#
# ko_model.similar_by_word('삼겹살', 10)
# ko_model.save('new_model')
#
# for w, sim in ko_model.similar_by_word('유튜브', 10):
#     print(f'{w}: {sim}')


IP = "ec2-13-124-107-195.ap-northeast-2.compute.amazonaws.com"
ko_model = models.fasttext.FastText.load('new_model')

conn = pg2.connect(database="createtrend", user="muna", password="muna112358!", host=IP,
                   port="5432")
conn.autocommit = False
cur = conn.cursor()
cur.execute(f"""SELECT idx FROM channel;""")
channel_list = cur.fetchall()

channel_vector = []
index_to_name = []
index_to_idx = []
idx_to_index = dict()


index = 0

for channel_idxx in channel_list:
    channel_idx = channel_idxx[0]

    cur.execute(f"""SELECT channel_name FROM channel WHERE idx = {channel_idx};""")
    channel_name = cur.fetchall()[0][0]

    cur.execute(f"""SELECT keyword, count(keyword) as cc
    FROM video_keyword
    WHERE video_idx IN (SELECT idx FROM video WHERE channel_idx = {channel_idx})
    GROUP BY keyword ORDER BY cc DESC LIMIT 10;""")

    res = cur.fetchall()
    all = np.zeros(300)
    total_weight = 0

    for keyword, weight in res:
        all += ko_model.wv.get_vector(keyword) * weight
        total_weight += weight

    if total_weight == 0:
        continue

    all /= total_weight

    index_to_name.append(channel_name)
    index_to_idx.append(index)
    idx_to_index[channel_idx] = index
    channel_vector.append(all)

    index += 1

cnp = np.array(channel_vector)
np.save('channel_vector_10', cnp)


distances = distance.cdist([cnp[idx_to_index[3093]]], cnp, "cosine")[0]
ind = np.argpartition(distances, 10)[:10]
for i in np.argpartition(distances, range(10))[:10]:
    print(index_to_name[i])

min_index = np.argmin(distances)
min_distance = distances[min_index]

# tree = neighbors.BallTree(cnp)
# tree.query([cnp[499]], 10)
# idx_to_index[2888]
# index_to_name[idx_to_index[254]]
# for i in range(len(temp)):
#     res = []
#     for j in range(len(temp)):
#         res.append(1 - spatial.distance.cosine(temp[i], temp[j]))
#     total.append(res)
#
# for line in total:
#     line = [str(e) for e in line]
#     print("\t".join(line))
