/* Counts clicks on Amazon links (amazon.com / amazon.ca) on whoaneat.com.
   Sends one small beacon per click to /api/click; never changes the link or blocks the visit.
   Sent: ASIN, amazon.com or .ca, this page's path, the ?src value, the referrer.
   The server keeps only the referrer's host name and stores nothing personal. */
(function () {
  if (!navigator.sendBeacon) return;
  var src = '';
  try {
    src = new URLSearchParams(location.search).get('src') || '';
    if (src) sessionStorage.setItem('wn_click_src', src);
    else src = sessionStorage.getItem('wn_click_src') || '';
  } catch (e) {}
  function send(a) {
    try {
      var u = new URL(a.href);
      var m = u.hostname.match(/(^|\.)amazon\.(com|ca)$/);
      if (!m) return;
      var asin = (u.pathname.match(/\/dp\/([A-Z0-9]{10})/i) || [])[1];
      if (!asin) return;
      navigator.sendBeacon('/api/click', JSON.stringify({
        asin: asin, market: m[2], path: location.pathname, src: src, ref: document.referrer || ''
      }));
    } catch (e) {}
  }
  function onClick(e) {
    if (e.type === 'auxclick' && e.button !== 1) return;
    var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (a) send(a);
  }
  document.addEventListener('click', onClick, true);
  document.addEventListener('auxclick', onClick, true);
})();
