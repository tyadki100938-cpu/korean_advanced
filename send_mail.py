import smtplib
import os
import random
from google import genai # import文が変わります
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def generate_eiken_pre1_prompt():
    """
    英検準1級対策用の学習コンテンツ生成プロンプトをランダムな組み合わせで作成する。
    戻り値: str (AIへの入力用プロンプト)
    """
    # --- バリエーションの設定 ---
    topics = [
        "社会・経済（少子高齢化、格差社会、労働環境）",
        "科学・テクノロジー（AI、再生可能エネルギー、宇宙開発）",
        "環境・自然（気候変動、生物多様性、リサイクル）",
        "文化・教育（異文化理解、オンライン教育、伝統保存）",
        "ビジネス（リモートワーク、リーダーシップ、マーケティング）",
        "医療・健康（公衆衛生、メンタルヘルス、先端医療）"
    ]
    
    levels = [
        "単語・熟語（パス単レベルの語彙力強化）",
        "長文読解・文脈判断（段落の趣旨や論理展開の把握）",
        "英作文・二次対策（論理的な意見構築と表現力）"
    ]
    
    styles = [
        "語句選択形式（空所に最も適切な語を選ぶ）",
        "パラフレーズ形式（同じ意味になるように言い換える）",
        "要約・記述形式（ポイントを30語程度の英語でまとめる）",
        "論点指摘形式（提示された意見のメリット・デメリットを述べる）"
    ]

    # ランダムに組み合わせて「今日のお題」を決定
    topic = random.choice(topics)
    level = random.choice(levels)
    style = random.choice(styles)

    # --- プロンプトの組み立て ---
    prompt = f"""
あなたは英検準1級対策の専門講師です。
合格に必要な「ハイレベルな語彙」と「論理的思考」を養う最高の学習コンテンツを1つ作成してください。

【設定】
- テーマ: {topic}
- 重点項目: {level}
- 出題形式: {style}

【構成案】
1. **Key Insight**: 
   そのテーマでよく使われる英検準1級レベルの重要語彙やフレーズを2つピックアップし、
   単なる意味だけでなく、文脈での使い方やニュアンスを英語と日本語で解説してください。

2. **Challenge Question**: 
   設定された形式で1問出題してください。
   （長文や選択肢は、実際の試験の難易度・トーンを再現すること）

3. **Deep Analysis**: 
   解答、日本語訳、および解説。
   特に「なぜその語・表現が最適なのか」「正解に至る論理的プロセス」を重点的に説明してください。
   また、関連して覚えておくべき類義語や反意語も提示してください。
""".strip()

    return prompt

def generate_study_material():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    prompt = generate_eiken_pre1_prompt()

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
    msg['Subject'] = "英検準1級 学習コンテンツ"

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