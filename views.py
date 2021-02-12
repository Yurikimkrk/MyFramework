from framework import render


def main_view(request):
    secret = request.get('secret_key', None)
    return '200 OK', render('index.html', secret=secret)


def contacts_view(request):
    contacts = request.get('contacts', None)
    return '200 OK', render('contacts.html', contacts=contacts)


def about_view(request):
    return '200 OK', "Very important info"
