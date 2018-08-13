# Sensor_view
## 動作環境
- ### Python3.0以上が動作するPC

## 起動方法(Linux)
### 1. (管理者権限)virtualenv のインストール
```
$ pip3 install virtualenv
```

### 2. Python3仮想環境でpip install
```
$ virtualenv env/python
$ python_env=env/python/bin
$ $python_env/pip install -r requirements.txt
```
**`$python_env`はログオフと同時に消える**

### 3. Webサーバ起動
```
$ $python_env/python app.py
```

### 4. ブラウザから接続
```
http://localhost:5000/
```

### 仮想環境削除
```
$ rm -r env
```