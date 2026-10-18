# SweetDrop China v2: pop-up (M1-2, TX Huaihai) -> street store Wukang-Anfu (M3-12). Dough made on site.
FX=6.7
ING=8.4   # ingredients per cookie incl. ~5% waste (on-site dough)
# channel economics per cookie (prices incl. VAT; VAT handled separately)
CH={
 'instore': dict(price=31.0, fee_pct=0.006, pack=1.5),          # avg ticket incl. custom options
 'douyin':  dict(price=24.5, fee_pct=0.05,  pack=1.5),          # voucher 2 for 49, Douyin fee ~5% [A]
 'delivery':dict(price=32.0*0.85, fee_pct=0.22, pack=2.5),      # 15% merchant coupon; Meituan/Ele.me commission+delivery ~22%
}
MIX_STORE={'instore':0.50,'douyin':0.15,'delivery':0.35}
MIX_POP  ={'instore':0.80,'douyin':0.20,'delivery':0.0}
SCN={'bad':dict(pop=300,store=280),'normal':dict(pop=500,store=450),'good':dict(pop=800,store=700)}  # cookies/day
GIFT={'bad':300,'normal':500,'good':800}  # gift boxes per festival month (6 cookies, 168 net)
FEST=[False,False,True,False,False,True,True,False,False,False,True,False]  # Mar..Feb: May(520),Aug(Qixi),Sep(Mid-Autumn),Jan(CNY)
months=['Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec','Jan','Feb']
LAB_STORE=(12000+2*9000+2*7000)*1.30+8000   # mgr, 2 bakers, 2 crew, +30% social ins/housing fund, + part-time
FIX_STORE={'rent':60*30*30+3000,'labour':LAB_STORE,'utilities':8000,'marketing':30000,'admin':8000}
FIX_POP  ={'rent':5000*30,'labour':LAB_STORE,'utilities':5000,'marketing':30000,'admin':8000}
DEP=(330000+260000+80000)/60  # store fit-out, equipment, reusable pop-up booth; 5 yrs
def unit(ch,mix):
    p=sum(CH[c]['price']*mix[c] for c in mix)
    v=sum((ING+CH[c]['pack']+CH[c]['price']*CH[c]['fee_pct'])*mix[c] for c in mix)
    return p,v
def run(s):
    rows=[]
    for i,m in enumerate(months):
        pop=i<2
        mix=MIX_POP if pop else MIX_STORE
        cpd=SCN[s]['pop' if pop else 'store']
        n=cpd*30
        p,v=unit(CH,mix)
        rev=n*p; var=n*v
        g=GIFT[s] if FEST[i] else 0
        rev+=g*178; var+=g*(6*ING+15+18+178*0.006)   # gift box 178 incl VAT, tin 15, SF 18
        fix=dict(FIX_POP if pop else FIX_STORE)
        rows.append(dict(m=m,cookies=n+6*g,rev=rev,var=var,fix=sum(fix.values()),fixd=fix))
    R=sum(r['rev'] for r in rows)
    vat_rate=0.01 if R/1.01<=5_000_000 else None
    if vat_rate: vat=R-R/1.01
    else:
        net=R/1.06; vat=(R-net) - sum(r['cookies'] for r in rows)*ING*0.09  # input VAT credit on ingredients ~9%
    sur=vat*0.12*0.5  # city/education surcharges, halved for small enterprises
    netrev=R-vat
    var=sum(r['var'] for r in rows); fix=sum(r['fix'] for r in rows)
    ebitda=netrev-var-fix-sur
    ebit=ebitda-DEP*12
    cit=max(0,ebit)*0.05 if ebit<=3e6 else ebit*0.25
    agg={k:sum(r['fixd'][k] for r in rows) for k in rows[0]['fixd']}
    return dict(rows=rows,R=R,vat=vat,sur=sur,netrev=netrev,var=var,fix=fix,agg=agg,ebitda=ebitda,ebit=ebit,cit=cit,ni=ebit-cit,cookies=sum(r['cookies'] for r in rows))
for s in SCN:
    r=run(s)
    print(f"\n== {s}: cookies {r['cookies']:,.0f}  gross rev {r['R']:,.0f}  VAT {r['vat']:,.0f}  net rev {r['netrev']:,.0f}")
    print(f" var {r['var']:,.0f} ({r['var']/r['netrev']*100:.0f}%)  contrib {r['netrev']-r['var']:,.0f}")
    print(' fixed', {k:round(v) for k,v in r['agg'].items()}, f"total {r['fix']:,.0f}")
    print(f" surcharges {r['sur']:,.0f}  EBITDA {r['ebitda']:,.0f} ({r['ebitda']/r['netrev']*100:.1f}%)  dep {DEP*12:,.0f}  EBIT {r['ebit']:,.0f}  CIT {r['cit']:,.0f}  NI {r['ni']:,.0f}")
    # monthly store-phase steady EBITDA (non-fest)
    st=[x for i,x in enumerate(r['rows']) if i>=2 and not FEST[i]][0]
    e_store=st['rev']/1.01-st['var']-st['fix'] if r['R']/1.01<=5e6 else st['rev']/1.06*1.0-st['var']-st['fix']
    pop=r['rows'][0]; e_pop=pop['rev']/1.01-pop['var']-pop['fix']
    print(f" pop-up month rev {pop['rev']:,.0f} EBITDA≈{e_pop:,.0f} | store normal month rev {st['rev']:,.0f} EBITDA≈{e_store:,.0f}")
    cum=0;mn=0
    for i,x in enumerate(r['rows']):
        cum+=x['rev']/1.01-x['var']-x['fix']; mn=min(mn,cum)
    print(f" min cumulative EBITDA {mn:,.0f}")
p,v=unit(CH,MIX_STORE); print('\nstore blended price/cookie',round(p,2),'var',round(v,2),'contrib',round(p/1.01-v,2))
for c in CH:
    pp=CH[c]['price']; vv=ING+CH[c]['pack']+pp*CH[c]['fee_pct']; print(c,pp,round(vv,2),'contrib',round(pp/1.01-vv,2),f"{(pp/1.01-vv)/(pp/1.01)*100:.0f}%")
print('fixed store/month',round(sum(FIX_STORE.values())),'labour',round(LAB_STORE),'pop/month',round(sum(FIX_POP.values())))
be=sum(FIX_STORE.values())/(p/1.01-v)/30; print('BE cookies/day store',round(be))

BUDGET={'WFOE setup, licences (pop-up + store), trademarks':60000,'Pop-up booth (modular, reused)':80000,
'Store fit-out 60 sqm incl. kitchen ventilation':330000,'Equipment (2 ovens, mixer, chillers, display)':260000,
'Store rent deposit (3 months)':171000,'Pre-opening payroll, training, recipe R&D':160000,'Launch marketing':150000,
'Opening inventory, packaging, gift-box design':60000,'Contingency':129000,'Operating reserve':500000}
T=sum(BUDGET.values()); print('\nBUDGET',T,round(T/FX))
for k,v in BUDGET.items(): print(f' {k}: {v:,} ({v/FX/1000:.1f}k$, {v/T*100:.1f}%)')
def year2(s):
    # 12 store months + 4 festival gift months
    cpd=SCN[s]['store']; p,v=unit(CH,MIX_STORE); n=cpd*360; g=GIFT[s]*4
    R=n*p+g*178; var=n*v+g*(6*ING+15+18+178*0.006); fix=sum(FIX_STORE.values())*12
    if R/1.01<=5e6: vat=R-R/1.01
    else: vat=(R-R/1.06)-(n+6*g)*ING*0.09
    e=R-vat-var-fix-vat*0.06
    return R,e
spent=T-171000-500000
for s in SCN:
    r=run(s); R2,e2=year2(s)
    y1cash=r['ebitda']-r['cit']
    y2cash=e2-max(0,e2-DEP*12)*0.05
    left=spent-y1cash
    pb = None if y1cash+y2cash*3<spent and y2cash<=0 else (12*spent/y1cash if y1cash>=spent else 12+left/(y2cash/12))
    print(s,'Y2 rev',round(R2),'Y2 EBITDA',round(e2),'payback months on spent',spent, None if pb is None else round(pb,1))
r=run('normal'); print('normal netrev/cookie', round(r['netrev']/r['cookies'],2),'var/cookie',round(r['var']/r['cookies'],2),'fix/cookie',round(r['fix']/r['cookies'],2),'ebitda/cookie',round(r['ebitda']/r['cookies'],2))
