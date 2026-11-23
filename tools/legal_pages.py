# Builds /terms (EN), /regulamin (PL) and /refunds for loopworkbooks.com from privacy.html's head, header and footer.
# Content follows his real practice: site FAQ + deal cards, the Patty agreement (net sales, 30-day notice, 14-day buyer
# refunds), the 22 Nov refund rule (first half back if the $199 book isn't approved) and the Black Week offer.
# Not reviewed by a lawyer.
import os, re
os.chdir(r'F:\Claude\loopwork\public')
def rd(p): return open(p, encoding='utf-8').read()
def wr(p, s): open(p, 'w', encoding='utf-8', newline='').write(s)

priv = rd('privacy.html')
head = priv[:priv.index('<title>')]
head_rest = priv[priv.index('<link rel="preconnect"'):priv.index('<body>')]
header = priv[priv.index('<header class="nav">'):priv.index('</header>') + len('</header>')]
footer = priv[priv.index('<footer class="footer">'):priv.index('</footer>') + len('</footer>')]
script_tag = re.search(r'<script src="/script.js[^"]*"></script>', priv).group(0)

UPDATED_EN = '22 November 2026'
UPDATED_PL = '22 listopada 2026'

def toc(body, label):
    # A linked contents list built from the numbered sections, placed before the first one.
    items = re.findall(r'<h2 id="([^"]+)">(\d+\.\s[^<]+)</h2>', body)
    if not items:
        return body
    nav = ('  <nav class="legal-toc" aria-label="%s"><p>%s</p><ul>' % (label, label)
           + ''.join('<li><a href="#%s">%s</a></li>' % (i, t) for i, t in items) + '</ul></nav>\n\n')
    k = body.index('  <h2 ')
    return body[:k] + nav + body[k:]

def page(path, lang, title, body):
    if path in ('terms.html', 'regulamin.html'):
        body = toc(body, 'Contents' if lang == 'en' else 'Spis treści')
    h = head.replace('<html lang="en">', '<html lang="%s">' % lang)
    s = (h + '<title>%s</title>\n<meta name="robots" content="noindex">\n' % title + head_rest
         + '<body>\n' + header + '\n<main class="section narrow legal">\n' + body.strip('\n') + '\n</main>\n\n'
         + footer + '\n' + script_tag + '\n</body>\n</html>\n')
    if lang == 'pl':
        s = s.replace('<header class="nav">', '<header class="nav" lang="en">', 1).replace('<footer class="footer">', '<footer class="footer" lang="en">', 1)
    wr(path, s)

# ---------------------------------------------------------------- English terms
TERMS = '''
  <h1 class="page-h1">Terms</h1>
  <p class="legal-meta">Last updated ''' + UPDATED_EN + '''. Polish version: <a href="/regulamin" lang="pl">Regulamin</a>. Refunds in short: <a href="/refunds">Refunds</a>.</p>
  <p>These terms explain how working with Loopwork works: asking for a free chapter, the two ways to have a book made, payments and refunds, and buying one of the books we sell. Our <a href="/privacy">privacy notice</a> explains what we do with your data.</p>

  <h2 id="who">1. Who we are</h2>
  <p>Loopwork is run by Volodymyr Verbytskyi, Kielce, Poland, email <a href="mailto:hello@loopworkbooks.com">hello@loopworkbooks.com</a>. Loopwork is not a registered company: Volodymyr runs it as an individual under the Polish rules for unregistered activity (<span lang="pl">działalność nierejestrowana</span>).</p>
  <p>In these terms, "we" and "us" means Loopwork. "You" means the creator we make a book with, or a reader who buys one of our books.</p>

  <h2 id="website">2. Using this website</h2>
  <ul>
    <li>The site is free to use. You need an up-to-date web browser, and an email address to ask for a free chapter.</li>
    <li>When you send the form, you ask us to look at your public posts and reply to you about a possible book. That is all the form does. It ends once we have replied, or earlier if you ask us to stop.</li>
    <li>Please don't send anything unlawful, or anyone else's details, through the form.</li>
  </ul>

  <h2 id="free-chapter">3. The free chapter</h2>
  <p>We read your public posts, suggest a book idea with an outline, and write and design one real chapter. It costs nothing, and you don't owe us anything for it. If you don't go ahead, we don't publish or sell that chapter anywhere.</p>

  <h2 id="agreement">4. How we agree to work together</h2>
  <p>Before any work on the full book starts, we confirm in writing (an email is enough): the book, the deal you chose, the price or split, and that these terms apply. That exchange and these terms are our agreement. If we also sign a separate written agreement with you, it applies wherever it differs from these terms.</p>

  <h2 id="share">5. Share the sales (no upfront cost)</h2>
  <ul>
    <li>You pay nothing. We write, design and launch the book, and we split net sales 50/50 from the first sale. During Black Friday week the split is 60/40 in your favour (section 7).</li>
    <li>"Net sales" means what buyers pay, minus sales tax or VAT where it applies, card and platform fees, refunds and chargebacks.</li>
    <li>The book sells through our shared Whop page. Whop splits each sale automatically and puts your share into your own Whop balance, which you can withdraw whenever you like.</li>
    <li>You get three review rounds plus a final check.</li>
    <li>It is your book, with your name and your content. While we work together, it is sold only through the shared page.</li>
    <li>Ending it: before launch, either of us can stop at any time by telling the other in writing, with nothing to pay. After launch, either of us can end it with 30 days' written notice. Sales during the notice period are split as usual, and then the book comes off sale. If you would like to keep selling it yourself, we can agree a buyout of our share. Readers keep the copies they bought.</li>
  </ul>

  <h2 id="own">6. Own it outright (one-time fee)</h2>
  <ul>
    <li>You pay a one-time fee per book and keep every sale, after store fees. The fee is $199 a book for your first 3 books if you start by 31 December 2026. From 1 January 2027 it is $290 a book. During Black Friday week it is $149 (section 7). We confirm your price in writing before you pay anything.</li>
    <li>You pay half when you start and half when you approve the finished book. Payments go through Whop.</li>
    <li>You get two review rounds plus a typo check.</li>
    <li>Once you have paid in full, the book is yours to sell or give away anywhere. We set up the sales page in your own Whop account and give you the final files.</li>
    <li>If you don't approve the book, you don't pay the second half, and we refund the first half (section 9).</li>
  </ul>

  <h2 id="black-week">7. Black Friday week offer, until 30 November 2026</h2>
  <ul>
    <li><strong>Share the sales:</strong> you keep 60% of net sales and we keep 40%, for as long as that book sells with us.</li>
    <li><strong>Own it outright:</strong> $149 a book instead of $199.</li>
    <li>To get it, ask for your free chapter, or tell us you want to go ahead, by 30 November 2026 at 23:59 Polish time. Then start the book by 31 December 2026: for Share the sales, by confirming in writing; for Own it outright, by paying the first half.</li>
  </ul>

  <h2 id="timing">8. Timing and changes</h2>
  <ul>
    <li>The free chapter usually takes a few days. A full first draft takes about two weeks, then as long as your reviews take. These are estimates, not fixed deadlines. If something delays us, we tell you.</li>
    <li>Changes beyond the review rounds of your deal, new chapters, or a new edition later are agreed with you before we do them.</li>
  </ul>

  <h2 id="refunds">9. Refunds and your right to withdraw</h2>
  <ul>
    <li><strong>Own it outright:</strong> until you approve the book, you can stop at any time. If you stop, or don't approve the finished book, we refund the half you paid upfront in full, within 14 days of you telling us, to the payment method you used. If we can't deliver the book for any reason, we refund everything you paid.</li>
    <li><strong>Share the sales:</strong> you don't pay us anything, so there is nothing to refund.</li>
    <li id="withdraw"><strong>Your legal right to withdraw:</strong> if you are a consumer, or a sole trader for whom this agreement is not part of your professional activity, you can withdraw within 14 days of making the agreement, without giving a reason. Email us, or use the model form at the end of these terms. Our refund promise above goes further than this right: until you approve the book, you get your upfront payment back in full. If you ask us to start straight away and then approve the finished book and pay in full within those 14 days, the service is complete and the right to withdraw ends.</li>
  </ul>

  <h2 id="content">10. Your content, the book and AI</h2>
  <ul>
    <li>Your content stays yours: your writing, photos, methods and name. You let us use it only to make, sell and promote your book, and we only publish promotion you have approved.</li>
    <li>You confirm that the content you give us is yours, or that you have the right to use it.</li>
    <li>We keep your unpublished material private and use it only for your book.</li>
    <li>We draft text with AI tools, and we edit every page by hand against your own posts. Some illustrations may be made with AI. We tell you which ones before you approve the book.</li>
    <li>We show your book to other people as an example of our work only with your OK.</li>
    <li>We don't make books that give medical, legal or financial advice.</li>
  </ul>

  <h2 id="readers">11. Buying one of our books</h2>
  <ul>
    <li>Our books are digital (PDF). Whop runs the checkout and delivers the file.</li>
    <li>Books on our Whop page (whop.com/loopworkbooks) are sold by us together with the author. Books on an author's own Whop page are sold by that author, under their own terms.</li>
    <li>For a book bought from our page: if you change your mind, ask within 14 days of buying and we refund you. If the file doesn't open, or the book isn't what its page described, we fix it or refund you. Email <a href="mailto:hello@loopworkbooks.com">hello@loopworkbooks.com</a> from the email you bought with.</li>
  </ul>

  <h2 id="complaints">12. Complaints</h2>
  <p>Email <a href="mailto:hello@loopworkbooks.com">hello@loopworkbooks.com</a>, tell us what went wrong and what you would like us to do. We reply within 14 days. If you are a consumer, you can also get free help from a consumer ombudsman (in Poland, the <span lang="pl">miejski</span> or <span lang="pl">powiatowy rzecznik konsumentów</span>) or the Trade Inspection (<span lang="pl">Inspekcja Handlowa</span>). More information is at <a href="https://uokik.gov.pl" target="_blank" rel="noopener">uokik.gov.pl</a>. In the EU, the European Consumer Centre in your country can help with cross-border problems.</p>

  <h2 id="responsibility">13. Responsibility</h2>
  <p>We don't promise any number of sales. Each of us pays our own taxes on our share. If something goes wrong because of us, our responsibility is limited to what you paid us for that book. This limit doesn't apply to your rights as a consumer, or to harm caused on purpose or through gross negligence.</p>

  <h2 id="law">14. Law, language and changes</h2>
  <ul>
    <li>Polish law applies. If you are a consumer living in another country, you keep the protections your own country's law gives you.</li>
    <li>If we disagree, we first try to sort it out by talking. If that doesn't work, the court that has jurisdiction under the law decides.</li>
    <li>These terms exist in English and in Polish (<a href="/regulamin" lang="pl">Regulamin</a>). They say the same thing. If they ever differ, the Polish version prevails.</li>
    <li>We may update these terms. The version in force when you start a book applies to that book, unless you agree to a change. The date at the top shows the last update.</li>
  </ul>

  <h2 id="model-form">Model withdrawal form</h2>
  <p>Copy this into an email to <a href="mailto:hello@loopworkbooks.com">hello@loopworkbooks.com</a> only if you want to withdraw:</p>
  <blockquote class="legal-form">
    <p>To: Volodymyr Verbytskyi, Loopwork, Kielce, Poland, hello@loopworkbooks.com</p>
    <p>I hereby withdraw from my agreement for the following service: [your book]</p>
    <p>Agreed on: [date]</p>
    <p>Name: [your name]<br>Email: [your email]<br>Date: [today's date]</p>
  </blockquote>
'''

# ---------------------------------------------------------------- Polish regulamin
REG = '''
  <h1 class="page-h1">Regulamin</h1>
  <p class="legal-meta">Ostatnia aktualizacja: ''' + UPDATED_PL + '''. Wersja angielska: <a href="/terms" lang="en">Terms</a>.</p>
  <p>Ten regulamin opisuje, jak wygląda współpraca z Loopwork: prośba o darmowy rozdział, dwa sposoby przygotowania książki, płatności i zwroty oraz zakup jednej z naszych książek. Informacje o danych osobowych są w <a href="/privacy" lang="en">polityce prywatności</a> (po angielsku).</p>

  <h2 id="kim-jestesmy">1. Kim jesteśmy</h2>
  <p>Loopwork prowadzi Volodymyr Verbytskyi, Kielce, Polska, e-mail <a href="mailto:hello@loopworkbooks.com">hello@loopworkbooks.com</a>. Loopwork nie jest zarejestrowaną firmą: Volodymyr prowadzi ją jako osoba fizyczna w ramach działalności nierejestrowanej.</p>
  <p>W regulaminie „my” oznacza Loopwork, a „Ty” oznacza twórcę, z którym przygotowujemy książkę, albo czytelnika, który kupuje jedną z naszych książek.</p>

  <h2 id="strona">2. Korzystanie ze strony</h2>
  <ul>
    <li>Strona jest bezpłatna. Potrzebujesz aktualnej przeglądarki internetowej, a do prośby o darmowy rozdział także adresu e-mail.</li>
    <li>Wysyłając formularz, prosisz nas o przejrzenie Twoich publicznych postów i odpowiedź w sprawie możliwej książki. Formularz służy tylko do tego. Ta usługa kończy się, gdy odpowiemy, albo wcześniej, jeśli poprosisz nas o zaprzestanie kontaktu.</li>
    <li>Nie przesyłaj przez formularz treści niezgodnych z prawem ani danych innych osób.</li>
  </ul>

  <h2 id="darmowy-rozdzial">3. Darmowy rozdział</h2>
  <p>Czytamy Twoje publiczne posty, proponujemy pomysł na książkę z konspektem oraz piszemy i projektujemy jeden prawdziwy rozdział. Jest bezpłatny i nic nam za niego nie jesteś winien. Jeśli nie zdecydujesz się na współpracę, nie publikujemy ani nie sprzedajemy tego rozdziału.</p>

  <h2 id="umowa">4. Jak zawieramy umowę</h2>
  <p>Zanim zaczniemy pracę nad całą książką, potwierdzamy na piśmie (wystarczy e-mail): książkę, wybrany wariant, cenę albo podział i to, że obowiązuje ten regulamin. Ta wymiana wiadomości razem z regulaminem jest naszą umową. Jeśli podpiszemy z Tobą osobną umowę pisemną, ma ona pierwszeństwo tam, gdzie różni się od regulaminu.</p>

  <h2 id="podzial">5. Wariant „Dzielimy się sprzedażą” (bez opłaty z góry)</h2>
  <ul>
    <li>Nic nie płacisz. Piszemy, projektujemy i wprowadzamy książkę do sprzedaży, a przychód netto dzielimy 50/50 od pierwszej sprzedaży. W czasie Black Week podział wynosi 60/40 na Twoją korzyść (punkt 7).</li>
    <li>„Przychód netto” to kwota zapłacona przez kupujących, pomniejszona o podatek od sprzedaży lub VAT (jeśli dotyczy), opłaty kartowe i opłaty platformy, zwroty oraz obciążenia zwrotne (chargebacki).</li>
    <li>Książka jest sprzedawana przez naszą wspólną stronę na Whop. Whop automatycznie dzieli każdą sprzedaż i przekazuje Twoją część na Twoje saldo Whop, które możesz wypłacić w dowolnym momencie.</li>
    <li>Masz trzy rundy poprawek oraz końcowe sprawdzenie.</li>
    <li>To Twoja książka, z Twoim nazwiskiem i Twoimi treściami. Dopóki współpracujemy, jest sprzedawana tylko przez wspólną stronę.</li>
    <li>Zakończenie współpracy: przed premierą każde z nas może zakończyć ją w dowolnym momencie, informując drugą stronę na piśmie, bez żadnych opłat. Po premierze każde z nas może ją zakończyć z 30-dniowym wypowiedzeniem na piśmie. Sprzedaż w okresie wypowiedzenia dzielimy jak zwykle, a potem książka zostaje wycofana ze sprzedaży. Jeśli chcesz dalej sprzedawać ją samodzielnie, możemy uzgodnić wykup naszej części. Czytelnicy zachowują kupione egzemplarze.</li>
  </ul>

  <h2 id="na-wlasnosc">6. Wariant „Książka na własność” (jednorazowa opłata)</h2>
  <ul>
    <li>Płacisz jednorazową opłatę za książkę i zatrzymujesz całą sprzedaż, po opłatach sklepu. Opłata wynosi 199 USD za książkę za Twoje pierwsze 3 książki, jeśli zaczniesz do 31 grudnia 2026 r. Od 1 stycznia 2027 r. wynosi 290 USD za książkę. W czasie Black Week wynosi 149 USD (punkt 7). Zanim cokolwiek zapłacisz, potwierdzamy Twoją cenę na piśmie.</li>
    <li>Płacisz połowę na start i połowę po zaakceptowaniu gotowej książki. Płatności przechodzą przez Whop.</li>
    <li>Masz dwie rundy poprawek oraz korektę literówek.</li>
    <li>Po zapłacie całości książka należy do Ciebie: możesz ją sprzedawać lub rozdawać gdziekolwiek. Konfigurujemy stronę sprzedaży na Twoim własnym koncie Whop i przekazujemy Ci pliki końcowe.</li>
    <li>Jeśli nie zaakceptujesz książki, nie płacisz drugiej połowy, a my zwracamy pierwszą (punkt 9).</li>
  </ul>

  <h2 id="black-week">7. Oferta Black Week, do 30 listopada 2026 r.</h2>
  <ul>
    <li><strong>Dzielimy się sprzedażą:</strong> zatrzymujesz 60% przychodu netto, a my 40%, przez cały czas, gdy ta książka sprzedaje się u nas.</li>
    <li><strong>Książka na własność:</strong> 149 USD za książkę zamiast 199 USD.</li>
    <li>Aby skorzystać z oferty, poproś o darmowy rozdział albo napisz nam, że chcesz zacząć, do 30 listopada 2026 r. do godziny 23:59 czasu polskiego. Następnie rozpocznij książkę do 31 grudnia 2026 r.: w wariancie „Dzielimy się sprzedażą” przez potwierdzenie na piśmie, a w wariancie „Książka na własność” przez zapłatę pierwszej połowy.</li>
  </ul>

  <h2 id="terminy">8. Terminy i zmiany</h2>
  <ul>
    <li>Darmowy rozdział zwykle zajmuje kilka dni. Pierwsza pełna wersja książki zajmuje około dwóch tygodni, a potem tyle, ile trwają Twoje poprawki. To szacunki, a nie sztywne terminy. Jeśli coś nas opóźni, informujemy Cię o tym.</li>
    <li>Zmiany wykraczające poza rundy poprawek Twojego wariantu, nowe rozdziały lub późniejsze nowe wydanie uzgadniamy z Tobą przed wykonaniem.</li>
  </ul>

  <h2 id="zwroty">9. Zwroty i prawo odstąpienia od umowy</h2>
  <ul>
    <li><strong>Książka na własność:</strong> dopóki nie zaakceptujesz książki, możesz zrezygnować w dowolnym momencie. Jeśli zrezygnujesz albo nie zaakceptujesz gotowej książki, zwracamy w całości połowę zapłaconą z góry, w ciągu 14 dni od Twojej informacji, tą samą metodą płatności. Jeśli z jakiegokolwiek powodu nie możemy dostarczyć książki, zwracamy wszystko, co zapłaciłeś.</li>
    <li><strong>Dzielimy się sprzedażą:</strong> nic nam nie płacisz, więc nie ma czego zwracać.</li>
    <li id="odstapienie"><strong>Ustawowe prawo odstąpienia:</strong> jeśli jesteś konsumentem albo przedsiębiorcą na prawach konsumenta (osobą fizyczną, dla której umowa nie ma charakteru zawodowego), możesz odstąpić od umowy w ciągu 14 dni od jej zawarcia, bez podawania przyczyny. Napisz do nas e-mail albo użyj wzoru formularza na końcu regulaminu. Nasza obietnica zwrotu idzie dalej niż to prawo: dopóki nie zaakceptujesz książki, odzyskujesz całą wpłatę z góry. Jeśli poprosisz nas o rozpoczęcie pracy od razu, a następnie zaakceptujesz gotową książkę i zapłacisz całość w ciągu tych 14 dni, usługa jest w pełni wykonana i prawo odstąpienia wygasa.</li>
  </ul>

  <h2 id="tresci">10. Twoje treści, książka i AI</h2>
  <ul>
    <li>Twoje treści pozostają Twoje: teksty, zdjęcia, metody i nazwisko. Pozwalasz nam ich używać tylko do przygotowania, sprzedaży i promocji Twojej książki, a promocję publikujemy wyłącznie po Twojej akceptacji.</li>
    <li>Potwierdzasz, że przekazane nam treści są Twoje albo że masz prawo z nich korzystać.</li>
    <li>Twoje nieopublikowane materiały zachowujemy w poufności i używamy ich tylko do Twojej książki.</li>
    <li>Teksty szkicujemy przy pomocy narzędzi AI i każdą stronę redagujemy ręcznie na podstawie Twoich postów. Część ilustracji może być wygenerowana przez AI. Mówimy Ci, które, zanim zaakceptujesz książkę.</li>
    <li>Pokazujemy Twoją książkę innym jako przykład naszej pracy tylko za Twoją zgodą.</li>
    <li>Nie przygotowujemy książek z poradami medycznymi, prawnymi ani finansowymi.</li>
  </ul>

  <h2 id="czytelnicy">11. Zakup jednej z naszych książek</h2>
  <ul>
    <li>Nasze książki są cyfrowe (PDF). Whop obsługuje płatność i dostarcza plik.</li>
    <li>Książki na naszej stronie Whop (whop.com/loopworkbooks) sprzedajemy my wspólnie z autorem. Książki na własnej stronie Whop autora sprzedaje ten autor, na swoich warunkach.</li>
    <li>Książka kupiona na naszej stronie: jeśli zmienisz zdanie, napisz w ciągu 14 dni od zakupu, a zwrócimy pieniądze. Jeśli plik się nie otwiera albo książka nie jest taka, jak opisano na jej stronie, naprawimy to albo zwrócimy pieniądze. Napisz na <a href="mailto:hello@loopworkbooks.com">hello@loopworkbooks.com</a> z adresu e-mail użytego przy zakupie.</li>
  </ul>

  <h2 id="reklamacje">12. Reklamacje</h2>
  <p>Napisz na <a href="mailto:hello@loopworkbooks.com">hello@loopworkbooks.com</a>, co poszło nie tak i czego od nas oczekujesz. Odpowiadamy w ciągu 14 dni. Jeśli jesteś konsumentem, możesz też skorzystać z bezpłatnej pomocy miejskiego lub powiatowego rzecznika konsumentów albo Inspekcji Handlowej, a także z pozasądowych sposobów rozwiązywania sporów, np. stałych polubownych sądów konsumenckich. Więcej informacji znajdziesz na <a href="https://uokik.gov.pl" target="_blank" rel="noopener">uokik.gov.pl</a>. W sprawach transgranicznych w UE pomaga Europejskie Centrum Konsumenckie.</p>

  <h2 id="odpowiedzialnosc">13. Odpowiedzialność</h2>
  <p>Nie obiecujemy żadnej liczby sprzedanych egzemplarzy. Każde z nas samo rozlicza podatki od swojej części. Jeśli coś pójdzie nie tak z naszej winy, nasza odpowiedzialność jest ograniczona do kwoty, którą zapłaciłeś nam za daną książkę. To ograniczenie nie dotyczy Twoich praw jako konsumenta ani szkód wyrządzonych umyślnie lub z rażącego niedbalstwa.</p>

  <h2 id="prawo">14. Prawo, język i zmiany</h2>
  <ul>
    <li>Obowiązuje prawo polskie. Jeśli jesteś konsumentem mieszkającym w innym kraju, zachowujesz ochronę, którą daje Ci prawo Twojego kraju.</li>
    <li>W razie sporu najpierw próbujemy porozumieć się w rozmowie. Jeśli to się nie uda, spór rozstrzyga sąd właściwy według przepisów prawa.</li>
    <li>Regulamin istnieje po polsku i po angielsku (<a href="/terms" lang="en">Terms</a>). Obie wersje mają tę samą treść. W razie rozbieżności rozstrzyga wersja polska.</li>
    <li>Możemy aktualizować regulamin. Do danej książki stosuje się wersja obowiązująca w chwili jej rozpoczęcia, chyba że zgodzisz się na zmianę. Data na górze pokazuje ostatnią aktualizację.</li>
  </ul>

  <h2 id="wzor-formularza">Wzór formularza odstąpienia od umowy</h2>
  <p>(formularz ten należy wypełnić i odesłać tylko w przypadku chęci odstąpienia od umowy, np. e-mailem na <a href="mailto:hello@loopworkbooks.com">hello@loopworkbooks.com</a>)</p>
  <blockquote class="legal-form">
    <p>Adresat: Volodymyr Verbytskyi, Loopwork, Kielce, Polska, hello@loopworkbooks.com</p>
    <p>Ja niniejszym informuję o moim odstąpieniu od umowy o świadczenie następującej usługi: [Twoja książka]</p>
    <p>Data zawarcia umowy: [data]</p>
    <p>Imię i nazwisko konsumenta: [imię i nazwisko]<br>Adres konsumenta: [adres]<br>Podpis konsumenta (tylko jeżeli formularz jest przesyłany w wersji papierowej)<br>Data: [dzisiejsza data]</p>
  </blockquote>
'''

# ---------------------------------------------------------------- Refunds summary (English)
REFUNDS = '''
  <h1 class="page-h1">Refunds</h1>
  <p class="legal-meta">Last updated ''' + UPDATED_EN + '''. The full rules are in our <a href="/terms#refunds">terms</a> (<a href="/regulamin#zwroty" lang="pl">po polsku</a>).</p>

  <h2>If we make a book with you</h2>
  <ul>
    <li><strong>Own it outright:</strong> you pay half when you start. Until you approve the finished book you can stop at any time, and if you stop or don't approve it, we refund that half in full. If we can't deliver the book for any reason, we refund everything you paid.</li>
    <li><strong>Share the sales:</strong> you pay nothing upfront, so there is nothing to refund.</li>
    <li>If you are a consumer, you also have a legal right to withdraw within 14 days of making the agreement. Our promise above already covers it. <a href="/terms#withdraw">How it works</a>.</li>
  </ul>

  <h2>If you bought one of our books</h2>
  <ul>
    <li>Bought from our Whop page (whop.com/loopworkbooks): changed your mind? Ask within 14 days of buying and we refund you.</li>
    <li>If the file doesn't open, or the book isn't what its page described, we fix it or refund you.</li>
    <li>Books on an author's own Whop page are sold by that author, under their own refund terms.</li>
  </ul>

  <h2>How to ask</h2>
  <p>Email <a href="mailto:hello@loopworkbooks.com">hello@loopworkbooks.com</a> with what you bought or agreed, and the email you used. We reply within 14 days and refund to the payment method you used.</p>
'''

page('terms.html', 'en', 'Terms | Loopwork', TERMS)
page('regulamin.html', 'pl', 'Regulamin | Loopwork', REG)
page('refunds.html', 'en', 'Refunds | Loopwork', REFUNDS)
print('ok')
