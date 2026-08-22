// Όταν το κινητό εγκαθιστά τον Service Worker
self.addEventListener('install', (event) => {
    console.log('Armέξ Service Worker: Εγκαταστάθηκε επιτυχώς!');
    self.skipWaiting();
});

// Όταν η εφαρμογή πάει να "τραβήξει" δεδομένα
self.addEventListener('fetch', (event) => {

    if (event.request.url.includes('onrender.com') || event.request.method !== 'GET') {
        return; 
    }
    event.respondWith(fetch(event.request).catch(() => {
        console.log("Είσαι offline!");
    }));
});