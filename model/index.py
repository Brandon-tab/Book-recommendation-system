import os
import django
import json
import numpy as np
from tqdm import tqdm

os.environ.setdefault('DJANGO_SETTINGS_MODULE','doubanBook.settings')
django.setup()
from myApp.models import BookList,User

# 从BookList模型获取所有数据
# 解析每本书的评论列表(JSON格式)
# 构建评分数据列表，每个元素包含: [userId, bookId, rating, createTime, realId]
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

# 创建用户-物品评分矩阵(UI矩阵)
# 矩阵维度由最大用户ID和最大书籍ID决定
# 将评分数据填充到矩阵对应位置
def getUIMat(data):
    user_list = [i[0] for i in data]
    item_list = [i[1] for i in data]
    UI_matrix = np.zeros((max(user_list) + 1,max(item_list) + 1))
    for each_interation in tqdm(data,total=len(data)):
        UI_matrix[each_interation[0]][each_interation[1]] = each_interation[2]

    return UI_matrix

class MF():
    # init: 初始化模型参数
    # R: 用户 - 物品评分矩阵
    # K: 潜在特征维度
    # alpha: 学习率
    # beta: 正则化参数
    # iterations: 迭代次数
    def __init__(self,R,K,alpha,beta,iterations):
        self.R = R
        self.num_users,self.num_items = R.shape
        self.K = K
        self.alpha =alpha
        self.beta = beta
        self.iterations = iterations

    # train: 训练模型
    # 初始化用户特征矩阵P和物品特征矩阵Q
    # 初始化用户偏置b_u和物品偏置b_i
    # 计算全局平均评分b
    # 使用SGD进行迭代优化
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

    # mse: 计算均方根误差(RMSE)
    def mse(self):
        xs, ys = self.R.nonzero()
        predicted = self.full_matrix()
        error = 0
        for x, y in zip(xs, ys):
            error += pow(self.R[x, y] - predicted[x, y], 2)
        return np.sqrt(error)

    # sgd: 随机梯度下降实现
    # 更新用户和物品的偏置项
    # 更新用户和物品的特征向量
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

    # full_matrix: 重建完整的评分矩阵
    def full_matrix(self):
        return self.b + self.b_u[:,np.newaxis] + self.b_i[np.newaxis:,] + self.P.dot(self.Q.T)

# modelFn(each_user)函数:
# 获取所有评分数据
# 构建观测数据集(只保留userId, bookId, rating)
# 创建用户-物品评分矩阵
# 初始化并训练MF模型
# 获取指定用户的预测评分
# 返回评分最高的N本书籍ID(按评分降序排列)
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
