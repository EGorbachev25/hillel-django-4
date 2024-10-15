from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from hillelDjango4.tasks import hello_world_task


def hello_world(request):
    # random_time = random() * 10  # 0-10 seconds
    #
    # sleep(random_time)
    name = request.GET.get('name', 'World')

    # Apply async in 3 seconds
    hello_world_task.delay(name)

    return HttpResponse('Hello, World!')


def index(request):
    return render(request, 'index.html')


@cache_page(60)
def current_time(request):
    time = datetime.now().strftime('%H:%M:%S')

    return HttpResponse(f'Current time is {time}')
