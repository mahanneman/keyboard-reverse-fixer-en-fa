import tkinter as tk
from tkinter import ttk, scrolledtext
import webbrowser  # اضافه شده برای باز کردن لینک

class KeyboardCorrectorApp:
    def __init__(self, root):
        self.root = root
        root.title("تصحیح‌کننده‌ی کیبورد فارسی")
        root.geometry("750x700")
        root.configure(bg='#1e1e1e')

        # ---------- استایل ----------
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#1e1e1e', foreground='white', font=('Segoe UI', 10))
        style.configure('TButton', background='#333333', foreground='white', borderwidth=1, padding=6)
        style.map('TButton', background=[('active', '#555555')])

        # ---------- بخش ورودی ----------
        title = ttk.Label(root, text="متن انگلیسیِ اشتباه را وارد کنید و گزینه‌ی صحیح را انتخاب کنید",
                          font=('Segoe UI', 12, 'bold'))
        title.pack(pady=10)

        # جعبه‌ی ورودی با اسکرول
        self.input_text = scrolledtext.ScrolledText(
            root, height=6, bg='#2d2d2d', fg='white',
            insertbackground='white', font=('Tahoma', 11), wrap=tk.WORD
        )
        self.input_text.pack(padx=20, pady=10, fill=tk.X)

        # منوی راست‌کلیک برای ورودی
        self.input_menu = tk.Menu(root, tearoff=0, bg='#2d2d2d', fg='white')
        self.input_menu.add_command(label="برش", command=lambda: self.input_text.event_generate("<<Cut>>"))
        self.input_menu.add_command(label="کپی", command=lambda: self.input_text.event_generate("<<Copy>>"))
        self.input_menu.add_command(label="پیست", command=lambda: self.input_text.event_generate("<<Paste>>"))
        self.input_menu.add_command(label="حذف", command=lambda: self.input_text.event_generate("<<Clear>>"))
        self.input_menu.add_separator()
        self.input_menu.add_command(label="انتخاب همه", command=lambda: self.input_text.event_generate("<<SelectAll>>"))
        self.input_text.bind("<Button-3>", self.show_input_menu)

        # دکمه‌ی تبدیل
        convert_btn = ttk.Button(root, text="تبدیل / نمایش گزینه‌ها", command=self.convert)
        convert_btn.pack(pady=5)

        # برچسب وضعیت
        self.status_label = ttk.Label(root, text="", foreground='lightgreen')
        self.status_label.pack(pady=5)

        # ---------- بخش خروجی با اسکرول ----------
        output_container = tk.Frame(root, bg='#1e1e1e')
        output_container.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        # کانواس و اسکرولبار
        self.canvas = tk.Canvas(output_container, bg='#1e1e1e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(output_container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # فریم داخلی برای گزینه‌ها
        self.output_frame = tk.Frame(self.canvas, bg='#1e1e1e')
        self.canvas.create_window((0, 0), window=self.output_frame, anchor="nw", width=self.canvas.winfo_width())

        # به‌روزرسانی اسکرول هنگام تغییر اندازه
        self.output_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=e.width))

        # اسکرول با ماوس (ویندوز و لینوکس)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)   # برای لینوکس
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        # ---------- نگاشت‌های مختلف ----------
        base_map = {
            'q': 'ض', 'w': 'ص', 'e': 'ث', 'r': 'ق', 't': 'ف', 'y': 'غ',
            'u': 'ع', 'i': 'ه', 'o': 'خ', 'p': 'ح', '[': 'ج', ']': 'چ',
            '\\': 'گ',
            'a': 'ش', 's': 'س', 'd': 'ی', 'f': 'ب', 'g': 'ل', 'h': 'ا',
            'j': 'ت', 'k': 'ن', 'l': 'م', ';': 'پ', "'": 'ک',
            'z': 'ظ', 'x': 'ط', 'c': 'ز', 'v': 'ر', 'b': 'ذ', 'n': 'د',
            'm': 'ئ', ',': 'و', '.': '.', '/': '/',
            'Z': 'ژ'
        }

        opt1 = base_map.copy()
        opt2 = base_map.copy()
        opt2[';'] = 'ب'
        opt2['f'] = 'پ'
        opt3 = base_map.copy()
        opt3['t'] = 'ژ'
        opt3['Z'] = 'ف'
        opt4 = opt3.copy()
        opt4[';'] = 'ب'
        opt4['f'] = 'پ'

        self.maps = {
            "گزینه ۱ (استاندارد)": opt1,
            "گزینه ۲ (پ ↔ ب)": opt2,
            "گزینه ۳ (ژ ↔ ف)": opt3,
            "گزینه ۴ (هر دو)": opt4
        }

        # ---------- فوتر (اضافه شده) ----------
        footer_frame = tk.Frame(root, bg='#1e1e1e')
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        # لینک گیت‌هاب (کلیک‌شدنی)
        link_label = tk.Label(footer_frame,
                              text="https://github.com/mahanneman",
                              bg='#1e1e1e',
                              fg='#4a9eff',
                              font=('Segoe UI', 9, 'underline'),
                              cursor='hand2')
        link_label.pack(side=tk.LEFT, padx=10)
        link_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/mahanneman"))

        # نسخه
        version_label = tk.Label(footer_frame,
                                 text="نسخه ۱.۰",
                                 bg='#1e1e1e',
                                 fg='gray',
                                 font=('Segoe UI', 9))
        version_label.pack(side=tk.RIGHT, padx=10)

    # ---------- توابع کمکی ----------
    def _on_mousewheel(self, event):
        # اسکرول با چرخ ماوس
        if event.num == 4:   # لینوکس بالا
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5: # لینوکس پایین
            self.canvas.yview_scroll(1, "units")
        else:                # ویندوز
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def show_input_menu(self, event):
        self.input_menu.tk_popup(event.x_root, event.y_root)

    def convert_text(self, text, mapping):
        result = []
        for ch in text:
            if ch in mapping:
                result.append(mapping[ch])
            elif ch.isalpha() and ch.lower() in mapping:
                result.append(mapping[ch.lower()])
            else:
                result.append(ch)
        return ''.join(result)

    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        preview = text[:40] + ('...' if len(text) > 40 else '')
        self.status_label.config(text=f"✅ کپی شد: {preview}")

    def convert(self):
        # پاک کردن گزینه‌های قبلی
        for widget in self.output_frame.winfo_children():
            widget.destroy()

        input_data = self.input_text.get("1.0", tk.END).strip()
        if not input_data:
            self.status_label.config(text="⚠️ لطفاً متنی وارد کنید.")
            return

        # ساخت گزینه‌ها
        for name, mapping in self.maps.items():
            result = self.convert_text(input_data, mapping)

            frame = tk.Frame(self.output_frame, bg='#2d2d2d', bd=1, relief=tk.RAISED)
            frame.pack(fill=tk.X, pady=6)

            # عنوان
            lbl_name = tk.Label(frame, text=name, bg='#2d2d2d', fg='#aaaaaa',
                                font=('Segoe UI', 9, 'bold'), anchor='w')
            lbl_name.pack(anchor='w', padx=8, pady=(4, 0))

            # متن خروجی (قابل کلیک)
            lbl_text = tk.Label(frame, text=result, bg='#2d2d2d', fg='#ffffff',
                                font=('Tahoma', 12), cursor='hand2',
                                wraplength=650, justify='right', anchor='e')
            lbl_text.pack(anchor='e', padx=8, pady=5, fill=tk.X)

            # کلیک چپ برای کپی
            lbl_text.bind("<Button-1>", lambda e, t=result: self.copy_to_clipboard(t))

            # منوی راست‌کلیک برای کپی
            menu = tk.Menu(self.root, tearoff=0, bg='#2d2d2d', fg='white')
            menu.add_command(label="کپی متن", command=lambda t=result: self.copy_to_clipboard(t))
            lbl_text.bind("<Button-3>", lambda e, m=menu: m.tk_popup(e.x_root, e.y_root))

            # دکمه‌ی کپی
            copy_btn = tk.Button(frame, text="📋 کپی", bg='#444444', fg='white',
                                 relief=tk.FLAT, activebackground='#666666',
                                 command=lambda t=result: self.copy_to_clipboard(t))
            copy_btn.pack(anchor='e', padx=8, pady=4)

        self.status_label.config(text="👆 روی هر گزینه کلیک کنید یا راست‌کلیک کنید تا کپی شود.")

# ----------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = KeyboardCorrectorApp(root)
    root.mainloop()