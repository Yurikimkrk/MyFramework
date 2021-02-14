from framework import render
from framework import Application


def main_view(request):
    secret = request.get('secret_key', None)
    return '200 OK', render('index.html', secret=secret)


def contacts_view(request):
    contacts = request.get('contacts', None)
    if request['method'] == 'POST':
        data = request['data']
        title = data['title']
        text = data['text']
        email = data['email']
        print(f'Нам пришло сообщение! Отправитель - {email}, '
              f'тема - {Application.decode_value(title)}, текст - '
              f' {Application.decode_value(text)}.')
    return '200 OK', render('contacts.html', contacts=contacts)


def about_view(request):
    return '200 OK', "Very important info"
