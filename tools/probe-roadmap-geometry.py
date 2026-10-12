import re,json,html,subprocess,sys
import os
from pathlib import Path
if hasattr(sys.stdout, 'reconfigure'):
 sys.stdout.reconfigure(encoding='utf-8')
sp=os.environ.get('ROADMAP_TMP',os.path.dirname(os.path.abspath(__file__)))
os.makedirs(sp,exist_ok=True)
src=(Path(__file__).resolve().parent.parent/'organic-reaction-roadmap.html').read_text(encoding='utf-8')
probe = """
<script>
window.addEventListener('load',function(){setTimeout(function(){
 var cv=document.querySelector('.canvas');var cb=cv.getBoundingClientRect();var K=cb.width/cv.offsetWidth;
 var boxes=[];
 document.querySelectorAll('.canvas .node,.canvas .lbl,.canvas .pill').forEach(function(e){
  var r=e.getBoundingClientRect();
  boxes.push({t:e.className.split(' ')[0],x:Math.round((r.left-cb.left)/K),y:Math.round((r.top-cb.top)/K),
   w:Math.round(r.width/K),h:Math.round(r.height/K),
   s:(e.querySelector('.nm,b')||e).textContent.trim().slice(0,26)});});
 var wires=[];
 document.querySelectorAll('svg.wires > g path').forEach(function(p,i){
  var points=[],length=p.getTotalLength();
  for(var s=0;s<length;s+=2){var pt=p.getPointAtLength(s);points.push([pt.x,pt.y]);}
  var end=p.getPointAtLength(length);points.push([end.x,end.y]);
  wires.push({i:i,k:p.parentNode.dataset.k,d:p.getAttribute('d'),points:points});});
 var o=document.createElement('pre');o.id='PROBE';o.textContent=JSON.stringify({boxes:boxes,wires:wires});
 document.body.appendChild(o);},1200);});
</script>
"""
open(sp+"/probe.html","w",encoding="utf-8").write(src.replace("</body>",probe+"</body>"))
subprocess.run(['C:/Program Files/Google/Chrome/Application/chrome.exe','--headless','--disable-gpu',
  '--virtual-time-budget=6000','--incognito','--disable-application-cache','--dump-dom',Path(sp,'probe.html').resolve().as_uri()],
  stdout=open(sp+"/dom.html","w",encoding="utf-8"),stderr=subprocess.DEVNULL)
d=open(sp+"/dom.html",encoding="utf-8",errors="replace").read()
m=re.search(r'<pre id="PROBE">(.*?)</pre>',d,re.S)
if not m:
 raise SystemExit('Chrome did not produce geometry. Inspect dom.html and check that headless Chrome can run in this environment.')
json.dump(json.loads(html.unescape(m.group(1))),open(sp+"/geo.json","w"),indent=0)
print("probed")
