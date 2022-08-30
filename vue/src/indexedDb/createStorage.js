import { DB_STATUS, DB_NAME, DB_VERSION } from './connectDb';

if (DB_STATUS === 200) {

  const request = indexedDB.open(DB_NAME, DB_VERSION);

  request.onerror = function(event) {
    window.alert('Database error: ' + event.target.errorCode);
  };

  request.onupgradeneeded = function(event) {
    let db = event.target.result;
    createObjects(db);
  };


  /**
   * createObjects.
   *
   * @author	ANDRÉS FELIPE JOYA
   * @since	v0.0.1
   * @version	v1.0.0	Thursday, September 9th, 2021.
   * @param	mixed	db
   * @return	void
   */
  function createObjects(db) {
    try {
      objectStoreLogin(db);
      objectForestal(db);
      objectPesquero(db);
      objectAgricola(db);
      objectPecuario(db);
      objectEvent(db);
      objectProductor(db);
      objectMapa(db);
      objectEncabezado(db);
    } catch(error) {
      console.log(error);
    }
  }

  /**
   * objectStoreLogin.
   *
   * @author	ANDRÉS FELIPE JOYA
   * @since	v0.0.1
   * @version	v1.0.0	Thursday, September 9th, 2021.
   * @param	mixed	db
   * @return	void
   */
  function objectStoreLogin(db) {
    let objectStore = db.createObjectStore("login", { keyPath: "id_obj" });

    objectStore.createIndex("activo", "activo", { unique: false });
    objectStore.createIndex("apellido", "apellido", { unique: false });
    objectStore.createIndex("cargo", "cargo", { unique: false });
    objectStore.createIndex("email", "email", { unique: true });
    objectStore.createIndex("id", "id", { unique: true });
    objectStore.createIndex("idDocumento", "idDocumento", { unique: false });
    objectStore.createIndex("id_rol", "id_rol", { unique: false });
    objectStore.createIndex("institucion", "institucion", { unique: false });
    objectStore.createIndex("nombre", "nombre", { unique: false });
    objectStore.createIndex("nombre_rol", "nombre_rol", { unique: false });
    objectStore.createIndex("nuDocumento", "nuDocumento", { unique: true });
    objectStore.createIndex("permisos_usuario", "permisos_usuario", { unique: false });
    objectStore.createIndex("usuario", "usuario", { unique: true });
    objectStore.createIndex("token", "token", { unique: true });

    objectStore.transaction.oncomplete = function(event) {
    }
  }

  /**
   * objectForestal.
   *
   * @author	ANDRÉS FELIPE JOYA
   * @since	v0.0.1
   * @version	v1.0.0	Thursday, September 9th, 2021.
   * @param	mixed	db
   * @return	void
   */
  function objectForestal(db) {
    let objectStore = db.createObjectStore("forestal", { keyPath: "id_obj" });

    objectStore.createIndex("actividad", "actividad", { unique: false });
    objectStore.createIndex("eqvCarga", "eqvCarga", { unique: false });
    objectStore.createIndex("especieForestal", "especieForestal", { unique: false });
    objectStore.createIndex("faseProductiva", "faseProductiva", { unique: false });
    objectStore.createIndex("fuenteSemilla", "fuenteSemilla", { unique: false });
    objectStore.createIndex("lotePropaga", "lotePropaga", { unique: false });
    objectStore.createIndex("objePlantacion", "objePlantacion", { unique: false });
    objectStore.createIndex("presentacionPlaguicida", "presentacionPlaguicida", { unique: false });
    objectStore.createIndex("rubros", "rubros", { unique: false });
    objectStore.createIndex("tipoFertilizante", "tipoFertilizante", { unique: false });
    objectStore.createIndex("tipoInfraestrcutura", "tipoInfraestrcutura", { unique: false });
    objectStore.createIndex("tipoMaquinaria", "tipoMaquinaria", { unique: false });
    objectStore.createIndex("tipoPlaguicida", "tipoPlaguicida", { unique: false });
    objectStore.createIndex("tipoSemilla", "tipoSemilla", { unique: false });
    objectStore.createIndex("unidad", "unidad", { unique: false });
    objectStore.createIndex("unidadSemilla", "unidadSemilla", { unique: false });

    objectStore.transaction.oncomplete = function(event) {
    }
  }

  /**
   * objectPesquero.
   *
   * @author	ANDRÉS FELIPE JOYA
   * @since	v0.0.1
   * @version	v1.0.0	Thursday, September 9th, 2021.
   * @param	mixed	db
   * @return	void
   */
  function objectPesquero(db) {
    let objectStore = db.createObjectStore("pesquero", { keyPath: "id_obj" });

    objectStore.createIndex("activeType", "activeType", { unique: false });
    objectStore.createIndex("buildingType", "buildingType", { unique: false });
    objectStore.createIndex("embqMaterial", "embqMaterial", { unique: false });
    objectStore.createIndex("fishingType", "fishingType", { unique: false });
    objectStore.createIndex("lossType", "lossType", { unique: false });
    objectStore.createIndex("propType", "propType", { unique: false });
    objectStore.createIndex("redType", "redType", { unique: false });

    objectStore.transaction.oncomplete = function(event) {
    }
  }

  /**
   * objectAgricola.
   *
   * @author	ANDRÉS FELIPE JOYA
   * @since	v0.0.1
   * @version	v1.0.0	Thursday, September 9th, 2021.
   * @param	mixed	db
   * @return	void
   */
  function objectAgricola(db) {
    let objectStore = db.createObjectStore("agricola", { keyPath: "id_obj" });

    objectStore.createIndex("gricola", "gricola", { unique: false });
    objectStore.createIndex("areaUnity", "areaUnity", { unique: false });
    objectStore.createIndex("assruanceType", "assruanceType", { unique: false });
    objectStore.createIndex("bankingEntity", "bankingEntity", { unique: false });
    objectStore.createIndex("cropType", "cropType", { unique: false });
    objectStore.createIndex("directCosts", "directCosts", { unique: false });
    objectStore.createIndex("equivCharge", "equivCharge", { unique: false });
    objectStore.createIndex("fertilizerType", "fertilizerType", { unique: false });
    objectStore.createIndex("harvestUnity", "harvestUnity", { unique: false });
    objectStore.createIndex("indirectCosts", "indirectCosts", { unique: false });
    objectStore.createIndex("infraestructureType", "infraestructureType", { unique: false });
    objectStore.createIndex("machineryData", "machineryData", { unique: false });
    objectStore.createIndex("pesticideType", "pesticideType", { unique: false });
    objectStore.createIndex("plantingMaterial", "plantingMaterial", { unique: false });
    objectStore.createIndex("presentation", "presentation", { unique: false });
    objectStore.createIndex("seedSource", "seedSource", { unique: false });

    objectStore.transaction.oncomplete = function(event) {
    }
  }

  /**
   * objectPecuario.
   *
   * @author	ANDRÉS FELIPE JOYA
   * @since	v0.0.1
   * @version	v1.0.0	Thursday, September 9th, 2021.
   * @param	mixed	db
   * @return	void
   */
  function objectPecuario(db) {
    let objectStore = db.createObjectStore("pecuario", { keyPath: "id_obj" });

    objectStore.createIndex("pecuario", "pecuario", { unique: false });
    objectStore.createIndex("activeType", "activeType", { unique: false });
    objectStore.createIndex("activity", "activity", { unique: false });
    objectStore.createIndex("affectedSistem", "affectedSistem", { unique: false });
    objectStore.createIndex("areaUnity", "areaUnity", { unique: false });
    objectStore.createIndex("constructionType", "constructionType", { unique: false });
    objectStore.createIndex("equivCharge", "equivCharge", { unique: false });
    objectStore.createIndex("harvestUnity", "harvestUnity", { unique: false });
    objectStore.createIndex("inputType", "inputType", { unique: false });
    objectStore.createIndex("machineryAv", "machineryAv", { unique: false });
    objectStore.createIndex("machineryTypeBBA", "machineryTypeBBA", { unique: false });
    objectStore.createIndex("machineryTypePEM", "machineryTypePEM", { unique: false });
    objectStore.createIndex("machneryAq", "machneryAq", { unique: false });
    objectStore.createIndex("rubro", "rubro", { unique: false });
    objectStore.createIndex("typeProduct", "typeProduct", { unique: false });
    objectStore.createIndex("unity", "unity", { unique: false });

    objectStore.transaction.oncomplete = function(event) {
    }
  }

  /**
   * objectProductor.
   *
   * @author	ANDRÉS FELIPE JOYA
   * @since	v0.0.1
   * @version	v1.0.0	Thursday, September 9th, 2021.
   * @param	mixed	db
   * @return	void
   */
  function objectProductor(db) {
    let objectStore = db.createObjectStore("productor", { keyPath: "id_obj" });

    objectStore.createIndex("condicionJuridica", "condicionJuridica", { unique: false });
    objectStore.createIndex("gruposEtnicos", "gruposEtnicos", { unique: false });
    objectStore.createIndex("sexo", "sexo", { unique: false });
    objectStore.createIndex("tipoProductor", "tipoProductor", { unique: false });
    objectStore.createIndex("tipoRelacionPredio", "tipoRelacionPredio", { unique: false });
    objectStore.createIndex("tiposDocumento", "tiposDocumento", { unique: false });

    objectStore.transaction.oncomplete = function(event) {
    }
  }

  /**
   * objectMapa.
   *
   * @author	ANDRÉS FELIPE JOYA
   * @since	v0.0.1
   * @version	v1.0.0	Thursday, September 9th, 2021.
   * @param	mixed	db
   * @return	void
   */
  function objectMapa(db) {
    let objectStore = db.createObjectStore("mapa", { keyPath: "id_obj" });

    objectStore.createIndex("departamentos", "departamentos", { unique: false });
    objectStore.createIndex("municipios", "municipios", { unique: false });
    objectStore.createIndex("veredas", "veredas", { unique: false });

    objectStore.transaction.oncomplete = function(event) {
    }
  }

  /**
   * objectEncabezado.
   *
   * @author	ANDRÉS FELIPE JOYA
   * @since	v0.0.1
   * @version	v1.0.0	Thursday, September 9th, 2021.
   * @param	mixed	db
   * @return	void
   */
  function objectEncabezado(db) {
    let objectStore = db.createObjectStore("encabezado", { keyPath: "id_obj" });

    objectStore.createIndex("enfermedades", "enfermedades", { unique: false });
    objectStore.createIndex("plagas", "plagas", { unique: false });
    objectStore.createIndex("sistemaProductivo", "sistemaProductivo", { unique: false });
    objectStore.createIndex("subEvento", "subEvento", { unique: false });
    objectStore.createIndex("tipoEvento", "tipoEvento", { unique: false });

    objectStore.transaction.oncomplete = function(event) {
    }
  }

  /**
   * objectEvent.
   *
   * @author	ANDRÉS FELIPE JOYA
   * @since	v0.0.1
   * @version	v1.0.0	Thursday, September 9th, 2021.
   * @param	mixed	db
   * @return	void
   */
  function objectEvent(db) {
    let objectStore = db.createObjectStore("newEvent", { keyPath: "id_obj" });

    objectStore.createIndex("dataEncabezadoEvento", "dataEncabezadoEvento", { unique: false });
    objectStore.createIndex("dataProductor", "dataProductor", { unique: false });
    objectStore.createIndex("dataEspecies", "dataEspecies", { unique: false });

    objectStore.transaction.oncomplete = function(event) {
    }
  }

}
