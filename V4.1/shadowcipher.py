#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShadowCipher v2.0 — آزمایشگاه رمز، استگانوگرافی و کدهای جاسوسی
Python 3 · stdlib only
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import base64, codecs, hashlib, html, urllib.parse
import re, secrets, uuid
from collections import Counter

# ═══════════════════════════════════════════════════════
#  ثابت‌ها
# ═══════════════════════════════════════════════════════
PERSIAN_DIGITS = '۰۱۲۳۴۵۶۷۸۹'
ENGLISH_DIGITS = '0123456789'
LATIN = 'abcdefghijklmnopqrstuvwxyz'

# ═══════════════════════════════════════════════════════
#  توابع کمکی (بدون تغییر منطقی)
# ═══════════════════════════════════════════════════════
def caesar(text, shift, decrypt=False):
    s = -shift if decrypt else shift
    out = []
    for ch in text:
        if 'a' <= ch <= 'z':
            out.append(chr((ord(ch) - 97 + s) % 26 + 97))
        elif 'A' <= ch <= 'Z':
            out.append(chr((ord(ch) - 65 + s) % 26 + 65))
        else:
            out.append(ch)
    return ''.join(out)

def vigenere(text, key, decrypt=False):
    if not key:
        raise ValueError('کلید لازم است')
    key = ''.join(c for c in key.lower() if c in LATIN) or 'a'
    res, ki = [], 0
    for ch in text:
        low = ch.lower()
        if low in LATIN:
            shift = LATIN.index(key[ki % len(key)])
            if decrypt:
                shift = -shift
            new = LATIN[(LATIN.index(low) + shift) % 26]
            res.append(new.upper() if ch.isupper() else new)
            ki += 1
        else:
            res.append(ch)
    return ''.join(res)

def atbash(text):
    res = []
    for ch in text:
        if 'a' <= ch <= 'z':
            res.append(chr(122 - (ord(ch) - 97)))
        elif 'A' <= ch <= 'Z':
            res.append(chr(90 - (ord(ch) - 65)))
        else:
            res.append(ch)
    return ''.join(res)

def rot13(text):
    return codecs.encode(text, 'rot_13')

# ─── استگانوگرافی ───
def extract_first_of_words(t): return ''.join(w[0] for w in t.split() if w)
def extract_last_of_words(t):  return ''.join(w[-1] for w in t.split() if w)
def extract_first_of_lines(t): return ''.join(l.strip()[0] for l in t.splitlines() if l.strip())
def extract_last_of_lines(t):  return ''.join(l.strip()[-1] for l in t.splitlines() if l.strip())

def extract_every_nth_char(t, n=2, start=0):
    n = max(1, int(n)); return t[start::n]

def extract_every_nth_word(t, n=2, start=0):
    words = t.split(); n = max(1, int(n)); return ' '.join(words[start::n])

def extract_odd_positions(t):  return t[1::2]
def extract_even_positions(t): return t[0::2]

def extract_letters_only_nth(t, n=3):
    letters = [c for c in t if c.isalpha()]; n = max(1, int(n))
    return ''.join(letters[::n])

def extract_after_punctuation(t):
    return ''.join(re.findall(r'[.!?,;:]\s*([A-Za-zآ-ی])', t))

def extract_capital_letters(t): return ''.join(c for c in t if c.isupper())
def extract_digits(t): return ''.join(c for c in t if c.isdigit())

def extract_between_brackets(t):
    return ' '.join(x for grp in re.findall(r'\[([^\]]+)\]|\(([^\)]+)\)|\{([^\}]+)\}', t) for x in grp if x)

def extract_quoted(t):
    return ' '.join(x for grp in re.findall(r'"([^"]+)"|«([^»]+)»', t) for x in grp if x)

def extract_acrostic_paragraphs(t):
    paras = re.split(r'\n\s*\n', t)
    return ''.join(p.strip()[0] for p in paras if p.strip())

def extract_skip_first_n_of_line(t, n=1):
    n = max(0, int(n))
    return ''.join(l.strip()[n:n+1] for l in t.splitlines() if len(l.strip()) > n)

def extract_diagonal_simple(t, width=5):
    lines = [l.strip() for l in t.splitlines() if l.strip()]
    if not lines: return ''
    width = max(2, int(width)); res = []
    for i, line in enumerate(lines):
        pos = i % width
        if pos < len(line): res.append(line[pos])
    return ''.join(res)

def extract_reverse_lines_first(t):
    lines = [l.strip() for l in t.splitlines() if l.strip()]
    return ''.join(l[0] for l in reversed(lines) if l)

def extract_word_index_key(t, key):
    if not key.strip():
        raise ValueError('کلید ایندکس لازم است (مثال: 1 3 5 8)')
    indices = [int(x) - 1 for x in re.findall(r'\d+', key)]
    words = t.split(); res = []
    for i in indices:
        if 0 <= i < len(words) and words[i]:
            res.append(words[i][0])
    return ''.join(res)

def extract_line_word_letter(t, key):
    if not key.strip():
        raise ValueError('کلید به صورت خط.کلمه.حرف لازم است')
    lines = t.splitlines(); res = []
    for li, wi, ci in re.findall(r'(\d+)\.(\d+)\.(\d+)', key):
        li, wi, ci = int(li) - 1, int(wi) - 1, int(ci) - 1
        if 0 <= li < len(lines):
            words = lines[li].split()
            if 0 <= wi < len(words) and 0 <= ci < len(words[wi]):
                res.append(words[wi][ci])
    return ''.join(res)

def extract_null_cipher_first(t, n=1):
    words = t.split(); n = max(1, int(n))
    return ''.join(words[i][0] for i in range(0, len(words), n) if words[i])

def extract_vowels(t): return ''.join(c for c in t if c.lower() in 'aeiouآایو')
def extract_consonants(t):
    return ''.join(c for c in t if c.isalpha() and c.lower() not in 'aeiouآایو')

def extract_middle_letter_words(t):
    return ''.join(w[len(w)//2] for w in t.split() if len(w) >= 3)

def extract_by_keyword_positions(t, keyword):
    if not keyword: raise ValueError('کلید لازم است')
    key = keyword.lower(); res = []; ki = 0
    for ch in t:
        if ki >= len(key): break
        if ch.lower() == key[ki]:
            res.append(ch); ki += 1
    return ''.join(res)

def hide_first_letters(secret, cover_words_hint=None):
    secret = re.sub(r'[^a-zA-Zآ-ی]', '', secret)
    if not secret: return 'پیام خالی است'
    samples = ['امروز', 'هوا', 'خوب', 'است', 'و', 'من', 'به', 'خانه', 'می‌روم',
               'دوست', 'گفت', 'که', 'فردا', 'می‌آید', 'با', 'ما', 'بازی',
               'کنیم', 'این', 'کتاب', 'بسیار', 'جالب', 'بود', 'پیشنهاد',
               'می‌کنم', 'آن', 'را', 'بخوانید', 'صبح', 'زود', 'بیدار', 'شدم']
    res = []
    for ch in secret:
        for w in samples:
            if w and w[0].lower() == ch.lower():
                res.append(w); break
        else:
            res.append(ch + 'xx')
    return ' '.join(res)

def hide_every_nth(secret, cover, n=3):
    n = max(2, int(n))
    secret = re.sub(r'\s+', '', secret)
    chars = list(cover); si = 0
    for i in range(0, len(chars), n):
        if si < len(secret) and chars[i].isalpha():
            chars[i] = secret[si]; si += 1
    return ''.join(chars)

# ─── Morse / NATO / Braille / Leet ───
MORSE = {
    'a':'.-','b':'-...','c':'-.-.','d':'-..','e':'.','f':'..-.','g':'--.',
    'h':'....','i':'..','j':'.---','k':'-.-','l':'.-..','m':'--','n':'-.',
    'o':'---','p':'.--.','q':'--.-','r':'.-.','s':'...','t':'-','u':'..-',
    'v':'...-','w':'.--','x':'-..-','y':'-.--','z':'--..',
    '0':'-----','1':'.----','2':'..---','3':'...--','4':'....-',
    '5':'.....','6':'-....','7':'--...','8':'---..','9':'----.',
}
MORSE_R = {v: k for k, v in MORSE.items()}

def morse_enc(t): return ' '.join(MORSE.get(c.lower(), '') for c in t)

def morse_dec(t):
    return ''.join(MORSE_R.get(c, ' ') if c else ' ' for c in t.split())

NATO = dict(zip('abcdefghijklmnopqrstuvwxyz',
    ['Alpha','Bravo','Charlie','Delta','Echo','Foxtrot','Golf','Hotel',
     'India','Juliett','Kilo','Lima','Mike','November','Oscar','Papa',
     'Quebec','Romeo','Sierra','Tango','Uniform','Victor','Whiskey',
     'X-ray','Yankee','Zulu']))

BRAILLE = dict(zip('abcdefghijklmnopqrstuvwxyz',
    '⠁⠃⠉⠙⠑⠋⠛⠓⠊⠚⠅⠇⠍⠝⠕⠏⠟⠗⠎⠞⠥⠧⠺⠭⠽⠵'))
BRAILLE[' '] = ' '

LEET = str.maketrans('aegilos', '4361105')


# ═══════════════════════════════════════════════════════
#  تم رنگی
# ═══════════════════════════════════════════════════════
C = {
    'bg':      '#0a0d16',
    'panel':   '#131824',
    'card':    '#1a2030',
    'card2':   '#1e2536',
    'border':  '#252d42',
    'text':    '#e5e9f2',
    'dim':     '#8a93a8',
    'accent':  '#4d9fff',
    'accent2': '#6fb5ff',
    'green':   '#4ade80',
    'red':     '#f87171',
    'yellow':  '#fbbf24',
    'purple':  '#a78bfa',
}


# ═══════════════════════════════════════════════════════
#  کلاس اصلی
# ═══════════════════════════════════════════════════════
class ShadowCipher(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('ShadowCipher')
        self.configure(bg=C['bg'])
        self.minsize(860, 560)
        self._center_window(980, 680)

        self._setup_style()
        self._build_ui()
        self._set_status('آماده — متنی وارد کنید')

    # ─── وسط‌چین ───
    def _center_window(self, w, h):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = max(20, (sh - h) // 2 - 30)
        self.geometry(f'{w}x{h}+{x}+{y}')

    # ─── استایل ───
    def _setup_style(self):
        s = ttk.Style(self)
        try:
            s.theme_use('clam')
        except Exception:
            pass

        # پایه
        s.configure('.', background=C['bg'], foreground=C['text'],
                    fieldbackground=C['card2'], borderwidth=0,
                    focuscolor='none')

        s.configure('TFrame', background=C['bg'])
        s.configure('Card.TFrame', background=C['panel'])
        s.configure('Card2.TFrame', background=C['card'])

        # برچسب‌ها
        s.configure('TLabel', background=C['bg'], foreground=C['text'],
                    font=('Segoe UI', 10))
        s.configure('Card.TLabel', background=C['panel'], foreground=C['text'],
                    font=('Segoe UI', 9))
        s.configure('CardMuted.TLabel', background=C['panel'],
                    foreground=C['dim'], font=('Segoe UI', 8))
        s.configure('Title.TLabel', background=C['bg'],
                    foreground=C['accent'],
                    font=('Segoe UI', 15, 'bold'))
        s.configure('Subtitle.TLabel', background=C['bg'],
                    foreground=C['dim'], font=('Segoe UI', 9))
        s.configure('Section.TLabel', background=C['bg'],
                    foreground=C['accent'],
                    font=('Segoe UI', 10, 'bold'))
        s.configure('Muted.TLabel', background=C['bg'],
                    foreground=C['dim'], font=('Segoe UI', 9))
        s.configure('Status.TLabel', background=C['bg'],
                    foreground=C['green'], font=('Segoe UI', 9))

        # دکمه‌ها
        s.configure('TButton',
                    background=C['card2'], foreground=C['text'],
                    padding=(12, 7), font=('Segoe UI', 9),
                    borderwidth=0, relief='flat', anchor='center')
        s.map('TButton',
              background=[('active', C['border']),
                          ('pressed', C['accent'])],
              foreground=[('pressed', '#ffffff')])

        s.configure('Accent.TButton',
                    background=C['accent'], foreground='#ffffff',
                    font=('Segoe UI', 9, 'bold'),
                    padding=(14, 7))
        s.map('Accent.TButton',
              background=[('active', C['accent2'])])

        s.configure('Danger.TButton',
                    background='#2a1e28', foreground=C['red'],
                    font=('Segoe UI', 9), padding=(14, 7))
        s.map('Danger.TButton',
              background=[('active', '#3d2a35')])

        # Notebook
        s.configure('TNotebook',
                    background=C['bg'], borderwidth=0,
                    tabmargins=(0, 4, 0, 0))
        s.configure('TNotebook.Tab',
                    background=C['panel'], foreground=C['dim'],
                    padding=(16, 7), font=('Segoe UI', 9, 'bold'),
                    borderwidth=0)
        s.map('TNotebook.Tab',
              background=[('selected', C['card2']),
                          ('active', C['card'])],
              foreground=[('selected', C['accent']),
                          ('active', C['text'])])

        # ورودی‌ها
        s.configure('TEntry',
                    fieldbackground=C['card2'], foreground=C['text'],
                    insertcolor=C['accent'], borderwidth=0,
                    padding=7)
        s.configure('TSpinbox',
                    fieldbackground=C['card2'], foreground=C['text'],
                    borderwidth=0, padding=7)

    # ─── ساخت UI ───
    def _build_ui(self):
        # ═══ هدر ═══
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=20, pady=(14, 8))

        ttk.Label(header, text='◈ ShadowCipher',
                  style='Title.TLabel').pack(side=tk.LEFT)
        ttk.Label(header, text='آزمایشگاه رمز · استگانوگرافی · کد جاسوسی',
                  style='Subtitle.TLabel').pack(side=tk.LEFT, padx=(12, 0), pady=(6, 0))

        # ═══ ورودی ═══
        in_card = tk.Frame(self, bg=C['border'])
        in_card.pack(fill=tk.X, padx=20, pady=(0, 6))

        in_inner = tk.Frame(in_card, bg=C['panel'])
        in_inner.pack(fill=tk.X, padx=1, pady=1)

        lbl_row = tk.Frame(in_inner, bg=C['panel'])
        lbl_row.pack(fill=tk.X, padx=10, pady=(6, 0))
        ttk.Label(lbl_row, text='▸  متن ورودی / متن پوششی',
                  style='CardMuted.TLabel').pack(side=tk.LEFT)

        self.input_box = tk.Text(
            in_inner, height=4, bg=C['card'], fg=C['text'],
            insertbackground=C['accent'], font=('Consolas', 11),
            wrap=tk.WORD, relief=tk.FLAT, borderwidth=0,
            padx=10, pady=8, selectbackground=C['accent'],
            selectforeground='#ffffff', undo=True)
        self.input_box.pack(fill=tk.X, padx=8, pady=(2, 8))

        # ═══ کلید + N ═══
        key_row = ttk.Frame(self)
        key_row.pack(fill=tk.X, padx=20, pady=(0, 8))

        ttk.Label(key_row, text='کلید:',
                  style='Muted.TLabel').pack(side=tk.LEFT)
        self.key_var = tk.StringVar()
        ttk.Entry(key_row, textvariable=self.key_var,
                  width=26, font=('Consolas', 10)
                  ).pack(side=tk.LEFT, padx=(6, 16), ipady=1)

        ttk.Label(key_row, text='N:',
                  style='Muted.TLabel').pack(side=tk.LEFT)
        self.n_var = tk.StringVar(value='2')
        sp = ttk.Spinbox(key_row, from_=1, to=20, width=5,
                         textvariable=self.n_var, font=('Consolas', 10))
        sp.pack(side=tk.LEFT, padx=(6, 0), ipady=1)

        # ═══ تب‌ها ═══
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 8))

        self._tab_stego()
        self._tab_classic()
        self._tab_encode()
        self._tab_special()
        self._tab_analyze()
        self._tab_persian()

        # ═══ خروجی ═══
        out_card = tk.Frame(self, bg=C['border'])
        out_card.pack(fill=tk.X, padx=20, pady=(0, 6))

        out_inner = tk.Frame(out_card, bg=C['panel'])
        out_inner.pack(fill=tk.X, padx=1, pady=1)

        out_lbl = tk.Frame(out_inner, bg=C['panel'])
        out_lbl.pack(fill=tk.X, padx=10, pady=(6, 0))
        ttk.Label(out_lbl, text='▸  نتیجه',
                  style='CardMuted.TLabel').pack(side=tk.LEFT)

        self.out_box = tk.Text(
            out_inner, height=6, bg=C['card'], fg=C['green'],
            insertbackground=C['accent'], font=('Consolas', 11),
            wrap=tk.WORD, relief=tk.FLAT, borderwidth=0,
            padx=10, pady=8)
        self.out_box.pack(fill=tk.X, padx=8, pady=(2, 8))

        # ═══ نوار پایین ═══
        bottom = ttk.Frame(self)
        bottom.pack(fill=tk.X, padx=20, pady=(0, 12))

        self.status_lbl = ttk.Label(bottom, text='', style='Status.TLabel')
        self.status_lbl.pack(side=tk.LEFT)

        ttk.Button(bottom, text='✕  پاک کردن',
                   style='Danger.TButton',
                   command=self._clear).pack(side=tk.RIGHT, padx=(6, 0))
        ttk.Button(bottom, text='⎘  کپی نتیجه',
                   style='Accent.TButton',
                   command=self._copy_out).pack(side=tk.RIGHT)

    # ══════════════════════════════════════════════
    #  تب استگانوگرافی
    # ══════════════════════════════════════════════
    def _tab_stego(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text='  🕵  استگانوگرافی  ')

        # توضیح
        info = ttk.Label(
            tab,
            text='الگوهای استخراج و مخفی‌سازی شبیه فیلم‌ها: Acrostic، Book Cipher، Null Cipher و ...',
            style='Subtitle.TLabel')
        info.pack(anchor='w', padx=12, pady=(10, 6))

        # کانتینر اسکرول
        wrap = ttk.Frame(tab)
        wrap.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        canvas = tk.Canvas(wrap, bg=C['bg'], highlightthickness=0, bd=0)
        scroll = ttk.Scrollbar(wrap, orient='vertical', command=canvas.yview)
        inner = tk.Frame(canvas, bg=C['bg'])

        inner_id = canvas.create_window((0, 0), window=inner, anchor='nw')
        canvas.configure(yscrollcommand=scroll.set)

        inner.bind('<Configure>',
                   lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>',
                    lambda e: canvas.itemconfig(inner_id, width=e.width))

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # اسکرول با ماوس
        for w in (canvas, inner):
            w.bind('<MouseWheel>',
                   lambda e: canvas.yview_scroll(int(-e.delta / 120), 'units'))
            w.bind('<Button-4>',
                   lambda e: canvas.yview_scroll(-1, 'units'))
            w.bind('<Button-5>',
                   lambda e: canvas.yview_scroll(1, 'units'))

        # ─── بخش ۱: استخراج ───
        self._section(inner, '◆  استخراج پیام مخفی')

        extract_ops = [
            ('حرف اول کلمات',    lambda: self._run(extract_first_of_words)),
            ('حرف آخر کلمات',    lambda: self._run(extract_last_of_words)),
            ('حرف اول خطوط',     lambda: self._run(extract_first_of_lines)),
            ('حرف آخر خطوط',     lambda: self._run(extract_last_of_lines)),
            ('اول هر پاراگراف',  lambda: self._run(extract_acrostic_paragraphs)),
            ('هر N کاراکتر',     lambda: self._run(lambda t: extract_every_nth_char(t, self._get_n()))),
            ('هر N کلمه',        lambda: self._run(lambda t: extract_every_nth_word(t, self._get_n()))),
            ('موقعیت فرد',       lambda: self._run(extract_odd_positions)),
            ('موقعیت زوج',       lambda: self._run(extract_even_positions)),
            ('حروف بزرگ',        lambda: self._run(extract_capital_letters)),
            ('فقط اعداد',        lambda: self._run(extract_digits)),
            ('حروف صدادار',      lambda: self._run(extract_vowels)),
            ('حروف بی‌صدا',      lambda: self._run(extract_consonants)),
            ('حرف وسط کلمات',    lambda: self._run(extract_middle_letter_words)),
            ('بعد از علائم',     lambda: self._run(extract_after_punctuation)),
            ('داخل براکت',       lambda: self._run(extract_between_brackets)),
            ('داخل گیومه',       lambda: self._run(extract_quoted)),
            ('Null (اول N کلمه)', lambda: self._run(lambda t: extract_null_cipher_first(t, self._get_n()))),
            ('پرش N از خطوط',    lambda: self._run(lambda t: extract_skip_first_n_of_line(t, self._get_n()))),
            ('خواندن مورب',      lambda: self._run(lambda t: extract_diagonal_simple(t, self._get_n()))),
            ('معکوس خطوط → اول', lambda: self._run(extract_reverse_lines_first)),
            ('ایندکس کلمه (۱ ۳ ۵)', lambda: self._run(lambda t: extract_word_index_key(t, self.key_var.get()))),
            ('کتاب‌رمز (خط.کلمه.حرف)', lambda: self._run(lambda t: extract_line_word_letter(t, self.key_var.get()))),
            ('تطبیق با کلید',    lambda: self._run(lambda t: extract_by_keyword_positions(t, self.key_var.get()))),
            ('حروف هر N',        lambda: self._run(lambda t: extract_letters_only_nth(t, self._get_n()))),
        ]
        self._grid_buttons(inner, extract_ops)

        # ─── بخش ۲: مخفی‌سازی ───
        self._section(inner, '◆  مخفی‌سازی پیام')

        hide_ops = [
            ('ساخت با حرف اول', lambda: self._run(hide_first_letters)),
            ('پنهان در متن (N)', lambda: self._run(lambda t: hide_every_nth(self.key_var.get() or 'SECRET', t, self._get_n()))),
        ]
        self._grid_buttons(inner, hide_ops)

        # راهنما
        help_frame = tk.Frame(inner, bg=C['panel'])
        help_frame.pack(fill=tk.X, padx=10, pady=(16, 12))

        tk.Label(help_frame, text='◈ راهنما',
                 bg=C['panel'], fg=C['accent'],
                 font=('Segoe UI', 10, 'bold'),
                 anchor='w').pack(fill=tk.X, padx=12, pady=(8, 4))

        help_text = (
            'Acrostic — حرف اول کلمات/خطوط، پیام اصلی را می‌سازد (شعرهای مخفی)\n'
            'Book Cipher — کلید: "خط.کلمه.حرف" مثل 2.1.3  5.4.1\n'
            'Null Cipher — فقط بعضی کلمات مهم‌اند، بقیه برای گمراهی\n'
            'مقدار N را از اسپینر بالا تنظیم کنید · کلید را در کادر «کلید» بنویسید'
        )
        tk.Label(help_frame, text=help_text, bg=C['panel'], fg=C['dim'],
                 font=('Segoe UI', 9), justify=tk.LEFT,
                 anchor='w').pack(fill=tk.X, padx=12, pady=(0, 10))

    # ══════════════════════════════════════════════
    #  تب رمز کلاسیک
    # ══════════════════════════════════════════════
    def _tab_classic(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text='  ⚔  رمز کلاسیک  ')

        ttk.Label(tab, text='الگوریتم‌های رمزنگاری تاریخی',
                  style='Subtitle.TLabel').pack(anchor='w', padx=12, pady=(10, 8))

        ops = [
            ('سزار +۳',               lambda: self._run(lambda t: caesar(t, 3))),
            ('سزار −۳ (رمزگشایی)',    lambda: self._run(lambda t: caesar(t, 3, True))),
            ('سزار با N (رمزگذاری)',  lambda: self._run(lambda t: caesar(t, self._get_n()))),
            ('سزار با N (رمزگشایی)',  lambda: self._run(lambda t: caesar(t, self._get_n(), True))),
            ('ویژنر (کلید)',          lambda: self._run(lambda t: vigenere(t, self.key_var.get()))),
            ('ویژنر (رمزگشایی)',      lambda: self._run(lambda t: vigenere(t, self.key_var.get(), True))),
            ('Atbash',               lambda: self._run(atbash)),
            ('ROT13',                lambda: self._run(rot13)),
            ('معکوس کل متن',         lambda: self._run(lambda t: t[::-1])),
            ('معکوس کلمات',          lambda: self._run(lambda t: ' '.join(t.split()[::-1]))),
            ('معکوس خطوط',           lambda: self._run(lambda t: '\n'.join(t.splitlines()[::-1]))),
            ('UPPERCASE',            lambda: self._run(str.upper)),
            ('lowercase',            lambda: self._run(str.lower)),
            ('Title Case',           lambda: self._run(str.title)),
            ('Swap Case',            lambda: self._run(str.swapcase)),
        ]
        self._grid_buttons(tab, ops)

    # ══════════════════════════════════════════════
    #  تب کدگذاری
    # ══════════════════════════════════════════════
    def _tab_encode(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text='  🔐  کدگذاری  ')

        ttk.Label(tab, text='تبدیل متن به کد و بالعکس',
                  style='Subtitle.TLabel').pack(anchor='w', padx=12, pady=(10, 8))

        ops = [
            ('Base64 → کد',    lambda: self._run(lambda t: base64.b64encode(t.encode()).decode())),
            ('Base64 ← متن',   lambda: self._run(lambda t: base64.b64decode(t.encode()).decode('utf-8', 'replace'))),
            ('Hex با فاصله',   lambda: self._run(lambda t: ' '.join(f'{ord(c):02x}' for c in t))),
            ('Hex ← متن',      lambda: self._run(lambda t: ''.join(chr(int(h, 16)) for h in t.split()))),
            ('Binary 8-bit',   lambda: self._run(lambda t: ' '.join(f'{ord(c):08b}' for c in t))),
            ('Binary ← متن',   lambda: self._run(lambda t: ''.join(chr(int(b, 2)) for b in t.split()))),
            ('URL Encode',     lambda: self._run(urllib.parse.quote)),
            ('URL Decode',     lambda: self._run(urllib.parse.unquote)),
            ('HTML Escape',    lambda: self._run(html.escape)),
            ('HTML Unescape',  lambda: self._run(html.unescape)),
            ('Unicode Escape', lambda: self._run(lambda t: t.encode('unicode_escape').decode())),
            ('MD5',            lambda: self._run(lambda t: hashlib.md5(t.encode()).hexdigest())),
            ('SHA-256',        lambda: self._run(lambda t: hashlib.sha256(t.encode()).hexdigest())),
            ('SHA-512',        lambda: self._run(lambda t: hashlib.sha512(t.encode()).hexdigest())),
            ('CRC32',          lambda: self._run(lambda t: format(__import__('binascii').crc32(t.encode()) & 0xffffffff, '08x'))),
            ('JSON Pretty',    lambda: self._run(lambda t: __import__('json').dumps(__import__('json').loads(t), ensure_ascii=False, indent=2))),
            ('حذف فاصله',      lambda: self._run(lambda t: t.replace(' ', ''))),
            ('فقط حروف',       lambda: self._run(lambda t: ''.join(c for c in t if c.isalpha()))),
            ('فقط اعداد',      lambda: self._run(lambda t: ''.join(c for c in t if c.isdigit()))),
            ('Trim',           lambda: self._run(lambda t: t.strip())),
        ]
        self._grid_buttons(tab, ops)

    # ══════════════════════════════════════════════
    #  تب ویژه
    # ══════════════════════════════════════════════
    def _tab_special(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text='  📡  Morse و ویژه  ')

        ttk.Label(tab, text='کدهای ارتباطی و الفبای خاص',
                  style='Subtitle.TLabel').pack(anchor='w', padx=12, pady=(10, 8))

        ops = [
            ('Morse → کد',        lambda: self._run(morse_enc)),
            ('Morse ← کد',        lambda: self._run(morse_dec)),
            ('NATO Phonetic',     lambda: self._run(lambda t: ' '.join(NATO.get(c.lower(), c) for c in t))),
            ('Braille',           lambda: self._run(lambda t: ''.join(BRAILLE.get(c.lower(), c) for c in t))),
            ('Leet Speak',        lambda: self._run(lambda t: t.lower().translate(LEET))),
            ('Strip Vowels',      lambda: self._run(extract_consonants)),
            ('فقط حروف بزرگ',     lambda: self._run(lambda t: ''.join(c for c in t if c.isupper()))),
        ]
        self._grid_buttons(tab, ops)

    # ══════════════════════════════════════════════
    #  تب تحلیل
    # ══════════════════════════════════════════════
    def _tab_analyze(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text='  📊  تحلیل  ')

        ttk.Label(tab, text='آمار و ساختار متن',
                  style='Subtitle.TLabel').pack(anchor='w', padx=12, pady=(10, 8))

        def analysis(t):
            words = re.findall(r'\S+', t)
            lines = t.splitlines()
            letters = [c for c in t if c.isalpha()]
            return (
                f'◆ کاراکتر : {len(t)}\n'
                f'◆ کلمه     : {len(words)}\n'
                f'◆ خط       : {len(lines)}\n'
                f'◆ حروف یکتا : {len(set(c.lower() for c in letters))}\n'
                f'◆ کلمات یکتا: {len(set(words))}\n'
                f'◆ میانگین طول کلمه: {sum(len(w) for w in words)/max(1,len(words)):.2f}\n'
                f'◆ زمان خواندن: {len(words)/200:.1f} دقیقه\n\n'
                f'◆ فرکانس حروف (۳۰ اول):\n'
                + '\n'.join(f'   {c} : {n}'
                            for c, n in Counter(c.lower() for c in letters).most_common(30))
            )

        ops = [
            ('تحلیل کامل',        lambda: self._run(analysis)),
            ('تعداد کاراکتر',     lambda: self._run(lambda t: str(len(t)))),
            ('تعداد کلمات',       lambda: self._run(lambda t: str(len(re.findall(r'\S+', t))))),
            ('تعداد خطوط',        lambda: self._run(lambda t: str(len(t.splitlines())))),
            ('فرکانس حروف',       lambda: self._run(lambda t: '\n'.join(f'{c} : {n}' for c, n in Counter(c for c in t if c.isalpha()).most_common(40)))),
            ('فرکانس کلمات',      lambda: self._run(lambda t: '\n'.join(f'{w} : {n}' for w, n in Counter(re.findall(r'\S+', t)).most_common(30)))),
            ('بلندترین کلمه',     lambda: self._run(lambda t: max(re.findall(r'\S+', t), key=len, default=''))),
            ('کوتاه‌ترین کلمه',    lambda: self._run(lambda t: min(re.findall(r'\S+', t), key=len, default=''))),
        ]
        self._grid_buttons(tab, ops)

    # ══════════════════════════════════════════════
    #  تب فارسی و ابزار
    # ══════════════════════════════════════════════
    def _tab_persian(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text='  🌙  فارسی و ابزار  ')

        ttk.Label(tab, text='استانداردسازی فارسی و ابزارهای عمومی',
                  style='Subtitle.TLabel').pack(anchor='w', padx=12, pady=(10, 8))

        ops = [
            ('اعداد فارسی → انگلیسی', lambda: self._run(lambda t: t.translate(str.maketrans(PERSIAN_DIGITS, ENGLISH_DIGITS)))),
            ('اعداد انگلیسی → فارسی', lambda: self._run(lambda t: t.translate(str.maketrans(ENGLISH_DIGITS, PERSIAN_DIGITS)))),
            ('عربی → فارسی (ی/ک)',    lambda: self._run(lambda t: t.replace('ي', 'ی').replace('ك', 'ک'))),
            ('فارسی → عربی',          lambda: self._run(lambda t: t.replace('ی', 'ي').replace('ک', 'ك'))),
            ('حذف اعراب',             lambda: self._run(lambda t: re.sub(r'[\u064B-\u0652\u0670\u0640]', '', t))),
            ('حذف کشیده',             lambda: self._run(lambda t: t.replace('\u0640', ''))),
            ('استخراج کلمات فارسی',   lambda: self._run(lambda t: ' '.join(re.findall(r'[\u0600-\u06FF]+', t)))),
            ('حذف کلمات انگلیسی',     lambda: self._run(lambda t: re.sub(r'[A-Za-z]+', '', t).strip())),
            ('یکسان‌سازی فاصله',      lambda: self._run(lambda t: re.sub(r'[ \t]+', ' ', t).strip())),
            ('UUID v4',               lambda: self._run(lambda t: str(uuid.uuid4()))),
            ('پسورد تصادفی',          lambda: self._run(lambda t: secrets.token_urlsafe(16))),
            ('Timestamp',             lambda: self._run(lambda t: str(int(__import__('time').time())))),
            ('SHA-256 کوتاه',         lambda: self._run(lambda t: hashlib.sha256(t.encode()).hexdigest()[:16])),
            ('کد یونیکد حروف',        lambda: self._run(lambda t: ' '.join(f'{ord(c):04x}' for c in t))),
            ('تاریخ/ساعت',            lambda: self._run(lambda t: __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'))),
        ]
        self._grid_buttons(tab, ops)

    # ══════════════════════════════════════════════
    #  کمکی‌های UI
    # ══════════════════════════════════════════════
    def _section(self, parent, title):
        row = tk.Frame(parent, bg=C['bg'])
        row.pack(fill=tk.X, padx=8, pady=(8, 4))
        tk.Label(row, text=title, bg=C['bg'], fg=C['accent'],
                 font=('Segoe UI', 10, 'bold'),
                 anchor='w').pack(side=tk.LEFT)
        tk.Frame(row, bg=C['border'], height=1).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0), pady=(8, 0))

    def _grid_buttons(self, parent, ops, cols=3):
        grid = tk.Frame(parent, bg=C['bg'])
        grid.pack(fill=tk.X, padx=6, pady=(2, 4))
        for i, (name, cmd) in enumerate(ops):
            r, c = divmod(i, cols)
            b = ttk.Button(grid, text=name, command=cmd)
            b.grid(row=r, column=c, padx=3, pady=3, sticky='ew')
        for c in range(cols):
            grid.columnconfigure(c, weight=1, uniform='btn')

    # ══════════════════════════════════════════════
    #  منطق اجرا
    # ══════════════════════════════════════════════
    def _get_n(self):
        try:
            return max(1, int(self.n_var.get()))
        except (ValueError, TypeError):
            return 2

    def _run(self, func):
        text = self.input_box.get('1.0', 'end-1c')
        try:
            result = func(text)
            self.out_box.delete('1.0', tk.END)
            self.out_box.insert(tk.END, str(result))
            self._set_status(f'✓ انجام شد  ·  طول نتیجه: {len(str(result))}')
        except Exception as e:
            self.out_box.delete('1.0', tk.END)
            self.out_box.insert(tk.END, f'✕ خطا: {type(e).__name__}\n{str(e)}')
            self._set_status('✕ خطا در اجرا', error=True)

    def _copy_out(self):
        text = self.out_box.get('1.0', 'end-1c')
        self.clipboard_clear()
        self.clipboard_append(text)
        self._set_status('⎘ نتیجه در کلیپ‌بورد کپی شد')

    def _clear(self):
        self.input_box.delete('1.0', tk.END)
        self.out_box.delete('1.0', tk.END)
        self.key_var.set('')
        self.n_var.set('2')
        self._set_status('✕ همه پاک شد')

    def _set_status(self, msg, error=False):
        self.status_lbl.config(
            text=msg,
            foreground=C['red'] if error else C['green'])




# ============================================================================
# Additive usability layer. All original helpers and ShadowCipher methods above
# are intentionally retained. Legacy transforms keep their original semantics.
# ============================================================================
import json
from pathlib import Path
from tkinter import filedialog, messagebox

TRANSLATIONS = {'حرف اول کلمات': 'First letters of words', 'حرف آخر کلمات': 'Last letters of words', 'حرف اول خطوط': 'First letters of lines', 'حرف آخر خطوط': 'Last letters of lines', 'اول هر پاراگراف': 'First character of paragraphs', 'هر N کاراکتر': 'Every Nth character', 'هر N کلمه': 'Every Nth word', 'موقعیت فرد': 'Odd index positions (1, 3, 5...)', 'موقعیت زوج': 'Even index positions (0, 2, 4...)', 'حروف بزرگ': 'Uppercase letters', 'فقط اعداد': 'Digits only', 'حروف صدادار': 'Extract vowels (legacy heuristic)', 'حروف بی\u200cصدا': 'Extract consonants (legacy heuristic)', 'حرف وسط کلمات': 'Middle letters of words', 'بعد از علائم': 'Letters after punctuation', 'داخل براکت': 'Inside brackets', 'داخل گیومه': 'Inside quotation marks', 'Null (اول N کلمه)': 'Null cipher: first letter every N words', 'پرش N از خطوط': 'Character at index N in each line', 'خواندن مورب': 'Diagonal reading', 'معکوس خطوط → اول': 'Reverse lines, extract initials', 'ایندکس کلمه (۱ ۳ ۵)': 'Word index key (1 3 5)', 'کتاب\u200cرمز (خط.کلمه.حرف)': 'Book cipher (line.word.character)', 'تطبیق با کلید': 'Match key as a subsequence', 'حروف هر N': 'Every Nth letter only', 'ساخت با حرف اول': 'Build acrostic cover', 'پنهان در متن (N)': 'Hide key in cover text (N)', 'سزار +۳': 'Caesar +3', 'سزار −۳ (رمزگشایی)': 'Caesar -3 / Decode', 'سزار با N (رمزگذاری)': 'Caesar N / Encode', 'سزار با N (رمزگشایی)': 'Caesar N / Decode', 'ویژنر (کلید)': 'Vigenere / Encode', 'ویژنر (رمزگشایی)': 'Vigenere / Decode', 'معکوس کل متن': 'Reverse complete text', 'معکوس کلمات': 'Reverse word order', 'معکوس خطوط': 'Reverse lines', 'Base64 → کد': 'Base64 / Encode', 'Base64 ← متن': 'Base64 / Decode (legacy)', 'Hex با فاصله': 'Unicode code points / Hex', 'Hex ← متن': 'Hex code points / Decode', 'Binary 8-bit': 'Binary code points (minimum 8 bits)', 'Binary ← متن': 'Binary code points / Decode', 'حذف فاصله': 'Remove spaces', 'فقط حروف': 'Letters only', 'Morse → کد': 'Morse / Encode (legacy)', 'Morse ← کد': 'Morse / Decode (legacy)', 'فقط حروف بزرگ': 'Uppercase letters only', 'تحلیل کامل': 'Full text analysis', 'تعداد کاراکتر': 'Character count', 'تعداد کلمات': 'Word count', 'تعداد خطوط': 'Line count', 'فرکانس حروف': 'Character frequency', 'فرکانس کلمات': 'Word frequency', 'بلندترین کلمه': 'Longest word', 'کوتاه\u200cترین کلمه': 'Shortest word', 'اعداد فارسی → انگلیسی': 'Persian digits to English', 'اعداد انگلیسی → فارسی': 'English digits to Persian', 'عربی → فارسی (ی/ک)': 'Arabic letters to Persian', 'فارسی → عربی': 'Persian letters to Arabic', 'حذف اعراب': 'Remove diacritics', 'حذف کشیده': 'Remove tatweel', 'استخراج کلمات فارسی': 'Extract Persian-range tokens', 'حذف کلمات انگلیسی': 'Remove English words', 'یکسان\u200cسازی فاصله': 'Normalize horizontal spaces', 'پسورد تصادفی': 'Random password', 'SHA-256 کوتاه': 'Short SHA-256', 'کد یونیکد حروف': 'Unicode character codes', 'تاریخ/ساعت': 'Local date and time', 'آزمایشگاه رمز · استگانوگرافی · کد جاسوسی': 'Cipher, steganography and text laboratory', '▸  متن ورودی / متن پوششی': '1. Input / Cover text', 'کلید:': 'Key:', '▸  نتیجه': '3. Output', '✕  پاک کردن': 'Clear workspace', '⎘  کپی نتیجه': 'Copy output', '◆  استخراج پیام مخفی': 'Extract hidden patterns', '◆  مخفی\u200cسازی پیام': 'Hide a message', '◈ راهنما': 'Quick guide', 'الگوریتم\u200cهای رمزنگاری تاریخی': 'Historical ciphers — educational use only', 'تبدیل متن به کد و بالعکس': 'Encode text and inspect character representations', 'کدهای ارتباطی و الفبای خاص': 'Communication codes and alternative alphabets', 'آمار و ساختار متن': 'Text statistics and structure', 'استانداردسازی فارسی و ابزارهای عمومی': 'Persian normalization and general utilities', 'الگوهای استخراج و مخفی\u200cسازی شبیه فیلم\u200cها: Acrostic، Book Cipher، Null Cipher و ...': 'Acrostic, book cipher, null cipher and other extraction patterns'}
GUIDE = """SHADOWCIPHER — QUICK START

1. Paste your text in Input, or use File > Open UTF-8 text.
2. Choose a tab and click a tool. The result appears immediately.
3. Copy or save the result. Use output as input chains operations.

Find tool searches ALL original tools by English or Persian name.
Select a result and press Enter or Run selected. Double-click also runs it.
Favorites are session-only and never remove tools from their original tabs.

KEY AND N
Vigenere: enter a Latin-letter key.
Caesar N: N is the shift.
Every Nth character/word starts at index 0, then N, 2N, and so on.
Odd/even extraction preserves the original zero-based indexing convention.
Word index: enter 1 3 5; indexes are one-based.
Book cipher: enter line.word.character triples such as 1.1.1 2.3.2.
Hide key in cover: Input is the cover, Key is the message. The original
algorithm inserts only at eligible alphabetic positions and may truncate
messages when the cover is too short. Always verify extraction yourself.

LEGACY COMPATIBILITY
All original tools, duplicate buttons, functions and six tabs remain.
This release improves access, not cipher definitions. Legacy Morse can lose
word boundaries and unsupported characters. Base64 decoding may replace
invalid UTF-8. Hex/binary tools represent code points, not UTF-8 bytes.
Full analysis and helper-generated messages can remain Persian, even with
English UI labels. Persian cover-word samples are intentionally preserved.
The N fallback remains 2 for invalid text and clamps numbers to at least 1.

SAFETY AND PRIVACY
Historical ciphers, acrostics, Braille, Leet and Base64 are not secure encryption.
MD5 is a legacy digest; a plain hash is not a password-storage system.
No network requests or automatic workspace/history saving are added.
Saved files and clipboard history can retain your text. Keys are shown by
default for original compatibility; toggle Hide key to mask them visually.
Tools run synchronously, so large input can pause the interface. Save work
before trying large transformations; no sandbox or cancellation is provided.

SHORTCUTS
Ctrl/Cmd+O: Open file       Ctrl/Cmd+S: Save output
Ctrl/Cmd+F: Find tool       Ctrl/Cmd+Shift+C: Copy output
F1: Help                   Ctrl/Cmd+Plus/Minus: Change editor font size
"""

class EnhancedShadowCipher(ShadowCipher):
    """Non-destructive extension of the original six-tab application."""

    def __init__(self):
        self.tool_catalog = []
        self.favorites = set()
        self._english = True
        self._font_size = 11
        super().__init__()
        self.title('ShadowCipher')
        self.minsize(1050, 780)
        self._center_window(1180, 880)
        self._install_menu()
        self._install_editors()
        self._translate_widgets()
        self._set_status(f'Ready | {len(self.tool_catalog)} original tool buttons | F1: Help')
        self.bind('<F1>', lambda e: self._help())
        for mod in ('Control', 'Command'):
            for key, fn in [('o', self._open_file), ('s', self._save_file),
                            ('f', self._finder), ('Shift-C', self._copy_out)]:
                self.bind(f'<{mod}-{key}>', lambda e, f=fn: (f(), 'break')[1])
            self.bind(f'<{mod}-plus>', lambda e: self._zoom(1))
            self.bind(f'<{mod}-equal>', lambda e: self._zoom(1))
            self.bind(f'<{mod}-minus>', lambda e: self._zoom(-1))
        self.protocol('WM_DELETE_WINDOW', self._close)

    def _grid_buttons(self, parent, ops, cols=3):
        # Register every entry, including duplicate labels, without filtering.
        start = len(self.tool_catalog)
        for name, command in ops:
            self.tool_catalog.append((name, command))
        if parent.master == self.nb:
            # All original non-steganography tabs gain vertical scrolling.
            wrap = ttk.Frame(parent)
            wrap.pack(fill=tk.BOTH, expand=True)
            canvas = tk.Canvas(wrap, bg=C['bg'], highlightthickness=0)
            bar = ttk.Scrollbar(wrap, orient='vertical', command=canvas.yview)
            content = ttk.Frame(canvas)
            item = canvas.create_window((0, 0), window=content, anchor='nw')
            content.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
            canvas.bind('<Configure>', lambda e: canvas.itemconfigure(item, width=e.width))
            canvas.configure(yscrollcommand=bar.set)
            bar.pack(side=tk.RIGHT, fill=tk.Y)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            super()._grid_buttons(content, ops, cols)
        else:
            super()._grid_buttons(parent, ops, cols)

    def _install_menu(self):
        menu = tk.Menu(self)
        file = tk.Menu(menu, tearoff=False)
        for label, fn in [('Open UTF-8 text...', self._open_file), ('Save output...', self._save_file),
                          ('Copy output', self._copy_out), ('Use output as input', self._chain),
                          ('Clear workspace', self._clear)]:
            file.add_command(label=label, command=fn)
        file.add_separator()
        file.add_command(label='Exit', command=self._close)
        menu.add_cascade(label='File', menu=file)
        tools = tk.Menu(menu, tearoff=False)
        tools.add_command(label='Find tool / Favorites...', command=self._finder)
        tools.add_command(label='Load example text', command=self._example)
        self.hide_key = tk.BooleanVar(value=False)
        tools.add_checkbutton(label='Hide key', variable=self.hide_key, command=self._mask_key)
        tools.add_command(label='Larger editor text', command=lambda: self._zoom(1))
        tools.add_command(label='Smaller editor text', command=lambda: self._zoom(-1))
        menu.add_cascade(label='Tools', menu=tools)
        helpmenu = tk.Menu(menu, tearoff=False)
        helpmenu.add_command(label='Quick start and compatibility notes', command=self._help)
        helpmenu.add_command(label='About', command=lambda: messagebox.showinfo('About ShadowCipher',
            f'ShadowCipher 2.1\n{len(self.tool_catalog)} original tool buttons preserved.\nOffline Python / Tkinter application.\nEducational use; not secure encryption.', parent=self))
        menu.add_cascade(label='Help', menu=helpmenu)
        self.configure(menu=menu)

    def _install_editors(self):
        for widget in (self.input_box, self.out_box):
            bar = ttk.Scrollbar(widget.master, orient='vertical', command=widget.yview)
            bar.pack(side=tk.RIGHT, fill=tk.Y)
            widget.configure(yscrollcommand=bar.set)
            widget.bind('<Control-a>', lambda e, w=widget: self._select_all(w))
            widget.bind('<Command-a>', lambda e, w=widget: self._select_all(w))
            context = tk.Menu(widget, tearoff=False)
            for label, event in [('Cut','<<Cut>>'),('Copy','<<Copy>>'),('Paste','<<Paste>>')]:
                context.add_command(label=label, command=lambda e=event,w=widget:w.event_generate(e))
            context.add_command(label='Select all', command=lambda w=widget:self._select_all(w))
            widget.bind('<Button-3>', lambda e,m=context:self._popup(m,e))
        quick = ttk.Frame(self)
        quick.pack(fill=tk.X, padx=20, pady=(0, 8), before=self.nb)
        for label, fn in [('Find tool',self._finder), ('Open file',self._open_file),
                          ('Load example',self._example), ('Save output',self._save_file),
                          ('Use output as input',self._chain), ('Help',self._help)]:
            ttk.Button(quick, text=label, command=fn).pack(side=tk.LEFT,padx=(0,5))

    @staticmethod
    def _popup(menu,event):
        try:menu.tk_popup(event.x_root,event.y_root)
        finally:menu.grab_release()

    @staticmethod
    def _select_all(widget):
        widget.tag_add(tk.SEL,'1.0','end-1c')
        widget.focus_set()
        return 'break'

    def _translate_widgets(self):
        def walk(w):
            try:
                text=w.cget('text')
                if text in TRANSLATIONS:w.configure(text=TRANSLATIONS[text])
                elif text.startswith('Acrostic —'):
                    w.configure(text='Acrostic: initials reveal a message.\nBook cipher: use line.word.character triples, e.g. 2.1.3 5.4.1.\nNull cipher: selected words carry the message.\nSet N above; enter a key when the chosen tool needs one.')
            except tk.TclError:pass
            for child in w.winfo_children():walk(child)
        walk(self)
        for tab,label in zip(self.nb.tabs(),['Steganography','Classical ciphers','Encoding','Morse and special','Analysis','Persian and utilities']):
            self.nb.tab(tab,text='  '+label+'  ')

    def _mask_key(self):
        def walk(w):
            if isinstance(w,ttk.Entry) and str(w.cget('textvariable'))==str(self.key_var):
                w.configure(show='*' if self.hide_key.get() else '')
            for child in w.winfo_children():walk(child)
        walk(self)

    def _zoom(self,delta):
        self._font_size=max(8,min(28,self._font_size+delta))
        for widget in (self.input_box,self.out_box):widget.configure(font=('Consolas',self._font_size))

    def _open_file(self):
        path=filedialog.askopenfilename(parent=self,title='Open UTF-8 text',filetypes=[('Text','*.txt'),('All files','*')])
        if not path:return
        try:
            text=Path(path).read_text(encoding='utf-8-sig')
            if not self._replace_ok('Replace current input?'):return
            self.input_box.delete('1.0',tk.END)
            self.input_box.insert('1.0',text)
            self._set_status('UTF-8 input loaded.')
        except (OSError,UnicodeError) as exc:messagebox.showerror('Cannot open file',str(exc),parent=self)

    def _replace_ok(self,question):
        return not self.input_box.get('1.0','end-1c') or messagebox.askyesno('Replace input',question,parent=self)

    def _save_file(self):
        text=self.out_box.get('1.0','end-1c')
        path=filedialog.asksaveasfilename(parent=self,title='Save output',defaultextension='.txt',filetypes=[('Text','*.txt'),('All files','*')])
        if path:
            try:
                with open(path,'w',encoding='utf-8',newline='') as f:f.write(text)
                self._set_status('Output saved as UTF-8.')
            except OSError as exc:messagebox.showerror('Cannot save file',str(exc),parent=self)

    def _chain(self):
        if self._replace_ok('Replace input with the current output?'):
            text=self.out_box.get('1.0','end-1c')
            self.input_box.delete('1.0',tk.END)
            self.input_box.insert('1.0',text)
            self._set_status('Output copied to input. Choose the next tool.')

    def _example(self):
        if self._replace_ok('Replace input with example text?'):
            self.input_box.delete('1.0',tk.END)
            self.input_box.insert('1.0','Secret messages are fun.\nEvery line can hide a clue.\nCode carefully and check the result.\nRead the initials!\n\nسلام دنیا ۱۲۳')
            self._set_status('Example loaded. Try First letters of lines or an analysis tool.')

    def _run(self,func):
        # Same transformation and editable output behavior as the original.
        text=self.input_box.get('1.0','end-1c')
        try:
            result=str(func(text))
            self.out_box.delete('1.0',tk.END)
            self.out_box.insert(tk.END,result)
            self._set_status(f'Done | {len(result):,} output characters')
        except Exception as exc:
            self.out_box.delete('1.0',tk.END)
            self.out_box.insert(tk.END,f'Error: {type(exc).__name__}\n{exc}')
            self._set_status('Operation failed. Check input, Key and N.',error=True)

    def _copy_out(self):
        super()._copy_out()
        self._set_status('Output copied to clipboard.')

    def _clear(self):
        if not messagebox.askyesno('Clear workspace','Clear input, output, Key and N?',parent=self):return
        super()._clear()
        self._set_status('Workspace cleared.')

    def _finder(self):
        win=tk.Toplevel(self)
        win.title('Find tool — all original operations')
        win.geometry('740x540')
        query=tk.StringVar()
        favorites_only=tk.BooleanVar()
        ttk.Label(win,text='Search English or Persian names. Select a tool, then Run selected.').pack(anchor='w',padx=12,pady=8)
        entry=ttk.Entry(win,textvariable=query)
        entry.pack(fill=tk.X,padx=12)
        ttk.Checkbutton(win,text='Favorites only (this session)',variable=favorites_only,command=lambda:refresh()).pack(anchor='w',padx=12,pady=6)
        frame=ttk.Frame(win)
        frame.pack(fill=tk.BOTH,expand=True,padx=12)
        listing=tk.Listbox(frame,exportselection=False,font=('TkDefaultFont',11))
        bar=ttk.Scrollbar(frame,command=listing.yview)
        listing.configure(yscrollcommand=bar.set)
        bar.pack(side=tk.RIGHT,fill=tk.Y)
        listing.pack(side=tk.LEFT,fill=tk.BOTH,expand=True)
        visible=[]
        def refresh(*args):
            listing.delete(0,tk.END)
            visible.clear()
            q=query.get().casefold().split()
            for i,(name,cmd) in enumerate(self.tool_catalog):
                english=TRANSLATIONS.get(name,name)
                if favorites_only.get() and i not in self.favorites:continue
                if not all(x in (name+' '+english).casefold() for x in q):continue
                visible.append(i)
                listing.insert(tk.END,('* ' if i in self.favorites else '')+english)
            if visible:listing.selection_set(0)
        def run(event=None):
            selection=listing.curselection()
            if selection:
                name,cmd=self.tool_catalog[visible[selection[0]]]
                win.destroy()
                cmd()
        def favorite():
            selection=listing.curselection()
            if selection:
                i=visible[selection[0]]
                if i in self.favorites:self.favorites.remove(i)
                else:self.favorites.add(i)
                refresh()
        row=ttk.Frame(win)
        row.pack(fill=tk.X,padx=12,pady=10)
        ttk.Button(row,text='Run selected',command=run).pack(side=tk.LEFT)
        ttk.Button(row,text='Toggle favorite',command=favorite).pack(side=tk.LEFT,padx=6)
        ttk.Button(row,text='Close',command=win.destroy).pack(side=tk.RIGHT)
        query.trace_add('write',refresh)
        listing.bind('<Double-Button-1>',run)
        win.bind('<Return>',run)
        win.bind('<Escape>',lambda e:win.destroy())
        refresh()
        entry.focus_set()

    def _help(self):
        win=tk.Toplevel(self)
        win.title('ShadowCipher — Quick start and safety')
        win.geometry('800x650')
        text=scrolledtext.ScrolledText(win,wrap=tk.WORD,padx=16,pady=16,font=('TkDefaultFont',11))
        text.pack(fill=tk.BOTH,expand=True)
        text.insert('1.0',GUIDE)
        text.configure(state='disabled')
        ttk.Button(win,text='Close',command=win.destroy).pack(pady=8)

    def _close(self):
        if self.input_box.get('1.0','end-1c') or self.out_box.get('1.0','end-1c'):
            if not messagebox.askyesno('Exit ShadowCipher','Unsaved workspace will be lost. Exit?',parent=self):return
        self.destroy()


if __name__ == '__main__':
    EnhancedShadowCipher().mainloop()
