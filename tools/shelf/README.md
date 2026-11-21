# The bookshelf ("On the shelf")

The 3D bookcase on the home page (`#books`) and on `/books`. One script builds it:

```
python -I tools/shelf/build_shelf.py
```

It rewrites `public/img/bookcase.jpg`, `public/img/bookcase-m.jpg`, `public/img/empty-*.jpg`, the shelf CSS block at the
end of `public/styles.css`, and the `<div class="bookcase">` block in `public/index.html` and `public/books.html`.
Run it after any change below, check the page locally, then commit. Pushing to `main` deploys the site.

## How it works

- `src/bookcase-oak.webp` is the empty oak bookcase (Higgsfield, gpt_image_2_6, upscaled to 2K). Its four shelves are evenly
  spaced, and the twine-tied "In production" stack is part of this photo.
- `src/<key>-standing.webp` are the books, each rendered standing on a transparent background in the same pose and light
  (upright, turned about 25 degrees so the spine shows, true 2:3 proportions). The script pastes them onto the shelves with
  a soft shadow.
- On hover, an empty-shelf patch (`public/img/empty-<key>.jpg`, cut from the empty bookcase) fades in over the painted book,
  and a CSS 3D copy of the book, posed to match it exactly, opens in place: contents page on the left, chapter page on
  the right. A click goes to the book's page. Phones show the painted shelf, and a tap goes straight to the book's page.
- The stack plays `public/img/untie.mp4` on hover (driven by `public/untie.js`) and plays it backwards on leave.

## Shelf coordinates (1024 x 1024 render space)

| Shelf | Floor y (where a book's bottom goes) | Label y | Free x range |
|---|---|---|---|
| 1 (top) | 217 | 225 | about 110 to 400, and 860 to 940 |
| 2 (stack) | 413 | 424 | about 110 to 700 |
| 3 | 601 | 617 | about 110 to 520, and 680 to 940 |

Desktop shows the top three shelves (`DH = 648`). Phones show the crop `MC = (380, 0, 1010, 640)`, so a book that must show on
phones needs to stand between x 400 and 990.

## Adding a book

1. **Render it standing.** In Higgsfield, use `gpt_image_2_6`, aspect 2:3, quality high, resolution 2k, background
   transparent. Give two references: `src/yours-standing.webp` (for the pose and light) and the book's cover image. Use this
   prompt, changing the spine line to match the book:

   > Photorealistic standing hardcover book, posed, lit and proportioned exactly like the first reference image (upright,
   > seen straight on at eye level, turned about 25 degrees to the left so the spine on the left is visible, standard tall
   > 6 by 9 inch proportions, about 2.5 cm thick, soft warm light from the upper left). Its front cover is exactly the second
   > reference image, reproduced faithfully with all of its text and artwork, filling the whole front cover with a matte
   > finish. The spine is [colour] and reads only '[TITLE]' running down the spine, nothing else on the spine. Isolated on
   > a fully transparent background, whole book in frame, no shadow plane.

   Keep the spine to the title only, because image models misspell names. Save the result as `src/<key>-standing.webp`.
2. **Find its cover box.** This is the front cover's left, top, right and bottom in the image's own pixels. The left edge is
   where the spine meets the cover. The existing books are around `(280, 130, 1267, 1950)`.
3. **Add it to the script.** In `build_shelf.py`:
   - Add an entry to `SRC` with its file, its cover box, `ys=1.0`, where it stands (`cx` and `floor`), `height` (184 on the
     top shelf) and `t` (spine depth, about 20).
   - Add an entry to `BOOKS` with its URL, title, author, price, spine colours, and three images in `public/img/`: the
     cover, a contents page and a chapter page (each 667 x 1000, rendered from the book PDF).
   - Add a label in `labels()`.
4. **Build and check.** Run the script, open the page locally (`python -m http.server 8788 --directory public`), check the
   resting shelf and the hover, at desktop width and at phone width.

## The untie clip

`src/untie-raw.mp4` is the raw Grok Video 1.5 clip (start frame: the stack crop `x 675-995, y 270-450` of the bookcase).
The site uses seconds 0.75 to 3.2, slowed down and encoded all-intra so it can play backwards smoothly:

```
ffmpeg -y -ss 0.75 -t 2.45 -i tools/shelf/src/untie-raw.mp4 -an -vf "setpts=1.35*PTS,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,scale=640:360:flags=lanczos,format=yuv420p" -c:v libx264 -preset slow -crf 24 -g 1 -movflags +faststart public/img/untie.mp4
ffmpeg -y -i public/img/untie.mp4 -frames:v 1 -q:v 3 public/img/untie-poster.jpg
```
