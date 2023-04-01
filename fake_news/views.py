from django.shortcuts import render
from fake_news.models import News
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