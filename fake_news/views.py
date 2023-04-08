import csv
import os
import re
import string
import threading
from datetime import date

import joblib
import pandas as pd
from django.contrib import messages
from django.contrib.auth import authenticate as auth_user
from django.contrib.auth import login as log
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

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
    file_path = os.path.join(os.path.dirname(__file__), dir_path, 'new_data.csv')
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='', encoding='latin1') as csvfile:
        fieldnames = ['text', 'class']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def check_news(request):
    return render(request, 'admin_check_news.html')

def download_csv(request):
    file_path = os.path.join(os.path.dirname(__file__), 'datasets', 'new_data.csv')
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        csv_data = [row for row in reader]
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="new_data.csv"'
    writer = csv.writer(response)
    writer.writerow(['text', 'class'])
    for row in csv_data:
        writer.writerow([row['text'], row['class']])
    return response

def upload_csv(request):
    context = {}
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        file_name = os.path.join(os.path.dirname(__file__), 'datasets', 'new_data.csv')
        os.remove(file_name)
        with open(file_name, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        message =  'File uploaded successfully.'
        context = {"message":message}
    return render(request, "admin_check_news.html", context)

def update(request):
    thread = threading.Thread(target=update_thread, args =(request,) )
    thread.start()
    message = "Wait till models are updates"
    context = {"message":message}
    return render(request, "admin_check_news.html", context)


def update_thread(request):
    data_true = pd.read_csv('fake_news\\datasets\\True.csv', encoding='latin1')
    data_fake = pd.read_csv('fake_news\\datasets\\Fake.csv', encoding='latin1')
    data_fake["class"] = 0
    data_true["class"] = 1
    data = pd.concat([data_fake, data_true], axis=0)
    data = data.drop(['title', 'subject', 'date'], axis=1)
    data = data.sample(frac=1)
    data.reset_index(inplace=True)
    data.drop(['index'], axis=1, inplace=True)
    data_new = pd.read_csv('fake_news\\datasets\\new_data.csv', encoding='latin1')
    data = pd.concat([data, data_new], axis=0)
    data = preprocess(data)
    x = data['text']
    y = data['class']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25)
    print("Data Split")
    vectorization = TfidfVectorizer()
    xv_train = vectorization.fit_transform(x_train)
    # xv_test = vectorization.transform(x_test)
    print("Vectorize")
    LR = LogisticRegression()
    LR.fit(xv_train, y_train)
    print("Logistic")
    DT = DecisionTreeClassifier()
    DT.fit(xv_train, y_train)
    print("DecisionTree")
    RF = RandomForestClassifier()
    RF.fit(xv_train, y_train)
    print("RandomForest")
    Flag = save_models(vectorization,LR,DT,RF)
    if Flag:
        message = "Models updated successfully"
        file_path_new = os.path.join(os.path.dirname(__file__), 'datasets', 'new_data.csv')
        with open(file_path_new, 'r') as source_file:
            reader = csv.reader(source_file)
            data = [row for row in reader]
        os.remove(file_path_new)
        today = date.today().strftime('%Y-%m-%d')
        for row in data:
            row.append(today)
        file_path_all = os.path.join(os.path.dirname(__file__), 'datasets', 'all_mod.csv')
        with open(file_path_all, 'a', newline='') as dest_file:
            writer = csv.writer(dest_file)
            writer.writerows(data)
    else: 
        message = "Failed to update models"
    context = {"message": message}
    return render(request, "admin_check_news.html", context)

def preprocess(df):
    df['text'] = df['text'].astype(str)
    df['text'] = df['text'].apply(wordopt)
    return df

def wordopt(text):
        text = text.lower()
        text = re.sub('\[.*?\]', '', text)
        text = re.sub("\\W", " ", text)
        text = re.sub('http?://\S+|www\.\S+', '', text)
        text = re.sub('<.*?>+', '', text)
        text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
        text = re.sub('\n', '', text)
        text = re.sub('\w*\d\w*', '', text)
        text = re.sub('\s+', ' ', text)
        return text
def save_models(vectorization,LR,DT,RF):
    model_dir = "fake_news\pred_models"
    for filename in os.listdir(model_dir):
        if filename.endswith('.pkl'):
            os.remove(os.path.join(model_dir, filename))
    try:
        joblib.dump(LR, f"{model_dir}/logistic_regression.pkl")
        joblib.dump(DT, f"{model_dir}/decision_tree.pkl")
        joblib.dump(RF, f"{model_dir}/random_forest.pkl")
        joblib.dump(vectorization, f"{model_dir}/vectorizer.pkl")
        return True
    except:
        return False