(function(){
  const B=window.MCM_BASE||'';const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
  const money=v=>'$'+Number(v).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
  const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

  // ---- shop grid ----
  const shop=$('.shop');
  if(shop){
    const grid=$('#grid'), more=$('#more'), count=$('#count');
    const params=new URLSearchParams(location.search);
    let state={cat:shop.dataset.preset||params.get('cat')||'',stone:params.get('stone')||'',q:params.get('q')||'',price:params.get('price')||'',sort:params.get('sort')||'new'};
    let data=[],meta={},shown=0,list=[];const PAGE=48;
    $('#q').value=state.q;$('#stone').value=state.stone;$('#price').value=state.price;$('#sort').value=state.sort;
    const card=x=>`<a class="card" href="${B}/products/${x.h}/"><div class="ph"><img loading="lazy" src="${esc(x.i)}" alt="${esc(x.t)}" width="400" height="400"></div><div class="meta"><span class="tag" style="--c:${meta.cats[x.c].color}">${esc(x.s!=='Other'?x.s:meta.cats[x.c].name)}</span><h3>${esc(x.t)}</h3><p class="price">${x.n>1?'<small>'+x.n+' options from</small> ':''}${x.k?'<s>'+money(x.k)+'</s> ':''}${money(x.p)}</p></div></a>`;
    function apply(){
      const q=state.q.toLowerCase().trim();const [lo,hi]=state.price?state.price.split('-').map(Number):[0,1e9];
      list=data.filter(x=>(!state.cat||x.c===state.cat)&&(!state.stone||x.s===state.stone)&&x.p>=lo&&x.p<hi&&(!q||x.t.toLowerCase().includes(q)));
      const so={new:(a,b)=>b.d.localeCompare(a.d),lo:(a,b)=>a.p-b.p,hi:(a,b)=>b.p-a.p,az:(a,b)=>a.t.localeCompare(b.t)}[state.sort];
      list.sort(so);shown=0;grid.innerHTML='';page();
      count.textContent=list.length.toLocaleString()+' item'+(list.length===1?'':'s');
      $$('.f').forEach(b=>b.classList.toggle('on',b.dataset.cat===state.cat));
      if(!shop.dataset.preset){const u=new URLSearchParams();Object.entries(state).forEach(([k,v])=>{if(v&&!(k==='sort'&&v==='new'))u.set(k,v)});history.replaceState(null,'',location.pathname+(u.toString()?'?'+u:''));}
      if(!list.length)grid.innerHTML='<p>No pieces match those filters yet. Try another stone or price range.</p>';
    }
    function page(){grid.insertAdjacentHTML('beforeend',list.slice(shown,shown+PAGE).map(card).join(''));shown+=PAGE;more.hidden=shown>=list.length;}
    more.onclick=page;
    $$('.f').forEach(b=>b.onclick=()=>{ if(shop.dataset.preset){location.href=B+(b.dataset.cat?'/shop/'+meta.cats[b.dataset.cat].slug+'/':'/shop/');return;} state.cat=b.dataset.cat;apply();});
    let t;$('#q').oninput=e=>{clearTimeout(t);t=setTimeout(()=>{state.q=e.target.value;apply()},180)};
    ['stone','price','sort'].forEach(k=>$('#'+k).onchange=e=>{state[k]=e.target.value;apply()});
    Promise.all([fetch(B+'/data/catalog.json').then(r=>r.json()),fetch(B+'/data/meta.json').then(r=>r.json())]).then(([d,m])=>{data=d;meta=m;apply();});
  }

  // ---- product page ----
  const P=window.MCM_PRODUCT;
  if(P){
    const buy=$('#buy'),price=$('#price'),stock=$('#stock'),sel=$('#variant'),cmp=$('#cmp');
    let variants=null;
    function setVariant(id){
      const v=variants&&variants.find(v=>String(v.id)===String(id));
      buy.href=`${P.shop}/cart/${id}:1${P.cartAttr}`;
      if(!v)return;
      price.textContent=money(v.price/100);
      if(v.compare_at_price&&v.compare_at_price>v.price){cmp.hidden=false;cmp.textContent=money(v.compare_at_price/100)}else{cmp.hidden=true}
      stock.classList.toggle('out',!v.available);stock.querySelector('span').textContent=v.available?'In stock':'Sold out';
      buy.textContent=v.available?'Buy now':'Sold out';buy.setAttribute('aria-disabled',String(!v.available));
    }
    if(sel)sel.onchange=e=>setVariant(e.target.value);
    // live price + stock straight from the Shopify store
    fetch(`${P.shop}/products/${P.handle}.js`).then(r=>r.ok?r.json():Promise.reject(r.status)).then(p=>{
      variants=p.variants;
      if(sel){[...sel.options].forEach(o=>{const v=variants.find(v=>String(v.id)===o.value);if(v){o.disabled=!v.available;o.dataset.price=v.price}});}
      const first=sel?sel.value:(variants.find(v=>v.available)||variants[0]).id;
      setVariant(first);
    }).catch(()=>{stock.querySelector('span').textContent='In stock (checked at checkout)'});
    $$('.th').forEach(b=>b.onclick=()=>{$('#mainimg').src=b.dataset.src;$$('.th').forEach(x=>x.classList.remove('on'));b.classList.add('on')});
  }
})();
