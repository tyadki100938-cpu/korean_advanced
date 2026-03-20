import smtplib
import os
import random
from google import genai # import文が変わります
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone

# --- YouTube動画取得関数 ---
def get_youtube_videos(query, max_results=3):
    api_key = os.getenv('YOUTUBE_API_KEY') # GitHub Secretsに登録してください
    if not api_key:
        return "（YouTube APIキーが設定されていません）"

    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # 過去24時間以内の動画を取得
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        
        request = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            publishedAfter=yesterday.isoformat(),
            maxResults=max_results,
            order='relevance'
        )
        res = request.execute()
        
        videos = []
        for item in res.get('items', []):
            title = item['snippet']['title']
            v_id = item['id']['videoId']
            videos.append(f"・{title}\n  https://www.youtube.com/watch?v={v_id}")
        
        if not videos:
            return "本日の新しい動画は見つかりませんでした。"
            
        return "\n".join(videos)
    except Exception as e:
        return f"動画の取得中にエラーが発生しました: {e}"

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
    msg['Subject'] = "【毎日配信】韓国語能力試験対策コンテンツ"

    # 1. 従来の学習コンテンツを生成
    study_content = generate_study_material()

    # 2. YouTubeから関連動画（例：韓国語学習）を取得
    # クエリは自由に変更してください
    video_content = get_youtube_videos("韓国語学習", max_results=3)

    # 3. 本文を結合
    full_body = f"""
    {study_content}

    --------------------------------------------------
    【本日の関連動画】
    {video_content}
    --------------------------------------------------
    """

    msg.attach(MIMEText(full_body, 'plain'))        

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
        f.write(full_body)

if __name__ == "__main__":
    send_mail()