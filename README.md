# UploaderApp

## 概要
UploaderApp は、ローカルの画像ファイルを FTPS 経由でサーバーにアップロードするための GUI ツールです。
本リポジトリは Tkinter ベースのクライアントと FTPS 通信ロジックを含みます。

## 必要環境
- Python 3.8 以上
- 標準ライブラリ: ftplib, threading, queue, pathlib, json, logging, tkinter
- 画像プレビューや変換が必要なら Pillow を追加: `pip install pillow`

## ファイル構成
```
UploaderApp/
|- app.py
|- gui.py
|- img_uploader.py
|- settings.json
|- README.md
|- logs/
|- common/
   |- img/
      |- dirA/
      |- dirB/
      |- dirC/
```

## セットアップと実行
1. 仮想環境を作成:
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt  # (任意。標準ライブラリのみなら不要)
```

2. `settings.json` を作成 / 更新:
```json
{
  "host": "your-ftps-host",
  "port": 21,
  "user": "username",
  "password": "password",
  "remote_base": "/common",
  "local_base": "common"
}
```
**注意**: 設定ファイルにパスワードを平文で置く場合、リポジトリ管理は避けるか `.gitignore` に追加してください。より安全には、環境変数や別ファイルで上書きする方式を検討してください。

3. アプリを起動:
```bash
python app.py
```

## 使い方（GUI）
- 「チェック」ボタン: ローカル `common/img` の直下にある各ディレクトリを検出し、サーバー上の対応ディレクトリに対して差分チェックを行います。チェック処理中はインジケーターが表示されます。
- 差分結果: 新規ファイルはデフォルトでチェック済み、既存ファイルは未チェックかつファイル名に「(既存)」が表示されます。
- 「アップロード」ボタン: チェックボックスで選択したファイルを FTPS にアップロードします。アップロード中はプログレスが表示されます。
- メインコンソール: チェックしたファイル総数、アップロード対象数、アップロード成功/失敗数を表示します。

## 開発者向け注意点
- Tkinter の UI 更新はメインスレッドで行う。差分チェック／アップロードはワーカースレッドで実行し、`queue.Queue` を経由して UI に結果を送ってください。
- FTPS のファイル一覧はローカルのディレクトリ単位で `nlst()` を 1 回だけ呼ぶように最適化してください（`nlst()` の呼び出し回数を最小化することが改修の主目的です）。

## テスト
基本的にユニットテストで FTPS クライアントと DiffChecker を分離してテストします。ftplib はネットワーク I/O が発生するため、pytest と unittest.mock で接続と nlst の返り値をモックすることを推奨します。

---

© UploaderApp
