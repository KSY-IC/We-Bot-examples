
# We-Bot 制御サンプル（Coral TPU Edge） (C) 2020 KSY
KSY社製のWe-Botを制御するサンプルです。

## License
このサンプルはApache 2.0ライセンスで配布します。
Apache 2.0ライセンスの詳細はソースコード内の記述を参照ください。

## ファイル名
- webot_detect.py

## 概要
カメラの画像をCoral TPU EdgeのObject Detectionを用い、人がいる方向に自動で向きます。
このサンプルは以下の事を行います。
- OpenCVを使ってカメラから画像を入力します。
- 入力した画像をTensorFlow Lite APIを使って物体検出を行います。
- 物体検出したら、検出物がカメラの入力画像の中心になるようにモーターの制御を行います。

※本プログラムはCoral TPU EdgeのサンプルをベースにWe-Botの制御を追加しています。


## 実行環境の構築方法
- 以下のページを参考にCoral TPU Edgeの動作環境を構築します。
https://coral.ai/docs/accelerator/get-started/

- 以下のページから、カメラを使う場合のサンプルを取得します。
https://github.com/google-coral/examples-camera

- 以下のコマンドを実行し、サンプルのソースコードをクローンします。
```
git clone https://github.com/google-coral/examples-camera.git --depth 1
```

- 学習モデルをダウンロードします。
```
cd examples-camera
sh download_models.sh
```

- 以下のコマンドを実行し、必要なモジュールをインストールします。
```
cd examples-camera/opencv
sudo install_requirements.sh
```

- webot_detect.pyをexamples-camera/opencvにコピーします。




## 実行方法
実行環境を整えたのちに、以下のコマンドを入力してください。
```
python3 we_bot_pi_demo.py
```

## 停止方法
入力画像が表示されているウィンドウを選び、qキーを押します。



