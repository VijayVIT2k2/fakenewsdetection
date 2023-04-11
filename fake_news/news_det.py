import pandas as pd
import re
import string
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

class FakeNewsDetector:
    def wordopt(self, text):
        text = re.sub(r'^Reuters\s+', '', text)
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

    def __init__(self):
        data_true = pd.read_csv('fake_news\datasets\True.csv', encoding='latin1')
        data_fake = pd.read_csv('fake_news\datasets\Fake.csv', encoding='latin1')
        data_fake["class"] = 0
        data_true["class"] = 1
        self.data = pd.concat([data_fake, data_true], axis=0)
        self.data = self.data.drop(['title', 'subject', 'date'], axis=1)
        self.data = self.data.sample(frac=1)
        self.data.reset_index(inplace=True)
        self.data.drop(['index'], axis=1, inplace=True)
        self.data = self.preprocess(self.data)
        x = self.data['text']
        y = self.data['class']
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(x, y, test_size=0.25)
        # print("Hello")
        self.vectorization = joblib.load('fake_news/pred_models/vectorizer.pkl')
        # self.xv_train = self.vectorization.fit_transform(self.x_train)
        self.LR = joblib.load('fake_news/pred_models/logistic_regression.pkl')
        self.DT = joblib.load('fake_news/pred_models/decision_tree.pkl')
        self.RF = joblib.load('fake_news/pred_models/random_forest.pkl')

    def output(self, n):
        if n == 0:
            return "Fake News"
        elif n == 1:
            return "Real News"

    def preprocess(self, df):
        df['text'] = df['text'].astype(str)
        df['text'] = df['text'].apply(self.wordopt)
        return df

    def predict(self, text):
        boolean_flag = False
        preprocessed_text = self.preprocess(pd.DataFrame({'text': [text]}))
        new_text = preprocessed_text['text']
        new_v_text = self.vectorization.transform(new_text)
        pred_LR = self.LR.predict(new_v_text)
        pred_DT = self.DT.predict(new_v_text)
        pred_RF = self.RF.predict(new_v_text)
        self.predictions = [pred_LR,pred_DT,pred_RF]
        self.count = sum(self.predictions)
        pred_prob_LR = self.LR.predict_proba(new_v_text)
        pred_prob_DT = self.DT.predict_proba(new_v_text)
        pred_prob_RF = self.LR.predict_proba(new_v_text)
        probabilities = np.mean([pred_prob_LR,pred_prob_DT,pred_prob_RF], axis = 0)

        accuracy_score = [round(max(prob), 3) for prob in probabilities.tolist()]
        if self.count >= 2:
            boolean_flag = True
        else:
            boolean_flag = False
        # return boolean_flag
        return {
        'label': boolean_flag,
        # 'label_name': label_name,
        'probabilities': probabilities,
        'accuracy_score': accuracy_score
        }