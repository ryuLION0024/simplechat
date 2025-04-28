# lambda/index.py
import json
import os
#import boto3
#import re  # 正規表現モジュールをインポート
#from botocore.exceptions import ClientError
import urllib.request  # ★修正: boto3じゃなくurllibを使う

# グローバル変数としてクライアントを初期化（初期値）
bedrock_client = None

# モデルID
MODEL_ID = os.environ.get("MODEL_ID", "us.amazon.nova-lite-v1:0")

# --- Bedrockエンドポイントを組み立てる ---
# ★修正: boto3で呼び出さず、手動でエンドポイント作成
BEDROCK_ENDPOINT = f"https://bedrock-runtime.us-east-1.amazonaws.com/model/{MODEL_ID}/invoke"


def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))

        # --- リクエストボディからメッセージを取得 ---
        body = json.loads(event['body'])
        message = body['message']

        # --- Bedrockに渡すためのシンプルなリクエストペイロード ---
        request_payload = {
            "inputText": message  # ★修正: シンプルに inputText だけ送る
        }

        # --- HTTPリクエストを自分で組み立てる ---
        req = urllib.request.Request(
            BEDROCK_ENDPOINT,
            data=json.dumps(request_payload).encode('utf-8'),  # JSONをバイト列に変換
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST"
        )

        # --- ★ boto3.invoke_model() じゃなく、urllibでリクエスト送信！ ---
        with urllib.request.urlopen(req) as response:
            response_body = json.loads(response.read())

        print("Bedrock response:", json.dumps(response_body))
        
        # 成功レスポンスの返却
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": messages
            })
        }
        
    except Exception as error:
        print("Error:", str(error))
        
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
