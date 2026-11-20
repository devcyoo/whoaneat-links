/* Picks the Amazon tracking ID from ?src= (kept for the visit) and applies it to every amazon.com link. */
(function () {
  var MAP = { ig: 'whoaneatig-20', pin: 'whoaneatpin-20', tt: 'whoaneattt-20' };
  var src = null;
  try { src = new URLSearchParams(location.search).get('src'); } catch (e) {}
  try {
    if (src && MAP[src]) sessionStorage.setItem('wn_src', src);
    else src = sessionStorage.getItem('wn_src');
  } catch (e) {}
  var tag = MAP[src] || 'whoaneatweb-20';
  window.WN_TAG = tag;
  window.wnRetag = function (root) {
    (root || document).querySelectorAll('a[href*="amazon.com/dp/"]').forEach(function (a) {
      var u = new URL(a.href); u.searchParams.set('tag', tag); a.href = u.toString();
    });
  };
  document.addEventListener('DOMContentLoaded', function () { window.wnRetag(); });
})();
