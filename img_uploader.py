# img_uploader.py
import os
from ftplib import FTP_TLS

# -----------------------
# リモートファイルが存在するか確認
# -----------------------
def remote_file_exists(ftps: FTP_TLS, remote_path: str) -> bool:
    """
    指定のリモートファイルが存在するか確認
    """
    directory, filename = os.path.split(remote_path)
    try:
        ftps.cwd(directory)
        files = ftps.nlst()
        return filename in files
    except Exception:
        return False

# -----------------------
# ファイルをアップロード
# -----------------------
def upload_directory(settings: dict, log_callback=None, target_list=None):
    """
    settings: 設定辞書
    log_callback: ログ出力関数
    target_list: [(local_path, remote_path), ...] のリスト
    """
    local_base = settings.get("local_base", "common")
    remote_base = settings.get("remote_base", "/")
    host = settings["host"]
    port = settings.get("port", 21)
    user = settings["user"]
    passwd = settings["password"]

    ftps = FTP_TLS()
    ftps.connect(host, port)
    ftps.login(user, passwd)
    ftps.prot_p()

    for local_file, remote_file in (target_list or []):
        remote_dir = os.path.dirname(remote_file).replace("\\", "/")
        # リモートディレクトリ作成
        try:
            dirs = remote_dir.strip("/").split("/")
            path = ""
            for d in dirs:
                path += "/" + d
                try:
                    ftps.mkd(path)
                    if log_callback:
                        log_callback(f"ディレクトリ作成: {path}")
                except:
                    pass  # 既に存在する場合は無視
        except Exception as e:
            if log_callback:
                log_callback(f"ディレクトリ作成失敗: {e}")

        # ファイルアップロード
        with open(local_file, "rb") as f:
            try:
                ftps.storbinary(f"STOR {remote_file}", f)
                if log_callback:
                    log_callback(f"アップロード: {local_file} -> {remote_file}")
            except Exception as e:
                if log_callback:
                    log_callback(f"アップロード失敗: {local_file} -> {remote_file} ({e})")

    ftps.quit()
