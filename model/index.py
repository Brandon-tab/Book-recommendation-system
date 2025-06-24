import os
import django
import json
import numpy as np
from tqdm import tqdm

os.environ.setdefault('DJANGO_SETTINGS_MODULE','豆瓣图书数据分析可视化系统.settings')
django.setup()
from myApp.models import BookList,User

def getAllData():
    allData = BookList.objects.all()
    commentList = []
    for i in allData:
        comment_list = json.loads(i.commentList)
        for j in comment_list:
            commentList.append(j)
            j['realId'] = i.id
    rateList = []
    for i in comment_list:
        rateList.append([int(i['userId']),int(i['bookId']),int(i['start']),i['createTime'],int(i['realId'])])
    return rateList

def getUIMat(data):
    user_list = [i[0] for i in data]
    item_list = [i[1] for i in data]
    UI_matrix = np.zeros((max(user_list) + 1,max(item_list) + 1))
    for each_interation in tqdm(data,total=len(data)):
        UI_matrix[each_interation[0]][each_interation[1]] = each_interation[2]

    return UI_matrix

class MF():
    def __init__(self,R,K,alpha,beta,iterations):
        self.R = R
        self.num_users,self.num_items = R.shape
        self.K = K
        self.alpha =alpha
        self.beta = beta
        self.iterations = iterations


    def train(self):
        self.P = np.random.normal(scale=1./self.K, size=(self.num_users, self.K))
        self.Q = np.random.normal(scale=1./self.K, size=(self.num_items, self.K))
        self.b_u = np.zeros(self.num_users)
        self.b_i = np.zeros(self.num_items)
        self.b = np.mean(self.R[np.where(self.R != 0)])
        self.samples = [
            (i, j, self.R[i, j])
            for i in range(self.num_users)
            for j in range(self.num_items)
            if self.R[i, j] > 0
        ]
        training_process = []
        for i in tqdm(range(self.iterations), total=self.iterations):
            np.random.shuffle(self.samples)
            self.sgd()
            mse = self.mse()
            training_process.append((i, mse))
            if (i == 0) or ((i+1) % (self.iterations / 10) == 0):
                pass
        return training_process

    def mse(self):
        xs, ys = self.R.nonzero()
        predicted = self.full_matrix()
        error = 0
        for x, y in zip(xs, ys):
            error += pow(self.R[x, y] - predicted[x, y], 2)
        return np.sqrt(error)

    def sgd(self):
        for i, j, r in self.samples:
            prediction = self.get_rating(i, j)
            e = (r - prediction)
            self.b_u[i] += self.alpha * (e - self.beta * self.b_u[i])
            self.b_i[j] += self.alpha * (e - self.beta * self.b_i[j])
            self.P[i, :] += self.alpha * (e * self.Q[j, :] - self.beta * self.P[i,:])
            self.Q[j, :] += self.alpha * (e * self.P[i, :] - self.beta * self.Q[j,:])

    def get_rating(self, i, j):
        prediction = self.b + self.b_u[i] + self.b_i[j] + self.P[i, :].dot(self.Q[j, :].T)
        return prediction

    def full_matrix(self):
        return self.b + self.b_u[:,np.newaxis] + self.b_i[np.newaxis:,] + self.P.dot(self.Q.T)


def modelFn(each_user):
    startList = getAllData()
    obs_dataset = []
    for i in startList:
        obs_dataset.append([i[0],i[4],i[2]])

    R = getUIMat(obs_dataset)
    mf = MF(R,K=2,alpha=0.1,beta=0.8,iterations=10)
    mf.train()
    user_ratings = mf.full_matrix()[each_user].tolist()
    topN = [(i,user_ratings.index(i)) for i in user_ratings]
    topN = [i[1] for i in sorted(topN,key=lambda x:x[0],reverse=True)]
    return topN

if __name__ == '__main__':
    print(modelFn(1))
