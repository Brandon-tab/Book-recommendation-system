from myApp.models import *


def getAllUserList():
    user_list = User.objects.all()
    return user_list

def getAllBookList():
    book_list = BookList.objects.all()
    return book_list