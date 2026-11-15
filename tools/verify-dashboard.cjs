// Bounded local QA; no persistent server and no external requests.
const {chromium}=require('../sources/demo-suite/node_modules/playwright');
const fs=require('fs'),path=require('path'),cp=require('child_process');
const http=require('http');
const status=url=>new Promise((resolve,reject)=>http.get(url,r=>{r.resume();r.on('end',()=>resolve(r.statusCode));}).on('error',reject));
const root=path.resolve(__dirname,'..'), dir=path.resolve(process.argv[2]||path.join(root,'artifacts/dashboard'));
(async()=>{let server,browser;try{
 server=cp.spawn('python3',['-m','http.server','4340','--bind','127.0.0.1','--directory',dir],{stdio:'ignore'});
 for(let i=0;i<50;i++){if(server.exitCode!==null)throw Error('QA port unavailable');try{if((await status('http://127.0.0.1:4340/'))===200)break}catch{}await new Promise(r=>setTimeout(r,100));}
 browser=await chromium.launch({headless:true,chromiumSandbox:true});
 const page=await browser.newPage({viewport:{width:1440,height:1100}});
 await page.route('**/*',r=>r.request().url().startsWith('http://127.0.0.1:4340/')?r.continue():r.abort());
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:4340/');
 if(await page.locator('article').count()!==2)throw Error('Missing reference cards');
 await page.locator('details').evaluateAll(es=>es.forEach(e=>e.open=true));
 const clips=[];for(const video of await page.locator('video').all()){
  clips.push(await video.evaluate(async v=>{v.muted=true;await v.play();await new Promise(r=>setTimeout(r,150));const d={duration:v.duration,played:v.currentTime>0};v.pause();if(!d.played||!Number.isFinite(d.duration))throw Error('Video did not play');return d;}));
 }
 for(const url of await page.locator('a[href]').evaluateAll(es=>es.map(e=>e.href))){if((await status(url))!==200)throw Error('Broken link');}
 if(await page.locator('img').evaluateAll(es=>es.some(e=>!e.complete||!e.naturalWidth)))throw Error('Image failed');
 await page.locator('details').evaluateAll(es=>es.forEach(e=>e.open=false));
 await page.screenshot({path:path.join(root,'artifacts/dashboard-desktop.png'),fullPage:true});
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(root,'artifacts/dashboard-mobile.png'),fullPage:true});
 if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Mobile horizontal overflow');
 if(errors.length)throw Error(errors.join('; '));
 const result={status:'verified',sandbox:true,cards:2,playedClips:clips.length,clips,mobileOverflow:false};
 fs.writeFileSync(path.join(root,'artifacts/dashboard-qa.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
}finally{if(browser)await browser.close();if(server)server.kill('SIGTERM')}})().catch(e=>{console.error(e);process.exitCode=1});
