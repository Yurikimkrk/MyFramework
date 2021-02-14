from framework import Application
import views

urlpatterns = {
    '/': views.main_view,
    '/about/': views.about_view,
    '/contacts/': views.contacts_view,
}


def secret_controller(request):
    request['secret_key'] = 'Important info!'
    request['contacts'] = 'Important contacts!'


front_controllers = [
    secret_controller
]

application = Application(urlpatterns, front_controllers)
