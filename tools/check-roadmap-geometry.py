import json,re
import os
sp=os.environ.get('ROADMAP_TMP',os.path.dirname(os.path.abspath(__file__)))
g=json.load(open(sp+"/geo.json"))
NUM=re.compile(r'-?\d*\.?\d+')
def segs(d):
    toks=re.findall(r'([MHVLmhvl])([^MHVLmhvl]*)',d); x=y=0.0; pts=[]
    for c,a in toks:
        n=[float(v) for v in NUM.findall(a)]
        if c=='M': x,y=n[0],n[1]; pts.append((x,y))
        elif c=='H': x=n[0]; pts.append((x,y))
        elif c=='V': y=n[0]; pts.append((x,y))
        elif c=='L': x,y=n[0],n[1]; pts.append((x,y))
    return [(pts[i],pts[i+1]) for i in range(len(pts)-1)]
def seg_box(p,q,b):
    x0,y0=p; x1,y1=q
    bx0,by0,bx1,by1=b['x'],b['y'],b['x']+b['w'],b['y']+b['h']
    if abs(y0-y1)<.01:
        if not(by0<=y0<=by1): return False
        a,bb=min(x0,x1),max(x0,x1); return not(bb<=bx0 or a>=bx1)
    if abs(x0-x1)<.01:
        if not(bx0<=x0<=bx1): return False
        a,bb=min(y0,y1),max(y0,y1); return not(bb<=by0 or a>=by1)
    return False
bx=g['boxes']; nb=[b for b in bx if b['t']!='pill']
allb=bx  # wires must not pass under pills either
print("=== 1. box/box overlaps ===")
c1=0
for i in range(len(nb)):
    for j in range(i+1,len(nb)):
        a,b=nb[i],nb[j]
        if not(a['x']+a['w']<=b['x'] or b['x']+b['w']<=a['x'] or a['y']+a['h']<=b['y'] or b['y']+b['h']<=a['y']):
            print("  %s:%r <-> %s:%r"%(a['t'],a['s'],b['t'],b['s'])); c1+=1
print("  total",c1)
print("=== 2. wire through box ===")
TRIM=17; c2=0
for w in g['wires']:
    ss=segs(w['d']); P0,P1=ss[0][0],ss[-1][1]
    def anchor(b):
        for pt in (P0,P1):
            if b['x']-22<=pt[0]<=b['x']+b['w']+22 and b['y']-22<=pt[1]<=b['y']+b['h']+22: return True
        return False
    hits=[]
    for si,(p,q) in enumerate(ss):
        pp,qq=list(p),list(q)
        dx,dy=qq[0]-pp[0],qq[1]-pp[1]; L=(dx*dx+dy*dy)**.5 or 1
        if si==0: pp[0]+=dx/L*TRIM; pp[1]+=dy/L*TRIM
        if si==len(ss)-1: qq[0]-=dx/L*TRIM; qq[1]-=dy/L*TRIM
        for b in allb:
            if anchor(b): continue
            if seg_box(pp,qq,b): hits.append("%s:%s"%(b['t'],b['s']))
    if hits:
        print("  wire#%d [%s] %s"%(w['i'],w['k'],w['d']))
        for h in sorted(set(hits)): print("       X "+h)
        c2+=1
print("  total",c2)
print("=== 3. arrowhead hidden under ANY box ===")
c3=0
for w in g['wires']:
    x,y=segs(w['d'])[-1][1]
    for b in bx:
        dx=max(b['x']-x,x-(b['x']+b['w']),0); dy=max(b['y']-y,y-(b['y']+b['h']),0)
        if (dx*dx+dy*dy)**.5<7:
            print("  wire#%d end(%d,%d) -> %s:%r"%(w['i'],x,y,b['t'],b['s'][:28])); c3+=1
print("  total",c3)

print("=== 4. pill escaping its node ===")
c4=0
for p in [b for b in bx if b['t']=='pill']:
    for n in [b for b in bx if b['t']=='node']:
        if not(p['x']+p['w']<=n['x'] or n['x']+n['w']<=p['x'] or p['y']+p['h']<=n['y'] or n['y']+n['h']<=p['y']):
            if not(p['x']>=n['x'] and p['x']+p['w']<=n['x']+n['w'] and p['y']>=n['y'] and p['y']+p['h']<=n['y']+n['h']):
                print("  pill %r sticks out of %s"%(p['s'][:28],n['s'])); c4+=1
print("  total",c4)
