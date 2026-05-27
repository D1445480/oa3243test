import sys
from flask import current_app
from app.models import User

def send_sms(to_phone, message):
    """
    發送簡訊功能。
    如果 config 中有設定 Twilio 密鑰，將會試圖使用 Twilio SDK 發送；
    若無設定，則預設在主控台/伺服器日誌中模擬輸出發送內容。
    """
    account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
    auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
    from_number = current_app.config.get('TWILIO_PHONE_NUMBER')

    if account_sid and auth_token and from_number:
        try:
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                body=message,
                from_=from_number,
                to=to_phone
            )
            print(f"[Twilio SMS] Sent successfully to {to_phone}. SID: {message.sid}", file=sys.stderr)
            return True
        except Exception as e:
            print(f"[Twilio SMS Error] Failed to send to {to_phone}: {str(e)}", file=sys.stderr)
            # 發生錯誤時降級使用 Mock 輸出
            print(f"[SMS Fallback Mock] To: {to_phone} | Msg: {message}", file=sys.stderr)
            return False
    else:
        # Mock 模擬發送輸出到終端機 (標準錯誤或標準輸出)
        print(f"\n[MOCK SMS] =========================================", file=sys.stderr)
        print(f"[MOCK SMS] 傳送至: {to_phone}", file=sys.stderr)
        print(f"[MOCK SMS] 簡訊內容: {message}", file=sys.stderr)
        print(f"[MOCK SMS] =========================================\n", file=sys.stderr)
        return True

def notify_users_of_new_event(event):
    """
    查詢資料庫中所有已訂閱 (receive_sms = True) 且手機欄位有值的使用者，
    批次發送新活動的簡訊通知。
    """
    # 查詢所有訂閱用戶
    subscribers = User.query.filter(
        User.receive_sms == True,
        User.phone != None,
        User.phone != ''
    ).all()

    if not subscribers:
        print(f"[SMS Service] No subscribers to notify for event: {event.title}", file=sys.stderr)
        return 0

    # 格式化活動日期
    date_str = event.event_date.strftime('%Y-%m-%d %H:%M')
    
    # 簡訊主內容範本
    sms_body = f"「校園活動通知」全新活動《{event.title}》已發布！舉辦時間：{date_str}，地點：{event.location}。快登入平台查看詳情吧！"

    success_count = 0
    for user in subscribers:
        print(f"[SMS Service] Triggering SMS for user: {user.username} ({user.phone})", file=sys.stderr)
        if send_sms(user.phone, sms_body):
            success_count += 1

    return success_count
