from django.shortcuts import render, redirect
from django.contrib.auth import authenticate as auth_user, login as log
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import threading
import csv
import os

from fake_news.news_det import FakeNewsDetector

def home(request):
    if request.method == 'POST':
        news_text = request.POST.get('news_text')
        detector = FakeNewsDetector()
        # plot_url = detector.plot_wordcloud()
        prediction = detector.predict(news_text)
        if(prediction['label'] is True):
            pred_result = "The news content is REAL"
        elif(prediction['label'] is False):
            pred_result = "The news content is FAKE"
        else:
            pred_result = ""        
        context = {
            'news_text': news_text,
            'prediction': pred_result,
            'acc_score' : prediction['accuracy_score']
        }
        return render(request, 'result.html', context)
    return render(request, 'home.html')

def login(request):
    return render(request, 'login.html')

def user_home(request):
    return render(request, 'user_home.html')
    
def authenticate(request):
    print(request.POST.get('username'))
    print(request.POST.get('password'))
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth_user(request, username=username, password=password)
        print(request.POST.get('username'))
        print(request.POST.get('password'))
        if user is not None:
            user_obj = User.objects.get(username = username)
            print(user_obj.username)
            print(user_obj.get_username)
            log(request, user)
            return render(request, 'user_home.html')
        else:
            error_message = "Invalid username or password. Please try again."
            messages.error(request, error_message)
            return redirect('login')
    else:
        return redirect('login')
    
def register(request):
    if request.method == 'POST':
        print("POST Method")
        form = UserCreationForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password1')
        print(username)
        print(password)
        if form.is_valid():
            print('Form is valid')
            username = request.POST.get('username')
            password = request.POST.get('password1')
            create_user = User.objects.create_user(username=username, password=password)
            create_user.save()
            print(username)
            user = auth_user(request, username=username, password=password)
            log(request, user)
            user = User.objects.get(username=username)
            print(user.username)
            return render(request,"user_home.html")
        else:
            print(form.errors)
    else:        
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def add_news(request):
    return render(request,'add_news.html')

def pro_news(request):
    text = request.POST.get('input')
    out = request.POST.get('option')
    context = {
        'text':text,
        'out':out
    }
    t = threading.Thread(target=news_process, args=[context])
    t.start()
    return render(request, 'added.html')

def news_process(context):
    text = context['text']
    out = context['out']
    if out == 'yes':
        out = True
    elif out == 'no':
        out = False
    det = FakeNewsDetector()
    pred = det.predict(text)
    if out==pred['label']:
        pass
    elif out!=pred['label']:
        out_class = None
        if out == True:
            out_class = 1
        elif out == False:
            out_class = 0
        data = {
            'text':text,
            'class':out_class
        }
        write_to_csv(data)

def write_to_csv(data):
    dir_path = "datasets"
    filename = os.path.join(dir_path, "new_data.csv")
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as csvfile:
        fieldnames = ['text', 'class']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def check_news(request):
    file_path = os.path.join(os.path.dirname(__file__), 'datasets', 'new_data.csv')
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        csv_data = [row for row in reader]
        context = {'data':csv_data}
    return render(request, 'admin_check_news.html', context)