// Όταν το κινητό εγκαθιστά τον Service Worker
self.addEventListener('install', (event) => {
    console.log('Armέξ Service Worker: Εγκαταστάθηκε επιτυχώς!');
    self.skipWaiting();
});

// Όταν η εφαρμογή πάει να "τραβήξει" δεδομένα
self.addEventListener('fetch', (event) => {
    // Προς το παρόν, του λέμε απλά να αφήνει την κίνηση να περνάει κανονικά στο ίντερνετ
    event.respondWith(fetch(event.request).catch(() => {
        console.log("Είσαι offline!");
    }));
});