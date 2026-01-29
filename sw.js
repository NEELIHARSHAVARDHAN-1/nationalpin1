self.addEventListener('fetch', e => {
  e.respondWith(
    caches.open('nk-cache').then(cache =>
      cache.match(e.request).then(resp =>
        resp || fetch(e.request).then(net => {
          cache.put(e.request, net.clone());
          return net;
        })
      )
    )
  );
});
