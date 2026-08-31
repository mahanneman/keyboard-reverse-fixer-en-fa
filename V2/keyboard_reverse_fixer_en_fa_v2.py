import tkinter as tk
from tkinter import ttk, scrolledtext
from itertools import combinations
import webbrowser  # برای باز کردن لینک

class SmartKeyboardCorrector:
    def __init__(self, root):
        self.root = root
        root.title("تصحیح‌کننده‌ی کیبورد فارسی")
        root.geometry("900x800")
        root.configure(bg='#1e1e1e')

        # ======== استایل ========
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#1e1e1e', foreground='white', font=('Segoe UI', 10))
        style.configure('TButton', background='#333333', foreground='white', borderwidth=1, padding=6)
        style.map('TButton', background=[('active', '#555555')])

        # ======== عنوان ========
        title = ttk.Label(root, text=" انگلیسی اشتباه را وارد کنید - گزینه‌ها به صورت زنده نمایش داده می‌شوند",
                          font=('Segoe UI', 12, 'bold'))
        title.pack(pady=(10, 0))

        # ======== زیرنویس با لینک گیت‌هاب ========
        footer_frame = tk.Frame(root, bg='#1e1e1e')
        footer_frame.pack(pady=(2, 10))

        footer_label = tk.Label(footer_frame, 
                                text="تهیه شده توسط MA.AD.GH",
                                bg='#1e1e1e',
                                fg='#aaaaaa',
                                font=('Segoe UI', 9))
        footer_label.pack(side=tk.LEFT)

        # لینک گیت‌هاب (کلیک‌شدنی)
        link_label = tk.Label(footer_frame,
                              text="https://github.com/mahanneman",
                              bg='#1e1e1e',
                              fg='#4a9eff',
                              font=('Segoe UI', 9, 'underline'),
                              cursor='hand2')
        link_label.pack(side=tk.LEFT)
        link_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/mahanneman"))

        # ======== جعبه‌ی ورودی ========
        self.input_text = scrolledtext.ScrolledText(
            root, height=5, bg='#2d2d2d', fg='white',
            insertbackground='white', font=('Tahoma', 11), wrap=tk.WORD
        )
        self.input_text.pack(padx=20, pady=10, fill=tk.X)

        # ======== فعال‌سازی Ctrl+A ========
        self.input_text.bind('<Control-a>', lambda e: self.input_text.event_generate("<<SelectAll>>"))
        self.input_text.bind('<Control-A>', lambda e: self.input_text.event_generate("<<SelectAll>>"))

        # ======== منوی راست‌کلیک عمومی برای کل پنجره ========
        self.root_menu = tk.Menu(root, tearoff=0, bg='#2d2d2d', fg='white')
        self.root_menu.add_command(label="برش", command=self.cut_text)
        self.root_menu.add_command(label="کپی", command=self.copy_text)
        self.root_menu.add_command(label="پیست", command=self.paste_text)
        self.root_menu.add_command(label="حذف", command=self.clear_text)
        self.root_menu.add_separator()
        self.root_menu.add_command(label="انتخاب همه", command=self.select_all_text)
        self.root.bind("<Button-3>", self.show_root_menu)

        # ======== برچسب وضعیت ========
        self.status_label = ttk.Label(root, text="", foreground='lightgreen')
        self.status_label.pack(pady=5)

        # ======== بخش خروجی با اسکرول ========
        output_container = tk.Frame(root, bg='#1e1e1e')
        output_container.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(output_container, bg='#1e1e1e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(output_container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.output_frame = tk.Frame(self.canvas, bg='#1e1e1e')
        self.canvas.create_window((0, 0), window=self.output_frame, anchor="nw")

        self.output_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=e.width))

        # اسکرول با ماوس
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        # ======== ۱. تعریف جابه‌جایی‌های انگلیسی (۷ مورد شایع) ========
        english_swaps = [
            ("انگلیسی-QWERTY→AZERTY", {'a':'q', 'q':'a', 'z':'w', 'w':'z', 'm':';', ';':'m'}),
            ("انگلیسی-QWERTY→DVORAK", {
                'q':"'", 'w':',', 'e':'.', 'r':'p', 't':'y', 'y':'f', 'u':'g', 'i':'c', 'o':'r', 'p':'l',
                'a':'a', 's':'o', 'd':'e', 'f':'u', 'g':'i', 'h':'d', 'j':'h', 'k':'t', 'l':'n', ';':'s',
                'z':';', 'x':'q', 'c':'j', 'v':'k', 'b':'x', 'n':'b', 'm':'m'
            }),
            ("انگلیسی-QWERTY→COLEMAK", {
                'q':'q', 'w':'w', 'e':'f', 'r':'p', 't':'g', 'y':'j', 'u':'l', 'i':'u', 'o':'y', 'p':';',
                'a':'a', 's':'r', 'd':'s', 'f':'t', 'g':'d', 'h':'h', 'j':'n', 'k':'e', 'l':'i', ';':'o',
                'z':'z', 'x':'x', 'c':'c', 'v':'v', 'b':'b', 'n':'k', 'm':'m'
            }),
            ("انگلیسی-شیفت‌خورده (چپ→راست)", {
                'q':'w','w':'e','e':'r','r':'t','t':'y','y':'u','u':'i','i':'o','o':'p','p':'[',
                'a':'s','s':'d','d':'f','f':'g','g':'h','h':'j','j':'k','k':'l','l':';',';':"'",
                'z':'x','x':'c','c':'v','v':'b','b':'n','n':'m','m':',',',':'.'
            }),
            ("انگلیسی-شیفت‌خورده (راست→چپ)", {
                'w':'q','e':'w','r':'e','t':'r','y':'t','u':'y','i':'u','o':'i','p':'o','[':'p',
                's':'a','d':'s','f':'d','g':'f','h':'g','j':'h','k':'j','l':'k',';':'l',"'":';',
                'x':'z','c':'x','v':'c','b':'v','n':'b','m':'n',',':'m','.':','
            }),
            ("انگلیسی-کیبورد عددی (اشتباه)", {
                '1':'2','2':'3','3':'4','4':'5','5':'6','6':'7','7':'8','8':'9','9':'0','0':'-'
            }),
            ("انگلیسی-CapsLock معکوس", {
                'a':'A','b':'B','c':'C','d':'D','e':'E','f':'F','g':'G','h':'H','i':'I','j':'J',
                'k':'K','l':'L','m':'M','n':'N','o':'O','p':'P','q':'Q','r':'R','s':'S','t':'T',
                'u':'U','v':'V','w':'W','x':'X','y':'Y','z':'Z'
            })
        ]

        # ======== ۲. تعریف جابه‌جایی‌های فارسی (۲۵ مورد پرکاربرد) ========
        persian_swaps = [
            ("فارسی-پ↔ب", {';':'ب', 'f':'پ'}),
            ("فارسی-ژ↔ف", {'t':'ژ', 'Z':'ف'}),
            ("فارسی-گ↔ک", {'\\':'ک', "'":'گ'}),
            ("فارسی-چ↔ج", {']':'ج', '[':'چ'}),
            ("فارسی-ش↔س", {'a':'س', 's':'ش'}),
            ("فارسی-ه↔ا", {'i':'ا', 'h':'ه'}),
            ("فارسی-ت↔ن", {'j':'ن', 'k':'ت'}),
            ("فارسی-م↔ل", {'l':'ل', 'g':'م'}),
            ("فارسی-ر↔ز", {'v':'ز', 'c':'ر'}),
            ("فارسی-د↔ذ", {'n':'ذ', 'b':'د'}),
            ("فارسی-و↔.", {',':'.', '.':'و'}),
            ("فارسی-ع↔غ", {'u':'غ', 'y':'ع'}),
            ("فارسی-خ↔ح", {'o':'ح', 'p':'خ'}),
            ("فارسی-ث↔ص", {'e':'ص', 'w':'ث'}),
            ("فارسی-ض↔ق", {'q':'ق', 'r':'ض'}),
            ("فارسی-ی↔ئ", {'d':'ئ', 'm':'ی'}),
            ("فارسی-ک↔گ (ویندوز)", {"'":'گ', '\\':'ک'}),
            ("فارسی-ژ (لینوکس)", {'z':'ژ'}),
            ("فارسی-پ (لینوکس)", {'p':'پ'}),
            ("فارسی-چ (لینوکس)", {'c':'چ'}),
            ("فارسی-گ (لینوکس)", {'g':'گ'}),
            ("فارسی-ی (لینوکس)", {'y':'ی'}),
            ("فارسی-ک (لینوکس)", {'k':'ک'}),
            ("فارسی-ج (لینوکس)", {'j':'ج'}),
            ("فارسی-ح (لینوکس)", {'h':'ح'})
        ]

        # ======== ۳. ترکیب هوشمندانه برای رسیدن به ۵۰ گزینه ========
        base = self._make_base_map()
        self.all_options = []
        
        # ۳-۱. استاندارد
        self.all_options.append(("استاندارد (ویندوز)", base))
        
        # ۳-۲. استاندارد لینوکس
        linux_base = base.copy()
        linux_base.update({'z':'ژ', 'p':'پ', 'c':'چ', 'g':'گ', 'y':'ی', 'k':'ک', 'j':'ج', 'h':'ح'})
        self.all_options.append(("استاندارد (لینوکس)", linux_base))
        
        # ۳-۳. تک جابه‌جایی‌های فارسی
        for name, swap in persian_swaps:
            mp = base.copy()
            mp.update(swap)
            self.all_options.append((name, mp))
        
        # ۳-۴. تک جابه‌جایی‌های انگلیسی
        for name, swap in english_swaps:
            mp = base.copy()
            mp.update(swap)
            self.all_options.append((name, mp))
        
        # ۳-۵. ترکیب‌های دوگانه
        persian_indices = list(range(2, 2+len(persian_swaps)))
        english_indices = list(range(2+len(persian_swaps), 2+len(persian_swaps)+len(english_swaps)))
        
        combos = []
        for pi in persian_indices[:10]:
            for ei in english_indices[:5]:
                name1 = self.all_options[pi][0]
                name2 = self.all_options[ei][0]
                mp = self.all_options[pi][1].copy()
                mp.update(self.all_options[ei][1])
                combos.append((f"{name1} + {name2}", mp))
        
        for i in range(min(5, len(persian_indices))):
            for j in range(i+1, min(i+3, len(persian_indices))):
                if i != j:
                    name1 = self.all_options[persian_indices[i]][0]
                    name2 = self.all_options[persian_indices[j]][0]
                    mp = self.all_options[persian_indices[i]][1].copy()
                    mp.update(self.all_options[persian_indices[j]][1])
                    combos.append((f"{name1} + {name2}", mp))
        
        needed = 50 - len(self.all_options)
        for name, mp in combos[:needed]:
            self.all_options.append((name, mp))

        # ======== ۴. متغیرهای پین ========
        self.pinned = [False] * len(self.all_options)

        # ======== ۵. اتصال رویدادها ========
        self.input_text.bind('<KeyRelease>', self.on_text_change)
        self.input_text.bind('<ButtonRelease-1>', self.on_text_change)
        self.input_text.bind('<<Paste>>', self.on_text_change)
        self.input_text.bind('<<Cut>>', self.on_text_change)
        self.input_text.bind('<Delete>', self.on_text_change)
        self.input_text.bind('<BackSpace>', self.on_text_change)

        self.on_text_change(None)

    # ---------- توابع منوی عمومی ----------
    def cut_text(self):
        self.input_text.event_generate("<<Cut>>")
    def copy_text(self):
        self.input_text.event_generate("<<Copy>>")
    def paste_text(self):
        self.input_text.event_generate("<<Paste>>")
    def clear_text(self):
        self.input_text.delete("1.0", tk.END)
    def select_all_text(self):
        self.input_text.event_generate("<<SelectAll>>")

    def show_root_menu(self, event):
        self.root_menu.tk_popup(event.x_root, event.y_root)

    # ---------- توابع کمکی ----------
    def _make_base_map(self):
        return {
            'q': 'ض', 'w': 'ص', 'e': 'ث', 'r': 'ق', 't': 'ف', 'y': 'غ',
            'u': 'ع', 'i': 'ه', 'o': 'خ', 'p': 'ح', '[': 'ج', ']': 'چ',
            '\\': 'گ',
            'a': 'ش', 's': 'س', 'd': 'ی', 'f': 'ب', 'g': 'ل', 'h': 'ا',
            'j': 'ت', 'k': 'ن', 'l': 'م', ';': 'پ', "'": 'ک',
            'z': 'ظ', 'x': 'ط', 'c': 'ز', 'v': 'ر', 'b': 'ذ', 'n': 'د',
            'm': 'ئ', ',': 'و', '.': '.', '/': '/',
            'Z': 'ژ'
        }

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def convert_text(self, text, mapping):
        res = []
        for ch in text:
            if ch in mapping:
                res.append(mapping[ch])
            elif ch.isalpha() and ch.lower() in mapping:
                res.append(mapping[ch.lower()])
            else:
                res.append(ch)
        return ''.join(res)

    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        preview = text[:40] + ('...' if len(text) > 40 else '')
        self.status_label.config(text=f"✅ کپی شد: {preview}")

    def toggle_pin(self, index):
        self.pinned[index] = not self.pinned[index]
        self.on_text_change(None)

    def on_text_change(self, event):
        for widget in self.output_frame.winfo_children():
            widget.destroy()

        input_data = self.input_text.get("1.0", tk.END).strip()
        if not input_data:
            self.status_label.config(text="⏳ متنی را تایپ کنید تا ۵۰ گزینه نمایش داده شوند.")
            return

        pinned_indices = [i for i in range(len(self.all_options)) if self.pinned[i]]
        unpinned_indices = [i for i in range(len(self.all_options)) if not self.pinned[i]]
        sorted_indices = pinned_indices + unpinned_indices

        for idx in sorted_indices:
            name, mapping = self.all_options[idx]
            result = self.convert_text(input_data, mapping)
            is_pinned = self.pinned[idx]

            frame = tk.Frame(self.output_frame, bg='#2d2d2d', bd=1, relief=tk.RAISED)
            frame.pack(fill=tk.X, pady=4)

            top_row = tk.Frame(frame, bg='#2d2d2d')
            top_row.pack(fill=tk.X, padx=5, pady=(3,0))

            lbl_name = tk.Label(top_row, text=f"{'📌 ' if is_pinned else ''}{name}", 
                               bg='#2d2d2d', fg='#88ff88' if is_pinned else '#aaaaaa',
                               font=('Segoe UI', 9, 'bold'), anchor='w')
            lbl_name.pack(side=tk.LEFT)

            pin_btn = tk.Button(top_row, text="📌" if not is_pinned else "📍", 
                               bg='#444444' if not is_pinned else '#6666ff',
                               fg='white', relief=tk.FLAT, 
                               command=lambda i=idx: self.toggle_pin(i))
            pin_btn.pack(side=tk.RIGHT, padx=2)

            copy_btn = tk.Button(top_row, text="📋 کپی", bg='#444444', fg='white',
                                relief=tk.FLAT, activebackground='#666666',
                                command=lambda t=result: self.copy_to_clipboard(t))
            copy_btn.pack(side=tk.RIGHT, padx=2)

            lbl_text = tk.Label(frame, text=result, bg='#2d2d2d', fg='#ffffff',
                                font=('Tahoma', 12), cursor='hand2',
                                wraplength=750, justify='right', anchor='e')
            lbl_text.pack(anchor='e', padx=8, pady=5, fill=tk.X)
            lbl_text.bind("<Button-1>", lambda e, t=result: self.copy_to_clipboard(t))

            menu = tk.Menu(self.root, tearoff=0, bg='#2d2d2d', fg='white')
            menu.add_command(label="کپی متن", command=lambda t=result: self.copy_to_clipboard(t))
            lbl_text.bind("<Button-3>", lambda e, m=menu: m.tk_popup(e.x_root, e.y_root))

        self.status_label.config(text=f"✅ {len(sorted_indices)} گزینه نمایش داده شد. روی هر کدام کلیک کنید تا کپی شود.")

# ----------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartKeyboardCorrector(root)
    root.mainloop()