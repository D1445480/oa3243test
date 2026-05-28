from app import create_app

# 建立 Flask 應用程式實例
app = create_app()

if __name__ == '__main__':
    # 僅在直接執行此檔案時以開發模式啟動伺服器
    app.run(host='0.0.0.0', port=5000)
