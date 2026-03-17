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
    # --- バリエーションの設定 ---
    topics = [
        "社会・経済（少子高齢化、格差社会、ワークライフバランス）",
        "科学・テクノロジー（AI、倫理、デジタル格差）",
        "環境・エネルギー（気候危機、脱プラスチック、持続可能性）",
        "文化・教育（韓流の持続性、多文化社会、早期教育）",
        "政治・法（個人情報保護、デマ・フェイクニュース、市民意識）",
        "心理・健康（メンタルヘルス、幸福の定義、現代病）"
    ]
    
    levels = [
        "高級語彙・慣用句（四字熟語、ことわざ、擬音語・擬態語）",
        "論理的読解（文章の要旨、筆者の態度、論理展開の把握）",
        "記述・作文（TOPIK第54問対策：論理的な意見の展開）"
    ]
    
    styles = [
        "空所補充形式（文脈に合う副詞や接続詞、慣用表現を選ぶ）",
        "書き換え形式（同じ意味をより格式高い表現や簡潔な表現で言い換える）",
        "要約・論述形式（提示された資料を分析し、60〜100字程度でまとめる）",
        "反論・代案提示形式（ある意見に対し、論理的な根拠を挙げて反論する）"
    ]

    # ランダムに組み合わせ
    topic = random.choice(topics)
    level = random.choice(levels)
    style = random.choice(styles)
    importance = random.int(1, 100)

    # --- プロンプトの組み立て ---
    prompt = f"""
あなたは韓国語講師になったブラックピンクのジスです。
学習コンテンツを1つ作成してください。

【設定】
- テーマ: {topic}
- 重点項目: {level}
- 出題形式: {style}
- 重要度: {importance}%

【構成案】
1. **Key Insight (오늘의 핵심 포인트)**: 
   そのテーマでよく使われる上級レベルの重要語彙や四字熟語、表現を2つピックアップしてください。
   単なる意味だけでなく、ニュースや論文でどのように使われるかのニュアンスを韓国語と日本語で解説してください。

2. **Challenge Question (실戦演習)**: 
   設定された形式で1問出題してください。
   （TOPIKの「読み」や「書き」の難易度・トーンを再現し、文末表現は「〜다/ㄴ다」のハンダ体を使用すること）

3. **Deep Analysis (심層分析)**: 
   解答、日本語訳、および解説。
   特に「上級らしい表現の選び方」や「論理の組み立て方」を重点的に説明してください。
   また、関連して覚えておくべき類義語や、反対の立場を述べる際の表現も提示してください。
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
    msg['Subject'] = "韓国語能力試験(TOPIK II) 学習コンテンツ"

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