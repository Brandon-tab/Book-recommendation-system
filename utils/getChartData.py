from utils.getPublicData import *
import json
userList = list(getAllUserList())
bookList = list(getAllBookList())

def getHomeDataPage():
    userLen = len(userList)
    maxPrice = 0
    maxPriceBookName = ''
    typeLen = []
    maxRate = 0
    maxPageNum = 0
    rateList = []
    for i in bookList:
        rateList.append(float(i.rate))
        if maxPrice < int(i.price):
            maxPrice = int(i.price)
            maxPriceBookName = i.title

        typeLen.append(i.tag)

        if maxRate < float(i.rate):
            maxRate = float(i.rate)

        if maxPageNum < int(i.pageNum):
            maxPageNum = int(i.pageNum)

    typeLen = len(list(set(typeLen)))
    rateList = list(set(rateList))
    rateListNum = [0 for x in range(len(rateList))]
    rateList = list(sorted(rateList,key=lambda x:x,reverse=True))
    for i in bookList:
        for index,j in enumerate(rateList):
            if float(i.rate) == j:
                rateListNum[index] += 1

    print(rateList)
    print(rateListNum)

    createUserDic = {}
    for u in userList:
        time = u.createTime.strftime("%Y-%m-%d")
        if createUserDic.get(time,-1) == -1:
            createUserDic[time] = 1
        else:
            createUserDic[time] += 1

    createUserList = []
    for k,v in createUserDic.items():
        createUserList.append({
            'name':k,
            'value':v
        })
    print(createUserList)
    commentList = []
    for i in bookList:
        comments = json.loads(i.commentList)
        for j in comments:
            commentList.append(j)


    # print(userLen,typeLen,maxPrice,maxPriceBookName,maxRate,maxPageNum)
    return userLen,typeLen,maxPrice,maxPriceBookName,maxRate,maxPageNum,rateList,rateListNum,createUserList,commentList

def changePassword(uname,passwordData):
    oldPwd = passwordData['oldPassword']
    newPwd = passwordData['newPassword']
    checkPwd = passwordData['checkPassword']
    user = User.objects.get(username=uname)
    if oldPwd != user.password: return '原密码不正确'
    if newPwd != checkPwd:return '密码确认失败'

    user.password = newPwd
    user.save()