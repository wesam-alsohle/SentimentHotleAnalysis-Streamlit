from flair.models import TextClassifier
from flair.data import Sentence
from textblob import TextBlob
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import text2emotion as te
# from fer import FER
import matplotlib.pyplot as plt
import cv2
import numpy as np

"""
    Argument:
        Single Text(String) 

    Returns:
        Returns emotion(String)
"""

sia = TextClassifier.load('en-sentiment')
# emo_detector = FER(mtcnn=True)

# For Text data
def flair(text):
    text=str(text)
    sentence = Sentence(text)
    sia.predict(sentence)
    score = str(sentence.labels[0])
    startIdx = int(score.rfind("("))
    endIdx = int(score.rfind(")"))
    percentage = float(score[startIdx+1:endIdx])
    if percentage < 0.60:
        return "NEUTRAL"
    elif "POSITIVE" in str(score):
        return "POSITIVE"
    elif "NEGATIVE" in str(score):
        return "NEGATIVE"
    
    
# For Text data
def textBlob(text):
    tb = TextBlob(text)
    polarity = round(tb.polarity, 2)
    if polarity>0:
        return "Positive"
    elif polarity==0:
        return "Neutral"
    else:
        return "Negative"
    
    
# For Text data
def vader(text):
    #analyze the sentiment for the text
    scores = SentimentIntensityAnalyzer().polarity_scores(text)
    if scores['compound'] >= 0.05 :
        return "Positive"
 
    elif scores['compound'] <= - 0.05 :
        return "Negative"
 
    else :
        return "Neutral"
        

# For Text data
def text2emotion(text):
    emotion = dict(te.get_emotion(text))
    emotion = sorted(emotion.items(), key =
             lambda kv:(kv[1], kv[0]), reverse=True)
    emotionStr = list(emotion)[0][0]
    if(list(emotion)[1][1]>=0.5 or list(emotion)[1][1] == list(emotion)[0][1]):
        emotionStr+=" - {}".format(list(emotion)[1][0])
    #print(emotion, emotionStr)
    return emotionStr
