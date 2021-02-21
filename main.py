from framework import render, Application
from models import TrainingSite
from logger import Logger

site = TrainingSite()
logger = Logger('main')


def main_view(request):
    logger.log('Список курсов')
    print(f'Список курсов - {site.courses}')
    return '200 OK', render('index.html', objects_list=site.courses)


def about_view(request):
    logger.log('Информация о портале')
    return '200 OK', render('about.html')


def contacts_view(request):
    logger.log('Наши контакты')
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


def create_course(request):
    if request['method'] == 'POST':
        data = request['data']
        name = data['name']
        category_id = data.get('category_id')
        category = None
        if category_id:
            category = site.find_category_by_id(int(category_id))

            course = site.create_course('record', name, category)
            site.courses.append(course)
        return '200 OK', render('create_course.html')
    else:
        categories = site.categories
        return '200 OK', render('create_course.html', categories=categories)


def create_category(request):
    if request['method'] == 'POST':
        data = request['data']
        name = data['name']

        name = Application.decode_value(name)
        category_id = data.get('category_id')

        category = None
        if category_id:
            category = site.find_category_by_id(int(category_id))

        new_category = site.create_category(name, category)

        site.categories.append(new_category)
        return '200 OK', render('create_category.html')
    else:
        categories = site.categories
        return '200 OK', render('create_category.html', categories=categories)


def copy_course(request):
    request_params = request['request_params']
    name = request_params['name']
    old_course = site.get_course(name)
    if old_course:
        new_name = f'{name}(copy)'
        new_course = old_course.clone()
        new_course.name = new_name
        site.courses.append(new_course)

    return '200 OK', render('index.html', objects_list=site.courses)


def category_list(request):
    logger.log('Список категорий')
    return '200 OK', render('category_list.html', objects_list=site.categories)


urlpatterns = {
    '/': main_view,
    '/about/': about_view,
    '/contacts/': contacts_view,
    '/create-course/': create_course,
    '/create-category/': create_category,
    '/copy-course/': copy_course,
    '/category-list/': category_list,
}


def secret_controller(request):
    request['contacts'] = 'Important contacts!'


front_controllers = [
    secret_controller
]

application = Application(urlpatterns, front_controllers)
