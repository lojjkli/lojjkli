'use strict';
// Only text nodes and locally created elements are used in previews.
window.TaggyFormatting = (() => {
  const actions = [
    ['bold','B','Bold','**','**'], ['italic','I','Italic','*','*'],
    ['underline','U','Underline','__','__'], ['strike','S','Strikethrough','~~','~~'],
    ['spoiler','Hide','Spoiler','||','||'], ['code','Code','Inline code','`','`'],
    ['block','{ }','Code block','```\n','\n```'],
    ['h1','H1','Large heading','# ',''], ['h2','H2','Medium heading','## ',''],
    ['h3','H3','Small heading','### ',''], ['quote','>','Quote','> ','']
  ];
  const embedded = new Set(['embed-description','verification-description','tickets-description','role-panel-description']);
  const node = (tag,text,className) => { const element=document.createElement(tag);if(text!==undefined)element.textContent=text;if(className)element.className=className;return element; };
  function inline(target,text,depth=0) {
    if(depth>4){target.append(document.createTextNode(text));return;}
    const pattern=/(`[^`\n]+`|\*\*[^\n]+?\*\*|__[^\n]+?__|~~[^\n]+?~~|\|\|[^\n]+?\|\||\*[^*\n]+\*)/g;
    let start=0,match;
    while((match=pattern.exec(text))){
      target.append(document.createTextNode(text.slice(start,match.index)));
      const token=match[0],mark=token.startsWith('**')?'**':token.startsWith('__')?'__':token.startsWith('~~')?'~~':token.startsWith('||')?'||':token[0];
      const tag={'**':'strong','__':'u','~~':'s','||':'span','*':'em','`':'code'}[mark],element=node(tag);
      if(mark==='||'){element.className='markdown-spoiler';element.title='Spoiler';}
      if(mark==='`')element.textContent=token.slice(1,-1);else inline(element,token.slice(mark.length,-mark.length),depth+1);
      target.append(element);start=pattern.lastIndex;
    }
    target.append(document.createTextNode(text.slice(start)));
  }
  function render(text,target,{headings=true}={}) {
    target.replaceChildren();const lines=String(text||'').split('\n');let codeLines=null;
    for(const line of lines){
      if(line.startsWith('```')){if(codeLines===null)codeLines=[];else{target.append(node('pre',codeLines.join('\n')));codeLines=null;}continue;}
      if(codeLines!==null){codeLines.push(line);continue;}
      const heading=headings&&line.match(/^(#{1,3})\s+(.+)$/),quote=line.match(/^>\s?(.*)$/);
      const element=node(heading?'h'+(heading[1].length+2):quote?'blockquote':'div');
      inline(element,heading?heading[2]:quote?quote[1]:line||'\u00a0');target.append(element);
    }
    if(codeLines!==null)target.append(node('pre',codeLines.join('\n')));
    if(!text)target.append(node('span','Your text preview appears here.','caption'));
  }
  function mount(input){
    if(input.dataset.markdownReady||['poll-answers','poll-question'].includes(input.id)||input.dataset.noFormatting!==undefined)return;
    input.dataset.markdownReady='true';
    const editor=node('div',undefined,'markdown-editor'),label=input.closest('label');
    const wrap=label||input;wrap.before(editor);editor.append(wrap);
    const toolbar=node('div',undefined,'markdown-toolbar');toolbar.setAttribute('role','toolbar');toolbar.setAttribute('aria-label','Format '+(input.getAttribute('aria-label')||input.id?.replaceAll('-',' ')||'message'));
    const status=node('span','Select text, then choose a format.','caption markdown-help');status.setAttribute('role','status');
    let selection=[input.selectionStart,input.selectionEnd];
    for(const event of ['select','keyup','mouseup','input','focus'])input.addEventListener(event,()=>{selection=[input.selectionStart,input.selectionEnd];});
    for(const [key,label,title,before,after]of actions){
      const button=node('button',label);button.type='button';button.title=title;button.setAttribute('aria-label',title);button.dataset.format=key;button.disabled=input.disabled;
      button.addEventListener('mousedown',event=>event.preventDefault());
      button.addEventListener('click',()=>{
        if(input.disabled||input.readOnly)return;
        let [start,end]=selection;const isLine=['h1','h2','h3','quote'].includes(key);
        if(isLine){start=input.value.lastIndexOf('\n',Math.max(0,start-1))+1;const next=input.value.indexOf('\n',end);end=next===-1?input.value.length:next;}
        const selected=input.value.slice(start,end),content=selected||'text';
        const replacement=isLine?content.split('\n').map(line=>before+line.replace(/^(?:#{1,3}|>)\s+/, '')).join('\n'):before+content+after;
        if(input.maxLength>=0&&input.value.length-(end-start)+replacement.length>input.maxLength){status.textContent='This format would exceed the '+input.maxLength+' character limit.';return;}
        input.focus();input.setSelectionRange(start,end);
        const oldValue=input.value;let inserted=false;
        try{inserted=document.execCommand('insertText',false,replacement)&&input.value!==oldValue;}catch(_){}
        if(!inserted){input.setRangeText(replacement,start,end,'end');input.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertText',data:replacement}));}
        const offset=isLine?before.length:before.length;input.setSelectionRange(start+offset,start+replacement.length-after.length);selection=[input.selectionStart,input.selectionEnd];
        status.textContent=title+' added.'+(inserted?' Use Ctrl+Z or ⌘Z to undo.':'');sync();
      });toolbar.append(button);
    }
    toolbar.addEventListener('keydown',event=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;const buttons=[...toolbar.querySelectorAll('button')].filter(button=>!button.disabled),index=buttons.indexOf(document.activeElement);event.preventDefault();buttons[event.key==='Home'?0:event.key==='End'?buttons.length-1:(index+(event.key==='ArrowRight'?1:-1)+buttons.length)%buttons.length]?.focus();});
    const details=node('details',undefined,'markdown-preview-details'),summary=node('summary','Preview in Discord'),preview=node('div',undefined,'markdown-preview');details.append(summary,preview);
    const isEmbed=embedded.has(input.id)||input.dataset.ticketQuestion!==undefined||input.dataset.field==='value';
    if(isEmbed)details.append(node('p','Discord embed text supports emphasis, code and quotes. Headings work in regular messages.','caption'));
    editor.append(toolbar,status,details);
    function sync(){for(const button of toolbar.querySelectorAll('button'))button.disabled=input.disabled||input.readOnly;render(input.value,preview,{headings:!isEmbed});}
    input.addEventListener('input',sync);new MutationObserver(sync).observe(input,{attributes:true,attributeFilter:['disabled','readonly']});details.addEventListener('toggle',sync);sync();
  }
  function scan(root=document){if(root.matches?.('textarea'))mount(root);for(const input of root.querySelectorAll?.('textarea')||[])mount(input);}
  new MutationObserver(records=>{for(const record of records)for(const added of record.addedNodes)if(added.nodeType===1)scan(added);}).observe(document.documentElement,{childList:true,subtree:true});
  scan();return {mount,scan,render};
})();
