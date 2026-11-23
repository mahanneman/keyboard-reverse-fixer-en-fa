#!/usr/bin/env python3
"""Smart Text Toolkit: an offline, standard-library desktop application."""
from __future__ import annotations

import argparse
import base64
import binascii
import bz2
import codecs
import csv
import gzip
import hashlib
import hmac
import html
import io
import json
import lzma
import math
import queue
import re
import secrets
import string
import threading
import time
import unicodedata
import urllib.parse
import uuid
import zlib
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

VERSION = "2.0"
MAX_INPUT = 2_000_000
MAX_OUTPUT = 8_000_000
PERSIAN = "اآبپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی"
LATIN = string.ascii_lowercase

@dataclass(frozen=True)
class Operation:
    name: str
    category: str
    function: Callable[[str, str, str], str]
    description: str
    example: str = "Hello, world!"
    labels: tuple[str, ...] = ()
    defaults: tuple[str, ...] = ()
    warning: str = ""

OPERATIONS: list[Operation] = []

def add(name, category, fn, description, example="Hello, world!", labels=(), defaults=(), warning=""):
    OPERATIONS.append(Operation(name, category, fn, description, example, labels, defaults, warning))

def simple(name, category, fn, description, example="Hello, world!"):
    add(name, category, lambda t, a, b: fn(t), description, example)

def pair(name, category, enc, dec, example="Hello, world!", description="", labels=(), defaults=(), warning=""):
    for action, fn in (("Encode", enc), ("Decode", dec)):
        add(f"{name} / {action}", category, fn,
            description or f"{action} UTF-8 text using {name}. Invalid input is reported, not silently replaced.",
            example if action == "Encode" else "", labels, defaults, warning)

def execute(op, text, a="", b=""):
    if len(text.encode("utf-8")) > MAX_INPUT:
        raise ValueError("Input exceeds the 2 MB UTF-8 limit. Use a smaller document.")
    for label, value in zip(op.labels, (a, b)):
        if not value:
            raise ValueError(f"Enter a value for {label}.")
    result = str(op.function(text, a, b))
    if len(result.encode("utf-8")) > MAX_OUTPUT:
        raise ValueError("Output exceeds the 8 MB UTF-8 limit. Use a smaller input.")
    return result

def words(t):
    return re.findall(r"\b\w+\b", t, re.UNICODE)

def summary(t):
    w = words(t)
    return "\n".join((f"Characters: {len(t):,}", f"UTF-8 bytes: {len(t.encode('utf-8')):,}",
        f"Words: {len(w):,}", f"Lines: {len(t.splitlines()):,}",
        f"Unique words (case-insensitive): {len(set(x.casefold() for x in w)):,}",
        f"Reading time estimate (200 words/minute): {len(w)/200:.2f} minutes"))

simple("Text overview", "Analysis", summary, "Count Unicode code points, UTF-8 bytes and word tokens. Reading time is a rough estimate.")
for name, fn in [
    ("Character count", len), ("Character count without whitespace", lambda t: sum(not c.isspace() for c in t)),
    ("Word count", lambda t: len(words(t))), ("Line count", lambda t: len(t.splitlines())),
    ("Nonempty line count", lambda t: sum(bool(x.strip()) for x in t.splitlines())),
    ("Unique word count", lambda t: len(set(w.casefold() for w in words(t)))),
    ("Longest word", lambda t: max(words(t), key=len, default="")),
    ("Shortest word", lambda t: min(words(t), key=len, default="")),
    ("Digit count", lambda t: sum(c.isdecimal() for c in t)),
    ("Whitespace count", lambda t: sum(c.isspace() for c in t)),
    ("Word frequency", lambda t: "\n".join(f"{w}\t{n}" for w,n in Counter(w.casefold() for w in words(t)).most_common())),
    ("Character frequency", lambda t: "\n".join(f"{c!r}\t{n}" for c,n in Counter(t).most_common())),
    ("Unicode inspector", lambda t: "\n".join(f"U+{ord(c):04X}\t{c!r}\t{unicodedata.name(c, 'UNNAMED')}" for c in t)),
]:
    simple(name, "Analysis", fn, f"Calculate {name.lower()}. Word tools use Unicode word tokens; characters are code points, not visual grapheme clusters.")

for name, fn in [("UPPERCASE", str.upper), ("lowercase", str.lower), ("Title Case", str.title),
                 ("Swap case", str.swapcase), ("Capitalize first character", str.capitalize),
                 ("Casefold", str.casefold),
                 ("Alternating case", lambda t: "".join(c.upper() if i % 2 else c.lower() for i,c in enumerate(t)))]:
    simple(name, "Letter case", fn, f"Apply {name.lower()} to the text. Scripts without letter case remain unchanged.")

for name, fn in [
    ("Trim edges", str.strip), ("Collapse all whitespace", lambda t: " ".join(t.split())),
    ("Collapse horizontal whitespace", lambda t: re.sub(r"[^\S\r\n]+", " ", t)),
    ("Reverse characters", lambda t: t[::-1]), ("Reverse word order", lambda t: " ".join(t.split()[::-1])),
    ("Reverse lines", lambda t: "\n".join(t.splitlines()[::-1])),
    ("Sort lines A to Z", lambda t: "\n".join(sorted(t.splitlines(), key=str.casefold))),
    ("Sort lines Z to A", lambda t: "\n".join(sorted(t.splitlines(), key=str.casefold, reverse=True))),
    ("Remove duplicate lines", lambda t: "\n".join(dict.fromkeys(t.splitlines()))),
    ("Remove blank lines", lambda t: "\n".join(x for x in t.splitlines() if x.strip())),
    ("Trim each line", lambda t: "\n".join(x.strip() for x in t.splitlines())),
    ("Number lines", lambda t: "\n".join(f"{i}. {line}" for i,line in enumerate(t.splitlines(), 1))),
    ("Remove whitespace", lambda t: "".join(c for c in t if not c.isspace())),
    ("Remove punctuation", lambda t: "".join(c for c in t if not unicodedata.category(c).startswith('P'))),
    ("Keep letters only", lambda t: "".join(c for c in t if c.isalpha())),
    ("Keep decimal digits only", lambda t: "".join(c for c in t if c.isdecimal())),
    ("First letter of each word", lambda t: "".join(x[0] for x in t.split())),
    ("First character of each line", lambda t: "".join(x[0] for x in t.splitlines() if x)),
    ("Last character of each line", lambda t: "".join(x[-1] for x in t.splitlines() if x)),
    ("Palindrome check", lambda t: "Yes (exact match)" if t == t[::-1] else "No (exact match)"),
]:
    simple(name, "Text cleanup", fn, f"{name}. Line-based transformations normalize line endings to LF and omit a final line terminator.")
add("Find and replace", "Text cleanup", lambda t,a,b: t.replace(a,b),
    "Replace literal text, not a regular expression. Leave Replacement empty to delete matches.",
    "Hello, world!", ("Find",), ("world",))
# This operation uses a second optional field, exposed explicitly in the UI.
add("Add prefix to lines", "Text cleanup", lambda t,a,b: "\n".join(a+x for x in t.splitlines()),
    "Add the same prefix to every line.", "First\nSecond", ("Prefix",), ("> ",))

for name, enc, dec in [
    ("Base64", base64.b64encode, lambda b: base64.b64decode(b, validate=True)),
    ("Base32", base64.b32encode, lambda b: base64.b32decode(b, casefold=True)),
    ("Hex", base64.b16encode, lambda b: base64.b16decode(b, casefold=True)),
    ("Base85", base64.b85encode, base64.b85decode),
    ("ASCII85", base64.a85encode, base64.a85decode),
]:
    pair(name, "Encoding", lambda t,a,b,f=enc: f(t.encode('utf-8')).decode('ascii'),
         lambda t,a,b,f=dec: f(re.sub(r"\s+", "", t).encode('ascii')).decode('utf-8'))

def url64_decode(t):
    t = re.sub(r"\s+", "", t)
    if not re.fullmatch(r"[A-Za-z0-9_-]*={0,2}", t):
        raise ValueError("Use URL-safe Base64 characters only.")
    return base64.b64decode(t + '=' * (-len(t) % 4), altchars=b'-_', validate=True).decode('utf-8')
pair("Base64 URL-safe", "Encoding", lambda t,a,b: base64.urlsafe_b64encode(t.encode()).decode().rstrip('='), lambda t,a,b: url64_decode(t))
pair("URL percent encoding", "Encoding", lambda t,a,b: urllib.parse.quote(t, safe=''), lambda t,a,b: urllib.parse.unquote(t, errors='strict'))
pair("HTML entities", "Encoding", lambda t,a,b: html.escape(t), lambda t,a,b: html.unescape(t))
pair("ROT13", "Encoding", lambda t,a,b: codecs.encode(t,'rot13'), lambda t,a,b: codecs.encode(t,'rot13'))
def rot47(t):
    return ''.join(chr(33+(ord(c)-33+47)%94) if 33 <= ord(c) <= 126 else c for c in t)
pair("ROT47", "Encoding", lambda t,a,b: rot47(t), lambda t,a,b: rot47(t))
simple("JSON string escape", "Encoding", lambda t: json.dumps(t, ensure_ascii=True), "Return a complete quoted JSON string; preserves Unicode on decode.")
def unquote_json(t):
    obj = json.loads(t)
    if not isinstance(obj, str):
        raise ValueError("Enter a quoted JSON string, not an object or number.")
    return obj
simple("JSON string unescape", "Encoding", unquote_json, "Decode a complete quoted JSON string.", '"Hello\\nworld"')
for name, radix, fmt in [("UTF-8 binary bytes",2,'08b'),("UTF-8 octal bytes",8,'03o'),("UTF-8 decimal bytes",10,'d'),("UTF-8 hex bytes",16,'02x')]:
    pair(name,"Encoding", lambda t,a,b,f=fmt: ' '.join(format(x,f) for x in t.encode()),
         lambda t,a,b,r=radix: bytes(int(x,r) for x in t.split()).decode('utf-8'))

simple("Format JSON", "Structured data", lambda t: json.dumps(json.loads(t), ensure_ascii=False, indent=2), "Validate and format JSON with two-space indentation.", '{"name":"Alex","active":true}')
simple("Minify JSON", "Structured data", lambda t: json.dumps(json.loads(t),ensure_ascii=False,separators=(',',':')), "Remove optional JSON whitespace.", '{"name": "Alex"}')
simple("Validate JSON", "Structured data", lambda t: (json.loads(t), "Valid JSON")[1], "Validate JSON; errors include line and column information.", '{"name":"Alex"}')
def delimit(t, source, target):
    out = io.StringIO(newline='')
    csv.writer(out, delimiter=target, lineterminator='\n').writerows(csv.reader(io.StringIO(t, newline=''), delimiter=source, strict=True))
    return out.getvalue()
simple("CSV to TSV", "Structured data", lambda t: delimit(t, ',', '\t'), "Convert delimited records with proper handling of quotes and embedded delimiters.", 'name,note\nAlex,"Hello, world"')
simple("TSV to CSV", "Structured data", lambda t: delimit(t, '\t', ','), "Convert tab-separated records using CSV quoting rules.", 'name\tnote\nAlex\tHello')
simple("Inspect URL", "Structured data", lambda t: json.dumps(urllib.parse.urlsplit(t)._asdict(), indent=2), "Display URL components without opening a network connection.", 'https://example.com/path?q=hello#section')
simple("Escape regex characters", "Structured data", re.escape, "Escape text for use as a literal regular-expression fragment.", 'price (EUR): 10.00')

# Read at most one byte beyond the limit rather than decompressing without a bound.
def decompress_text(t, kind):
    raw = base64.b64decode(re.sub(r'\s+','',t), validate=True)
    if kind == 'zlib':
        d = zlib.decompressobj()
        data = d.decompress(raw, MAX_OUTPUT + 1)
        if len(data) > MAX_OUTPUT or d.unconsumed_tail:
            raise ValueError("Decompressed data exceeds the 8 MB limit.")
        if not d.eof or d.unused_data:
            raise ValueError("Truncated stream or unexpected trailing compressed data.")
    else:
        cls = {'gzip': gzip.GzipFile, 'bz2': bz2.BZ2File, 'lzma': lzma.LZMAFile}[kind]
        with (cls(fileobj=io.BytesIO(raw), mode='rb') if kind == 'gzip' else cls(io.BytesIO(raw), 'rb')) as stream:
            data = stream.read(MAX_OUTPUT + 1)
        if len(data) > MAX_OUTPUT:
            raise ValueError("Decompressed data exceeds the 8 MB limit.")
    return data.decode('utf-8')
for name, kind, comp in [("Zlib",'zlib',zlib.compress),("Gzip",'gzip',gzip.compress),("BZ2",'bz2',bz2.compress),("LZMA",'lzma',lzma.compress)]:
    add(f"{name} / Compress", "Compression", lambda t,a,b,f=comp: base64.b64encode(f(t.encode())).decode(), "Compress UTF-8 text and return Base64. Small documents may get larger.")
    add(f"{name} / Decompress", "Compression", lambda t,a,b,k=kind: decompress_text(t,k), "Decode Base64 and decompress UTF-8 text with an 8 MB output limit.", "")

for algo in ['md5','sha1','sha224','sha256','sha384','sha512','sha3_224','sha3_256','sha3_384','sha3_512','blake2b','blake2s']:
    add(algo.upper(), "Hashes", lambda t,a,b,h=algo: hashlib.new(h,t.encode()).hexdigest(),
        "Compute a one-way digest of UTF-8 text. Hashes cannot be decrypted.",
        warning="MD5 and SHA-1 are legacy algorithms; do not use them for security-sensitive integrity checks." if algo in ('md5','sha1') else "A plain hash is not password storage or encryption.")
for algo in ['sha256','sha512']:
    add(f"HMAC-{algo.upper()}", "Hashes", lambda t,a,b,h=algo: hmac.new(a.encode(),t.encode(),h).hexdigest(),
        "Compute a keyed message authentication code. Keep the secret key private.", labels=("Secret key",))
simple("CRC32", "Hashes", lambda t: f'{zlib.crc32(t.encode()):08x}', "Compute an error-detection checksum, not a security hash.")
simple("Adler32", "Hashes", lambda t: f'{zlib.adler32(t.encode()):08x}', "Compute an error-detection checksum, not a security hash.")

WARNING = "Educational only. Classical ciphers and repeating-key XOR do not protect sensitive information."
def shift(t, n, alphabet=LATIN):
    table = {c:alphabet[(i+n)%len(alphabet)] for i,c in enumerate(alphabet)}
    if alphabet == LATIN:
        table.update({k.upper():v.upper() for k,v in list(table.items())})
    return ''.join(table.get(c,c) for c in t)
def vig(t,key,decrypt=False,beaufort=False,alphabet=LATIN):
    key = ''.join(c for c in key.lower() if c in alphabet)
    if not key:
        raise ValueError("The key must contain letters from the selected alphabet.")
    out=[]
    i=0
    for c in t:
        low=c.lower()
        if low in alphabet:
            x,k=alphabet.index(low),alphabet.index(key[i%len(key)])
            n = k-x if beaufort else x + (-k if decrypt else k)
            v=alphabet[n%len(alphabet)]
            out.append(v.upper() if c.isupper() else v)
            i+=1
        else:
            out.append(c)
    return ''.join(out)
for name, fn in [("Caesar",lambda t,a,b,d: shift(t,(-1 if d else 1)*int(a))),
    ("Vigenere", lambda t,a,b,d: vig(t,a,d)),
    ("Persian Vigenere",lambda t,a,b,d: vig(t,a,d,alphabet=PERSIAN)),
    ("Beaufort",lambda t,a,b,d: vig(t,a,beaufort=True))]:
    pair(name,"Educational ciphers",lambda t,a,b,f=fn:f(t,a,b,False),lambda t,a,b,f=fn:f(t,a,b,True),
         description="Transform letters while preserving other characters. Beaufort uses the same transform in both directions.",
         labels=("Shift" if name=='Caesar' else "Key",),defaults=("3" if name=='Caesar' else "کلید" if name.startswith('Persian') else "LEMON",),warning=WARNING)
def atbash(t):
    return t.translate(str.maketrans(LATIN+LATIN.upper(), LATIN[::-1]+LATIN.upper()[::-1]))
pair("Atbash","Educational ciphers",lambda t,a,b:atbash(t),lambda t,a,b:atbash(t),warning=WARNING)
def columnar(t,key,decrypt=False):
    if not key.strip():
        raise ValueError("Enter a nonblank key.")
    n=len(key)
    order=sorted(range(n), key=lambda i:(key[i],i))
    if not decrypt:
        return ''.join(t[i::n] for i in order)
    cols={}
    offset=0
    for i in order:
        length=len(t)//n + (i < len(t)%n)
        cols[i]=t[offset:offset+length]
        offset+=length
    return ''.join(cols[i%n][i//n] for i in range(len(t)))
pair("Columnar transposition","Educational ciphers",lambda t,a,b:columnar(t,a),lambda t,a,b:columnar(t,a,True),
     description="Reorder columns without adding or deleting padding. Repeated key characters are supported.", labels=("Key",),defaults=("ZEBRA",),warning=WARNING)
def rail(t,n,decrypt=False):
    n=int(n)
    if not 2<=n<=100:
        raise ValueError("Rails must be between 2 and 100.")
    cycle=2*(n-1)
    positions=[min(i%cycle,cycle-i%cycle) for i in range(len(t))]
    order=sorted(range(len(t)),key=positions.__getitem__)
    if not decrypt:
        return ''.join(t[i] for i in order)
    out=['']*len(t)
    for i,c in zip(order,t):out[i]=c
    return ''.join(out)
pair("Rail fence","Educational ciphers",lambda t,a,b:rail(t,a),lambda t,a,b:rail(t,a,True),labels=("Rails (2-100)",),defaults=("3",),warning=WARNING)
def xor(t,key,decrypt=False):
    raw=base64.b64decode(t,validate=True) if decrypt else t.encode()
    k=key.encode()
    data=bytes(x^k[i%len(k)] for i,x in enumerate(raw))
    return data.decode('utf-8') if decrypt else base64.b64encode(data).decode()
pair("Repeating-key XOR (Base64)","Educational ciphers",lambda t,a,b:xor(t,a),lambda t,a,b:xor(t,a,True),labels=("Key",),defaults=("example",),warning=WARNING)

KB=dict(zip("qwertyuiop[]asdfghjkl;'zxcvbnm,", "ضصثقفغعهخحجچشسیبلاتنمکپظطزرذدئو"))
# Standard Windows Persian key positions (unshifted), with shifted Z for ژ.
KB.update({'\\':'گ', 'Z':'ژ', ';':'پ', "'":'ک'})
simple("English keys to Persian", "Persian and Unicode", lambda t: ''.join(KB.get(c,KB.get(c.lower(),c)) for c in t), "Repair text typed with English selected instead of Persian. Uses common Windows Persian key positions.", 'sghl')
simple("Persian keys to English", "Persian and Unicode", lambda t: ''.join({v:k for k,v in KB.items()}.get(c,c) for c in t), "Map supported Persian letters back to English keyboard positions.", 'سلام')
for name,fn in [
    ("Persian digits to English",lambda t:t.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩','01234567890123456789'))),
    ("English digits to Persian",lambda t:t.translate(str.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹'))),
    ("Arabic letters to Persian",lambda t:t.replace('ي','ی').replace('ك','ک')),
    ("Persian letters to Arabic",lambda t:t.replace('ی','ي').replace('ک','ك')),
    ("Remove Arabic diacritics",lambda t:re.sub('[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]','',t)),
    ("Remove tatweel",lambda t:t.replace('\u0640','')),
    ("Remove zero-width non-joiner",lambda t:t.replace('\u200c','')),
]:
    simple(name,"Persian and Unicode",fn,f"{name}; preserve unrelated text.", 'سلام دنیا ۱۲۳')
for form in ['NFC','NFD','NFKC','NFKD']:
    simple(f"Normalize {form}","Persian and Unicode",lambda t,f=form:unicodedata.normalize(f,t),
           f"Apply Unicode {form} normalization. Compatibility forms may change character distinctions.")
simple("Show invisible characters","Persian and Unicode",lambda t: ''.join(f'<U+{ord(c):04X} {unicodedata.name(c,"CONTROL")}>' if unicodedata.category(c) in ('Cf','Cc') else c for c in t),"Make control and formatting characters visible; this includes newlines and tabs.")
simple("Generate UUID v4","Generators",lambda t:str(uuid.uuid4()),"Generate a random identifier. Input is not used.","")
simple("Generate password","Generators",lambda t:secrets.token_urlsafe(24),"Generate 32 URL-safe characters using the operating system random source. Input is not used.","")
simple("Unix timestamp","Generators",lambda t:str(int(time.time())),"Return the current Unix timestamp in seconds. Input is not used.","")

HELP = """SMART TEXT TOOLKIT - QUICK START

1. Type a keyword in Search, or choose a category on the left.
2. Select a tool. Read its description before running it.
3. Paste text into Input, open a UTF-8 file, or click Load example.
4. Fill in any settings shown below the description.
5. Click Run tool. The result appears in Output.
6. Copy or save the output. Use output as input chains transformations.

Decode tools need data produced by the matching encoder. Their example button
creates a matching encoded sample automatically when a paired encoder exists.

KEYBOARD SHORTCUTS
Ctrl+Enter / Cmd+Enter: Run
Ctrl+O / Cmd+O: Open input file
Ctrl+S / Cmd+S: Save output
F1: Open this guide

PRIVACY AND SAFETY
The application makes no network requests and does not automatically save text,
keys, favorites or history. Clipboard contents and files you save are managed by
your operating system; other applications or clipboard history may retain them.
Favorites last only for this session. Keys are hidden unless Show values is on.
The ciphers are educational, not secure encryption. Hashes cannot be decrypted.
Never paste secrets into a tool unless you understand what it does.

LIMITS AND TEXT DETAILS
Input: 2 MB UTF-8. Output: 8 MB UTF-8. Decompression has an output limit.
These are usability guards, not a sandbox for hostile compressed files.
Do not open untrusted compressed data; decompression can still consume resources.
Words use Unicode word tokens, including digits and underscores. Characters are
Unicode code points, so combined letters and emoji can count as multiple units.
Most line tools normalize newlines to LF and drop a final line terminator.
UTF-8 decoding is strict: invalid data produces an error, not damaged text.
Jobs run one at a time in a background thread. Close the app to abandon a job.
"""

def launch():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    from tkinter.scrolledtext import ScrolledText

    class App:
        def __init__(self,root):
            self.root=root
            root.title(f"Smart Text Toolkit {VERSION}")
            root.geometry('1180x820')
            root.minsize(850,620)
            self.busy=False
            self.results=queue.Queue()
            self.favorites=set()
            self.visible=[]
            self.selected=None
            self.result_name=''
            self.search=tk.StringVar()
            self.category=tk.StringVar(value='All tools')
            self.fav_only=tk.BooleanVar()
            self.show_values=tk.BooleanVar()
            self.status=tk.StringVar(value=f'Ready | {len(OPERATIONS)} tools | Offline')
            self.params=[tk.StringVar(),tk.StringVar()]
            style=ttk.Style(root)
            if 'clam' in style.theme_names():style.theme_use('clam')
            style.configure('TButton',padding=(10,6))
            style.configure('Title.TLabel',font=('TkDefaultFont',17,'bold'))
            outer=ttk.Frame(root,padding=14)
            outer.pack(fill='both',expand=True)
            ttk.Label(outer,text='Smart Text Toolkit',style='Title.TLabel').pack(anchor='w')
            ttk.Label(outer,text='Choose a tool. Add your text. Run and copy the result.').pack(anchor='w',pady=(2,12))
            panes=ttk.Panedwindow(outer,orient='horizontal')
            panes.pack(fill='both',expand=True)
            side=ttk.Frame(panes,width=270,padding=(0,0,12,0))
            main=ttk.Frame(panes)
            panes.add(side,weight=1)
            panes.add(main,weight=4)
            ttk.Label(side,text='1. Choose a tool').pack(anchor='w')
            ttk.Entry(side,textvariable=self.search).pack(fill='x',pady=6)
            ttk.Combobox(side,textvariable=self.category,state='readonly',values=['All tools']+sorted({o.category for o in OPERATIONS})).pack(fill='x')
            ttk.Checkbutton(side,text='Favorites only',variable=self.fav_only,command=self.filter).pack(anchor='w',pady=6)
            listframe=ttk.Frame(side)
            listframe.pack(fill='both',expand=True)
            self.list=tk.Listbox(listframe,exportselection=False,activestyle='dotbox',font=('TkDefaultFont',10),borderwidth=1)
            scroll=ttk.Scrollbar(listframe,orient='vertical',command=self.list.yview)
            self.list.configure(yscrollcommand=scroll.set)
            scroll.pack(side='right',fill='y')
            self.list.pack(side='left',fill='both',expand=True)
            self.list.bind('<<ListboxSelect>>',self.select)
            ttk.Button(side,text='Toggle favorite',command=self.favorite).pack(fill='x',pady=(8,4))
            ttk.Button(side,text='Help / Quick start',command=self.help).pack(fill='x')
            self.title=ttk.Label(main,text='',font=('TkDefaultFont',13,'bold'))
            self.title.pack(anchor='w')
            self.description=ttk.Label(main,wraplength=680,justify='left')
            self.description.pack(fill='x',pady=(4,4))
            main.bind('<Configure>',lambda e:self.description.configure(wraplength=max(250,e.width-12)))
            self.warning=ttk.Label(main,foreground='#a34300',wraplength=650,justify='left')
            self.warning.pack(fill='x',pady=(0,4))
            self.settings=ttk.Frame(main)
            self.settings.pack(fill='x')
            self.param_labels=[]
            self.param_entries=[]
            for i in range(2):
                label=ttk.Label(self.settings)
                entry=ttk.Entry(self.settings,textvariable=self.params[i],show='*')
                self.param_labels.append(label)
                self.param_entries.append(entry)
            self.reveal=ttk.Checkbutton(self.settings,text='Show values',variable=self.show_values,command=self.reveal_values)
            ttk.Label(main,text='2. Input').pack(anchor='w',pady=(10,3))
            self.input=ScrolledText(main,height=8,wrap='word',undo=True,font=('TkFixedFont',11))
            self.input.pack(fill='both',expand=True)
            buttons=ttk.Frame(main)
            buttons.pack(fill='x',pady=6)
            for label,cmd in [('Open file',self.open_file),('Paste',self.paste),('Load example',self.example),('Clear',self.clear)]:
                ttk.Button(buttons,text=label,command=cmd).pack(side='left',padx=(0,5))
            runrow=ttk.Frame(main)
            runrow.pack(fill='x',pady=3)
            self.runbutton=ttk.Button(runrow,text='3. Run tool',command=self.run)
            self.runbutton.pack(side='left')
            self.progress=ttk.Progressbar(runrow,mode='indeterminate')
            self.progress.pack(side='left',fill='x',expand=True,padx=12)
            ttk.Label(main,text='4. Output (read-only)').pack(anchor='w',pady=(6,3))
            self.output=ScrolledText(main,height=8,wrap='word',state='disabled',font=('TkFixedFont',11))
            self.output.pack(fill='both',expand=True)
            outbuttons=ttk.Frame(main)
            outbuttons.pack(fill='x',pady=(6,0))
            for label,cmd in [('Copy output',self.copy),('Save output',self.save),('Use output as input',self.chain)]:
                ttk.Button(outbuttons,text=label,command=cmd).pack(side='left',padx=(0,5))
            ttk.Label(outer,textvariable=self.status,anchor='w').pack(fill='x',pady=(10,0))
            self.search.trace_add('write',lambda *args:self.filter())
            self.category.trace_add('write',lambda *args:self.filter())
            for mod in ['Control','Command']:
                for key,fn in [('Return',self.run),('o',self.open_file),('s',self.save)]:
                    root.bind(f'<{mod}-{key}>',lambda e,f=fn:(f(),'break')[1])
            root.bind('<F1>',lambda e:self.help())
            root.protocol('WM_DELETE_WINDOW',self.close)
            self.filter()
            self.root.after(100,self.poll)

        def filter(self):
            current=self.selected
            query=self.search.get().strip().casefold()
            self.visible=[o for o in OPERATIONS if (self.category.get()=='All tools' or o.category==self.category.get()) and (not self.fav_only.get() or o.name in self.favorites) and all(q in (o.name+' '+o.category+' '+o.description).casefold() for q in query.split())]
            self.list.delete(0,'end')
            for o in self.visible:self.list.insert('end',('* ' if o.name in self.favorites else '')+o.name)
            if self.visible:
                index=self.visible.index(current) if current in self.visible else 0
                self.list.selection_set(index)
                self.list.see(index)
                self.select()
            else:
                self.selected=None
                self.title.configure(text='No matching tools')
                self.description.configure(text='Try a different keyword or turn off Favorites only.')
                self.warning.configure(text='')
                for w in self.settings.winfo_children():w.grid_remove()

        def select(self,event=None):
            choice=self.list.curselection()
            if not choice:return
            op=self.visible[choice[0]]
            if op is self.selected:return
            self.selected=op
            self.title.configure(text=op.name)
            self.description.configure(text=op.description)
            self.warning.configure(text=op.warning)
            for w in self.settings.winfo_children():w.grid_remove()
            labels=list(op.labels)
            if op.name=='Find and replace':labels.append('Replacement (optional)')
            for i in range(2):
                self.params[i].set(op.defaults[i] if i<len(op.defaults) else '')
                if i<len(labels):
                    self.param_labels[i].configure(text=labels[i])
                    self.param_labels[i].grid(row=i,column=0,sticky='w',padx=(0,8),pady=3)
                    self.param_entries[i].grid(row=i,column=1,sticky='ew',pady=3)
            if labels:self.reveal.grid(row=0,column=2,padx=8)
            self.settings.columnconfigure(1,weight=1)

        def reveal_values(self):
            for e in self.param_entries:e.configure(show='' if self.show_values.get() else '*')

        def favorite(self):
            if not self.selected:return
            name=self.selected.name
            if name in self.favorites:self.favorites.remove(name)
            else:self.favorites.add(name)
            self.filter()

        def text(self,widget):return widget.get('1.0','end-1c')
        def set_input(self,text):
            self.input.delete('1.0','end')
            self.input.insert('1.0',text)
        def set_output(self,text):
            self.output.configure(state='normal')
            self.output.delete('1.0','end')
            self.output.insert('1.0',text)
            self.output.configure(state='disabled')

        def example(self):
            op=self.selected
            if not op:return
            sample=op.example
            if not sample and op.name.endswith(' / Decode'):
                enc=next((x for x in OPERATIONS if x.name==op.name.replace(' / Decode',' / Encode')),None)
                if enc:
                    try:sample=execute(enc,enc.example,*(v.get() for v in self.params))
                    except Exception as exc:
                        messagebox.showinfo('Example settings',str(exc),parent=self.root)
                        return
            if not sample and op.name.endswith(' / Decompress'):
                enc=next(x for x in OPERATIONS if x.name==op.name.replace(' / Decompress',' / Compress'))
                sample=execute(enc,enc.example)
            self.set_input(sample)
            self.status.set('Example loaded. Review the settings, then click Run tool.')

        def run(self):
            if self.busy or not self.selected:return
            op=self.selected
            text=self.text(self.input)
            params=[x.get() for x in self.params]
            if len(text.encode('utf-8'))>MAX_INPUT:
                messagebox.showerror('Input too large','Input exceeds the 2 MB UTF-8 limit.',parent=self.root)
                return
            self.busy=True
            self.runbutton.configure(state='disabled')
            self.progress.start(12)
            self.status.set(f'Running {op.name}...')
            def work():
                start=time.perf_counter()
                try:self.results.put((op.name,execute(op,text,*params),None,time.perf_counter()-start))
                except Exception as exc:self.results.put((op.name,None,f'{type(exc).__name__}: {exc}',0))
            threading.Thread(target=work,daemon=True).start()

        def poll(self):
            try:
                name,result,error,seconds=self.results.get_nowait()
                self.busy=False
                self.runbutton.configure(state='normal')
                self.progress.stop()
                if error:
                    self.status.set('Tool failed. Previous output, if any, is unchanged.')
                    messagebox.showerror('Could not process input',error+'\n\nCheck the input format and settings. For a working sample, use Load example.',parent=self.root)
                else:
                    self.result_name=name
                    self.set_output(result)
                    self.status.set(f'{name} | {len(result):,} output characters | {seconds:.3f} seconds')
            except queue.Empty:pass
            self.root.after(100,self.poll)

        def open_file(self):
            path=filedialog.askopenfilename(parent=self.root,title='Open UTF-8 text',filetypes=[('Text files','*.txt'),('All files','*')])
            if not path:return
            try:
                with open(path,'rb') as f:raw=f.read(MAX_INPUT+1)
                if len(raw)>MAX_INPUT:raise ValueError('File exceeds the 2 MB limit.')
                self.set_input(raw.decode('utf-8-sig'))
                self.status.set('Input file loaded as UTF-8.')
            except (OSError,UnicodeError,ValueError) as exc:messagebox.showerror('Cannot open file',str(exc),parent=self.root)

        def paste(self):
            try:self.set_input(self.root.clipboard_get())
            except tk.TclError:messagebox.showinfo('Clipboard empty','Copy some text first.',parent=self.root)

        def clear(self):
            if self.busy:
                messagebox.showinfo('Tool running','Wait for the current tool to finish before clearing.',parent=self.root)
                return
            if self.text(self.input) or self.text(self.output):
                if not messagebox.askyesno('Clear workspace','Clear input, output and key values?',parent=self.root):return
            self.set_input('')
            self.set_output('')
            for p in self.params:p.set('')
            self.status.set('Workspace cleared.')

        def copy(self):
            value=self.text(self.output)
            if not value:
                self.status.set('Output is empty. Run a tool first.')
                return
            self.root.clipboard_clear()
            self.root.clipboard_append(value)
            self.status.set(f'Copied output from {self.result_name}.')

        def save(self):
            value=self.text(self.output)
            if not value:
                messagebox.showinfo('No output','Run a tool before saving.',parent=self.root)
                return
            path=filedialog.asksaveasfilename(parent=self.root,title='Save output as UTF-8',defaultextension='.txt',filetypes=[('Text files','*.txt'),('All files','*')])
            if path:
                try:
                    with open(path,'w',encoding='utf-8',newline='') as f:f.write(value)
                    self.status.set('Output saved as UTF-8.')
                except OSError as exc:messagebox.showerror('Cannot save file',str(exc),parent=self.root)

        def chain(self):
            value=self.text(self.output)
            if not value:return
            if self.text(self.input) and not messagebox.askyesno('Replace input','Replace the current input with the output?',parent=self.root):return
            self.set_input(value)
            self.status.set('Output is now input. Choose the next tool and run it.')

        def help(self):
            win=tk.Toplevel(self.root)
            win.title('Quick start and safety notes')
            win.geometry('780x650')
            text=ScrolledText(win,wrap='word',padx=15,pady=15)
            text.pack(fill='both',expand=True)
            text.insert('1.0',HELP)
            text.configure(state='disabled')
            ttk.Button(win,text='Close',command=win.destroy).pack(pady=8)

        def close(self):
            if self.busy and not messagebox.askyesno('Tool still running','Close the application and abandon the running tool?',parent=self.root):return
            self.root.destroy()

    root=tk.Tk()
    App(root)
    root.mainloop()


def self_test():
    import unittest
    class Tests(unittest.TestCase):
        def test_pairs(self):
            samples=['Hello, world!','سلام دنیا ۱۲۳ 😀','\x00hello\x00','', '  last X\n\n']
            for op in OPERATIONS:
                suffix=' / Encode' if op.name.endswith(' / Encode') else ' / Compress' if op.name.endswith(' / Compress') else None
                if not suffix:continue
                target=op.name.replace(suffix,' / Decode' if suffix==' / Encode' else ' / Decompress')
                dec=next(x for x in OPERATIONS if x.name==target)
                args=list(op.defaults)+['','']
                for sample in samples:
                    with self.subTest(tool=op.name,sample=sample):
                        self.assertEqual(execute(dec,execute(op,sample,*args[:2]),*args[:2]),sample)
        def test_vectors(self):
            self.assertEqual(vig('ATTACKATDAWN','LEMON'),'LXFOPVEFRNHR')
            self.assertEqual(shift('Abc XYZ',3),'Def ABC')
            self.assertEqual(rot47(' A😀\n'),' p😀\n')
            self.assertEqual(xor(xor('سلام 😀','key'),'key',True),'سلام 😀')
            self.assertEqual(vig(vig('Attack!','KEY',beaufort=True),'KEY',beaufort=True),'Attack!')
        def test_columnar(self):
            for key in ['ZEBRA','BANANA','x','LONGKEY']:
                for t in ['','X','XXX','hello X\nسلام 😀']:
                    self.assertEqual(columnar(columnar(t,key),key,True),t)
        def test_errors(self):
            with self.assertRaises(ValueError):vig('abc','123')
            with self.assertRaises(ValueError):base64.b64decode('@@',validate=True)
            with self.assertRaises(UnicodeDecodeError):url64_decode('_w')
            with self.assertRaises(ValueError):rail('abc',1)
        def test_csv(self):
            text='name,note\nAlex,"Hello, world"\n'
            self.assertEqual(delimit(delimit(text,',','\t'),'\t',','),text)
        def test_examples(self):
            for op in OPERATIONS:
                if op.name.endswith((' / Decode',' / Decompress')):continue
                args=list(op.defaults)+['sample-key','sample-key']
                with self.subTest(tool=op.name):execute(op,op.example,*args[:2])
        def test_names(self):
            self.assertEqual(len({o.name for o in OPERATIONS}),len(OPERATIONS))
        def test_keyboard(self):
            op=next(x for x in OPERATIONS if x.name=='English keys to Persian')
            self.assertEqual(execute(op,'sghl'),'سلام')
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    return result.wasSuccessful()

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test',action='store_true',help='Run core tests without a graphical display')
    parser.add_argument('--list-tools',action='store_true',help='Print the tool catalog without opening the GUI')
    args=parser.parse_args()
    if args.self_test:
        raise SystemExit(0 if self_test() else 1)
    elif args.list_tools:
        for op in OPERATIONS:print(f'{op.category}: {op.name}')
    else:
        try:launch()
        except ImportError as exc:
            raise SystemExit(f'Tkinter is required for the desktop interface: {exc}. See README.md.')
