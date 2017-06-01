# fb-bot

## Token 設定
將 [fb_setting.py](https://github.com/chairco/fb-bot/blob/master/mybot/fb_setting.py) 裡面的內容改成你的，如下：

**ACCESS_TOKEN** token  (權杖)

**VERIFY_TOKEN** 自己設定，可以隨便打

```python
ACCESS_TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxx"

VERIFY_TOKEN = "1234567890"
```


## 使用 ngrok 建立  https 環境
雖然我是自己用 nginx + Let's Encrypt 建立一個 https 環境，但如果要偷懶也是有的。直接下載 [ngrok](https://ngrok.com/) ，免安裝版本，解壓縮即可使用，這個服務會自動 bind localhost 某個 port 然侯指向一個網址，讓外網的使用者可以連進來。

解壓縮之後再終端機鍵入指令

```cmd
.ngrok http 8000
```

![alt tag](http://i.imgur.com/p9lczTx.jpg)

如果路徑正確，會看到下圖紅色框就是網址，記得選 https

![alt tag](http://i.imgur.com/W1qdiFE.jpg)

接著找到 Webhooks ，然後按編輯 (如果你找不到，第一次在 Messenger 裡面)

![alt tag](http://i.imgur.com/SGYsfvT.jpg)