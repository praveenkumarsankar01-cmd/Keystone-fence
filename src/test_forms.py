import os, sys, threading, http.server, socketserver, functools
from PIL import Image
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(root + '/shots', exist_ok=True)
noise = Image.frombytes('RGB', (504, 378), os.urandom(504 * 378 * 3)).resize((4032, 3024), Image.BILINEAR)
noise.save(root + '/shots/phone.jpg', quality=92)
ORIG = os.path.getsize(root + '/shots/phone.jpg')
print('test photo: 4032x3024,', round(ORIG / 1024), 'KB')
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Q, directory=root + '/dist')); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
from playwright.sync_api import sync_playwright
R = []
def ok(name, cond, extra=''):
    R.append(cond); print(('PASS ' if cond else 'FAIL ') + name + (f'  [{extra}]' if extra else ''))
def chip(pg, name, value): pg.click(f'label:has(input[name="{name}"][value="{value}"]) span')
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    def page(path, mode='success', key=True):
        pg = b.new_page(viewport={'width': 390, 'height': 844}); calls = []
        def handle(route):
            body = route.request.post_data_buffer or b''
            calls.append(body)
            if mode == 'reject-photos' and b'filename=' in body:
                route.fulfill(status=400, content_type='application/json', body='{"success":false,"message":"file too large"}')
            else:
                route.fulfill(status=200, content_type='application/json', body='{"success":true}')
        pg.route('https://api.web3forms.com/**', handle)
        pg.goto(f'http://127.0.0.1:{port}/{path}', wait_until='domcontentloaded')
        if key: pg.evaluate("window.KEYSTONE_FORM.key='test-key'")
        return pg, calls
    def step1(pg, method='Call', who='Homeowner'):
        pg.fill('#e-name', 'Dana Reyes'); pg.fill('#e-phone', '(469) 555-0101'); pg.fill('#e-email', 'dana@example.com')
        chip(pg, 'contact_method', method); pg.fill('#e-addr', '12 Elm St'); pg.fill('#e-zip', '75093'); chip(pg, 'customer_type', who)

    # 1. no access key configured -> honest message, nothing sent, no fake success
    pg, calls = page('free-estimate/', key=False)
    step1(pg); pg.select_option('#e-service', label='Wood Privacy Fence'); pg.click('[data-next]')
    pg.fill('#e-desc', 'About 140 ft along the alley.'); pg.click('button[type=submit]'); pg.wait_for_timeout(300)
    msg = pg.inner_text('.form-status')
    ok('no key: "not connected" + phone shown, no false success', "isn't connected" in msg and not pg.is_visible('.success') and not calls, msg[:70])
    pg.close()

    # 2. validation
    pg, calls = page('free-estimate/')
    pg.click('[data-next]'); pg.wait_for_timeout(200)
    inv = pg.evaluate("document.querySelectorAll('.step-panel:not([hidden]) .invalid').length")
    ok('empty step 1 blocked, fields flagged', inv >= 7 and pg.is_visible('#e-name'), f'{inv} flagged')
    pg.fill('#e-phone', '555-12'); pg.fill('#e-email', 'not-an-email'); pg.click('[data-next]'); pg.wait_for_timeout(150)
    ok('short phone and malformed email rejected', pg.evaluate("['#e-phone','#e-email'].every(s=>document.querySelector(s).closest('.field').classList.contains('invalid'))"))
    pg.fill('#e-phone', '469 555 0101'); pg.wait_for_timeout(100)
    ok('error clears as soon as the field is fixed', not pg.evaluate("document.querySelector('#e-phone').closest('.field').classList.contains('invalid')"))
    pg.close()

    # 3. service prefill + happy path with a photo
    pg, calls = page('free-estimate/?service=pool-fence')
    v = pg.evaluate("document.querySelector('#e-service').value")
    ok('?service=pool-fence preselects the service', 'Pool Fence' in v, v)
    step1(pg); pg.click('[data-next]'); pg.wait_for_timeout(200)
    ok('step 2 opens after a valid step 1', pg.is_visible('#e-desc') and not pg.is_visible('#e-name'))
    pg.set_input_files('input[name=photos]', root + '/shots/phone.jpg')
    ok('photo thumbnail + count shown', pg.evaluate("document.querySelectorAll('.thumb').length") == 1, pg.inner_text('.js-photo-count'))
    pg.fill('#e-desc', 'Pool barrier, roughly 180 ft, two gates.'); pg.click('button[type=submit]')
    pg.wait_for_selector('.success.show', timeout=10000)
    body = calls[-1] if calls else b''
    need = [b'name="access_key"', b'test-key', b'Dana Reyes', b'Pool Fence', b'name="customer_type"', b'Homeowner',
            b'name="contact_method"', b'name="address"', b'name="description"', b'name="attachment"', b'filename="phone.jpg"', b'image/jpeg']
    missing = [n.decode() for n in need if n not in body]
    ok('success state shown after delivery', pg.is_visible('.success') and not pg.is_visible('form.js-lead'))
    ok('payload carries every field and the photo', not missing, 'missing: ' + ', '.join(missing) if missing else 'all present')
    ok('12 MP photo resized before upload', len(body) < ORIG * 0.6, f'request {round(len(body)/1024)} KB vs photo {round(ORIG/1024)} KB')
    pg.close()

    # 4. provider refuses the photos -> lead still delivered without them, customer told
    pg, calls = page('free-estimate/?service=wood-privacy-fence', 'reject-photos')
    step1(pg, 'Email', 'Builder / GC'); pg.click('[data-next]')
    pg.set_input_files('input[name=photos]', root + '/shots/phone.jpg')
    pg.fill('#e-desc', 'New build, 300 ft perimeter.'); pg.click('button[type=submit]')
    pg.wait_for_selector('.success.show', timeout=10000)
    ok('photos refused -> resent without them, lead delivered', len(calls) == 2 and b'filename=' not in calls[1] and b'photos_note' in calls[1], f'{len(calls)} requests')
    ok('customer told to text the photos instead', pg.is_visible('.js-photo-note'))
    pg.close()

    # 5. quick form on a service page
    pg, calls = page('gates/driveway-gates/')
    pg.fill('#q-name', 'Ana'); pg.fill('#q-phone', '469-555-0103'); pg.fill('#q-addr', '75034'); pg.click('#quote button[type=submit]')
    pg.wait_for_selector('#quote .success.show', timeout=8000)
    ok('quick form delivers, labelled with its service', bool(calls) and b'Driveway Gates' in calls[-1])
    pg.close()

    # 6. contact form
    pg, calls = page('contact/')
    pg.fill('#c-name', 'Lee'); pg.fill('#c-phone', '4695550104'); pg.fill('#c-email', 'lee@example.com'); pg.fill('#c-msg', 'Do you work in Wylie?')
    pg.click('form.js-lead button[type=submit]'); pg.wait_for_selector('.success.show', timeout=8000)
    ok('contact form delivers', bool(calls) and b'Do you work in Wylie?' in calls[-1])
    pg.close()

    # 7. mobile menu
    pg, calls = page('')
    pg.click('.js-menu'); pg.wait_for_timeout(350)
    ok('menu opens', pg.evaluate("document.getElementById('drawer').classList.contains('open')"))
    pg.click('.d-group:first-child .d-row'); pg.wait_for_timeout(100)
    ok('silo accordion expands to its services', pg.is_visible('.d-group:first-child .d-sub a.hub'))
    pg.keyboard.press('Escape'); pg.wait_for_timeout(350)
    ok('Escape closes the menu', not pg.evaluate("document.getElementById('drawer').classList.contains('open')"))
    pg.close()

    # 8. projects filter
    pg, calls = page('projects/')
    pg.click('.filters button[data-filter=gates]')
    vis = pg.evaluate("[...document.querySelectorAll('.proj-card')].filter(c=>!c.hidden).map(c=>c.dataset.silo)")
    ok('projects filter shows only that trade', vis and set(vis) == {'gates'}, f'{len(vis)} shown')
    pg.close()
    b.close()
srv.shutdown()
print(f"\n{sum(R)}/{len(R)} checks passed")
