// A mild superellipse: n=2 is an ellipse; 2.35 adds just a little squareness.
// Smooth cubic segments retain a clean vector contour at export resolution.
function ovalPoint(cx,cy,rx,ry,n,t){
  const c=Math.cos(t),s=Math.sin(t),power=2/n;
  return [cx+rx*Math.sign(c)*Math.abs(c)**power,cy+ry*Math.sign(s)*Math.abs(s)**power];
}
function ovalArc(cx,cy,rx,ry,n,start,end){
  const count=Math.max(24,Math.ceil(Math.abs(end-start)*24));
  const step=(end-start)/count;
  const point=i=>ovalPoint(cx,cy,rx,ry,n,start+i*step);
  const fmt=p=>p.map(v=>Number(v.toFixed(3))).join(' ');
  let d='M'+fmt(point(0));
  for(let i=0;i<count;i++){
    const p0=point(i-1),p1=point(i),p2=point(i+1),p3=point(i+2);
    const c1=p1.map((v,j)=>v+(p2[j]-p0[j])/6);
    const c2=p2.map((v,j)=>v-(p3[j]-p1[j])/6);
    d+=` C${fmt(c1)} ${fmt(c2)} ${fmt(p2)}`;
  }
  return d;
}
function balloonMarkup(id,w,h,d,warm=false){
  const tint=warm?'#F0D99A':'#D7B9EC',line=warm?'#EAE1CA':'#E5DCED';
  return `<svg viewBox="0 0 ${w} ${h}" aria-hidden="true"><defs><clipPath id="${id}-clip"><path d="${d}"/></clipPath><filter id="${id}-soft" x="-20%" y="-35%" width="140%" height="180%" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="7"/></filter></defs><path class="balloon-body" d="${d}" fill="#FFFFFF"/><g clip-path="url(#${id}-clip)"><path d="${d}" fill="none" stroke="${tint}" stroke-width="12" opacity=".42" filter="url(#${id}-soft)"/></g><path class="balloon-contour" d="${d}" fill="none" stroke="${line}" stroke-width="1.1" stroke-linejoin="round"/></svg>`;
}
// Balloon layers are independent from the device UI and floating source cards.
function renderBalloons(){
  document.querySelectorAll('.bubble').forEach((el,index)=>{
    el.querySelector('svg')?.remove();
    const style=getComputedStyle(el),w=parseFloat(style.width),h=parseFloat(style.height);
    const warm=el.dataset.speaker==='woman',edge=1.1;
    const cx=w/2,cy=h/2,rx=cx-edge,ry=cy-edge,n=2.35;
    const root=Math.max(cx-rx*.72,Math.min(cx+rx*.72,w*Number(el.dataset.tailRoot)));
    const lowerEdge=x=>cy+ry*Math.max(0,1-Math.abs((x-cx)/rx)**n)**(1/n);
    const [speakerX,speakerY]=el.dataset.anchor.split(',').map(Number);
    const baseY=lowerEdge(root),depth=Number(el.dataset.tailDepth||27)*.86;
    const dx=speakerX-(el.offsetLeft+root),dy=Math.max(20,speakerY-(el.offsetTop+baseY));
    const length=Math.hypot(dx,dy),tipX=root+dx/length*depth,tipY=baseY+dy/length*depth;
    const a=root-10.5,b=root+10.5,ay=lowerEdge(a),by=lowerEdge(b);
    const theta=x=>{const v=(x-cx)/rx;return Math.acos(Math.sign(v)*Math.abs(v)**(n/2));};
    const d=ovalArc(cx,cy,rx,ry,n,theta(b),theta(a)-Math.PI*2)+` C${a+4} ${ay+5} ${tipX-4} ${tipY-4} ${tipX} ${tipY} C${tipX+4} ${tipY-4} ${b-3} ${by+5} ${b} ${by} Z`;
    const id='balloon'+index;
    // A blurred inner rim follows the actual contour, rather than making the
    // four corners dark as an elliptical radial gradient does. The center stays white.
    el.insertAdjacentHTML('afterbegin',balloonMarkup(id,w,h,d,warm));
    el.dataset.bubbleReady='true';
    el.dataset.bubbleShape='rounded-oval';
    el.dataset.ovalExponent=String(n);
  });
  document.querySelectorAll('.thought-pod').forEach((el,index)=>{
    el.querySelector(':scope>svg')?.remove();
    const s=getComputedStyle(el),w=parseFloat(s.width),h=parseFloat(s.height);
    const d=ovalArc(w/2,h/2,w/2-1.1,h/2-1.1,2.35,0,Math.PI*2)+' Z';
    el.insertAdjacentHTML('afterbegin',balloonMarkup('thought'+index,w,h,d));
    el.querySelector(':scope>svg').classList.add('thought-shape');
    el.dataset.bubbleShape='rounded-oval';
  });
}
window.comicReady=document.fonts.ready.then(renderBalloons);
// Map editable 240x500 native UI to the four physical screen corners.
// data-quad coordinates are measured on the original 1254x1254 illustration.
function solve(A,b){
  const n=b.length;
  for(let i=0;i<n;i++){
    let p=i;for(let r=i+1;r<n;r++)if(Math.abs(A[r][i])>Math.abs(A[p][i]))p=r;
    [A[i],A[p]]=[A[p],A[i]];[b[i],b[p]]=[b[p],b[i]];
    const d=A[i][i];for(let c=i;c<n;c++)A[i][c]/=d;b[i]/=d;
    for(let r=0;r<n;r++)if(r!==i){const k=A[r][i];for(let c=i;c<n;c++)A[r][c]-=k*A[i][c];b[r]-=k*b[i];}
  }
  return b;
}
document.querySelectorAll('.in-photo-screen').forEach(el=>{
 const points=JSON.parse(el.dataset.quad).map(([x,y])=>[x*622/1254-19,y*622/1254]);
 const src=[[0,0],[240,0],[240,500],[0,500]],A=[],b=[];
 src.forEach(([x,y],i)=>{const [u,v]=points[i];A.push([x,y,1,0,0,0,-u*x,-u*y]);b.push(u);A.push([0,0,0,x,y,1,-v*x,-v*y]);b.push(v);});
 const [a,c,e,d,f,g,h,j]=solve(A,b);
 el.style.transform=`matrix3d(${a},${d},0,${h},${c},${f},0,${j},0,0,1,0,${e},${g},0,1)`;
});
const params=new URLSearchParams(location.search);
if(params.has('export'))document.body.classList.add('export');
else{
 document.body.classList.add('fit');
 const fit=()=>{const scale=Math.min(1,window.innerWidth/1800);document.querySelector('#comic').style.transform=`scale(${scale})`;document.body.style.height=`${1280*scale}px`;};
 window.addEventListener('resize',fit);fit();
}
