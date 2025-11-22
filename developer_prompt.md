# ChatGPT 用開発プロンプト (developer_prompt.md)

目的:
- 既存 UploaderApp の差分チェックを高速化（FTPS: nlst を最小化）
- Tkinter GUI をブロックしない実装（スレッド + queue）
- プログレスバー（チェック: インジケーター、アップロード: 割合可）を安定実装
- 既存コードを壊さない、既存の設計意図を尊重する

--- 必要な前提情報（既にプロジェクト側が提供済み）
- GUI: Tkinter
- 通信: FTPS（ftplib.FTP_TLS）
- settings.json のキー: host, port, user, password, remote_base, local_base
- local_base = "common", remote_base = "/common"
- 差分対象フォルダ: local_base/img/* の直下 3 フォルダ
- 既存判定: ファイル名 + 拡張子が一致すれば既存（サイズ/mtime は無視）
- 対象ファイル: 画像ファイル (png, jpg, jpeg, gif, webp, bmp)

--- 出力してほしいもの（優先順）
1. `img_uploader.py` に追加する/差し替える安全なコードスニペット:
   - `FTPSClient` クラス: connect(), disconnect(), list_dir(remote_path), upload_file(local_path, remote_path), ensure_dir(remote_path)
   - `DiffChecker` クラス: get_local_dirs(), get_local_files(dir), get_remote_filelist_for_local_dirs(local_dirs), compute_diff()
   - 例外処理とログ出力（logging モジュール使用）
2. `gui.py` に追加する/差し替える安全なコードスニペット:
   - `UploaderWorker(Thread)` 実装（差分チェック + アップロードを行い queue にイベントを送る）
   - Tkinter 側の queue ポーリング処理（root.after ベース）
   - プログレスバー（インジケーター）制御コード
3. 単体テストの簡易例（pytest での接続モックや、ローカル tmp ディレクトリを使った差分ロジックのテスト）

--- 守るべきルール（重要）
- 既存のファイル・変数名をむやみに書き換えないこと（存在しないと想定される場合は明示する）。
- Tkinter の UI 更新はメインスレッドでのみ行う。ワーカーは queue にメッセージを投げる。
- FTPS のリスト取得は**ローカルのディレクトリ単位**で行い、サーバーに対して不要な再帰 nlst を発行しない。
- ネットワーク例外は必ず捕捉して queue 経由で GUI にエラーイベントを投げる。
- 生成コードは Python 3.8 以上で実行できるようにする。
- 生成されたコードに対して、変更箇所や使い方の簡潔な説明コメントを付与すること。

--- 期待されるコードの構成例（擬似コード）
(ここでは実際の実装例を求めます。上記ルールに従った実装を返してください。)

--- 出力形式
- 各ファイルに対する差分パッチではなく、`img_uploader.py` と `gui.py` に直接貼れる完成スニペットを提供してください。
- 重要な変更点はコード中にコメントで説明してください。
- テストや設定方法も短い手順で記載してください。
