/* Amazon tag for every amazon.com link on whoaneat.com.
   Only whoaneat02-20 exists on the US Associates account (checked 2026-11-20),
   so every source uses it. Per-channel routing is kept below, switched off:
   once whoaneatig-20 / whoaneatpin-20 / whoaneattt-20 / whoaneatweb-20 exist
   (Associates > Manage Tracking IDs) and OneLink covers them, set ROUTING = true. */
(function () {
  var ROUTING = false;
  var DEFAULT_TAG = 'whoaneat02-20';
  var MAP = { ig: 'whoaneatig-20', pin: 'whoaneatpin-20', tt: 'whoaneattt-20', web: 'whoaneatweb-20' };
  var tag = DEFAULT_TAG;
  if (ROUTING) {
    var src = null;
    try { src = new URLSearchParams(location.search).get('src'); } catch (e) {}
    try {
      if (src && MAP[src]) sessionStorage.setItem('wn_src', src);
      else src = sessionStorage.getItem('wn_src');
    } catch (e) {}
    tag = MAP[src] || MAP.web;
  }
  window.WN_TAG = tag;
  window.wnRetag = function (root) {
    (root || document).querySelectorAll('a[href*="amazon.com/dp/"]').forEach(function (a) {
      var u = new URL(a.href); u.searchParams.set('tag', tag); a.href = u.toString();
    });
  };
  document.addEventListener('DOMContentLoaded', function () { window.wnRetag(); });
})();
