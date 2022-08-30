// loads an external script
export function loadScript(src) {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.onload = () => resolve();
    script.onerror = err => reject(err);
    script.src = src;
    document.head.appendChild(script);
  });
}

// clears IndexedDb storage
export function clearIndexedDb() {
  return new Promise(resolve => {
    // we clear the indexeddb state ourselves for now
    // @see https://github.com/cypress-io/cypress/issues/1208
    it(`load localforage script`, () =>
      loadScript('https://unpkg.com/localforage@1.5.5/dist/localforage.js').then(() => {
        localforage.config({
          driver: [localforage.INDEXEDDB],
          name: 'MyDb',
          storeName: 'my_store',
          version: '1.0',
        });
      }));

    it(`clear INDEXEDDB storage`, () => {
      cy.visit('/');
      localforage.clear();
    });
  });
}