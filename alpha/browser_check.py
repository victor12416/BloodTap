"""Optional real-browser checks. Install requirements-dev.txt first."""
import json
from pathlib import Path
import random
import tempfile
import threading
from playwright.sync_api import sync_playwright,expect
from alpha.game import Game
from alpha.server import make_server
from alpha import saves
import simulator as sim


def main():
    artifacts=Path('test-artifacts');artifacts.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as folder:
        game=Game(Path(folder)/'save.json',rng=random.Random(42))
        server=make_server(game,0)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        url=f'http://127.0.0.1:{server.server_port}'
        try:
            with sync_playwright() as pw:
                browser=pw.chromium.launch(channel='chrome',headless=True)
                page=browser.new_page(viewport={'width':1440,'height':1100},reduced_motion='reduce')
                errors=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto(url)
                expect(page.locator('#save-status')).to_contain_text('Progress saved')
                for _ in range(15):page.get_by_role('button',name='Gather echoes',exact=True).click()
                first=page.locator('.producer').first
                expect(first).to_be_enabled();first.click()
                expect(first.locator('.count')).to_have_text('1 owned')
                page.reload();expect(page.locator('.producer').first.locator('.count')).to_have_text('1 owned')
                page.get_by_role('button',name='Save & settings').click()
                with page.expect_download() as download:
                    page.get_by_role('link',name='Export save').click()
                exported=json.loads(Path(download.value.path()).read_text())
                assert exported['state']['owned'][0]==1
                # Import through the actual file picker with a valid richer save.
                sample=sim.State(bank=1e9,run_earned=8e12)
                payload=saves.encode(sample).encode()
                page.locator('#import-file').set_input_files({'name':'fixture.json','mimeType':'application/json','buffer':payload})
                expect(page.locator('#confirm')).to_be_visible();page.locator('#confirm-submit').click()
                expect(page.locator('#notice')).to_have_text('Save imported.')
                page.get_by_role('button',name='Close settings').click()
                page.locator('[data-quantity="10"]').click();page.locator('.producer').first.click()
                expect(page.locator('.producer').first.locator('.count')).to_have_text('10 owned')
                page.locator('.upgrade').first.click()
                game.state.omen_next=game.state.elapsed
                expect(page.locator('#omen')).to_be_visible(timeout=4000)
                page.locator('#omen').click();expect(page.locator('#omen')).to_be_hidden()
                page.screenshot(path=str(artifacts/'desktop.png'),full_page=True)
                # Keyboard activation, dialog cancellation, then explicit reset.
                page.locator('#vessel').focus();page.keyboard.press('Enter')
                page.locator('#reawaken').click();expect(page.locator('#confirm')).to_be_visible()
                page.locator('#confirm-input').fill('REAWAKEN');page.locator('#confirm-submit').click()
                expect(page.locator('#fragments')).to_have_text('2')
                page.locator('[data-key="U363"]').click();page.locator('[data-key="U281"]').click()
                expect(page.locator('#offline-info')).to_contain_text('5%')
                page.get_by_role('button',name='Save & settings').click();page.locator('#reset').click()
                page.locator('#confirm-cancel').click();expect(page.locator('#confirm')).not_to_be_visible()
                assert 'U281' in game.state.ascension_upgrades
                page.locator('#reset').click();page.locator('#confirm-input').fill('RESET');page.locator('#confirm-submit').click()
                expect(page.locator('#notice')).to_have_text('A new vigil begins.')
                page.get_by_role('button',name='Close settings').click()
                page.set_viewport_size({'width':390,'height':844});page.reload()
                expect(page.locator('#vessel')).to_be_visible()
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
                page.screenshot(path=str(artifacts/'mobile.png'),full_page=True)
                assert not errors,errors
                browser.close()
                print('PASS: desktop/mobile, tap/buy/upgrade/reload, export/import, Omen, keyboard, Reawakening, reset safeguards; no JS errors')
        finally:
            server.shutdown();server.server_close();thread.join(timeout=3)


if __name__=='__main__':main()
