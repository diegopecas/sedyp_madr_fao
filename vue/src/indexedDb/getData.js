import { DB_STATUS, DB_NAME, DB_VERSION } from './connectDb';

/**
 * getData.
 *
 * @author	ANDRÉS FELIPE JOYA
 * @since	v0.0.1
 * @version	v1.0.0	Thursday, September 9th, 2021.
 * @global
 * @param	strign	storeName
 * @param	strign	searchKey
 * @return	void
 */
function getData(storeName, searchKey) {

  if (DB_STATUS === 200) {
    return new Promise(
      function(resolve, reject) {
        const request = indexedDB.open(DB_NAME, DB_VERSION);

        request.onerror = (event) => {
          console.log('Error:');
          console.log(event.target.error.message);
          window.alert('Database error: ' + event.target.error.message);
        };

        request.onsuccess = (event) => {
          const db = event.target.result;
          const txn = db.transaction(storeName, "readonly");
          const store = txn.objectStore(storeName);
          var request = [];
          if (searchKey) {
            request = store.get(storeName);
          } else {
            request = store.getAll();
          }

          request.onerror = function (event) {
            console.log('Error:');
            console.log(event.target.error.message);
            window.alert('Database error: ' + event.target.error.message);
          }
          request.onsuccess = function (event) {
            const reuslt = (request.result) ? request.result : {};
            if (reuslt) resolve(reuslt);
            else reject(Error('object not data'));
          };
          txn.oncomplete = function () {
            db.close();
          };
        };
      }
    )
  }
}

export {getData as getData}
