from django.shortcuts import render, redirect
from django.contrib import messages
from myApp.models import *
from django.http import HttpResponseRedirect
from utils.getPublicData import *
from utils.getChartData import *


# Create your views here.
def home(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    print(userInfo.username)
    userLen, typeLen, maxPrice, maxPriceBookName, maxRate, maxPageNum, rateList, rateListNum, createUserList, commentList = getHomeDataPage()
    return render(request, 'index.html', {
        'userInfo': userInfo,
        'userLen': userLen,
        'typeLen': typeLen,
        'maxPrice': maxPrice,
        'maxPriceBookName': maxPriceBookName,
        'maxRate': maxRate,
        'maxPageNum': maxPageNum,
        'rateList': rateList,
        'rateListNum': rateListNum,
        'createUserList': createUserList,
        'commentList': commentList[:20]
    })


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html', {})
    else:
        uname = request.POST.get('username')
        pwd = request.POST.get('password')
        print(uname, pwd)
        try:
            user = User.objects.get(username=uname, password=pwd)
            request.session['username'] = uname
            print(user)
            return redirect('/myApp/home')
        except:
            messages.error(request, '登录失败，请输入正确用户名与密码')
            return HttpResponseRedirect('/myApp/login')


def logOut(request):
    request.session.clear()
    return redirect('login')


def register(request):
    if request.method == 'GET':
        return render(request, 'register.html', {})
    else:
        uname = request.POST.get('username')
        pwd = request.POST.get('password')
        rePwd = request.POST.get('checkPassword')
        print(uname, pwd, rePwd)
        message = ''
        try:
            User.objects.get(username=uname)
            message = '账号已存在'
            messages.error(request, '账号已存在')
            return HttpResponseRedirect('/myApp/register/')
        except:
            if not uname or not pwd or not rePwd:
                message = '不允许为空'
                messages.error(request, message)
                return HttpResponseRedirect('/myApp/register/')
            elif pwd != rePwd:
                message = '两次密码不相符'
                messages.error(request, message)
                return HttpResponseRedirect('/myApp/register/')
            else:
                message = '创建成功'
                User.objects.create(username=uname, password=pwd)
        return render(request, 'login.html', {})


def selfInfo(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    print(userInfo.username)
    if request.method == 'POST':
        print(request.POST)
        res = changePassword(uname, request.POST)
        if res != None:
            messages.error(request, res)
            return HttpResponseRedirect('/myApp/selfInfo')
    return render(request, 'selfInfo.html', {
        'userInfo': userInfo,
    })
