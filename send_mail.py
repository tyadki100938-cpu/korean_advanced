import smtplib
import os
import random
from google import genai # import文が変わります
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def generate_korean_advanced_prompt():
    """
    韓国語能力試験対策用の学習コンテンツ生成プロンプトを作成する。
    """

    prompt = f"""
トピックを自由に選んで韓国語を教えて！
""".strip()

    return prompt

def generate_study_material():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    prompt = generate_korean_advanced_prompt()

    # 【重要】 vertexai=False を指定することで、
    # Google AI Studio の API キーモードであることを明示します
    client = genai.Client(
        api_key=api_key,
        vertexai=False 
    )

    # model名はそのままで大丈夫です
    response = client.models.generate_content(
        model="models/gemini-2.5-flash", 
        contents=prompt
    )
    
    return response.text

def send_mail():
    # GitHub Secretsから環境変数を読み込む
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_PASSWORD")
    to_email = os.getenv("GMAIL_USER") # 送信先

    # メールの設定
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to_email
    msg['Subject'] = "ブラックピンクのジスより"

    body = generate_study_material()
    msg.attach(MIMEText(body, 'plain'))

    try:
        # GmailのSMTPサーバーに接続
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")
    
    # 結果をファイルに保存（GitHub ActionsでIssueにするため）
    with open("result.md", "w", encoding="utf-8") as f:
        f.write(body)

if __name__ == "__main__":
    send_mail()