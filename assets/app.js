(function(){var p=document.querySelector('.progress');if(!p||matchMedia('(prefers-reduced-motion:reduce)').matches)return;
function u(){var h=document.documentElement,m=h.scrollHeight-h.clientHeight;p.style.width=(m>0?h.scrollTop/m*100:0)+'%'}
addEventListener('scroll',u,{passive:true});u()})();
