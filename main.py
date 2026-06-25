import datetime
import os
import tkinter as tk
from tkinter import messagebox, ttk


class KakeiboApp:

    def __init__(self, root):
        self.root = root
        self.root.title("金銭管理システム (プロトタイプ)")
        self.root.geometry("600x400")

        self.csv_filename = "kakeibo.csv"

        # 画面コンポーネントの初期化
        self.create_widgets()

        # 起動時に既存のデータを読み込んで一覧に表示
        self.load_data()

    def create_widgets(self):
        """1画面内に「入力エリア」と「一覧表示エリア」を配置"""

        # --- 1. 入力エリア (上部) ---
        input_frame = tk.LabelFrame(self.root, text=" 支出登録 ", padding=10)
        input_frame.pack(fill="x", padx=10, pady=10)

        # 金額
        tk.Label(input_frame, text="金額 (円):").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.amount_entry = tk.Entry(input_frame)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        # カテゴリ
        tk.Label(input_frame, text="カテゴリ:").grid(
            row=0, column=2, sticky="w", padx=5, pady=5
        )
        self.category_entry = tk.Entry(input_frame)
        self.category_entry.grid(row=0, column=3, padx=5, pady=5)

        # 日付 (デフォルトで今日の日付を入力)
        tk.Label(input_frame, text="日付:").grid(
            row=0, column=4, sticky="w", padx=5, pady=5
        )
        self.date_entry = tk.Entry(input_frame)
        self.date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)

        # 登録ボタン
        register_btn = tk.Button(
            input_frame, text="登録", command=self.register_expense, bg="#4CAF50", fg="white"
        )
        register_btn.grid(row=0, column=6, padx=10, pady=5)

        # --- 2. 一覧表示エリア (下部) ---
        list_frame = tk.LabelFrame(self.root, text=" 支出一覧 ", padding=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # テーブル (TreeView) の設定
        columns = ("date", "category", "amount")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")

        # 列見出しの設定
        self.tree.heading("date", text="日付")
        self.tree.heading("category", text="カテゴリ")
        self.tree.heading("amount", text="金額 (円)")

        # 列幅の設定
        self.tree.column("date", width=150, anchor="center")
        self.tree.column("category", width=200, anchor="w")
        self.tree.column("amount", width=150, anchor="e")

        # スクロールバーの追加
        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def register_expense(self):
        """シーケンス図：ボタン押下時の入力チェック、保存、再描画処理"""
        amount_raw = self.amount_entry.get().strip()
        category = self.category_entry.get().strip()
        date_str = self.date_entry.get().strip()

        # 入力チェック (金額が空でないか、数値であるか)
        if not amount_raw:
            messagebox.showerror("入力エラー", "金額を入力してください。")
            return

        try:
            amount = int(amount_raw)
        except ValueError:
            messagebox.showerror(
                "入力エラー", "金額には半角数値を入力してください。"
            )
            return

        if not category:
            messagebox.showerror("入力エラー", "カテゴリを入力してください。")
            return

        # CSVへ保存
        self.save_to_csv(date_str, category, amount)

        # 一覧の更新
        self.load_data()

        # 入力フォームのクリア (日付は残す)
        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        messagebox.showinfo("完了", "支出を登録しました。")

    def save_to_csv(self, date_str, category, amount):
        """データをCSVファイルに追記保存"""
        # ファイルが存在しない場合はヘッダーを書き込む
        file_exists = os.path.exists(self.csv_filename)

        with open(self.csv_filename, mode="a", encoding="utf-8") as f:
            if not file_exists:
                f.write("日付,カテゴリ,金額\n")
            f.write(f"{date_str},{category},{amount}\n")

    def load_data(self):
        """CSVからデータを読み込んでテーブルを再描画"""
        # 既存の一覧をクリア
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not os.path.exists(self.csv_filename):
            return

        # CSVの読み込み（簡易パース）
        with open(self.csv_filename, mode="r", encoding="utf-8") as f:
            lines = f.readlines()
            if len(lines) <= 1:  # ヘッダーのみ、または空の場合
                return

            # 2行目（データ行）からループ処理
            for line in lines[1:]:
                line = line.strip()
                if line:
                    date_str, category, amount = line.split(",")
                    # カンマ区切りの金額表示に整形してテーブルに追加
                    formatted_amount = f"{int(amount):,}"
                    self.tree.insert(
                        "", "end", values=(date_str, category, formatted_amount)
                    )


if __name__ == "__main__":
    root = tk.Tk()
    app = KakeiboApp(root)
    root.mainloop()