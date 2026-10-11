// Standalone server for the downloadable atlas. Uses only built-in Node modules.
import {createServer} from 'node:http';
import {createReadStream} from 'node:fs';
import {stat} from 'node:fs/promises';
import {dirname,extname,isAbsolute,relative,resolve,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createGunzip} from 'node:zlib';
import {pipeline} from 'node:stream';
import {spawn} from 'node:child_process';

const directory=dirname(fileURLToPath(import.meta.url));
const root=resolve(directory,process.env.ATLAS_PUBLIC_DIR??'www');
const port=Number(process.env.ATLAS_PORT??3016);
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8',
 '.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8',
 '.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml','.woff2':'font/woff2',
 '.bin':'application/octet-stream','.gz':'application/octet-stream','.md':'text/plain; charset=utf-8'};

const server=createServer(async(req,res)=>{
 if(req.method!=='GET'&&req.method!=='HEAD'){res.writeHead(405,{Allow:'GET, HEAD'});res.end();return;}
 let pathname;
 try{pathname=decodeURIComponent(req.url.split('?')[0]);}catch{res.writeHead(400);res.end();return;}
 const filename=resolve(root,'.'+pathname),part=relative(root,filename);
 if(part==='..'||part.startsWith('..'+sep)||isAbsolute(part)||pathname.includes('\0')){res.writeHead(403);res.end();return;}
 let file=filename,decompress=false,info;
 try{
  info=await stat(file);
  if(info.isDirectory()){file=resolve(file,'index.html');info=await stat(file);}
 }catch{
  // The bundle stores model geometry once, compressed. Older browsers that
  // request the uncompressed URL receive the identical decompressed stream.
  if(extname(file)!=='.bin'){res.writeHead(404);res.end('Not found');return;}
  try{info=await stat(file+'.gz');file+='.gz';decompress=true;}catch{res.writeHead(404);res.end('Not found');return;}
 }
 if(!info.isFile()){res.writeHead(404);res.end();return;}
 res.setHeader('Content-Type',types[extname(decompress?filename:file)]??'application/octet-stream');
 res.setHeader('X-Content-Type-Options','nosniff');
 if(!decompress)res.setHeader('Content-Length',info.size);
 res.writeHead(200);
 if(req.method==='HEAD'){res.end();return;}
 const done=error=>{if(error&&!res.destroyed)res.destroy(error);};
 if(decompress)pipeline(createReadStream(file),createGunzip(),res,done);
 else pipeline(createReadStream(file),res,done);
});
server.on('error',error=>{
 console.error(error.code==='EADDRINUSE'?`Port ${port} jest zajety. Zamknij inne okno atlasu i uruchom ponownie.`:error.message);
 process.exitCode=1;
});
server.listen(port,'127.0.0.1',()=>{
 const url=`http://localhost:${server.address().port}/`;
 console.log(`Anatomy RE: ${url}\nZostaw to okno otwarte podczas korzystania z atlasu. Ctrl+C zamyka atlas.`);
 if(process.platform==='win32'&&process.env.ATLAS_NO_BROWSER!=='1'){
  const browser=spawn('cmd.exe',['/d','/c','start','',url],{windowsHide:true,stdio:'ignore'});
  browser.on('error',()=>console.log(`Otworz w przegladarce: ${url}`));
 }
});
