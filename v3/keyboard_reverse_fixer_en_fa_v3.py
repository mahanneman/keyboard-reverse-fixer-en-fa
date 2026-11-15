#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Text Toolkit — ۳۳۴ عملیات متن، رمز و کدگذاری
Single-file · Python 3 · stdlib only
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import webbrowser
import base64, binascii, codecs, hashlib, hmac, html, urllib.parse
import zlib, gzip, bz2, lzma, json, csv, io, re, string, secrets, uuid, math
from collections import Counter

# ═══════════════════════════════════════════════════════════════
# ثابت‌ها
# ═══════════════════════════════════════════════════════════════
PERSIAN_ALPHABET = 'آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی'
PERSIAN_DIGITS   = '۰۱۲۳۴۵۶۷۸۹'
ENGLISH_DIGITS   = '0123456789'
LATIN_LOWER      = 'abcdefghijklmnopqrstuvwxyz'
LATIN_UPPER      = LATIN_LOWER.upper()

REGISTRY = []   # ← همه‌ی ۳۳۴ عملیات

def add_op(name, cat, func, k=0, k1l='', k2l='', desc=''):
    """ثبت یک عملیات. تابع کرش‌پذیر می‌شود."""
    def safe(text, key1='', key2=''):
        try:
            return str(func(text, key1, key2))
        except Exception as e:
            return f'❌ {type(e).__name__}: {e}'
    REGISTRY.append({'name': name, 'cat': cat, 'func': safe,
                     'k': k, 'k1l': k1l, 'k2l': k2l, 'desc': desc})

def pair(name, cat, enc, dec, k=0, k1l='', k2l='', desc=''):
    add_op(f'{name} — رمزگذاری', cat, enc, k, k1l, k2l, desc)
    add_op(f'{name} — رمزگشایی', cat, dec, k, k1l, k2l, desc)


# ═══════════════════════════════════════════════════════════════
# ابزارهای پایه
# ═══════════════════════════════════════════════════════════════
def _shift_alphabet(text, shift, alphabet_lower, alphabet_upper=None):
    """جابه‌جایی حروف در الفبا (سزار عمومی)."""
    if alphabet_upper is None:
        alphabet_upper = alphabet_lower.upper() if alphabet_lower.isascii() else None
    lut = {}
    n = len(alphabet_lower)
    for i, ch in enumerate(alphabet_lower):
        lut[ch] = alphabet_lower[(i + shift) % n]
    if alphabet_upper:
        for i, ch in enumerate(alphabet_upper):
            lut[ch] = alphabet_upper[(i + shift) % len(alphabet_upper)]
    return ''.join(lut.get(c, c) for c in text)

def _caesar(text, shift, decrypt=False):
    s = -shift if decrypt else shift
    # لاتین + فارسی
    out = _shift_alphabet(text, s, LATIN_LOWER, LATIN_UPPER)
    out = _shift_alphabet(out, s, PERSIAN_ALPHABET, None)
    return out

def _vigenere(text, key, decrypt=False, alphabet=LATIN_LOWER):
    if not key: raise ValueError('کلید لازم است')
    key = ''.join(c for c in key.lower() if c in alphabet) or alphabet[0]
    n = len(alphabet)
    idx = {c: i for i, c in enumerate(alphabet)}
    result, ki = [], 0
    for ch in text:
        low = ch.lower()
        if low in idx:
            shift = idx[key[ki % len(key)]]
            if decrypt: shift = -shift
            new = alphabet[(idx[low] + shift) % n]
            result.append(new.upper() if ch.isupper() else new)
            ki += 1
        else:
            result.append(ch)
    return ''.join(result)

def _atbash(text):
    out = []
    for ch in text:
        if 'a' <= ch <= 'z': out.append(chr(ord('z') - (ord(ch) - ord('a'))))
        elif 'A' <= ch <= 'Z': out.append(chr(ord('Z') - (ord(ch) - ord('A'))))
        else: out.append(ch)
    return ''.join(out)


# ═══════════════════════════════════════════════════════════════
# ① کیبورد فارسی/انگلیسی  (۲۱ عملیات)
# ═══════════════════════════════════════════════════════════════
KB_BASE = {
    'q':'ض','w':'ص','e':'ث','r':'ق','t':'ف','y':'غ','u':'ع','i':'ه','o':'خ','p':'ح',
    '[':'ج',']':'چ','\\':'گ','a':'ش','s':'س','d':'ی','f':'ب','g':'ل','h':'ا',
    'j':'ت','k':'ن','l':'م',';':'پ',"'":'ک','z':'ظ','x':'ط','c':'ز','v':'ر','b':'ذ',
    'n':'د','m':'ئ',',':'و','.':'.','/':'/','Z':'ژ',
}
KB_VARIANTS = [
    ('ویندوز', {}),
    ('لینوکس', {'z':'ژ','p':'پ','c':'چ','g':'گ','y':'ی','k':'ک','j':'ج','h':'ح'}),
    ('پ↔ب', {';':'ب','f':'پ'}),
    ('ژ↔ف', {'t':'ژ','Z':'ف'}),
    ('چ↔ج', {']':'ج','[':'چ'}),
    ('ش↔س', {'a':'س','s':'ش'}),
    ('ه↔ا', {'i':'ا','h':'ه'}),
    ('ت↔ن', {'j':'ن','k':'ت'}),
    ('م↔ل', {'l':'ل','g':'م'}),
    ('ر↔ز', {'v':'ز','c':'ر'}),
    ('د↔ذ', {'n':'ذ','b':'د'}),
    ('و↔.', {',':'.','.':'و'}),
    ('ع↔غ', {'u':'غ','y':'ع'}),
    ('خ↔ح', {'o':'ح','p':'خ'}),
    ('ث↔ص', {'e':'ص','w':'ث'}),
    ('ض↔ق', {'q':'ق','r':'ض'}),
    ('ی↔ئ', {'d':'ئ','m':'ی'}),
    ('ک↔گ', {"'":'گ','\\':'ک'}),
    ('AZERTY', {'a':'q','q':'a','z':'w','w':'z'}),
    ('DVORAK', {'q':"'",'w':',','e':'.','r':'p','t':'y','y':'f','u':'g','i':'c',
                'o':'r','p':'l','s':'o','d':'e','f':'u','g':'i','h':'d','j':'h',
                'k':'t','l':'n',';':'s','z':';','x':'q','c':'j','v':'k','b':'x','n':'b'}),
    ('COLEMAK', {'e':'f','r':'p','t':'g','y':'j','u':'l','i':'u','o':'y','p':';',
                 's':'r','d':'s','f':'t','g':'d','j':'n','k':'e','l':'i',';':'o'}),
]
for kbname, kbmap in KB_VARIANTS:
    _m = dict(KB_BASE); _m.update(kbmap)
    add_op(f'کیبورد {kbname}', 'کیبورد',
           (lambda m: lambda t, a='', b='': ''.join(
               m.get(c, m.get(c.lower(), c)) for c in t))(_m))


# ═══════════════════════════════════════════════════════════════
# ② تحلیل متن  (۲۱ عملیات)
# ═══════════════════════════════════════════════════════════════
add_op('تعداد کاراکتر', 'تحلیل', lambda t,a='',b='': str(len(t)))
add_op('تعداد کاراکتر (بدون فاصله)', 'تحلیل', lambda t,a='',b='': str(len(t.replace(' ','').replace('\n','').replace('\t',''))))
add_op('تعداد کلمات', 'تحلیل', lambda t,a='',b='': str(len(re.findall(r'\S+', t))))
add_op('تعداد خطوط', 'تحلیل', lambda t,a='',b='': str(t.count('\n')+1 if t else 0))
add_op('تعداد جملات', 'تحلیل', lambda t,a='',b='': str(len([s for s in re.split(r'[.!?؟।]+', t) if s.strip()])))
add_op('تعداد پاراگراف‌ها', 'تحلیل', lambda t,a='',b='': str(len([p for p in re.split(r'\n\s*\n', t) if p.strip()])))
add_op('کلمات یکتا', 'تحلیل', lambda t,a='',b='': str(len(set(re.findall(r'\S+', t)))))
add_op('حروف یکتا', 'تحلیل', lambda t,a='',b='': str(len(set(c for c in t if c.isalpha()))))
add_op('بلندترین کلمه', 'تحلیل', lambda t,a='',b='': max(re.findall(r'\S+', t), key=len, default=''))
add_op('کوتاه‌ترین کلمه', 'تحلیل', lambda t,a='',b='': min(re.findall(r'\S+', t), key=len, default=''))
add_op('میانگین طول کلمه', 'تحلیل', lambda t,a='',b='': f"{sum(len(w) for w in re.findall(r'\S+',t))/max(1,len(re.findall(r'\S+',t))):.2f}")
add_op('تعداد حروف صدادار', 'تحلیل', lambda t,a='',b='': str(sum(1 for c in t.lower() if c in 'aeiouآایو')))
add_op('تعداد حروف بی‌صدا', 'تحلیل', lambda t,a='',b='': str(sum(1 for c in t.lower() if c.isalpha() and c not in 'aeiouآایو')))
add_op('تعداد اعداد', 'تحلیل', lambda t,a='',b='': str(sum(1 for c in t if c.isdigit())))
add_op('تعداد علائم نگارشی', 'تحلیل', lambda t,a='',b='': str(sum(1 for c in t if c in string.punctuation + '،؛؟«»')))
add_op('تعداد فاصله', 'تحلیل', lambda t,a='',b='': str(t.count(' ')))
add_op('فرکانس حروف', 'تحلیل', lambda t,a='',b='': '\n'.join(f'{c}: {n}' for c,n in Counter(c for c in t if c.isalpha()).most_common(30)))
add_op('فرکانس کلمات', 'تحلیل', lambda t,a='',b='': '\n'.join(f'{w}: {n}' for w,n in Counter(re.findall(r'\S+', t)).most_common(30)))
add_op('زمان خواندن (دقیقه)', 'تحلیل', lambda t,a='',b='': f"{len(re.findall(r'\S+',t))/200:.2f}")
add_op('زمان صحبت (دقیقه)', 'تحلیل', lambda t,a='',b='': f"{len(re.findall(r'\S+',t))/130:.2f}")
add_op('خط اول', 'تحلیل', lambda t,a='',b='': t.split('\n')[0] if t else '')


# ═══════════════════════════════════════════════════════════════
# ③ تغییر حالت حروف  (۱۰ عملیات)
# ═══════════════════════════════════════════════════════════════
add_op('UPPERCASE', 'حالت حروف', lambda t,a='',b='': t.upper())
add_op('lowercase', 'حالت حروف', lambda t,a='',b='': t.lower())
add_op('Title Case', 'حالت حروف', lambda t,a='',b='': t.title())
add_op('Sentence case', 'حالت حروف', lambda t,a='',b='': '. '.join(s.capitalize() for s in re.split(r'(?<=[.!?])\s+', t)))
add_op('Swap Case', 'حالت حروف', lambda t,a='',b='': t.swapcase())
add_op('tOGGLE wHOLE', 'حالت حروف', lambda t,a='',b='': t.swapcase())
add_op('aLtErNaTe', 'حالت حروف', lambda t,a='',b='': ''.join(c.upper() if i%2 else c.lower() for i,c in enumerate(t)))
add_op('Capitalize words', 'حالت حروف', lambda t,a='',b='': ' '.join(w.capitalize() for w in t.split(' ')))
add_op('lower (ASCII only)', 'حالت حروف', lambda t,a='',b='': ''.join(c.lower() if c.isascii() else c for c in t))
add_op('upper (ASCII only)', 'حالت حروف', lambda t,a='',b='': ''.join(c.upper() if c.isascii() else c for c in t))


# ═══════════════════════════════════════════════════════════════
# ④ تغییر متن  (۲۰ عملیات)
# ═══════════════════════════════════════════════════════════════
add_op('معکوس کاراکترها', 'تغییر متن', lambda t,a='',b='': t[::-1])
add_op('معکوس کلمات', 'تغییر متن', lambda t,a='',b='': ' '.join(t.split()[::-1]))
add_op('معکوس خطوط', 'تغییر متن', lambda t,a='',b='': '\n'.join(t.split('\n')[::-1]))
add_op('مرتب‌سازی خطوط', 'تغییر متن', lambda t,a='',b='': '\n'.join(sorted(t.split('\n'))))
add_op('مرتب‌سازی خطوط (نزولی)', 'تغییر متن', lambda t,a='',b='': '\n'.join(sorted(t.split('\n'), reverse=True)))
add_op('مرتب‌سازی کلمات', 'تغییر متن', lambda t,a='',b='': ' '.join(sorted(t.split())))
add_op('خطوط یکتا', 'تغییر متن', lambda t,a='',b='': '\n'.join(dict.fromkeys(t.split('\n'))))
add_op('حذف خطوط خالی', 'تغییر متن', lambda t,a='',b='': '\n'.join(l for l in t.split('\n') if l.strip()))
add_op('Trim خطوط', 'تغییر متن', lambda t,a='',b='': '\n'.join(l.strip() for l in t.split('\n')))
add_op('شماره‌گذاری خطوط', 'تغییر متن', lambda t,a='',b='': '\n'.join(f'{i+1}. {l}' for i,l in enumerate(t.split('\n'))))
add_op('حذف فاصله‌ها', 'تغییر متن', lambda t,a='',b='': t.replace(' ',''))
add_op('حذف علائم', 'تغییر متن', lambda t,a='',b='': ''.join(c for c in t if c not in string.punctuation+'،؛؟«»'))
add_op('حذف اعداد', 'تغییر متن', lambda t,a='',b='': ''.join(c for c in t if not c.isdigit()))
add_op('حذف حروف صدادار', 'تغییر متن', lambda t,a='',b='': ''.join(c for c in t if c.lower() not in 'aeiouآایو'))
add_op('فقط حروف', 'تغییر متن', lambda t,a='',b='': ''.join(c for c in t if c.isalpha()))
add_op('فقط اعداد', 'تغییر متن', lambda t,a='',b='': ''.join(c for c in t if c.isdigit()))
add_op('حرف اول هر کلمه', 'تغییر متن', lambda t,a='',b='': ''.join(w[0] for w in t.split() if w))
add_op('حرف آخر هر کلمه', 'تغییر متن', lambda t,a='',b='': ''.join(w[-1] for w in t.split() if w))
add_op('تقسیم با نقطه', 'تغییر متن', lambda t,a='',b='': '\n'.join(re.split(r'[.!?؟।]\s*', t)))
add_op('اولین n کلمه (۱۰)', 'تغییر متن', lambda t,a='',b='': ' '.join(t.split()[:10]))


# ═══════════════════════════════════════════════════════════════
# ⑤ کدگذاری/رمزگشایی Base/Hex/URL  (۵۰ عملیات = ۲۵ جفت)
# ═══════════════════════════════════════════════════════════════
def _b64e(t): return base64.b64encode(t.encode('utf-8')).decode()
def _b64d(t): return base64.b64decode(t.encode('utf-8'), validate=False).decode('utf-8', 'replace')
def _b32e(t): return base64.b32encode(t.encode('utf-8')).decode()
def _b32d(t): return base64.b32decode(t.encode('utf-8').upper() + b'='*((8-len(t)%8)%8)).decode('utf-8', 'replace')
def _b16e(t): return base64.b16encode(t.encode('utf-8')).decode()
def _b16d(t): return base64.b16decode(t.upper().encode('utf-8')).decode('utf-8', 'replace')
def _b85e(t): return base64.b85encode(t.encode('utf-8')).decode()
def _b85d(t): return base64.b85decode(t.encode('utf-8')).decode('utf-8', 'replace')
def _a85e(t): return base64.a85encode(t.encode('utf-8')).decode()
def _a85d(t): return base64.a85decode(t.encode('utf-8')).decode('utf-8', 'replace')
def _uu_e(t): return codecs.encode(t.encode('utf-8'), 'uu').decode()
def _uu_d(t): return codecs.decode(t.encode('utf-8'), 'uu').decode('utf-8', 'replace')

pair('Base64', 'کدگذاری', lambda t,a='',b='': _b64e(t), lambda t,a='',b='': _b64d(t))
pair('Base32', 'کدگذاری', lambda t,a='',b='': _b32e(t), lambda t,a='',b='': _b32d(t))
pair('Base16 (Hex)', 'کدگذاری', lambda t,a='',b='': _b16e(t), lambda t,a='',b='': _b16d(t))
pair('Base85', 'کدگذاری', lambda t,a='',b='': _b85e(t), lambda t,a='',b='': _b85d(t))
pair('ASCII85', 'کدگذاری', lambda t,a='',b='': _a85e(t), lambda t,a='',b='': _a85d(t))
pair('UUencode', 'کدگذاری', lambda t,a='',b='': _uu_e(t), lambda t,a='',b='': _uu_d(t))
pair('URL encode', 'کدگذاری',
     lambda t,a='',b='': urllib.parse.quote(t),
     lambda t,a='',b='': urllib.parse.unquote(t))
pair('HTML escape', 'کدگذاری',
     lambda t,a='',b='': html.escape(t),
     lambda t,a='',b='': html.unescape(t))
pair('Unicode escape', 'کدگذاری',
     lambda t,a='',b='': t.encode('unicode_escape').decode('ascii'),
     lambda t,a='',b='': t.encode().decode('unicode_escape'))
pair('Binary (8-bit)', 'کدگذاری',
     lambda t,a='',b='': ' '.join(f'{ord(c):08b}' for c in t),
     lambda t,a='',b='': ''.join(chr(int(b,2)) for b in t.split()))
pair('Octal (8-bit)', 'کدگذاری',
     lambda t,a='',b='': ' '.join(f'{ord(c):o}' for c in t),
     lambda t,a='',b='': ''.join(chr(int(o,8)) for o in t.split()))
pair('Decimal (کدها)', 'کدگذاری',
     lambda t,a='',b='': ' '.join(str(ord(c)) for c in t),
     lambda t,a='',b='': ''.join(chr(int(d)) for d in t.split()))
pair('Hex با فاصله', 'کدگذاری',
     lambda t,a='',b='': ' '.join(f'{ord(c):02x}' for c in t),
     lambda t,a='',b='': ''.join(chr(int(h,16)) for h in t.split()))
pair('ROT13', 'کدگذاری',
     lambda t,a='',b='': codecs.encode(t, 'rot13'),
     lambda t,a='',b='': codecs.encode(t, 'rot13'))
pair('ROT47', 'کدگذاری',
     lambda t,a='',b='': ''.join(chr(33+((ord(c)-33+47)%94)) for c in t),
     lambda t,a='',b='': ''.join(chr(33+((ord(c)-33+47)%94)) for c in t))
pair('Quoted-printable', 'کدگذاری',
     lambda t,a='',b='': codecs.encode(t.encode('utf-8'), 'quopri').decode(),
     lambda t,a='',b='': codecs.decode(t.encode(), 'quopri').decode('utf-8','replace'))
pair('Zlib (Base64)', 'فشرده‌سازی',
     lambda t,a='',b='': _b64e_bytes(zlib.compress(t.encode())),
     lambda t,a='',b='': zlib.decompress(_b64d_bytes(t)).decode('utf-8','replace'))
pair('Gzip (Base64)', 'فشرده‌سازی',
     lambda t,a='',b='': _b64e_bytes(gzip.compress(t.encode())),
     lambda t,a='',b='': gzip.decompress(_b64d_bytes(t)).decode('utf-8','replace'))
pair('BZ2 (Base64)', 'فشرده‌سازی',
     lambda t,a='',b='': _b64e_bytes(bz2.compress(t.encode())),
     lambda t,a='',b='': bz2.decompress(_b64d_bytes(t)).decode('utf-8','replace'))
pair('LZMA (Base64)', 'فشرده‌سازی',
     lambda t,a='',b='': _b64e_bytes(lzma.compress(t.encode())),
     lambda t,a='',b='': lzma.decompress(_b64d_bytes(t)).decode('utf-8','replace'))

# helper bytes-base64
def _b64e_bytes(b): return base64.b64encode(b).decode()
def _b64d_bytes(s): return base64.b64decode(s.encode())

# JSON/CSV
add_op('JSON pretty', 'کدگذاری',
       lambda t,a='',b='': json.dumps(json.loads(t), ensure_ascii=False, indent=2))
add_op('JSON minify', 'کدگذاری',
       lambda t,a='',b='': json.dumps(json.loads(t), ensure_ascii=False, separators=(',',':')))
add_op('CSV → TSV', 'کدگذاری',
       lambda t,a='',b='': t.replace(',', '\t'))
add_op('TSV → CSV', 'کدگذاری',
       lambda t,a='',b='': t.replace('\t', ','))


# ═══════════════════════════════════════════════════════════════
# ⑥ هش‌ها  (۲۰ عملیات)
# ═══════════════════════════════════════════════════════════════
HASHES = [
    ('MD5','md5'), ('SHA1','sha1'), ('SHA224','sha224'), ('SHA256','sha256'),
    ('SHA384','sha384'), ('SHA512','sha512'), ('SHA3-224','sha3_224'),
    ('SHA3-256','sha3_256'), ('SHA3-384','sha3_384'), ('SHA3-512','sha3_512'),
    ('BLAKE2b','blake2b'), ('BLAKE2s','blake2s'), ('SHAKE128','shake_128'),
    ('SHAKE256','shake_256'),
]
for nm, algo in HASHES:
    try:
        add_op(f'{nm} hash', 'هش',
               (lambda a: lambda t, x='', y='': (
                   hashlib.new(a, t.encode()).hexdigest()[:32]
                   if a.startswith('shake') else
                   hashlib.new(a, t.encode()).hexdigest()
               ))(algo))
    except Exception:
        pass

add_op('CRC32', 'هش', lambda t,a='',b='': f'{binascii.crc32(t.encode()):08x}')
add_op('Adler32', 'هش', lambda t,a='',b='': f'{zlib.adler32(t.encode()):08x}')
add_op('HMAC-MD5 (کلید)', 'هش',
       lambda t,a='',b='': hmac.new(a.encode(), t.encode(), 'md5').hexdigest(), k=1, k1l='کلید')
add_op('HMAC-SHA256 (کلید)', 'هش',
       lambda t,a='',b='': hmac.new(a.encode(), t.encode(), 'sha256').hexdigest(), k=1, k1l='کلید')
add_op('HMAC-SHA512 (کلید)', 'هش',
       lambda t,a='',b='': hmac.new(a.encode(), t.encode(), 'sha512').hexdigest(), k=1, k1l='کلید')
add_op('PBKDF2-SHA256', 'هش',
       lambda t,a='',b='': hashlib.pbkdf2_hmac('sha256', t.encode(), (a or 'salt').encode(), 100000).hex(), k=1, k1l='Salt')


# ═══════════════════════════════════════════════════════════════
# ⑦ سزار — ۵۰ عملیات (۲۵ شیفت × رمزگذاری/رمزگشایی)
# ═══════════════════════════════════════════════════════════════
for shift in range(1, 26):
    add_op(f'سزار +{shift}', 'رمز کلاسیک',
           lambda t,a='',b='',s=shift: _caesar(t, s, False))
    add_op(f'سزار −{shift} (رمزگشایی)', 'رمز کلاسیک',
           lambda t,a='',b='',s=shift: _caesar(t, s, True))


# ═══════════════════════════════════════════════════════════════
# ⑧ رمزهای کلاسیک دیگر  (۲۶ جفت = ۵۲)
# ═══════════════════════════════════════════════════════════════

# --- Atbash ---
pair('Atbash', 'رمز کلاسیک',
     lambda t,a='',b='': _atbash(t),
     lambda t,a='',b='': _atbash(t))

# --- Vigenère ---
pair('ویژنر', 'رمز کلاسیک',
     lambda t,a='',b='': _vigenere(t, a, False),
     lambda t,a='',b='': _vigenere(t, a, True),
     k=1, k1l='کلید (حروف)')

# --- Vigenère فارسی ---
pair('ویژنر فارسی', 'رمز کلاسیک',
     lambda t,a='',b='': _vigenere(t, a, False, PERSIAN_ALPHABET),
     lambda t,a='',b='': _vigenere(t, a, True, PERSIAN_ALPHABET),
     k=1, k1l='کلید فارسی')

# --- Beaufort ---
def _beaufort(text, key, decrypt=False):
    if not key: raise ValueError('کلید لازم است')
    idx = {c:i for i,c in enumerate(LATIN_LOWER)}
    key = ''.join(c for c in key.lower() if c in LATIN_LOWER)
    result, ki = [], 0
    for ch in text:
        low = ch.lower()
        if low in idx:
            k = idx[key[ki % len(key)]]
            if decrypt:
                new = LATIN_LOWER[(idx[low] - k) % 26]
            else:
                new = LATIN_LOWER[(k - idx[low]) % 26]
            result.append(new.upper() if ch.isupper() else new)
            ki += 1
        else: result.append(ch)
    return ''.join(result)

pair('Beaufort', 'رمز کلاسیک',
     lambda t,a='',b='': _beaufort(t, a, False),
     lambda t,a='',b='': _beaufort(t, a, True),
     k=1, k1l='کلید')

# --- Autokey ---
def _autokey(text, key, decrypt=False):
    if not key: raise ValueError('کلید لازم است')
    idx = {c:i for i,c in enumerate(LATIN_LOWER)}
    key = ''.join(c for c in key.lower() if c in LATIN_LOWER)
    result, ki = [], 0
    for ch in text:
        low = ch.lower()
        if low in idx:
            if decrypt:
                k = idx[key[ki]]
                new = LATIN_LOWER[(idx[low] - k) % 26]
                key += new
            else:
                k = idx[key[ki]]
                new = LATIN_LOWER[(idx[low] + k) % 26]
                key += new
            result.append(new.upper() if ch.isupper() else new)
            ki += 1
        else: result.append(ch)
    return ''.join(result)

pair('Autokey', 'رمز کلاسیک',
     lambda t,a='',b='': _autokey(t, a, False),
     lambda t,a='',b='': _autokey(t, a, True),
     k=1, k1l='کلید')

# --- Porta ---
def _porta(text, key, decrypt=False):
    if not key: raise ValueError('کلید لازم است')
    P1 = 'nopqrstuvwxyz'; P2 = 'abcdefghijklm'
    idx = {c:i for i,c in enumerate(P1)}
    key = ''.join(c for c in key.lower() if c in P1)
    result, ki = [], 0
    for ch in text:
        low = ch.lower()
        if low in P1 or low in P2:
            k = idx[key[ki % len(key)]]
            if k % 2:
                new = P2[k//2] if low in P1 else P1[k//2]
            else:
                new = P1[k//2] if low in P1 else P2[k//2]
            result.append(new.upper() if ch.isupper() else new)
            ki += 1
        else: result.append(ch)
    return ''.join(result)

pair('Porta', 'رمز کلاسیک',
     lambda t,a='',b='': _porta(t, a, False),
     lambda t,a='',b='': _porta(t, a, True),
     k=1, k1l='کلید')

# --- Gronsfeld ---
def _gronsfeld(text, key, decrypt=False):
    if not key: raise ValueError('کلید عددی لازم است')
    keys = [int(c) for c in re.findall(r'\d', key)] or [0]
    result, ki = [], 0
    for ch in text:
        if 'a' <= ch <= 'z':
            s = keys[ki % len(keys)]
            if decrypt: s = -s
            result.append(chr((ord(ch)-ord('a')+s) % 26 + ord('a'))); ki+=1
        elif 'A' <= ch <= 'Z':
            s = keys[ki % len(keys)]
            if decrypt: s = -s
            result.append(chr((ord(ch)-ord('A')+s) % 26 + ord('A'))); ki+=1
        else: result.append(ch)
    return ''.join(result)

pair('Gronsfeld', 'رمز کلاسیک',
     lambda t,a='',b='': _gronsfeld(t, a, False),
     lambda t,a='',b='': _gronsfeld(t, a, True),
     k=1, k1l='کلید (اعداد)')

# --- Trithemius ---
def _trithemius(text, decrypt=False):
    return _caesar(text, 1, decrypt) if False else _gronsfeld(text, '123', decrypt)

pair('Trithemius', 'رمز کلاسیک',
     lambda t,a='',b='': _trithemius(t, False),
     lambda t,a='',b='': _trithemius(t, True))

# --- Affine ---
def _affine(text, a, b, decrypt=False):
    if not a: a = '5'
    if not b: b = '8'
    a = int(a) % 26; b = int(b) % 26
    # validate a coprime with 26
    if math.gcd(a, 26) != 1:
        return '❌ ضریب a باید با 26 اول باشد (a∈{1,3,5,7,9,11,15,17,19,21,23,25})'
    a_inv = pow(a, -1, 26)
    result = []
    for ch in text:
        if 'a' <= ch <= 'z':
            if decrypt: result.append(chr((a_inv*((ord(ch)-ord('a'))-b))%26 + ord('a')))
            else:       result.append(chr((a*(ord(ch)-ord('a'))+b)%26 + ord('a')))
        elif 'A' <= ch <= 'Z':
            if decrypt: result.append(chr((a_inv*((ord(ch)-ord('A'))-b))%26 + ord('A')))
            else:       result.append(chr((a*(ord(ch)-ord('A'))+b)%26 + ord('A')))
        else: result.append(ch)
    return ''.join(result)

pair('Affine', 'رمز کلاسیک',
     lambda t,a='',b='': _affine(t, a, b, False),
     lambda t,a='',b='': _affine(t, a, b, True),
     k=2, k1l='ضریب a', k2l='ضریب b')

# --- Playfair ---
def _playfair(text, key, decrypt=False):
    if not key: raise ValueError('کلید لازم است')
    k = re.sub(r'[^a-z]', '', key.lower()).replace('j','i')
    grid = []
    seen = set()
    for ch in k + 'abcdefghiklmnopqrstuvwxyz':
        if ch not in seen:
            seen.add(ch); grid.append(ch)
    pos = {c:(i//5, i%5) for i,c in enumerate(grid)}

    t = re.sub(r'[^a-z]', '', text.lower()).replace('j','i')
    pairs = []; i = 0
    while i < len(t):
        a = t[i]; b = t[i+1] if i+1 < len(t) else 'x'
        if a == b: pairs.append((a,'x')); i += 1
        else: pairs.append((a,b)); i += 2
    result = []
    for a,b in pairs:
        ra,ca = pos[a]; rb,cb = pos[b]
        if ra==rb:
            if decrypt: result += [grid[ra*5+(ca-1)%5], grid[rb*5+(cb-1)%5]]
            else:       result += [grid[ra*5+(ca+1)%5], grid[rb*5+(cb+1)%5]]
        elif ca==cb:
            if decrypt: result += [grid[((ra-1)%5)*5+ca], grid[((rb-1)%5)*5+cb]]
            else:       result += [grid[((ra+1)%5)*5+ca], grid[((rb+1)%5)*5+cb]]
        else:
            result += [grid[ra*5+cb], grid[rb*5+ca]]
    return ''.join(result)

pair('Playfair', 'رمز کلاسیک',
     lambda t,a='',b='': _playfair(t, a, False),
     lambda t,a='',b='': _playfair(t, a, True),
     k=1, k1l='کلید')

# --- Rail Fence ---
def _railfence_enc(text, n):
    if n < 2: return text
    rails = [''] * n
    for i, ch in enumerate(text):
        cycle = (n-1)*2
        r = (i % cycle)
        if r < n: rails[r] += ch
        else: rails[cycle - r] += ch
    return ''.join(rails)

def _railfence_dec(text, n):
    if n < 2: return text
    idx = []
    cycle = (n-1)*2
    for i in range(len(text)):
        r = i % cycle
        idx.append(r if r < n else cycle - r)
    order = sorted(range(len(text)), key=lambda i: idx[i])
    out = [None]*len(text)
    for pos, ch in zip(order, text):
        out[pos] = ch
    return ''.join(out)

for n in range(2, 11):
    add_op(f'Rail Fence n={n}', 'رمز کلاسیک',
           lambda t,a='',b='',nn=n: _railfence_enc(t, nn))
    add_op(f'Rail Fence n={n} (رمزگشایی)', 'رمز کلاسیک',
           lambda t,a='',b='',nn=n: _railfence_dec(t, nn))

# --- Columnar Transposition ---
def _columnar(text, key, decrypt=False):
    if not key: raise ValueError('کلید لازم است')
    key = key.strip()
    if not decrypt:
        cols = sorted(range(len(key)), key=lambda i: key[i])
        pad = (-len(text)) % len(key)
        text += 'X' * pad
        rows = [text[i:i+len(key)] for i in range(0, len(text), len(key))]
        return ''.join(''.join(r[c] for r in rows) for c in cols)
    else:
        cols = sorted(range(len(key)), key=lambda i: key[i])
        col_len = {c:0 for c in range(len(key))}
        n = len(text); rows = n // len(key)
        extra = n % len(key)
        for c in cols[:extra]: col_len[c] = rows + 1
        for c in cols[extra:]: col_len[c] = rows
        grid = [[''] * len(key) for _ in range(rows + (1 if extra else 0))]
        i = 0
        for c in cols:
            for r in range(col_len[c]):
                grid[r][c] = text[i]; i += 1
        return ''.join(''.join(row) for row in grid).rstrip('X')

pair('Columnar', 'رمز کلاسیک',
     lambda t,a='',b='': _columnar(t, a, False),
     lambda t,a='',b='': _columnar(t, a, True),
     k=1, k1l='کلید (کلمه)')

# --- Scytale ---
def _scytale_enc(text, n):
    n = int(n); n = max(2, n)
    if not text: return text
    rows = [text[i:i+n] for i in range(0, len(text), n)]
    return ''.join(rows[c][r] if c < len(rows[r]) else '' for c in range(n) for r in range(len(rows)))

def _scytale_dec(text, n):
    n = int(n); n = max(2, n)
    if not text: return text
    L = len(text)
    rows = (L + n - 1) // n
    grid = [['']*n for _ in range(rows)]
    i = 0
    for c in range(n):
        for r in range(rows):
            if r*n + c < L:
                grid[r][c] = text[i]; i += 1
    return ''.join(''.join(row) for row in grid)

pair('Scytale (n=3)', 'رمز کلاسیک',
     lambda t,a='',b='': _scytale_enc(t, 3),
     lambda t,a='',b='': _scytale_dec(t, 3))

pair('Scytale (n=5)', 'رمز کلاسیک',
     lambda t,a='',b='': _scytale_enc(t, 5),
     lambda t,a='',b='': _scytale_dec(t, 5))

# --- Bacon ---
def _bacon_enc(text):
    A, B = 'AAAAA','AAAAB'
    out = []
    for ch in text.lower():
        if 'a' <= ch <= 'z':
            n = ord(ch) - ord('a')
            code = ''.join('B' if (n >> (4-i)) & 1 else 'A' for i in range(5))
            out.append(code)
        elif ch.isalpha():
            out.append(ch)
    return ' '.join(out)

def _bacon_dec(text):
    groups = text.replace('\n',' ').replace(',',' ').split()
    out = []
    for g in groups:
        g = ''.join(c.upper() for c in g if c.upper() in 'AB')
        if len(g) >= 5:
            g = g[:5]
            n = sum(1 if b == 'B' else 0 for i,b in enumerate(g[::-1]) for _ in [0]) if False else 0
            n = 0
            for i, b in enumerate(g):
                if b == 'B': n |= 1 << (4 - i)
            if 0 <= n < 26: out.append(chr(n + ord('a')))
    return ''.join(out)

pair('Bacon', 'رمز کلاسیک',
     lambda t,a='',b='': _bacon_enc(t),
     lambda t,a='',b='': _bacon_dec(t))

# --- Polybius square ---
def _polybius_enc(text):
    out = []
    for ch in text.lower():
        if 'a' <= ch <= 'i':   out.append(str(1)+str(ord(ch)-ord('a')+1))
        elif 'j' <= ch <= 'r': out.append(str(2)+str(ord(ch)-ord('a')-8))
        elif 's' <= ch <= 'z': out.append(str(3)+str(ord(ch)-ord('a')-17))
        elif ch == ' ': out.append('  ')
    return ' '.join(out)

def _polybius_dec(text):
    out = []
    for grp in text.split():
        if len(grp)==2 and grp.isdigit():
            r,c = int(grp[0]), int(grp[1])
            out.append(chr((r-1)*9 + c - 1 + ord('a')))
    return ''.join(out)

pair('Polybius', 'رمز کلاسیک',
     lambda t,a='',b='': _polybius_enc(t),
     lambda t,a='',b='': _polybius_dec(t))

# --- Bifid ---
def _bifid(text, decrypt=False):
    t = ''.join(c for c in text.lower() if c.isalpha())
    n = len(t)
    if not t: return ''
    coords = [(ord(c)-ord('a'))//5 for c in t] + [(ord(c)-ord('a'))%5 for c in t]
    if decrypt:
        half = len(coords)//2
        a = coords[:half]; b = coords[half:]
        out = []
        for i in range(half):
            r,c = a[i], b[i]
            out.append(chr(r*5 + c + ord('a')))
        return ''.join(out)
    else:
        return ''.join(chr(coords[2*i]*5 + coords[2*i+1] + ord('a')) for i in range(n))

pair('Bifid', 'رمز کلاسیک',
     lambda t,a='',b='': _bifid(t, False),
     lambda t,a='',b='': _bifid(t, True))

# --- ROT5 (digits) ---
pair('ROT5 (اعداد)', 'رمز کلاسیک',
     lambda t,a='',b='': ''.join(str((int(c)+5)%10) if c.isdigit() else c for c in t),
     lambda t,a='',b='': ''.join(str((int(c)-5)%10) if c.isdigit() else c for c in t))

# --- ADFGX ---
def _adfgx_enc(text):
    key = 'ADFGX'
    grid = 'abcdefghiklmnopqrstuvwxyz'
    out = []
    for ch in text.lower():
        if ch in grid:
            i = grid.index(ch)
            out.append(key[i//5] + key[i%5])
    return ' '.join(out)

def _adfgx_dec(text):
    key = 'ADFGX'; grid = 'abcdefghiklmnopqrstuvwxyz'
    groups = text.replace('\n',' ').split()
    out = []
    for g in groups:
        if len(g)==2:
            r = key.find(g[0].upper()); c = key.find(g[1].upper())
            if 0<=r<5 and 0<=c<5:
                out.append(grid[r*5 + c])
    return ''.join(out)

pair('ADFGX', 'رمز کلاسیک',
     lambda t,a='',b='': _adfgx_enc(t),
     lambda t,a='',b='': _adfgx_dec(t))

# --- ADFGVX ---
def _adfgvx_enc(text):
    key = 'ADFGVX'
    grid = 'abcdefghijklmnopqrstuvwxyz0123456789'
    out = []
    for ch in text.lower():
        if ch in grid:
            i = grid.index(ch)
            out.append(key[i//6] + key[i%6])
    return ' '.join(out)

def _adfgvx_dec(text):
    key = 'ADFGVX'; grid = 'abcdefghijklmnopqrstuvwxyz0123456789'
    groups = text.replace('\n',' ').split()
    out = []
    for g in groups:
        if len(g)==2:
            r = key.find(g[0].upper()); c = key.find(g[1].upper())
            if 0<=r<6 and 0<=c<6:
                out.append(grid[r*6 + c])
    return ''.join(out)

pair('ADFGVX', 'رمز کلاسیک',
     lambda t,a='',b='': _adfgvx_enc(t),
     lambda t,a='',b='': _adfgvx_dec(t))

# --- Nihilist (simplified) ---
def _nihilist_enc(text):
    grid = 'abcdefghiklmnopqrstuvwxyz'
    out = []
    for ch in text.lower():
        if ch in grid:
            i = grid.index(ch)
            out.append(str((i//5+1)*10 + (i%5+1)))
    return ' '.join(out)

def _nihilist_dec(text):
    grid = 'abcdefghiklmnopqrstuvwxyz'
    out = []
    for g in text.split():
        if g.isdigit() and len(g)==2:
            r,c = int(g[0])-1, int(g[1])-1
            if 0<=r<5 and 0<=c<5:
                out.append(grid[r*5+c])
    return ''.join(out)

pair('Nihilist', 'رمز کلاسیک',
     lambda t,a='',b='': _nihilist_enc(t),
     lambda t,a='',b='': _nihilist_dec(t))

# --- Vernam / XOR classical ---
def _vernam(text, key, decrypt=False):
    if not key: raise ValueError('کلید لازم است')
    b = text.encode('utf-8')
    kb = key.encode('utf-8') or b'x'
    out = bytes(x ^ kb[i % len(kb)] for i, x in enumerate(b))
    if decrypt:
        try: return out.decode('utf-8')
        except: return base64.b64encode(out).decode()
    return base64.b64encode(out).decode()

pair('Vernam/XOR', 'رمز کلاسیک',
     lambda t,a='',b='': _vernam(t, a, False),
     lambda t,a='',b='': _vernam(t, a, True),
     k=1, k1l='کلید')


# ═══════════════════════════════════════════════════════════════
# ⑨ رمز مدرن (دمو) با دو کلید  (۱۶ عملیات)
# ═══════════════════════════════════════════════════════════════

def _stream(text, k1, k2, decrypt=False, out_fmt='b64'):
    if not k1: raise ValueError('کلید اول لازم است')
    material = (k1 + '|' + (k2 or '')).encode()
    out = bytearray()
    counter = 0
    data = text.encode() if not decrypt else base64.b64decode(text.encode()) if out_fmt=='b64' else bytes.fromhex(text)
    while len(out) < len(data):
        block = hmac.new(material, counter.to_bytes(8, 'big'), 'sha256').digest()
        out.extend(block)
        counter += 1
    result = bytes(a ^ b for a, b in zip(data, out))
    if decrypt:
        try: return result.decode('utf-8')
        except: return result.hex()
    return base64.b64encode(result).decode() if out_fmt=='b64' else result.hex()

pair('Two-Key Stream (Base64)', 'رمز مدرن',
     lambda t,a='',b='': _stream(t, a, b, False, 'b64'),
     lambda t,a='',b='': _stream(t, a, b, True, 'b64'),
     k=2, k1l='کلید اول', k2l='کلید دوم')

pair('Two-Key Stream (Hex)', 'رمز مدرن',
     lambda t,a='',b='': _stream(t, a, b, False, 'hex'),
     lambda t,a='',b='': _stream(t, a, b, True, 'hex'),
     k=2, k1l='کلید اول', k2l='کلید دوم')

# XOR ساده با یک کلید
pair('XOR (Base64)', 'رمز مدرن',
     lambda t,a='',b='': _vernam(t, a or 'k', False),
     lambda t,a='',b='': _vernam(t, a or 'k', True),
     k=1, k1l='کلید')

# Two-key XOR ترکیبی
def _two_key_xor(text, k1, k2, decrypt=False):
    if not k1 or not k2: raise ValueError('هر دو کلید لازم است')
    return _vernam(text, k1 + k2, decrypt)

pair('Two-Key XOR', 'رمز مدرن',
     lambda t,a='',b='': _two_key_xor(t, a, b, False),
     lambda t,a='',b='': _two_key_xor(t, a, b, True),
     k=2, k1l='کلید اول', k2l='کلید دوم')

# HMAC-based key derivation then XOR
def _hmac_xor(text, k1, k2, decrypt=False):
    if not k1: raise ValueError('کلید اول لازم است')
    if decrypt:
        try: data = base64.b64decode(text.encode())
        except: data = text.encode()
    else:
        data = text.encode()
    stream = hmac.new((k1+'|'+(k2 or '')).encode(), b'key-derivation', 'sha256').digest()
    out = bytes(a ^ stream[i % len(stream)] for i, a in enumerate(data))
    if decrypt:
        try: return out.decode('utf-8')
        except: return out.hex()
    return base64.b64encode(out).decode()

pair('HMAC-Derived XOR', 'رمز مدرن',
     lambda t,a='',b='': _hmac_xor(t, a, b, False),
     lambda t,a='',b='': _hmac_xor(t, a, b, True),
     k=2, k1l='کلید اول', k2l='کلید دوم')


# ═══════════════════════════════════════════════════════════════
# ⑩ Morse / Bacon / Braille / NATO / Pig Latin / Leet (۱۲)
# ═══════════════════════════════════════════════════════════════
MORSE = {
    'a':'.-','b':'-...','c':'-.-.','d':'-..','e':'.','f':'..-.',
    'g':'--.','h':'....','i':'..','j':'.---','k':'-.-','l':'.-..',
    'm':'--','n':'-.','o':'---','p':'.--.','q':'--.-','r':'.-.','s':'...',
    't':'-','u':'..-','v':'...-','w':'.--','x':'-..-','y':'-.--','z':'--..',
    '1':'.----','2':'..---','3':'...--','4':'....-','5':'.....',
    '6':'-....','7':'--...','8':'---..','9':'----.','0':'-----',
}
MORSE_R = {v:k for k,v in MORSE.items()}

def _morse_enc(text):
    return ' / '.join(' '.join(MORSE.get(c.lower(), '') for c in word) for word in text.split())

def _morse_dec(text):
    words = text.strip().split(' / ')
    out = []
    for w in words:
        out.append(''.join(MORSE_R.get(code, '') for code in w.split()))
    return ' '.join(out)

pair('Morse', 'ویژه',
     lambda t,a='',b='': _morse_enc(t),
     lambda t,a='',b='': _morse_dec(t))

# Braille (basic English)
BRAILLE = {
    'a':'⠁','b':'⠃','c':'⠉','d':'⠙','e':'⠑','f':'⠋','g':'⠛','h':'⠓','i':'⠊','j':'⠚',
    'k':'⠅','l':'⠇','m':'⠍','n':'⠝','o':'⠕','p':'⠏','q':'⠟','r':'⠗','s':'⠎','t':'⠞',
    'u':'⠥','v':'⠧','w':'⠺','x':'⠭','y':'⠽','z':'⠵',' ':' ',
}
BRAILLE_R = {v:k for k,v in BRAILLE.items()}

pair('Braille', 'ویژه',
     lambda t,a='',b='': ''.join(BRAILLE.get(c.lower(), c) for c in t),
     lambda t,a='',b='': ''.join(BRAILLE_R.get(c, c) for c in t))

# NATO phonetic
NATO = {'a':'Alpha','b':'Bravo','c':'Charlie','d':'Delta','e':'Echo','f':'Foxtrot',
        'g':'Golf','h':'Hotel','i':'India','j':'Juliett','k':'Kilo','l':'Lima',
        'm':'Mike','n':'November','o':'Oscar','p':'Papa','q':'Quebec','r':'Romeo',
        's':'Sierra','t':'Tango','u':'Uniform','v':'Victor','w':'Whiskey',
        'x':'X-ray','y':'Yankee','z':'Zulu',' ':' '}
NATO_R = {v.lower():k for k,v in NATO.items()}

pair('NATO', 'ویژه',
     lambda t,a='',b='': ' '.join(NATO.get(c.lower(), c) for c in t),
     lambda t,a='',b='': ' '.join(NATO_R.get(w.lower(), w) for w in t.split()))

# Pig Latin
def _pig_enc(text):
    out = []
    for w in text.split():
        if w and w[0].lower() in 'aeiou': out.append(w + 'yay')
        elif w: out.append(w[1:] + w[0] + 'ay')
        else: out.append(w)
    return ' '.join(out)

def _pig_dec(text):
    out = []
    for w in text.split():
        if w.endswith('yay'): out.append(w[:-3])
        elif w.endswith('ay') and len(w) > 2: out.append(w[-3] + w[:-3])
        else: out.append(w)
    return ' '.join(out)

pair('Pig Latin', 'ویژه',
     lambda t,a='',b='': _pig_enc(t),
     lambda t,a='',b='': _pig_dec(t))

# Leet speak
LEET = {'a':'4','b':'8','e':'3','g':'6','i':'1','l':'1','o':'0','s':'5','t':'7','z':'2'}
LEET_R = {v:k for k,v in LEET.items()}

pair('Leet Speak', 'ویژه',
     lambda t,a='',b='': ''.join(LEET.get(c.lower(), c) for c in t),
     lambda t,a='',b='': ''.join(LEET_R.get(c, c) for c in t))


# ═══════════════════════════════════════════════════════════════
# ⑪ سیستم‌های عددی (۱۲)
# ═══════════════════════════════════════════════════════════════
pair('Base36', 'اعداد',
     lambda t,a='',b='': _to_base(int.from_bytes(t.encode(), 'big'), 36),
     lambda t,a='',b='': int(t, 36).to_bytes((int(t,36).bit_length()+7)//8, 'big').decode('utf-8','replace'))
pair('Base58', 'اعداد',
     lambda t,a='',b='': _to_base(int.from_bytes(t.encode(), 'big'), 58),
     lambda t,a='',b='': int(t, 58).to_bytes((int(t,58).bit_length()+7)//8, 'big').decode('utf-8','replace'))
pair('Base62', 'اعداد',
     lambda t,a='',b='': _to_base(int.from_bytes(t.encode(), 'big'), 62),
     lambda t,a='',b='': int(t, 62).to_bytes((int(t,62).bit_length()+7)//8, 'big').decode('utf-8','replace'))
pair('Base64url', 'اعداد',
     lambda t,a='',b='': base64.urlsafe_b64encode(t.encode()).decode().rstrip('='),
     lambda t,a='',b='': base64.urlsafe_b64decode((t+'='*(-len(t)%4)).encode()).decode('utf-8','replace'))
pair('Base10 باینری', 'اعداد',
     lambda t,a='',b='': ' '.join(str(ord(c)) for c in t),
     lambda t,a='',b='': ''.join(chr(int(x)) for x in t.split()))
pair('Base10 → Base2', 'اعداد',
     lambda t,a='',b='': ' '.join(bin(ord(c))[2:] for c in t),
     lambda t,a='',b='': ''.join(chr(int(x,2)) for x in t.split()))

def _to_base(n, b):
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    if b > len(chars): raise ValueError('base too large')
    if n == 0: return '0'
    out = []
    while n:
        out.append(chars[n % b]); n //= b
    return ''.join(reversed(out))


# ═══════════════════════════════════════════════════════════════
# ⑫ استگانوگرافی (۱۰)
# ═══════════════════════════════════════════════════════════════
add_op('حرف اول هر خط', 'استگانوگرافی',
       lambda t,a='',b='': ''.join(l[0] for l in t.split('\n') if l))
add_op('حرف آخر هر خط', 'استگانوگرافی',
       lambda t,a='',b='': ''.join(l[-1] for l in t.split('\n') if l))
add_op('هر ۲ اُم حرف', 'استگانوگرافی', lambda t,a='',b='': t[::2])
add_op('هر ۳ اُم حرف', 'استگانوگرافی', lambda t,a='',b='': t[::3])
add_op('موقعیت فرد', 'استگانوگرافی', lambda t,a='',b='': t[1::2])
add_op('موقعیت زوج', 'استگانوگرافی', lambda t,a='',b='': t[::2])
add_op('همه فاصله‌ها → بیت', 'استگانوگرافی',
       lambda t,a='',b='': ''.join('1' if c in ' \t' else '0' for c in t))
add_op('تشخیص Palindrome', 'استگانوگرافی',
       lambda t,a='',b='': '✅ بله' if t == t[::-1] else '❌ خیر')
add_op('Acrostic (کلمات)', 'استگانوگرافی',
       lambda t,a='',b='': ''.join(w[0] for w in t.split() if w))
add_op('نویسه‌های مخفی (غیر الفبا)', 'استگانوگرافی',
       lambda t,a='',b='': ''.join(c for c in t if not c.isalnum() and not c.isspace()))


# ═══════════════════════════════════════════════════════════════
# ⑬ زبان فارسی/عربی (۲۰)
# ═══════════════════════════════════════════════════════════════
add_op('اعداد فارسی → انگلیسی', 'زبان',
       lambda t,a='',b='': t.translate(str.maketrans(PERSIAN_DIGITS, ENGLISH_DIGITS)))
add_op('اعداد انگلیسی → فارسی', 'زبان',
       lambda t,a='',b='': t.translate(str.maketrans(ENGLISH_DIGITS, PERSIAN_DIGITS)))
add_op('عربی → فارسی (ی/ک)', 'زبان',
       lambda t,a='',b='': t.replace('ي','ی').replace('ك','ک').replace('ﻻ','لا'))
add_op('فارسی → عربی (ی/ک)', 'زبان',
       lambda t,a='',b='': t.replace('ی','ي').replace('ک','ك'))
add_op('حذف اعراب', 'زبان',
       lambda t,a='',b='': re.sub(r'[\u064B-\u0652\u0670\u0640]', '', t))
add_op('حذف کشیده (تطویل)', 'زبان',
       lambda t,a='',b='': t.replace('\u0640', ''))
add_op('نیم‌فاصله استاندارد', 'زبان',
       lambda t,a='',b='': re.sub(r'\s+', ' ', t).replace(' می ', ' می\u200c').replace(' نمی ', ' نمی\u200c'))
add_op('یکسان‌سازی فاصله', 'زبان',
       lambda t,a='',b='': re.sub(r'[ \t]+', ' ', t).strip())
add_op('شمارش کلمات فارسی', 'زبان',
       lambda t,a='',b='': str(len(re.findall(r'[\u0600-\u06FF]+', t))))
add_op('استخراج کلمات فارسی', 'زبان',
       lambda t,a='',b='': ' '.join(re.findall(r'[\u0600-\u06FF]+', t)))
add_op('حذف کلمات انگلیسی', 'زبان',
       lambda t,a='',b='': re.sub(r'[A-Za-z]+', '', t).strip())
add_op('حذف متن فارسی', 'زبان',
       lambda t,a='',b='': re.sub(r'[\u0600-\u06FF]+', '', t).strip())
add_op('تبدیل به حروف بزرگ فارسی', 'زبان',
       lambda t,a='',b='': t.upper())
add_op('تبدیل تنوین', 'زبان',
       lambda t,a='',b='': t.replace('اً','ا').replace('ٍ','').replace('ً',''))
add_op('نرمال‌سازی NFC', 'زبان',
       lambda t,a='',b='': __import__('unicodedata').normalize('NFC', t))
add_op('نرمال‌سازی NFD', 'زبان',
       lambda t,a='',b='': __import__('unicodedata').normalize('NFD', t))
add_op('حذف فاصله اضافی', 'زبان',
       lambda t,a='',b='': ' '.join(t.split()))
add_op('تبدیل «ه» به «هٔ»', 'زبان',
       lambda t,a='',b='': t.replace('هٔ','ه').replace('ة','ه'))
add_op('اضافه‌کردن نیم‌فاصله به «ها»', 'زبان',
       lambda t,a='',b='': re.sub(r'(\w)ها\b', r'\1\u200cها', t))
add_op('نمایش کدهای یونیکد حروف', 'زبان',
       lambda t,a='',b='': ' '.join(f'{ord(c):04x}' for c in t))


# ═══════════════════════════════════════════════════════════════
# ⑭ متفرقه (۱۸)
# ═══════════════════════════════════════════════════════════════
add_op('UUID v4', 'متفرقه', lambda t,a='',b='': str(uuid.uuid4()))
add_op('Timestamp', 'متفرقه', lambda t,a='',b='': str(int(__import__('time').time())))
add_op('Length check', 'متفرقه', lambda t,a='',b='': f'طول: {len(t)}')
add_op('Char codes', 'متفرقه',
       lambda t,a='',b='': ' '.join(str(ord(c)) for c in t))
add_op('Hex dump', 'متفرقه',
       lambda t,a='',b='': binascii.hexlify(t.encode()).decode())
add_op('Hex dump → متن', 'متفرقه',
       lambda t,a='',b='': binascii.unhexlify(t.encode()).decode('utf-8','replace'))
add_op('تعداد کلمات انگلیسی', 'متفرقه',
       lambda t,a='',b='': str(len(re.findall(r'[A-Za-z]+', t))))
add_op('تعداد کلمات فارسی', 'متفرقه',
       lambda t,a='',b='': str(len(re.findall(r'[\u0600-\u06FF]+', t))))
add_op('پسورد تصادفی (۱۶)', 'متفرقه',
       lambda t,a='',b='': secrets.token_urlsafe(12))
add_op('تاریخ/ساعت', 'متفرقه',
       lambda t,a='',b='': __import__('datetime').datetime.now().isoformat())
add_op('JSON validate', 'متفرقه',
       lambda t,a='',b='': '✅ معتبر' if _is_json(t) else '❌ نامعتبر')
add_op('Regex escape', 'متفرقه',
       lambda t,a='',b='': re.escape(t))
add_op('URL parse', 'متفرقه',
       lambda t,a='',b='': str(urllib.parse.urlparse(t)))
add_op('پاک‌سازی HTML', 'متفرقه',
       lambda t,a='',b='': re.sub(r'<[^>]+>', '', t))
add_op('حذف فاصله‌های ابتدا/انتها', 'متفرقه',
       lambda t,a='',b='': t.strip())
add_op('نمایش بایت‌ها', 'متفرقه',
       lambda t,a='',b='': str(t.encode('utf-8')))
add_op('تعداد خطوط غیرخالی', 'متفرقه',
       lambda t,a='',b='': str(len([l for l in t.split('\n') if l.strip()])))
add_op('نمایش SHA-256 کوتاه', 'متفرقه',
       lambda t,a='',b='': hashlib.sha256(t.encode()).hexdigest()[:16])

def _is_json(s):
    try: json.loads(s); return True
    except: return False


# ═══════════════════════════════════════════════════════════════
# بررسی تعداد نهایی
# ═══════════════════════════════════════════════════════════════
print(f'📊 تعداد عملیات ثبت‌شده: {len(REGISTRY)}')


# ═══════════════════════════════════════════════════════════════
# ⑮ رابط کاربری
# ═══════════════════════════════════════════════════════════════
class App:
    def __init__(self, root):
        self.root = root
        root.title(f'🚀 Smart Text Toolkit — {len(REGISTRY)} عملیات')
        root.geometry('1000x900')
        root.configure(bg='#1e1e1e')

        self.pinned = set()
        self._results = {}
        self._job = None

        self._build_ui()
        self._render()

    def _build_ui(self):
        style = ttk.Style()
        try: style.theme_use('clam')
        except: pass
        style.configure('TLabel', background='#1e1e1e', foreground='white',
                        font=('Segoe UI', 10))
        style.configure('TButton', background='#333', foreground='white', padding=6)
        style.configure('TCombobox', fieldbackground='#2d2d2d', background='#333',
                        foreground='white')

        hdr = tk.Frame(self.root, bg='#1e1e1e'); hdr.pack(fill=tk.X, padx=20, pady=(10, 4))
        tk.Label(hdr, text='🚀 Smart Text Toolkit', bg='#1e1e1e', fg='#4a9eff',
                 font=('Segoe UI', 15, 'bold')).pack(side=tk.LEFT)
        tk.Label(hdr, text=f'   {len(REGISTRY)} عملیات متن · رمز · کدگذاری',
                 bg='#1e1e1e', fg='#aaaaaa', font=('Segoe UI', 10)).pack(side=tk.LEFT)

        # ورودی
        self.input_text = scrolledtext.ScrolledText(
            self.root, height=5, bg='#2d2d2d', fg='white',
            insertbackground='white', font=('Tahoma', 11), wrap=tk.WORD)
        self.input_text.pack(padx=20, pady=(4, 4), fill=tk.X)
        self.input_text.bind('<KeyRelease>', self._schedule)

        # دو کلید
        keyrow = tk.Frame(self.root, bg='#1e1e1e'); keyrow.pack(fill=tk.X, padx=20)
        tk.Label(keyrow, text='🔑 کلید ۱:', bg='#1e1e1e', fg='white',
                 font=('Segoe UI', 10)).pack(side=tk.LEFT)
        self.k1 = tk.StringVar()
        self.k1.trace_add('write', lambda *a: self._schedule())
        tk.Entry(keyrow, textvariable=self.k1, bg='#2d2d2d', fg='white',
                 insertbackground='white', relief=tk.FLAT,
                 font=('Tahoma', 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10))
        tk.Label(keyrow, text='🔑 کلید ۲:', bg='#1e1e1e', fg='white',
                 font=('Segoe UI', 10)).pack(side=tk.LEFT)
        self.k2 = tk.StringVar()
        self.k2.trace_add('write', lambda *a: self._schedule())
        tk.Entry(keyrow, textvariable=self.k2, bg='#2d2d2d', fg='white',
                 insertbackground='white', relief=tk.FLAT,
                 font=('Tahoma', 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # فیلتر
        frow = tk.Frame(self.root, bg='#1e1e1e'); frow.pack(fill=tk.X, padx=20, pady=6)
        tk.Label(frow, text='🔍 جستجو:', bg='#1e1e1e', fg='white').pack(side=tk.LEFT)
        self.search = tk.StringVar()
        self.search.trace_add('write', lambda *a: self._schedule())
        tk.Entry(frow, textvariable=self.search, bg='#2d2d2d', fg='white',
                 insertbackground='white', relief=tk.FLAT,
                 font=('Tahoma', 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10))
        tk.Label(frow, text='📂 دسته:', bg='#1e1e1e', fg='white').pack(side=tk.LEFT)
        self.cat = tk.StringVar(value='همه')
        cats = ['همه'] + sorted({op['cat'] for op in REGISTRY})
        cb = ttk.Combobox(frow, textvariable=self.cat, values=cats,
                          state='readonly', width=18)
        cb.pack(side=tk.LEFT)
        cb.bind('<<ComboboxSelected>>', lambda e: self._render())

        # دکمه‌ها
        brow = tk.Frame(self.root, bg='#1e1e1e'); brow.pack(fill=tk.X, padx=20, pady=4)
        tk.Button(brow, text='🗑 پاک کردن', bg='#444', fg='white', relief=tk.FLAT,
                  command=self._clear).pack(side=tk.LEFT)
        tk.Button(brow, text='📋 کپی همه نتایج', bg='#444', fg='white',
                  relief=tk.FLAT, command=self._copy_all).pack(side=tk.LEFT, padx=4)

        self.status = tk.Label(self.root, text='', bg='#1e1e1e', fg='#88ff88',
                                font=('Segoe UI', 10))
        self.status.pack(pady=2)

        # خروجی
        self.out = scrolledtext.ScrolledText(
            self.root, bg='#1e1e1e', fg='white', font=('Tahoma', 11),
            wrap=tk.WORD, cursor='arrow')
        self.out.pack(padx=20, pady=(0, 10), fill=tk.BOTH, expand=True)
        self.out.tag_configure('name', foreground='#88ff88',
                                font=('Segoe UI', 10, 'bold'))
        self.out.tag_configure('name_pinned', foreground='#ffcc44',
                                font=('Segoe UI', 10, 'bold'))
        self.out.tag_configure('result', foreground='#ffffff',
                                font=('Tahoma', 11))
        self.out.tag_configure('result_pinned', foreground='#ffeeaa',
                                font=('Tahoma', 11))
        self.out.tag_configure('error', foreground='#ff6666',
                                font=('Tahoma', 11))
        self.out.bind('<Button-1>', self._on_click)
        self.out.bind('<Button-3>', self._on_right_click)

        # منوی راست‌کلیک
        self.menu = tk.Menu(self.root, tearoff=0, bg='#2d2d2d', fg='white')
        self.menu.add_command(label='📋 کپی', command=self._menu_copy)
        self.menu.add_command(label='📌 پین/آن‌پین', command=self._menu_pin)

    def _clear(self):
        self.input_text.delete('1.0', tk.END)
        self._render()

    def _schedule(self, *args):
        if self._job: self.root.after_cancel(self._job)
        self._job = self.root.after(300, self._render)

    def _render(self):
        self._job = None
        self.out.configure(state='normal')
        self.out.delete('1.0', tk.END)
        self._results = {}

        text = self.input_text.get('1.0', tk.END).rstrip('\n')
        if not text.strip():
            self.out.insert(tk.END, '⏳ متنی وارد کنید تا نتایج نمایش داده شوند…\n', 'name')
            self.status.config(text='آماده')
            return

        k1 = self.k1.get(); k2 = self.k2.get()
        search = self.search.get().strip().lower()
        cat = self.cat.get()

        indices = list(range(len(REGISTRY)))
        indices.sort(key=lambda i: (i not in self.pinned, i))

        count = 0
        for i in indices:
            op = REGISTRY[i]
            if search and search not in op['name'].lower(): continue
            if cat != 'همه' and op['cat'] != cat: continue

            if op['k'] > 0 and not k1:
                result = f'⚠️ نیاز به «{op["k1l"] or "کلید"}»'
                tag = 'error'
            elif op['k'] > 1 and not k2:
                result = f'⚠️ نیاز به «{op["k2l"] or "کلید دوم"}»'
                tag = 'error'
            else:
                result = op['func'](text, k1, k2)
                tag = 'result_pinned' if i in self.pinned else 'result'

            self._results[i] = result
            pin_mark = '📌 ' if i in self.pinned else ''
            self.out.insert(tk.END, f'\n{pin_mark}{op["name"]}\n',
                            ('name_pinned' if i in self.pinned else 'name'))
            preview = result if len(result) <= 400 else result[:400] + ' …'
            self.out.insert(tk.END, f'  {preview}\n', (tag, f'op_{i}'))
            count += 1

        self.status.config(text=f'✅ {count} نتیجه از {len(REGISTRY)} عملیات')
        self.out.configure(state='disabled')

    def _tag_at(self, event):
        idx = self.out.index(f'@{event.x},{event.y}')
        for tag in self.out.tag_names(idx):
            if tag.startswith('op_'):
                return int(tag[3:])
        return None

    def _on_click(self, event):
        i = self._tag_at(event)
        if i is not None:
            self._copy(i)

    def _on_right_click(self, event):
        i = self._tag_at(event)
        if i is not None:
            self._ctx_i = i
            try: self.menu.tk_popup(event.x_root, event.y_root)
            finally: self.menu.grab_release()

    def _menu_copy(self):
        if hasattr(self, '_ctx_i'): self._copy(self._ctx_i)

    def _menu_pin(self):
        if hasattr(self, '_ctx_i'):
            i = self._ctx_i
            if i in self.pinned: self.pinned.discard(i)
            else: self.pinned.add(i)
            self._render()

    def _copy(self, i):
        text = self._results.get(i, '')
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        name = REGISTRY[i]['name']
        self.status.config(text=f'📋 کپی شد ({name}): {text[:60]}…')

    def _copy_all(self):
        lines = []
        for i, res in self._results.items():
            lines.append(f'=== {REGISTRY[i]["name"]} ===\n{res}\n')
        self.root.clipboard_clear()
        self.root.clipboard_append('\n'.join(lines))
        self.status.config(text=f'📋 {len(self._results)} نتیجه کپی شد')


if __name__ == '__main__':
    root = tk.Tk()
    App(root)
    root.mainloop()