# Builds the "On the shelf" bookcase on loopworkbooks.com (home page #books and /books).
#   python -I tools/shelf/build_shelf.py
# Rewrites public/img/bookcase*.jpg, public/img/empty-*.jpg, the shelf CSS block at the end of public/styles.css and the
# <div class="bookcase"> block in public/index.html and public/books.html. See tools/shelf/README.md for adding a book.
import os, math
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(HERE, 'src') + os.sep        # source renders (see README.md)
os.chdir(os.path.join(HERE, '..', '..', 'public'))

DH = 648                      # desktop shows the top three shelves
MC = (380, 0, 1010, 640)      # phone crop: top three shelves, right part
MW, MH = MC[2] - MC[0], MC[3] - MC[1]
VID = (675, 270, 995, 450)    # where the untie clip sits (its start frame is this crop of the original render)

# ---------- images ----------
from PIL import ImageFilter
orig = Image.open(S + 'bookcase-oak.webp').convert('RGB').resize((2048, 2048), Image.LANCZOS)
case = orig.convert('RGBA')
k = 2.0
# each cutout: file, its cover box in the cutout's own pixels, extra vertical stretch to true 2:3 book proportions,
# where it stands now (centre x and floor y, 1024 space) and its height on the shelf
SRC = {
    'dog':   dict(file='dog-standing.webp',    cover=(280, 130, 1267, 1950), ys=1.0,   cx=495, floor=217, height=184, t=20),
    'reset': dict(file='reset-standing.webp',  cover=(285, 130, 1261, 1945), ys=1.0, cx=775, floor=217, height=184, t=18),
    'yours': dict(file='yours-standing.webp',  cover=(330, 140, 1260, 1950), ys=1.0, cx=600, floor=601, height=156, t=24),
}
placed = {}
from PIL import ImageDraw
for key, d in SRC.items():
    cut = Image.open(S + d['file']).convert('RGBA')
    a_full = cut.getchannel('A')
    bb = a_full.point(lambda v: 255 if v > 128 else 0).getbbox()
    sc = d['height'] * k / ((bb[3] - bb[1]) * d['ys'])          # px scale on the 2048 canvas (x)
    scy = sc * d['ys']
    img = cut.resize((round(cut.width * sc), round(cut.height * scy)), Image.LANCZOS)
    a_ = img.getchannel('A')
    px = round(d['cx'] * k - (bb[0] + bb[2]) / 2 * sc)
    py = round(d['floor'] * k - bb[3] * scy)
    sh = Image.new('L', case.size, 0); sh.paste(a_, (px + 10, py + 4))
    sh = sh.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * .32))
    cs = Image.new('L', case.size, 0)
    bx0, bx1 = px + round(bb[0] * sc), px + round(bb[2] * sc)
    by = py + round(bb[3] * scy)
    ImageDraw.Draw(cs).ellipse((bx0 - 6, by - 7, bx1 + 14, by + 7), fill=170)
    cs = cs.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * .55))
    shadow = Image.fromarray(np.maximum(np.asarray(sh), np.asarray(cs)))
    dark = Image.new('RGBA', case.size, (45, 25, 8, 255)); dark.putalpha(shadow)
    case = Image.alpha_composite(case, dark)
    case.alpha_composite(img, (px, py))
    cv = d['cover']
    to1024x = lambda v: (px + v * sc) / k
    to1024y = lambda v: (py + v * scy) / k
    placed[key] = dict(cover_box=(to1024x(cv[0]), to1024y(cv[1]), to1024x(cv[2]), to1024y(cv[3])),
                       patch=(to1024x(bb[0]) - 14, to1024y(bb[1]) - 6, to1024x(bb[2]) + 22, d['floor'] + 9),
                       t=(cv[0] - bb[0]) * sc / k, floor=d['floor'])
case = case.convert('RGB')
case.crop((0, 0, 2048, round(DH * k))).save('img/bookcase.jpg', quality=88, optimize=True, progressive=True)
mc = case.crop(tuple(round(v * k) for v in MC))
mc.resize((1100, round(1100 * mc.height / mc.width)), Image.LANCZOS).save('img/bookcase-m.jpg', quality=88, optimize=True, progressive=True)

BOOKS = [
    dict(key='dog', url='https://whop.com/loopworkbooks/the-overtired-dog', title='The Overtired Dog', who='Kris Downey', price='$19',
         spine='#22272b', ink='#eef0ee', page='img/book-ch2.jpg', cover='img/book-cover.jpg', inside='img/book-contents-dog.jpg', lip=225),
    dict(key='reset', url='https://whop.com/unclutter-it/the-small-steps-home-reset', title='The Small Steps Home Reset', who='Bridget Stralko', price='$20',
         spine='#efe6d2', ink='#2e2a5a', page='img/book-inside-reset.jpg', cover='img/book-cover-reset.jpg', inside='img/book-contents-reset.jpg', lip=225),
    dict(key='yours', url='#apply', title='Your book', who='you', price='', spine='#ebe2cf', ink='#a8853e', lip=617),
]
oc = np.asarray(orig).astype(np.float32)
for b_ in BOOKS:
    b_.update(placed[b_['key']])
    x0, y0, x1, y1 = [round(v * k) for v in b_['patch']]
    Image.fromarray(oc[y0:y1, x0:x1].astype(np.uint8)).save(f"img/empty-{b_['key']}.jpg", quality=86)   # the empty shelf, exactly
    b_['patch'] = tuple(v for v in b_['patch'])

pct = lambda v, tot: f'{v / tot * 100:.3f}%'
def box_vars(x0, y0, x1, y1):
    return (f'--x:{pct(x0, 1024)};--y:{pct(y0, DH)};--w:{pct(x1 - x0, 1024)};--h:{pct(y1 - y0, DH)};'
            f'--mx:{pct(x0 - MC[0], MW)};--my:{pct(y0 - MC[1], MH)};--mw:{pct(x1 - x0, MW)};--mh:{pct(y1 - y0, MH)}')
def at_vars(x, y):
    return f'--x:{pct(x, 1024)};--y:{pct(y, DH)};--mx:{pct(x - MC[0], MW)};--my:{pct(y - MC[1], MH)}'

def book_html(b, apply_href):
    cx0, cy0, cx1, cy1 = b['cover_box']
    th = math.radians(40)
    true_w = (cx1 - cx0) / math.cos(th)
    true_t = b['t'] / math.sin(th)
    size = f"--bw:{true_w / 1024 * 100:.3f};--bh:{(cy1 - cy0) / 1024 * 100:.3f};--bt:{true_t / 1024 * 100:.3f};--spine:{b['spine']};--spine-ink:{b['ink']}"
    book_box = (cx0, cy0, cx0 + true_w, cy1)
    if b['key'] == 'yours':
        href, extra, label = apply_href, '', 'Your book could be next: get a free chapter'
        page = '<div class="yours-page"><small>Chapter one</small><strong>Is on us.</strong><span>Get a free chapter &rarr;</span></div>'
        cover = '<div class="b3-front yours-cover"><span class="foil big">Your book</span></div>'
        inner = '<div class="b3-inner yours-inner"><span>Written from <b>your posts.</b></span><span>Designed by <b>us.</b></span><span>Approved by <b>you.</b></span></div>'
    else:
        href, extra, label = b['url'], ' target="_blank" rel="noopener"', f"{b['title']} by {b['who']}, {b['price']}, opens the book page on Whop"
        page = f'<img class="b3-page" src="{b["page"]}" alt="" loading="lazy">'
        cover = f'<img class="b3-front" src="{b["cover"]}" alt="Cover of {b["title"]} by {b["who"]}">'
        inner = f'<div class="b3-inner"><img src="{b["inside"]}" alt="" loading="lazy"></div>'
    return f'''
      <div class="empty" style="{box_vars(*b['patch'])};background-image:url(img/empty-{b['key']}.jpg)" data-k="{b['key']}" aria-hidden="true"></div>
      <a class="book3d" data-k="{b['key']}" href="{href}"{extra} aria-label="{label}" style="{box_vars(*book_box)};{size}">
        <span class="b3-body">{page}<span class="b3-cover">{cover}{inner}</span><span class="b3-spine"><span>{b['title']}</span></span><span class="b3-edge"></span><span class="b3-back"></span></span>
      </a>'''

def labels():
    out = ''
    for b in BOOKS[:2]:
        cx = (b['patch'][0] + b['patch'][2]) / 2
        out += f'\n      <span class="slot-label" style="{at_vars(cx, b["lip"])}"><span class="lt">{b["title"]}</span><b>{b["price"]}</b></span>'
    out += f'\n      <span class="slot-label" style="{at_vars(835, 424)}">In production</span>'
    out += f'\n      <span class="slot-label" style="{at_vars(600, 617)}">Your book could be next</span>'
    return out

def shelf(apply_href):
    books = ''.join(book_html(b, apply_href) for b in BOOKS)
    return (f'<div class="bookcase">\n      <picture class="bookcase-photo"><source media="(max-width: 600px)" srcset="img/bookcase-m.jpg">'
            f'<img src="img/bookcase.jpg" width="2048" height="{round(2048 * DH / 1024)}" alt="An oak bookcase with our books on the top shelf"></picture>'
            f'{books}\n      <div class="untie" style="{box_vars(*VID)}"><video muted playsinline preload="auto" poster="img/untie-poster.jpg" aria-hidden="true">'
            f'<source src="img/untie.mp4" type="video/mp4"></video></div>{labels()}\n    </div>')

CSS = r'''/* ---------- bookshelf v7 (22 Nov): books painted into the photo; hover lifts a 3D copy out and opens it ---------- */
.nav-links a[aria-current="page"] { color: var(--plum); }
.books-head { padding-bottom: 10px; }
.books-head .section-sub { margin-bottom: 0; }
.books-cta { padding-top: 40px; }
.books-cta .section-sub { margin-bottom: 22px; }
.foot-books { display: block; margin-top: 6px; }
.shelf-section { text-align: center; }
.shelf-section .section-sub { margin-left: auto; margin-right: auto; }
.shelf-hint { font-size: 13.5px; color: var(--soft); margin: 18px 0 0; }

.bookcase { position: relative; width: min(1440px, calc(100vw - 48px)); left: 50%; margin: 0 0 0 calc(min(1440px, calc(100vw - 48px)) / -2);
  container-type: inline-size; border-radius: 4px; --k: 1; --lab: 1.05cqw;
  box-shadow: 0 30px 60px -24px rgba(90, 60, 30, .45), 0 8px 20px rgba(90, 60, 30, .15); }
.bookcase-photo, .bookcase-photo img { display: block; width: 100%; height: auto; border-radius: 4px; }
.empty, .book3d, .untie { position: absolute; left: var(--x); top: var(--y); width: var(--w); height: var(--h); }
.slot-label { position: absolute; left: var(--x); top: var(--y); transform: translate(-50%, -50%); white-space: nowrap; z-index: 10; pointer-events: none;
  font-size: max(9px, var(--lab)); font-weight: 600; letter-spacing: .02em; color: #3b2516;
  background: linear-gradient(180deg, #f3e6bd 0%, #d9bd80 55%, #bd9a58 100%); padding: .22em .75em; border-radius: 2px;
  box-shadow: 0 1px 0 rgba(255,255,255,.55) inset, 0 1px 3px rgba(60, 35, 10, .45); }
.slot-label b { color: #8e2f50; margin-left: .45em; }

/* the empty shelf behind a lifted book */
.empty { background-size: 100% 100%; opacity: 0; transition: opacity .3s ease .05s; z-index: 1; pointer-events: none;
  -webkit-mask-image: radial-gradient(ellipse 58% 60% at 50% 50%, #000 78%, transparent 100%);
          mask-image: radial-gradient(ellipse 58% 60% at 50% 50%, #000 78%, transparent 100%); }
.bookcase:has(.book3d[data-k="dog"]:hover) .empty[data-k="dog"],
.bookcase:has(.book3d[data-k="reset"]:hover) .empty[data-k="reset"],
.bookcase:has(.book3d[data-k="yours"]:hover) .empty[data-k="yours"],
.bookcase:has(.book3d[data-k="dog"]:focus-visible) .empty[data-k="dog"],
.bookcase:has(.book3d[data-k="reset"]:focus-visible) .empty[data-k="reset"],
.bookcase:has(.book3d[data-k="yours"]:focus-visible) .empty[data-k="yours"] { opacity: 1; }

/* the 3D book: invisible on the shelf (the photo shows it), lifts out on hover */
.book3d { display: block; perspective: 2400px; perspective-origin: 0% 50%; z-index: 3; outline: none; opacity: 0; transition: opacity .12s ease;
  --t: calc(var(--bt) * 1cqw * var(--k)); }
.book3d:hover, .book3d:focus-visible, .book3d.is-open { z-index: 8; }
.b3-body { position: absolute; inset: 0; transform-style: preserve-3d; transform: rotateY(40deg); transform-origin: 0% 50%; }
.book3d:hover, .book3d:focus-visible, .book3d.is-open { opacity: 1; }
.b3-page, .b3-cover, .b3-front, .b3-inner, .b3-back { position: absolute; inset: 0; width: 100%; height: 100%; display: block; }
.b3-page { transform: translateZ(-1px); object-fit: cover; border-radius: 0 2px 2px 0; box-shadow: inset 6px 0 10px rgba(0,0,0,.1); }
.b3-cover { transform-origin: left center; transform-style: preserve-3d; transition: transform .8s .15s cubic-bezier(.3, .6, .2, 1); }
.book3d:hover .b3-cover, .book3d:focus-visible .b3-cover, .book3d.is-open .b3-cover { transform: rotateY(-165deg); }
.b3-front { backface-visibility: hidden; object-fit: cover; border-radius: 0 2px 2px 0; box-shadow: inset 3px 0 5px rgba(0,0,0,.22); }
.b3-inner { transform: rotateY(180deg); backface-visibility: hidden; background: #f3ece0; border-radius: 2px 0 0 2px; box-shadow: inset -8px 0 12px rgba(0,0,0,.08); overflow: hidden; }
.b3-inner img { width: 100%; height: 100%; object-fit: cover; display: block; }
.b3-spine { position: absolute; top: 0; left: calc(var(--t) * -1); width: var(--t); height: 100%; transform-origin: right center; transform: rotateY(-90deg); background: var(--spine); color: var(--spine-ink); display: flex; align-items: center; justify-content: center; box-shadow: inset 0 0 6px rgba(0,0,0,.3); overflow: hidden; }
.b3-spine span { writing-mode: vertical-rl; font-family: 'Fraunces', Georgia, serif; font-size: max(6px, calc(var(--t) * .45)); font-weight: 600; letter-spacing: .02em; white-space: nowrap; }
.b3-edge { position: absolute; top: 2%; left: 100%; width: var(--t); height: 96%; transform-origin: left center; transform: rotateY(90deg); background: repeating-linear-gradient(90deg, #fbf7ef 0 2px, #e2d7c6 2px 3px); }
.b3-back { transform: translateZ(calc(var(--t) * -1)) rotateY(180deg); background: var(--spine); border-radius: 2px; }

/* "your book" when lifted: cream linen, gold foil, opens to the free chapter */
.yours-cover { display: flex; align-items: center; justify-content: center; text-align: center; overflow: hidden;
  background: repeating-linear-gradient(0deg, rgba(120, 90, 60, .07) 0 1px, transparent 1px 3px),
    repeating-linear-gradient(90deg, rgba(120, 90, 60, .06) 0 1px, transparent 1px 3px), linear-gradient(160deg, #f6efe1, #e8dcc6); }
.yours-cover::before { content: ""; position: absolute; inset: 6%; border: 1px solid rgba(176, 138, 62, .65); }
.foil { font-family: 'Fraunces', Georgia, serif; font-weight: 600; line-height: 1.05;
  background: linear-gradient(100deg, #9c7a32 0%, #e8cf8a 35%, #b48a3c 55%, #f1dc9e 75%, #a27d34 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent; }
.foil.big { font-size: calc(var(--bw) * .16cqw * var(--k)); }
.yours-inner, .yours-page { display: flex; flex-direction: column; justify-content: center; padding: 0 12%; text-align: left; }
.yours-inner { gap: .5em; font-family: 'Fraunces', Georgia, serif; font-size: calc(var(--bw) * .085cqw * var(--k)); line-height: 1.2; color: #3a2233; }
.yours-inner b { color: #b5446a; font-weight: 600; }
.yours-page { position: absolute; inset: 0; transform: translateZ(-1px); background: #fbf8f1; box-shadow: inset 6px 0 10px rgba(0,0,0,.08); }
.yours-page small { font-size: calc(var(--bw) * .07cqw * var(--k)); letter-spacing: .12em; text-transform: uppercase; color: #b5446a; font-weight: 700; }
.yours-page strong { font-family: 'Fraunces', Georgia, serif; font-size: calc(var(--bw) * .15cqw * var(--k)); line-height: 1.1; color: #3a2233; margin: .4em 0 .5em; }
.yours-page span { font-size: calc(var(--bw) * .085cqw * var(--k)); font-weight: 700; color: #b5446a; }

/* the twine stack: the clip of its rope being pulled loose plays in place on hover (untie.js), reverses on leave */
.untie { z-index: 2;
  -webkit-mask-image: radial-gradient(ellipse 60% 64% at 50% 47%, #000 72%, transparent 100%);
          mask-image: radial-gradient(ellipse 60% 64% at 50% 47%, #000 72%, transparent 100%); }
.untie video { display: block; width: 100%; height: 100%; object-fit: cover; opacity: 0; transition: opacity .2s ease; }
.untie.on video { opacity: 1; }

@media (max-width: 600px) {
  .bookcase { --k: 1.6254; width: 100%; left: 0; margin: 0; }
  .empty, .book3d, .untie { left: var(--mx); top: var(--my); width: var(--mw); height: var(--mh); }
  .slot-label { left: var(--mx); top: var(--my); font-size: 9px; padding: 2px 6px; letter-spacing: 0; }
  .slot-label .lt { display: none; }
  .slot-label .lt + b { margin-left: 0; }
}
@media (hover: none) {
  .b3-body { display: none; }
  .book3d { opacity: 0 !important; }
}
@media (prefers-reduced-motion: reduce) {
  .b3-body, .b3-cover, .empty { transition: none; }
}
'''

css = open('styles.css', encoding='utf8').read()
css = css[:css.index('/* ---------- bookshelf v')] + CSS
open('styles.css', 'w', encoding='utf8').write(css)

for path, apply_href in (('index.html', '#apply'), ('books.html', '/#apply')):
    s = open(path, encoding='utf8').read()
    a = s.index('<div class="bookcase">')
    end = 'Your book could be next</span>\n    </div>'
    b2 = s.index(end, a) + len(end)
    s = s[:a] + shelf(apply_href) + s[b2:]
    open(path, 'w', encoding='utf8').write(s)
print('ok', case.size)
