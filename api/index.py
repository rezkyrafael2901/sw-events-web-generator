"""SW Events Generator — Vercel serverless."""
from __future__ import annotations
import base64, collections, datetime as dt, hashlib, json, math, random, zipfile
from io import BytesIO
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI()

EW = [("ACTIVITY_RESUMED",28),("ACTIVITY_PAUSED",27.5),("EVENT_23",22),("NOTIFICATION_INTERRUPTION",6),("NOTIFICATION_SEEN",4.5),("FOREGROUND_SERVICE_START",3.2),("FOREGROUND_SERVICE_STOP",3.2),("STANDBY_BUCKET_CHANGED",2.8),("USER_INTERACTION",1.6),("SCREEN_INTERACTIVE",0.9),("SCREEN_NON_INTERACTIVE",0.8),("KEYGUARD_HIDDEN",0.3),("KEYGUARD_SHOWN",0.2),("CONFIGURATION_CHANGE",0.1)]
BH=[.012,.008,.007,.006,.006,.009,.018,.036,.052,.068,.072,.065,.07,.064,.06,.062,.068,.075,.08,.078,.052,.042,.028,.018]
BP={"samsung":{"models":["samsung SM-A057F","samsung SM-A155F","samsung SM-A226B","samsung SM-A035F","samsung SM-A105G"],"av":["13","14"],"ec":[18000,76000],"cp":[.6,.82],"apps":[("com.whatsapp","com.whatsapp.HomeActivity",.205),("com.sec.android.app.launcher","com.android.quickstep.RecentsActivity",.15),("android","",.058),("com.google.android.gms","com.google.android.gms.common.api.GoogleApiActivity",.044),("com.instagram.android","com.instagram.mainactivity.InstagramMainActivity",.043),("com.facebook.katana","com.facebook.katana.LoginActivity",.038),("com.ss.android.ugc.trill","com.ss.android.ugc.aweme.splash.SplashActivity",.037),("org.telegram.messenger","org.telegram.ui.LaunchActivity",.035),("com.android.chrome","com.google.android.apps.chrome.Main",.034),("com.google.android.youtube","com.google.android.apps.youtube.app.WatchWhileActivity",.03),("com.samsung.android.dialer","com.samsung.android.dialer.DialtactsActivity",.024),("com.samsung.android.messaging","com.samsung.android.messaging.ui.view.main.WithActivity",.022),("com.sec.android.gallery3d","com.samsung.android.gallery.app.activity.GalleryActivity",.021),("com.sec.android.app.camera","com.sec.android.app.camera.Camera",.018),("com.android.settings","com.android.settings.Settings",.018),("com.google.android.gm","com.google.android.gm.ConversationListActivityGmail",.015),("id.dana","id.dana.home.HomeTabActivity",.014),("com.gojek.app","com.gojek.app.HomeActivity",.014),("com.shopee.id","com.shopee.app.ui.home.HomeActivity_",.013),("com.tokopedia.tkpd","com.tokopedia.tkpd.ConsumerMainActivity",.012),("com.spotify.music","com.spotify.music.MainActivity",.011),("com.android.vending","com.android.vending.AssetBrowserActivity",.011),("com.samsung.android.calendar","com.samsung.android.calendar.MainActivity",.008)]},"xiaomi":{"models":["Xiaomi 2201117PG","Xiaomi M2006C3MG","Xiaomi M2010J19SG","Xiaomi 24075RP89G","Redmi Note 13"],"av":["12","13","14"],"ec":[18000,105000],"cp":[.58,.8],"apps":[("com.whatsapp","com.whatsapp.HomeActivity",.17),("com.mi.android.globallauncher","com.miui.home.launcher.Launcher",.12),("com.miui.home","com.miui.home.launcher.Launcher",.072),("android","",.058),("org.telegram.messenger","org.telegram.ui.LaunchActivity",.048),("com.android.chrome","com.google.android.apps.chrome.Main",.044),("com.google.android.gms","com.google.android.gms.common.api.GoogleApiActivity",.04),("com.ss.android.ugc.trill","com.ss.android.ugc.aweme.splash.SplashActivity",.038),("com.instagram.android","com.instagram.mainactivity.InstagramMainActivity",.034),("com.google.android.youtube","com.google.android.apps.youtube.app.WatchWhileActivity",.032),("com.xiaomi.mipicks","com.xiaomi.mipicks.ui.MainActivity",.026),("com.miui.securitycenter","com.miui.securityscan.MainActivity",.024),("com.miui.gallery","com.miui.gallery.activity.HomePageActivity",.022),("com.android.settings","com.android.settings.Settings",.02),("com.google.android.apps.photos","com.google.android.apps.photos.home.HomeActivity",.018),("id.dana","id.dana.home.HomeTabActivity",.016),("com.gojek.app","com.gojek.app.HomeActivity",.015),("com.shopee.id","com.shopee.app.ui.home.HomeActivity_",.014),("com.mobile.legends","com.moba.unityplugin.MobaGameMainActivity",.013),("com.android.vending","com.android.vending.AssetBrowserActivity",.012),("com.miui.weather2","com.miui.weather2.ActivityWeatherMain",.01)]},"oppo":{"models":["OPPO CPH2577","OPPO CPH2387","OPPO CPH1909","OPPO CPH2591"],"av":["11","12","13","14"],"ec":[19000,76000],"cp":[.6,.84],"apps":[("com.whatsapp","com.whatsapp.HomeActivity",.165),("com.whatsapp.w4b","com.whatsapp.HomeActivity",.1),("com.android.launcher","com.android.launcher3.Launcher",.14),("com.oppo.launcher","com.oppo.launcher.Launcher",.052),("android","",.06),("com.facebook.lite","com.facebook.lite.MainActivity",.055),("org.telegram.messenger","org.telegram.ui.LaunchActivity",.045),("com.android.chrome","com.google.android.apps.chrome.Main",.04),("com.coloros.recents","com.coloros.recents.RecentsActivity",.038),("com.instagram.android","com.instagram.mainactivity.InstagramMainActivity",.034),("com.google.android.gms","com.google.android.gms.common.api.GoogleApiActivity",.03),("com.ss.android.ugc.trill","com.ss.android.ugc.aweme.splash.SplashActivity",.026),("com.google.android.youtube","com.google.android.apps.youtube.app.WatchWhileActivity",.024),("com.android.settings","com.android.settings.Settings",.022),("com.google.android.gm","com.google.android.gm.ConversationListActivityGmail",.019),("id.dana","id.dana.home.HomeTabActivity",.016),("com.gojek.app","com.gojek.app.HomeActivity",.015),("com.shopee.id","com.shopee.app.ui.home.HomeActivity_",.014),("com.spotify.music","com.spotify.music.MainActivity",.012),("com.android.vending","com.android.vending.AssetBrowserActivity",.012),("com.panjoy.android","",.01)]},"infinix":{"models":["Infinix X6833B","Infinix X669C","Infinix X6728B","Infinix X6886"],"av":["12","13","14"],"ec":[20000,65000],"cp":[.62,.83],"apps":[("com.whatsapp","com.whatsapp.HomeActivity",.17),("com.transsion.XOSLauncher","com.transsion.launcher.Launcher",.13),("android","",.055),("tw.nekomimi.nekogram","org.telegram.ui.LaunchActivity",.06),("com.android.chrome","com.google.android.apps.chrome.Main",.045),("com.instagram.android","com.instagram.mainactivity.InstagramMainActivity",.04),("com.twitter.android","com.twitter.app.main.MainActivity",.035),("com.google.android.gms","com.google.android.gms.common.api.GoogleApiActivity",.032),("com.authy.authy","com.authy.authy.activities.MainActivity",.03),("org.telegram.messenger","org.telegram.ui.LaunchActivity",.028),("com.google.android.gm","com.google.android.gm.ConversationListActivityGmail",.025),("com.openai.chatgpt","com.openai.chatgpt.MainActivity",.022),("com.android.settings","com.android.settings.Settings",.02),("id.dana","id.dana.home.HomeTabActivity",.016),("com.gojek.app","com.gojek.app.HomeActivity",.015),("com.ss.android.ugc.trill","com.ss.android.ugc.aweme.splash.SplashActivity",.014),("com.shopee.id","com.shopee.app.ui.home.HomeActivity_",.012),("com.android.vending","com.android.vending.AssetBrowserActivity",.011),("com.binance.dev","com.binance.dev.SplashActivity",.01),("com.google.android.youtube","com.google.android.apps.youtube.app.WatchWhileActivity",.01)]},"advan":{"models":["Advan G5","Advan G9 Pro","Advan i6C"],"av":["11","12","13"],"ec":[15000,55000],"cp":[.56,.78],"apps":[("com.whatsapp","com.whatsapp.HomeActivity",.18),("com.advan.launcher","",.11),("android","",.06),("com.android.chrome","com.google.android.apps.chrome.Main",.05),("org.telegram.messenger","org.telegram.ui.LaunchActivity",.042),("com.instagram.android","com.instagram.mainactivity.InstagramMainActivity",.036),("com.google.android.gms","com.google.android.gms.common.api.GoogleApiActivity",.03),("com.ss.android.ugc.trill","com.ss.android.ugc.aweme.splash.SplashActivity",.028),("com.google.android.youtube","com.google.android.apps.youtube.app.WatchWhileActivity",.024),("com.android.settings","com.android.settings.Settings",.022),("id.dana","id.dana.home.HomeTabActivity",.018),("com.gojek.app","com.gojek.app.HomeActivity",.016),("com.shopee.id","com.shopee.app.ui.home.HomeActivity_",.014),("com.google.android.gm","com.google.android.gm.ConversationListActivityGmail",.012),("com.android.vending","com.android.vending.AssetBrowserActivity",.011),("com.spotify.music","com.spotify.music.MainActivity",.01),("com.facebook.katana","com.facebook.katana.LoginActivity",.01)]}}

def _nw(items):
    s=sum(w for _,_,w in items); return [(p,c,w/s) for p,c,w in items]

def _gen(brand,model,av,count,seed,days):
    rng=random.Random(seed); prof=BP[brand]
    model=model or rng.choice(prof["models"]); av=av or rng.choice(prof["av"])
    if count is None: lo,hi=prof["ec"]; count=rng.randint(lo,hi)
    count=min(count,80000)
    if days is None: days=rng.uniform(7.1,9.8)
    end=dt.datetime(2026,5,26,rng.randint(5,20),rng.randint(0,59),rng.randint(0,59),tzinfo=dt.timezone.utc)
    start=end-dt.timedelta(days=days,minutes=rng.randint(0,180),seconds=rng.randint(0,59))
    apps=_nw(prof["apps"]); pkgs=[p for p,_,_ in apps]; cls={p:c for p,c,_ in apps}; pw=[w for _,_,w in apps]
    ct=rng.uniform(*prof["cp"]); tn=[t for t,_ in EW]; tw=[w*rng.uniform(.82,1.18) for _,w in EW]
    ds=[]; d=start.date()
    while d<=end.date(): ds.append(d); d+=dt.timedelta(days=1)
    ws=[]
    for day in ds:
        w=1.0
        if day.weekday() in(5,6): w*=rng.uniform(1.05,1.35)
        if day.weekday()==0: w*=rng.uniform(.72,1.05)
        if day==start.date(): w*=rng.uniform(.32,.65)
        if day==end.date(): w*=rng.uniform(.35,.75)
        w*=rng.uniform(.68,1.42); ws.append(w)
    s=sum(ws); dc={d:int(round(count*w/s)) for d,w in zip(ds,ws)}
    while sum(dc.values())<count: dc[rng.choice(ds)]+=1
    while sum(dc.values())>count: k=rng.choice([d for d in ds if dc[d]>20]); dc[k]-=1
    rows=[]
    for day,nd in sorted(dc.items()):
        hw=[max(.0004,w*rng.uniform(.7,1.35)) for w in BH]
        if day.weekday() in(5,6):
            for h in range(12,23): hw[h]*=rng.uniform(1.02,1.32)
            for h in range(7,11): hw[h]*=rng.uniform(.75,1.05)
        hs=sum(hw); hw=[x/hs for x in hw]; ph=[int(round(nd*w)) for w in hw]
        while sum(ph)<nd: ph[rng.randrange(24)]+=1
        while sum(ph)>nd: h=rng.choice([i for i,v in enumerate(ph) if v>0]); ph[h]-=1
        for hr,nh in enumerate(ph):
            rem=nh
            while rem>0:
                burst=min(rem,max(1,int(rng.lognormvariate(2.12,.8)))); rem-=burst
                cur=dt.datetime(day.year,day.month,day.day,hr,rng.randrange(60),rng.randrange(60),rng.randrange(1000)*1000,tzinfo=dt.timezone.utc)
                if cur<start: cur=start+dt.timedelta(seconds=rng.randint(0,2400),milliseconds=rng.randint(0,999))
                if cur>end: cur=end-dt.timedelta(seconds=rng.randint(0,2400),milliseconds=rng.randint(0,999))
                sp=rng.choices(pkgs,weights=pw,k=1)[0]
                for i in range(burst):
                    if i:
                        r=rng.random()
                        if r<.62: delta=rng.uniform(.04,.95)
                        elif r<.91: delta=rng.uniform(1,20)
                        elif r<.985: delta=rng.uniform(20,210)
                        else: delta=rng.uniform(210,950)
                        cur+=dt.timedelta(seconds=delta,milliseconds=rng.randint(0,25))
                    if not(start<=cur<=end): continue
                    pp=sp
                    if rng.random()<.13:
                        vl=pkgs[1] if len(pkgs)>1 else pkgs[0]
                        pp=rng.choices([vl,"android","com.google.android.gms","com.android.settings"],weights=[.46,.3,.17,.07],k=1)[0]
                    if i==0 and rng.random()<.7: typ="ACTIVITY_RESUMED"
                    elif i==burst-1 and rng.random()<.63: typ="ACTIVITY_PAUSED"
                    else: typ=rng.choices(tn,weights=tw,k=1)[0]
                    rec={"ts":int(cur.timestamp()*1000)+rng.randint(0,12),"package":pp,"type":typ}
                    c=cls.get(pp,"")
                    if c:
                        if typ in("ACTIVITY_RESUMED","ACTIVITY_PAUSED","EVENT_23","USER_INTERACTION","CONFIGURATION_CHANGE"): h=rng.random()<min(.94,ct+.18)
                        elif typ.startswith("FOREGROUND_SERVICE"): h=rng.random()<max(.25,ct-.3)
                        elif typ.startswith("SCREEN") or typ.startswith("KEYGUARD") or typ=="STANDBY_BUCKET_CHANGED": h=rng.random()<max(.04,ct-.58)
                        else: h=rng.random()<max(.08,ct-.48)
                        if h: rec["class"]=c
                    rows.append(rec)
    rows.sort(key=lambda r:r["ts"])
    while len(rows)>count: rows.pop(rng.randrange(len(rows)))
    while len(rows)<count:
        cur=start+dt.timedelta(seconds=rng.randint(0,max(1,int((end-start).total_seconds()))),milliseconds=rng.randint(0,999))
        pp=rng.choices(pkgs,weights=pw,k=1)[0]; typ=rng.choices(tn,weights=tw,k=1)[0]
        rec={"ts":int(cur.timestamp()*1000),"package":pp,"type":typ}
        if typ in("ACTIVITY_RESUMED","ACTIVITY_PAUSED","EVENT_23") and rng.random()<.86 and cls.get(pp): rec["class"]=cls[pp]
        rows.append(rec)
    rows.sort(key=lambda r:r["ts"])
    mn=dt.datetime.fromtimestamp(rows[0]["ts"]/1000,dt.timezone.utc)
    mx=dt.datetime.fromtimestamp(rows[-1]["ts"]/1000,dt.timezone.utc)
    iso=lambda t:t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest={"schema_version":1,"app_version":"1.0.0","android_version":av,"device_model":model,"export_generated_at":iso(mx),"window_start":iso(mn),"window_end":iso(mx),"event_count":len(rows),"notes":"Event-level data subject to Android system retention; older periods may be summarised only."}
    return rows,manifest

def _analyze(rows):
    pkg=collections.Counter(r["package"] for r in rows)
    typ=collections.Counter(r["type"] for r in rows)
    gaps=[(b["ts"]-a["ts"])/1000 for a,b in zip(rows,rows[1:])]
    cp=sum(1 for r in rows if "class" in r)/len(rows)*100 if rows else 0
    def q(vs,n):
        if not vs: return 0
        vs=sorted(vs); return vs[min(len(vs)-1,int((len(vs)-1)*n))]
    def H(c):
        t=sum(c.values()); return -sum((v/t)*math.log2(v/t) for v in c.values() if v and t) if t else 0
    return {"event_count":len(rows),"unique_packages":len(pkg),"package_entropy":round(H(pkg),3),"event_type_entropy":round(H(typ),3),"class_presence_pct":round(cp,2),"gap_p50":round(q(gaps,.5),3),"gap_p90":round(q(gaps,.9),3),"gap_p99":round(q(gaps,.99),3),"lte1":round(sum(g<=1 for g in gaps)/len(gaps)*100,2) if gaps else 0,"gt10m":round(sum(g>600 for g in gaps)/len(gaps)*100,2) if gaps else 0,"top_packages":pkg.most_common(30),"event_types":typ.most_common()}

def _score(m):
    s=100; r=[]
    if not(5000<=m["event_count"]<=110000): s-=15
    if not(55<=m["class_presence_pct"]<=86): s-=18
    if not(.25<=m["gap_p50"]<=1.2): s-=18
    if not(8<=m["gap_p90"]<=60): s-=12
    if not(80<=m["gap_p99"]<=900): s-=8
    if not(50<=m["lte1"]<=73): s-=14
    if not(.05<=m["gt10m"]<=3): s-=8
    if not(2.5<=m["package_entropy"]<=5.4): s-=6
    if not(1.5<=m["event_type_entropy"]<=3.5): s-=6
    return max(0,s)

def _zip(rows,manifest):
    nd="\n".join(json.dumps(r,separators=(",",":"),ensure_ascii=False) for r in rows)+"\n"
    ms=json.dumps(manifest,separators=(",",":"),ensure_ascii=False)
    buf=BytesIO()
    with zipfile.ZipFile(buf,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        z.writestr("events.ndjson",nd); z.writestr("manifest.json",ms)
    d=buf.getvalue(); return d,hashlib.sha256(d).hexdigest()

@app.get("/",response_class=HTMLResponse)
def index():
    import pathlib
    h=(pathlib.Path(__file__).resolve().parent.parent/"index.html").read_text()
    return HTMLResponse(h)

@app.get("/api/profiles")
def profiles():
    return {b:{"models":p["models"],"android_versions":p["av"],"event_count_range":p["ec"]} for b,p in BP.items()}

@app.post("/api/generate")
def generate(brand:str=Form("xiaomi"),model:Optional[str]=Form(None),android:Optional[str]=Form(None),count:Optional[str]=Form(None),days:Optional[str]=Form(None),seed:Optional[str]=Form(None)):
    brand=brand.lower().strip()
    if brand not in BP: raise HTTPException(400,"Unknown brand")
    def pi(v,lo,hi):
        if not v or not v.strip(): return None
        n=int(v.strip())
        if not lo<=n<=hi: raise HTTPException(400,f"Must be {lo}-{hi}")
        return n
    def pf(v,lo,hi):
        if not v or not v.strip(): return None
        n=float(v.strip())
        if not lo<=n<=hi: raise HTTPException(400,f"Must be {lo}-{hi}")
        return n
    try:
        rows,manifest=_gen(brand,(model or "").strip() or None,(android or "").strip() or None,pi(count,1000,80000),pi(seed,0,999999999),pf(days,1,14))
    except Exception as e: raise HTTPException(500,str(e))
    m=_analyze(rows); sc=_score(m); zb,sha=_zip(rows,manifest)
    return {"filename":"sw_events","zip_size":len(zb),"zip_sha256":sha,"zip_base64":base64.b64encode(zb).decode(),"summary":{"device_model":manifest["device_model"],"android_version":manifest["android_version"],"event_count":manifest["event_count"],"window_start":manifest["window_start"],"window_end":manifest["window_end"],"score":sc,"sha256":sha,"zip_size":len(zb),"top_packages":m["top_packages"][:10],"event_types":m["event_types"][:10]},"notice":"Synthetic QA fixture only."}
