require('./_headless_harness_stub.js');
const H = globalThis.__H;
// godmode: keep squad pinned so the run survives to exercise levels 2-4 naturally
H.startRun('campaign');
let step=0,lastLevel=1,maxSquadSeen=0;
try{
 for(step=0;step<60000;step++){
   if(H.G.squad<8)H.G.squad=8;           // keep alive, but cap still applies (<=15)
   H.update(0.1);
   maxSquadSeen=Math.max(maxSquadSeen,H.G.squad);
   const st=H.state;
   if(st==='perk'){H.pickPerkForce();H.G.state=H.G.boss?'boss':'play';}
   else if(st==='shop')H.levelStart();
   else if(st==='win'){console.log('WIN reached, cleared all levels');break;}
   else if(st==='dead'){H.G.state='play';}   // ignore deaths for progress test
   H.draw();
   if(H.G.level!==lastLevel){console.log(`level ${H.G.level} @${(step*0.1)|0}s squad=${H.G.squad} enemies=${H.enemies.count()}`);lastLevel=H.G.level;}
 }
 console.log(`ENDED clean: level=${H.G.level} state=${H.state} maxSquadSeen=${maxSquadSeen} (cap=${H.CFG.squadMax})`);
}catch(e){console.error(`THREW @level ${H.G.level} step ${step}:`,e.message);}
