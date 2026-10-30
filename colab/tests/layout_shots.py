"""Layout-level screenshots of all.html in 4 slices.

usage: uv run --with playwright python -I colab/tests/layout_shots.py $COLAB_TMP/<slug> <shots-dir>
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402  ($CHROME → Windows path → PATH)
from pathlib import Path
from playwright.sync_api import sync_playwright
D=Path(sys.argv[1]); O=Path(sys.argv[2])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=chrome(),args=['--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    pg=b.new_page(viewport={'width':1000,'height':900})
    pg.goto((D/'all.html').as_uri()); pg.wait_for_timeout(4000)
    h=pg.evaluate('document.body.scrollHeight'); print('height',h)
    # split the long page into ~4 layout shots
    n=4; step=h//n+1
    for i in range(n):
        pg.screenshot(path=str(O/f'layout-{i+1}.png'),clip={'x':0,'y':i*step,'width':1000,'height':min(step,h-i*step)},full_page=True)
    b.close()
