FX=6.7
# channel unit economics (per order), prices net of 1% VAT ignored for simplicity
ING=8.0; PACK=2.0  # per cookie
def orders(scn):
    k = dict(base=dict(vol=1.0, comm=0.20, ing=ING), pess=dict(vol=0.65, comm=0.23, ing=ING*1.10))[scn]
    ch = {
     'instore': dict(cookies=2, price=60, extra=0.006*60),          # payment fee 0.6%
     'delivery': dict(cookies=3, price=82, extra=None),               # 90 list - 8 merchant promo
     'gift': dict(cookies=6, price=168, extra=None),
    }
    out={}
    for n,c in ch.items():
        cogs=c['cookies']*(k['ing']+PACK)
        if n=='instore': var=cogs+c['extra']
        if n=='delivery': var=cogs+c['price']*k['comm']+2.0   # +insulated bag
        if n=='gift': var=6*k['ing']+15+18+168*0.006               # 6 cookies ingr, tin 15, SF 18
        out[n]=dict(price=c['price'],cookies=c['cookies'],var=var,contrib=c['price']-var)
    return out,k
base_daily={'instore':140,'delivery':65,'gift':6}
ramp=[1.0,1.0,0.95,0.90,0.85,0.85,0.90,0.90,0.85,0.85,0.90,0.85]  # opening hype then novelty decay, rotation/custom keep floor   # M1..M12 for instore/delivery (Mar27..Feb28)
months=['Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec','Jan','Feb']
giftmult=[1,1,3,1,1,3,5,1,1,2,2,5]  # 520 May, Qixi Aug, Mid-Autumn Sep, Xmas/NY Dec-Jan, Spring Festival Feb
FIX={'Rent+mgmt fee':48000,'Store labour (6 FTE + PT)':69000,'Central kitchen (shared unit, chef, shuttle)':30500,
     'Utilities':6000,'Marketing (ongoing)':30000,'Mini-Program/SaaS':3000,'Admin, accounting, insurance':7000}
CAPEX_DEP=(300000+220000+120000+80000)/60   # fit-out, store eq, CK eq, mini-program over 5y
def run(scn,show=False):
    o,k=orders(scn); rows=[]
    for i,m in enumerate(months):
        d={}
        for n in o:
            daily=base_daily[n]*k['vol']*(giftmult[i] if n=='gift' else ramp[i])
            d[n]=daily*30
        rev=sum(d[n]*o[n]['price'] for n in o)
        var=sum(d[n]*o[n]['var'] for n in o)
        cookies=sum(d[n]*o[n]['cookies'] for n in o)
        fix=sum(FIX.values())
        ebitda=rev-var-fix
        rows.append(dict(m=m,orders=sum(d.values()),cookies=cookies,rev=rev,var=var,fix=fix,ebitda=ebitda,ebit=ebitda-CAPEX_DEP))
    return o,rows
for s in ['base','pess']:
    o,r=run(s)
    print('\n==',s)
    for n,v in o.items(): print(n,{a:round(b,1) for a,b in v.items()}, 'margin',round(v['contrib']/v['price']*100,1))
    T=lambda key: sum(x[key] for x in r)
    for x in r: print(x['m'],round(x['orders']),round(x['cookies']),round(x['rev']),round(x['var']),round(x['ebitda']),round(x['ebit']))
    rev=T('rev');ck=T('cookies')
    print('YEAR rev',round(rev),'cookies',round(ck),'avg/cookie',round(rev/ck,2),'orders',round(T('orders')),'AOV',round(rev/T('orders'),1))
    print('var',round(T('var')),'fixed',round(T('fix')),'EBITDA',round(T('ebitda')),'Dep',round(CAPEX_DEP*12),'EBIT',round(T('ebit')))
    cit=max(0,T('ebit'))*0.05; print('CIT5%',round(cit),'NI',round(T('ebit')-cit))
    cum=0;mn=0
    for x in r: cum+=x['ebitda']; mn=min(mn,cum)
    print('min cumulative EBITDA',round(mn))
print('fixed/month',sum(FIX.values()),'dep/month',round(CAPEX_DEP))

BUDGET={'WFOE setup, licences, trademarks, Mini-Program ICP filing':60000,'WeChat Mini-Program + POS/CRM build':80000,
'Store fit-out (50 sqm)':300000,'Store equipment (ovens, warmers, chillers)':220000,'Central-kitchen equipment (shared unit)':120000,
'Rent deposit (3 mo) + 1 mo pre-opening rent':192000,'Pre-opening payroll, training, recipe R&D':140000,'Launch marketing':150000,
'Opening inventory, packaging & gift-tin design':80000,'Operating reserve (ramp + downside cover)':400000,'Contingency':158000}
tot=sum(BUDGET.values()); print('\nBUDGET',tot, round(tot/FX))
for k,v in BUDGET.items(): print(f'{k}: {v} ({v/FX/1000:.1f}k USD) {v/tot*100:.1f}%')
# payback: cumulative after-tax operating cash vs investment excluding refundable deposit and unspent reserve? use full ask, conservative
for s in ['base','pess']:
    o,r=run(s); cum=-tot; pb=None
    yr=[x['ebitda'] for x in r]
    ann=sum(yr); 
    m=0
    # year2 assume = steady avg of months 7-12 repeated
    y2=[sum(yr[6:])/6]*24
    seq=yr+y2
    for i,v in enumerate(seq):
        cum+=v*(0.95 if v>0 else 1)  # 5% CIT approx
        if cum>=0 and pb is None: pb=i+1
    print(s,'payback months after opening (full ask)',pb, 'Y1 EBITDA',round(ann), 'Y2 run-rate EBITDA/mo', round(y2[0]))
    # payback excluding refundable deposit 144k and unspent reserve 400k
    inv=tot-144000-400000; cum=-inv; pb=None
    for i,v in enumerate(seq):
        cum+=v*(0.95 if v>0 else 1)
        if cum>=0 and pb is None: pb=i+1
    print(s,'payback on spent capital',inv,pb)
o,r=run('base')
print('labour/yr',69000*12,'ingredients+pack base', round(sum(x['cookies'] for x in r)*(ING+PACK)))

print('\n=== detail')
for s in ['base','pess']:
    o,r=run(s)
    k=orders(s)[1]
    ck=sum(x['cookies'] for x in r); ingpack=ck*(k['ing']+PACK)
    # gift ingredient fix: gift uses 6*ing + tin15 (no PACK)  -> recompute exactly by channel
    vol={n:0 for n in o}
    for i,m in enumerate(months):
        for n in o: vol[n]+=base_daily[n]*k['vol']*(giftmult[i] if n=='gift' else ramp[i])*30
    print(s,{n:round(v) for n,v in vol.items()})
    food=vol['instore']*2*(k['ing']+PACK)+vol['delivery']*3*(k['ing']+PACK)+vol['gift']*(6*k['ing']+15)
    plat=vol['delivery']*(82*k['comm']+2)
    other=vol['instore']*0.36+vol['gift']*(18+168*0.006)
    print(' food+pack',round(food),'platform',round(plat),'pay+SF',round(other),'sum',round(food+plat+other),'var',round(sum(x['var'] for x in r)))
    q=[sum(x['rev'] for x in r[i:i+3]) for i in (0,3,6,9)]; qe=[sum(x['ebitda'] for x in r[i:i+3]) for i in (0,3,6,9)]
    print(' Q rev',[round(a) for a in q],'Q ebitda',[round(a) for a in qe])
    if s=='pess':
        saved=30000*8
        print(' pess with triggers EBITDA',round(sum(x['ebitda'] for x in r)+saved),'EBIT',round(sum(x['ebitda'] for x in r)+saved-144000))
        qe2=[qe[0],qe[1]+30000*2,qe[2]+90000,qe[3]+90000]; print(' Q ebitda w triggers',[round(a) for a in qe2])
        # break-even daily orders
fixed=sum(FIX.values())
o,_=run('base')
mixc=(140*o['instore']['contrib']+65*o['delivery']['contrib']+6*o['gift']['contrib'])/(211)
mixp=(140*60+65*82+6*168)/211
print('blended contrib/order',round(mixc,1),'AOV',round(mixp,1),'BE orders/day',round(fixed/30/mixc), 'BE rev/month', round(fixed/30/mixc*mixp*30))
print('steady daily rev base', 140*60+65*82+6*168, 'cookies/day',140*2+65*3+36)
