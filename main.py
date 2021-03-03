from wsgiref.simple_server import make_server
from framework import render, Application, DebugApplication, FakeApplication
from models import TrainingSite, BaseSerializer, EmailNotifier, SmsNotifier
from logger import Logger, debug
from framework.fwcbv import ListView, CreateView
from orm import UnitOfWork
from mappers import MapperRegistry

site = TrainingSite()
logger = Logger('main')
email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()
UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistry)


class CategoryCreateView(CreateView):
    template_name = 'create_category.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['categories'] = site.categories
        return context

    def create_obj(self, data: dict):
        name = data['name']
        name = Application.decode_value(name)
        category_id = data.get('category_id')

        category = None
        if category_id:
            category = site.find_category_by_id(int(category_id))

        new_category = site.create_category(name, category)
        site.categories.append(new_category)


class CategoryListView(ListView):
    queryset = site.categories
    template_name = 'category_list.html'


class StudentListView(ListView):
    template_name = 'student_list.html'

    def get_queryset(self):
        mapper = MapperRegistry.get_current_mapper('student')
        return mapper.all()


class StudentCreateView(CreateView):
    template_name = 'create_student.html'

    def create_obj(self, data: dict):
        name = data['name']
        name = Application.decode_value(name)
        new_obj = site.create_user('student', name)
        site.students.append(new_obj)
        new_obj.mark_new()
        UnitOfWork.get_current().commit()


class AddStudentByCourseCreateView(CreateView):
    template_name = 'add_student.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['courses'] = site.courses
        context['students'] = site.students
        return context

    def create_obj(self, data: dict):
        course_name = data['course_name']
        course_name = Application.decode_value(course_name)
        course = site.get_course(course_name)
        student_name = data['student_name']
        student_name = Application.decode_value(student_name)
        student = site.get_student(student_name)
        course.add_student(student)


urlpatterns = {
    '/create-category/': CategoryCreateView(),
    '/category-list/': CategoryListView(),
    '/student-list/': StudentListView(),
    '/create-student/': StudentCreateView(),
    '/add-student/': AddStudentByCourseCreateView(),
}


def secret_controller(request):
    request['contacts'] = 'Important contacts!'


front_controllers = [
    secret_controller
]

application = Application(urlpatterns, front_controllers)


# application = DebugApplication(urlpatterns, front_controllers)
# application = FakeApplication(urlpatterns, front_controllers)


@application.add_route('/')
def main_view(request):
    logger.log('Список курсов')
    print(f'Список курсов - {site.courses}')
    return '200 OK', render('index.html', objects_list=site.courses)


@application.add_route('/about/')
def about_view(request):
    logger.log('Информация о портале')
    return '200 OK', render('about.html')


@application.add_route('/contacts/')
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


@debug
@application.add_route('/create-course/')
def create_course(request):
    if request['method'] == 'POST':
        data = request['data']
        name = Application.decode_value(data['name'])
        category_id = data.get('category_id')
        if category_id:
            category = site.find_category_by_id(int(category_id))

            course = site.create_course('record', name, category)
            course.observers.append(email_notifier)
            course.observers.append(sms_notifier)
            site.courses.append(course)
        categories = site.categories
        return '200 OK', render('create_course.html', categories=categories)
    else:
        categories = site.categories
        return '200 OK', render('create_course.html', categories=categories)


@application.add_route('/copy-course/')
def copy_course(request):
    request_params = request['request_params']
    name = Application.decode_value(request_params['name'])
    old_course = site.get_course(name)
    if old_course:
        new_name = f'{name}(copy)'
        new_course = old_course.clone()
        new_course.name = new_name
        site.courses.append(new_course)

    return '200 OK', render('index.html', objects_list=site.courses)


@application.add_route('/api/')
def course_api(request):
    return '200 OK', BaseSerializer(site.courses).save()


with make_server('', 8000, application) as httpd:
    print("Serving on port 8000...")
    httpd.serve_forever()
