import { DB_STATUS, DB_NAME, DB_VERSION } from './connectDb';

/**
 * update.
 *
 * @author	ANDRÉS FELIPE JOYA
 * @since	v0.0.1
 * @version	v1.0.0	Thursday, September 9th, 2021.
 * @global
 * @param	object	data
 * @param	array	objects
 * @param	string	clear
 * @return	void
 */
function update(data, objects, clear) {

  if (DB_STATUS === 200) {

    if (data === 'undefined' || objects  === 'undefined'|| clear  === 'undefined') {
      console.log('Error:');
      console.log('Function "update" doest not receive the parameters complete');
    }

    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onerror = (event) => {
      console.log('Error:');
      console.log(event.target.error.message);
      window.alert('Database error: ' + event.target.error.message);
    };

    request.onsuccess = (event) => {
      for (let i = 0; i < objects.length; i++) {
        var nombre = objects[i];

        if (data.hasOwnProperty(nombre)) {
          const db = event.target.result;
          /**
           * Si clear es true, el key del objeto sera
           * el mismo nombre que este lleve.
           * Si no es así se asume que el objeto maneja
           * key autoincrementable.
           */
          if (clear) {
            clearObjectStore(db, objects[i]);
            data[nombre]['id_obj'] = nombre;
          }

          putData(db,data[nombre], nombre);
        }
      }
    };
  }
}

/**
 * clearObjectStore.
 *
 * @author	ANDRÉS FELIPE JOYA
 * @since	v0.0.1
 * @version	v1.0.0	Thursday, September 9th, 2021.
 * @global
 * @param	mixed	db
 * @param	mixed	storeName
 * @return	void
 */
function clearObjectStore(db, storeName) {
  const txn = db.transaction(storeName, 'readwrite');
  const store = txn.objectStore(storeName);
  let query = store.clear();

  query.onsuccess = function(event) {
    console.log('Success:');
    console.log(event);
  };
  query.onerror = function (event) {
    console.log('Error:');
    console.log(event.target.error.message);
    window.alert('Database store error: ' + event.target.error.message);
  };
  txn.oncomplete = function () {
    db.close();
  };
}

/**
 * putData.
 *
 * @author	ANDRÉS FELIPE JOYA
 * @since	v0.0.1
 * @version	v1.0.0	Thursday, September 9th, 2021.
 * @global
 * @param	mixed	db
 * @param	mixed	obj
 * @param	mixed	storeName
 * @return	void
 */
function putData(db, obj, storeName) {
  const txn = db.transaction(storeName, 'readwrite');
  const store = txn.objectStore(storeName);
  let query = store.put(obj);

  query.onsuccess = function (event) {
      console.log('Success:');
      console.log(event);
  };
  query.onerror = function (event) {
    console.log('Error:');
    console.log(event.target.error.message);
    window.alert('Database store error: ' + event.target.error.message);
  }
  txn.oncomplete = function () {
      db.close();
  };
}

export {update as update}


