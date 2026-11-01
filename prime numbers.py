import os
import sys
import threading
import random
import time
import gradio as gr

# 2億桁までロックを解除
sys.set_int_max_str_digits(200000000)

PROGRESS_FILE = "progress.txt"

def log_progress(message):
    """進捗をファイルに書き込む（これで再起動されても状態が残る）"""
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        f.write(message)

def is_prime_huge_async(n, k=5):
    """バックグラウンドで走る素数判定（進捗ログ付き）"""
    try:
        log_progress("【計算開始】5272万桁のメモリ領域を確保中...")
        if n <= 1:
            log_progress("結果: 素数ではない (1以下)")
            return
        if n in (2, 3, 5, 7):
            log_progress("結果: 素数")
            return
        if n % 2 == 0 or n % 3 == 0 or n % 5 == 0:
            log_progress("結果: 合成数 (2,3,5のいずれかの倍数)")
            return

        d = n - 1
        s = 0
        while d % 2 == 0:
            d //= 2
            s += 1

        for i in range(k):
            log_progress(f"【計算中】ミラー・ラビンテストを実行中... ({i+1}/{k} 回目)")
            a = random.randint(2, n - 2) if n > 4 else 2
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            composite = True
            for _ in range(s - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    composite = False
                    break
            if composite:
                log_progress("結果: 判定完了 🔴【合成数（素数ではありません）】")
                return

        log_progress("結果: 判定完了 🟢【おそらく素数（確率99.9%以上）】")
    except Exception as e:
        log_progress(f"エラーが発生しました: {str(e)}")

def start_calculation():
    """Web画面のボタンが押された時のトリガー"""
    # 2**175163803 - 1 の巨大数をセット
    p = 175163803
    
    # 計算スレッドを完全に裏に切り離す（これでWeb画面のタイムアウトを絶対防ぐ）
    t = threading.Thread(target=lambda: is_prime_huge_async(2**p - 1, k=5))
    t.daemon = True
    t.start()
    return "バックグラウンドで1億桁クラスの計算をスタートしました。下の『進捗を確認』ボタンを数分おきに押してください。"

def check_progress():
    """現在の計算状況をファイルから読み込んで画面に返す"""
    if not os.path.exists(PROGRESS_FILE):
        return "まだ計算は始まっていません。"
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        return f.read()

# --- GradioによるWeb画面の構築 ---
with gr.Blocks() as demo:
    gr.Markdown("# 🌌 究極の超巨大数・素数判定システム on Spaces")
    gr.Markdown("2の175,163,803乗 - 1（約5,272万桁）の判定をHugging Faceの裏サーバーで実行します。")
    
    with gr.Row():
        start_btn = gr.Button("🚀 計算をバックグラウンドで開始", variant="primary")
        refresh_btn = gr.Button("🔄 進捗・結果を更新確認")
        
    status_output = gr.Textbox(label="操作ステータス", value="準備完了")
    progress_output = gr.Textbox(label="現在の計算状況 / 最終結果", value="未開始", lines=5)

    # ボタンの動作紐付け
    start_btn.click(fn=start_calculation, outputs=status_output)
    refresh_btn.click(fn=check_progress, outputs=progress_output)

demo.launch()
