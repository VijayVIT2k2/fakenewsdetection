from django.shortcuts import render, redirect
from django.contrib.auth import authenticate as auth_user, login as log
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
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
    
def authenticate(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth_user(request, username=username, password=password)
        if user is not None:
            return render(request, 'add_news.html')
        else:
            error_message = "Invalid username or password. Please try again."
            messages.error(request, error_message)
            return redirect('login')
    else:
        return redirect('login')
    
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = auth_user(request, username=username, password=password)
            log(request, user)
            return redirect('add_news')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})