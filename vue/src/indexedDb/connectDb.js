const DB_NAME  = "faodb";
const DB_VERSION = 1;
var DB_STATUS  = 200;

if (!window.indexedDB) {
  window.alert("Su navegador no soporta una versión estable de indexedDB. Las funciones offline no estarán habilitadas.");
  statusDb = 500;
}

export { DB_STATUS, DB_NAME, DB_VERSION };
