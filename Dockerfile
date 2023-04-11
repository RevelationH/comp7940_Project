FROM python

COPY main.py .
COPY requirements.txt .
COPY hlxchatbot-firebase-adminsdk-uyu0n-50811b0183.json .

RUN pip install pip update
RUN pip install -r requirements.txt

ENV openai_api_key="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"
ENV BOT_TOKEN="5695935733:AAGPqTpwImg71fHk7VXBR4E_CtZyW2uUubg"
ENV rapid_api_key="e5c9d442dcmsh673adc11dd9977ep189064jsne34e76385143"
ENV rapid_api_host="google-translate1.p.rapidapi.com"
ENV firebase_api_key="166311192987"
ENV firebase_url="https://hlxchatbot-default-rtdb.firebaseio.com/"
ENV google_translate_url="https://google-translate1.p.rapidapi.com/language/translate/v2/"

CMD ["python", "main.py"]