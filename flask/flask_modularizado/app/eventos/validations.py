from app.helpers import validate_fields

# Validates that the event to save has all the needed information
def validate_data_event(data):
    obj = {
        'dataEncabezadoEvento': data['dataEncabezadoEvento'] if 'dataEncabezadoEvento' in data else None,
        'dataProductor': data['dataProductor'] if 'dataProductor' in data else None,
        'dataEspecies': data['dataEspecies'] if 'dataEspecies' in data else None
    }

    validacion = [
        {'campo': 'dataEncabezadoEvento', 'valor': data['dataEncabezadoEvento'], 'obligatorio': 1},
        {'campo': 'dataProductor', 'valor': data['dataProductor'], 'obligatorio': 1},
        {'campo': 'dataEspecies', 'valor': data['dataEspecies'], 'obligatorio': 1}
    ]

    estadoValidate = validate_fields(validacion)

    return obj, estadoValidate


# Validated the data from the event header
def validate_event_header(dataEncabezadoEvento, fechaActual):
        obj = {
            'tipoEv': dataEncabezadoEvento['tipoEv'] if 'tipoEv' in dataEncabezadoEvento else None,
            'subEv': dataEncabezadoEvento['subEv'] if 'subEv' in dataEncabezadoEvento else None,
            'latitud': dataEncabezadoEvento['latitud'] if 'latitud' in dataEncabezadoEvento else None,
            'longitud': dataEncabezadoEvento['longitud'] if 'longitud' in dataEncabezadoEvento else None,
            'altitud': float(dataEncabezadoEvento['altitud']) if 'altitud' in dataEncabezadoEvento and dataEncabezadoEvento['altitud'] else None,
            'precision': float(dataEncabezadoEvento['precision']) if 'precision' in dataEncabezadoEvento and dataEncabezadoEvento['precision'] else None,
            'fechaActual': fechaActual,
            'cod_municipio_FK': dataEncabezadoEvento['municipio'] if 'municipio' in dataEncabezadoEvento else None,
            'ubicacion_vereda': dataEncabezadoEvento['enVereda'] if 'enVereda' in dataEncabezadoEvento and dataEncabezadoEvento['enVereda'] else None,
            'cod_vereda_FK': dataEncabezadoEvento['codVereda'] if 'codVereda' in dataEncabezadoEvento and dataEncabezadoEvento['codVereda'] else None,
            'nom_puerto_desembarquee': dataEncabezadoEvento['nombrePuerto'] if 'nombrePuerto' in dataEncabezadoEvento and dataEncabezadoEvento['nombrePuerto'] else None,
            'idUsuario': dataEncabezadoEvento['idUsuario'] if 'idUsuario' in dataEncabezadoEvento else None,
            'observacion': dataEncabezadoEvento['observacion'] if 'observacion' in dataEncabezadoEvento else None,
            'cuarentenario': dataEncabezadoEvento['cuarentenario'] if 'cuarentenario' in dataEncabezadoEvento else None,
            'plagaCuarente': dataEncabezadoEvento['plagaCuarente'] if 'plagaCuarente' in dataEncabezadoEvento and dataEncabezadoEvento['plagaCuarente'] != '' else None,
            'enfermedadCuarente': dataEncabezadoEvento['enfermedadCuarente'] if 'enfermedadCuarente' in dataEncabezadoEvento and dataEncabezadoEvento['enfermedadCuarente'] != '' else None,
            'nombreEnfermedad': dataEncabezadoEvento['nombreEnfermedad'] if 'nombreEnfermedad' in dataEncabezadoEvento and dataEncabezadoEvento['nombreEnfermedad'] != '' else None,
            'nombrePlaga': dataEncabezadoEvento['nombrePlaga'] if 'nombrePlaga' in dataEncabezadoEvento and dataEncabezadoEvento['nombrePlaga'] != '' else None,
            'otroSubEvento': dataEncabezadoEvento['otroSubEvento'] if 'otroSubEvento' in dataEncabezadoEvento and dataEncabezadoEvento['otroSubEvento'] != '' else None
        }

        validacion = [
            {'campo': 'tipoEv', 'valor': obj['tipoEv'], 'obligatorio': 1},
            {'campo': 'subEv', 'valor': obj['subEv'], 'obligatorio': 1},
            {'campo': 'latitud', 'valor': obj['latitud'], 'obligatorio': 1},
            {'campo': 'longitud', 'valor': obj['longitud'], 'obligatorio': 1},
            {'campo': 'fechaActual',
                'valor': obj['fechaActual'], 'obligatorio': 1},
            {'campo': 'idUsuario',
                'valor': obj['idUsuario'], 'obligatorio': 1},
            {'campo': 'observacion',
                'valor': obj['observacion'], 'obligatorio': 1},
            {'campo': 'cuarentenario', 'valor': obj['cuarentenario'], 'obligatorio': 0},
            {'campo': 'plagaCuarente', 'valor': obj['plagaCuarente'], 'obligatorio': 0},
            {'campo': 'enfermedadCuarente', 'valor': obj['enfermedadCuarente'], 'obligatorio': 0},
            {'campo': 'nombreEnfermedad', 'valor': obj['nombreEnfermedad'], 'obligatorio': 0},
            {'campo': 'nombrePlaga', 'valor': obj['nombrePlaga'], 'obligatorio': 0},
            {'campos': 'otroSubEvento', 'valor': obj['otroSubEvento'], 'obligatorio': 0}
        ]

        estadoValidate = validate_fields(validacion)

        return obj, estadoValidate


# Validates the productor data
def fields_data_productor(data):
    obj = {
        'condJuridica': data['condJuridica'] if 'condJuridica' in data else None,
        'tipoProd': data['tipoProd'] if 'tipoProd' in data else None,
        'nombre': data['nombre'] if 'nombre' in data else None,
        'tipoDcto': data['tipoDcto'] if 'tipoDcto' in data else None,
        'dcto': data['dcto'] if 'dcto' in data else None,
        'dirRes': data['dirRes'] if 'dirRes' in data else None,
        'tel': data['tel'] if 'tel' in data else None,
        'sexo': data['sexo'] if 'sexo' in data else None,
        'fechaNac': data['fechaNac'] if 'fechaNac' in data else None,
        'gEtnico': data['gEtnico'] if 'gEtnico' in data else None,
        'relPre': data['relPre'] if 'relPre' in data else None,
        'email': data['email'] if 'email' in data else None
    }

    validacion = [
        {'campo': 'condJuridica',
            'valor': obj['condJuridica'], 'obligatorio': 1},
        {'campo': 'tipoProd', 'valor': obj['tipoProd'], 'obligatorio': 0},
        {'campo': 'nombre', 'valor': obj['nombre'], 'obligatorio': 1},
        {'campo': 'tipoDcto', 'valor': obj['tipoDcto'], 'obligatorio': 1},
        {'campo': 'dcto', 'valor': obj['dcto'], 'obligatorio': 1},
        {'campo': 'dirRes', 'valor': obj['dirRes'], 'obligatorio': 0},
        {'campo': 'tel', 'valor': obj['tel'], 'obligatorio': 0},
        {'campo': 'sexo', 'valor': obj['sexo'], 'obligatorio': 0},
        {'campo': 'fechaNac', 'valor': obj['fechaNac'], 'obligatorio': 0},
        {'campo': 'gEtnico', 'valor': obj['gEtnico'], 'obligatorio': 0},
        {'campo': 'relPre', 'valor': obj['relPre'], 'obligatorio': 1},
        {'campo': 'email', 'valor': obj['email'], 'obligatorio': 0}
    ]

    estadoValidate = validate_fields(validacion)

    return obj, estadoValidate


# Validate forestal systems fields to save
def validate_forestal_fields(dataEspecie):
    obj = {
        'faseProd': dataEspecie['faseProd'] if 'faseProd' in dataEspecie else None,
        'espAfectada': dataEspecie['espAfectada'] if 'espAfectada' in dataEspecie else None,
        'nombre': dataEspecie['nombre'] if 'nombre' in dataEspecie else None,
        'fecha': dataEspecie['fecha'] if 'fecha' in dataEspecie else None,
        'densHectarea': float(dataEspecie['densHectarea']) if 'densHectarea' in dataEspecie else None,
        'areaSembrada': float(dataEspecie['areaSembrada']) if 'areaSembrada' in dataEspecie else None,
        'objetivo': dataEspecie['objetivo'] if 'objetivo' in dataEspecie else None,
        'noArbolesAntesAfectacion': float(dataEspecie['noArbolesAntesAfectacion']) if 'noArbolesAntesAfectacion' in dataEspecie else None,
        'noEntresacas': dataEspecie['noEntresacas'] if 'noEntresacas' in dataEspecie else None,
        'diametroPromedio': float(dataEspecie['diametroPromedio']) if 'diametroPromedio' in dataEspecie else None,
        'alturaComercial': float(dataEspecie['alturaComercial']) if 'alturaComercial' in dataEspecie else None,
        'alturaTotal': float(dataEspecie['alturaTotal']) if 'alturaTotal' in dataEspecie else None,
        'plantacionAnos': float(dataEspecie['plantacionAnos']) if 'plantacionAnos' in dataEspecie else None,
        'porceArbolesTurnoFinal': float(dataEspecie['porceArbolesTurnoFinal']) if 'porceArbolesTurnoFinal' in dataEspecie else None,
        'valorVenderProduccionAfectada': float(str(dataEspecie['valorVenderProduccionAfectada']).replace(',','')) if 'valorVenderProduccionAfectada' in dataEspecie and dataEspecie['valorVenderProduccionAfectada'] else None,
        'areaAfectadaHectareas': float(dataEspecie['areaAfectadaHectareas']) if 'areaAfectadaHectareas' in dataEspecie else None,
        'fechaAfactaForestal': dataEspecie['fechaAfactaForestal'] if 'fechaAfactaForestal' in dataEspecie else None,
        'diasAfectoSistemaForestal': float(dataEspecie['diasAfectoSistemaForestal']) if 'diasAfectoSistemaForestal' in dataEspecie else None,
        'noArbolesAfectados': dataEspecie['noArbolesAfectados'] if 'noArbolesAfectados' in dataEspecie else None,
        'vlMaderaAfectado': float(str(dataEspecie['vlMaderaAfectado']).replace(',','')) if 'vlMaderaAfectado' in dataEspecie and dataEspecie['vlMaderaAfectado'] else None,
        'valEntreSacas': float(str(dataEspecie['valEntreSacas']).replace(',','')) if 'valEntreSacas' in dataEspecie and dataEspecie['valEntreSacas'] else None,
        'porceEntreSacas': float(dataEspecie['porceEntreSacas']) if 'porceEntreSacas' in dataEspecie else None,
        'afectacionesEnMaquinaria': dataEspecie['afectacionesEnMaquinaria'] if 'afectacionesEnMaquinaria' in dataEspecie else None
    }

    return obj


# Validated the relation event forestal system fields
def validate_relation_event_system_fields(idEvento, sistema, idSistema):
    obj = {
            'idEvento': idEvento['id'],
            'cod_sist_prod_afect_FK': sistema,
            'cod_cultivo_afectado_FK': idSistema if sistema == 1 else None,
            'cod_especie_forestal_FK': idSistema if sistema == 3 else None,
            'cod_novedad_pesquera_FK': idSistema if sistema == 4 else None,
            'cod_novedad_pecuaria_FK': idSistema if sistema == 2 else None,
            'cod_novedad_pecuaria_apicola_FK': idSistema if sistema == 5 else None
    }

    validacion = [
            {'campo': 'idEvento', 'valor': idEvento['id'], 'obligatorio': 1},
            {'campo': 'sistema', 'valor': sistema, 'obligatorio': 1},
            {'campo': 'idSistema', 'valor': idSistema, 'obligatorio': 1},
    ]
    estadoValidate = validate_fields(validacion)

    return obj, estadoValidate


# Validate the seed type in forestal system
def validate_seed_type_forestal(semillas):
    validatedSemilla = []
    for semilla in semillas:
        obj = {
            'espAfectada': semilla['espAfectada'] if 'espAfectada' in semilla else None,
            'canSemillas': semilla['canSemillas'] if 'canSemillas' in semilla else None,
            'valPesos': str(semilla['valPesos']).replace(',','') if 'valPesos' in semilla and semilla['valPesos'] else None,
            'cantSemillas': semilla['cantSemillas'] if 'cantSemillas' in semilla else None,
            'medidaSemilla': semilla['medidaSemilla'] if 'medidaSemilla' in semilla else None,
            'idTipoSemilla': semilla['idTipoSemilla'] if 'idTipoSemilla' in semilla else None,
            'fuenteSemilla': semilla['fuenteSemilla'] if 'fuenteSemilla' in semilla else None,
            'equivaleKilos': semilla['equivaleKilos'] if 'equivaleKilos' in semilla else None,
            'nuevaEquivalencia': semilla['nuevaEquivalencia'] if 'nuevaEquivalencia' in semilla else None,
            'idLotePropagacion': semilla['idLotePropagacion'] if 'idLotePropagacion' in semilla else None
        }

        validatedSemilla.append(obj)

    return validatedSemilla


# Validate the fertilizer type in forestal system
def validate_fert_type_forestal(fertilizantes):
    validatedFert = []
    for fertilizante in fertilizantes:
        obj = {
            'idTipoFertilizante': fertilizante['idTipoFertilizante'] if 'idTipoFertilizante' in fertilizante else None,
            'nombre': fertilizante['nombre'] if 'nombre' in fertilizante else None,
            'fechaAdquisicion': fertilizante['fechaAdquisicion'] if 'fechaAdquisicion' in fertilizante else None,
            'canFertilizante': fertilizante['canFertilizante'] if 'canFertilizante' in fertilizante else None,
            'valPesos': str(fertilizante['valPesos']).replace(',','') if 'valPesos' in fertilizante and fertilizante['valPesos'] else None,
        }

        validatedFert.append(obj)

    return validatedFert


# Validate the plaguicide type in forestal system
def validate_pla_type_forestal(plaguicidas):
    validatedPla = []
    for plaguicida in plaguicidas:
        obj = {
            'idTipoPlaguicida': plaguicida['idTipoPlaguicida'] if 'idTipoPlaguicida' in plaguicida else None,
            'idTipoPresentacion': plaguicida['idTipoPresentacion'] if 'idTipoPresentacion' in plaguicida else None,
            'cantPlaguicidaKg': plaguicida['cantPlaguicidaKg'] if 'cantPlaguicidaKg' in plaguicida else None,
            'cantPlaguicidaLt': plaguicida['cantPlaguicidaLt'] if 'cantPlaguicidaLt' in plaguicida else None,
            'valPesos': str(plaguicida['valPesos']).replace(',','') if 'valPesos' in plaguicida and plaguicida['valPesos'] else None,
        }

        validatedPla.append(obj)
    
    return validatedPla


# Validate the machinery type in forestal system
def validate_maq_type_forestal(maquinarias):
    validatedMaq = []
    for maquinaria in maquinarias:
        obj = {
            'anoAdquisicion': maquinaria['anoAdquisicion'] if 'anoAdquisicion' in maquinaria else None,
            'idTipoMaquinariaAgricola': maquinaria['idTipoMaquinariaAgricola'] if 'idTipoMaquinariaAgricola' in maquinaria else None,
            'valorPesos': str(maquinaria['valorPesos']).replace(',','') if 'valorPesos' in maquinaria and maquinaria['valorPesos'] else None,
            'porceDisminucion': maquinaria['porceDisminucion'] if 'porceDisminucion' in maquinaria else None
        }

        validatedMaq.append(obj)

    return validatedMaq

# Validate the relation forestal system with infrstructure
def validate_relation_system_infrastructure_fields(tipoInfraestructura):
    obj = {
		'cod_tipo_infraestrucrtura_FK': None,
        'cod_especie_semilla_fk': None,
		'cant_semilla_almacenada': None,
		'vlr_pesos_afectacion': None,
        'cod_tipo_material_siembra_fk': None,
        'cant_semilla_siembra': None,
        'cod_unidad_cantidad_semilla_fk': None,
		'cod_tip_semilla_FK': None,
        'cod_fuente_semilla_fk': None,
        'eqv_kg_carga_semilla_fk': None,
        'eqv_kg_carga_otro_semilla_fk': None,
        'kg_otro_semilla_fk': None,

		#'cod_unidad_FK': None,
		'cod_tipo_fertilizante_FK': None,
		'nombre_fertilizante': None,
        'fecha_adquisicion_fert': None,
		'cantidad': None,
		'valor_pesos_afectacion': None,


		'cod_tipo_plaguicida_FK': None,
		'presentacion_plaguicida': None,
		'cant_plaguicidas_kg': None,
		'cant_plaguicidas_lt': None,
		'vlr_pesos_afectacion_pla': None,


		'cod_tipo_maquinaria_FK': None,
		'edad_equipo_maq': None,
		'vlr_pesos_afectacion_maq': None,
        'porc_dism_prod_maq': None,

		'cod_especie_forestal_sembrada_FK': None,
	}
	
    validacion = [
		{'campo': 'tipoInfraestructura',
			'valor': tipoInfraestructura, 'obligatorio': 1},
	]

    estadoValidate = validate_fields(validacion)

    obj['cod_tipo_infraestrucrtura_FK'] = tipoInfraestructura

    return obj, estadoValidate


# Validate direct costs fields from forestal system
def validate_direct_costs_fields_forestal(costo, idSistema):
	obj = {
		'costo': str(costo['costo']).replace(',','') if costo['costo'] else None,
		'idActividad': costo['id'] if costo['id'] else None,
		'idSistema': idSistema if idSistema else None,
	}

	validacion = [
		{'campo': 'costo', 'valor': costo['costo'], 'obligatorio': 1},
		{'campo': 'idActividad', 'valor': costo['id'], 'obligatorio': 1},
		{'campo': 'idSistema', 'valor': idSistema, 'obligatorio': 1},
	]
	estadoValidate = validate_fields(validacion)

	return obj, estadoValidate


# Validate indirect costs fields from forestal system
def validate_indirect_costs_fields_forestal(costo, idSistema):
	obj = {
		'costo': str(costo['costo']).replace(',','') if costo['costo'] else None,
		'idRubro': costo['id'] if costo['id'] else None,
		'idSistema': idSistema if idSistema else None,
	}

	validacion = [
		{'campo': 'costo', 'valor': costo['costo'], 'obligatorio': 1},
		{'campo': 'idRubro', 'valor': costo['id'], 'obligatorio': 1},
		{'campo': 'idSistema', 'valor': idSistema, 'obligatorio': 1},
	]
	estadoValidate = validate_fields(validacion)

	return obj, estadoValidate


def validate_fields_agro(cultivo):
    fechaPrimeCosecha = cultivo['fechaPrimeCosecha'] if 'fechaPrimeCosecha' in cultivo else None
    fechaEsperaCosecha = cultivo['fechaEsperaCosecha'] if 'fechaEsperaCosecha' in cultivo else None

    if fechaPrimeCosecha:
        add_day_prime = str(fechaPrimeCosecha).split('-')
        if len(add_day_prime)<3:
            fechaPrimeCosecha = fechaPrimeCosecha+'-01'
    
    if fechaEsperaCosecha :
        add_day_espera = str(fechaEsperaCosecha).split('-')
        if len(add_day_espera)<3:
            fechaEsperaCosecha = fechaEsperaCosecha+'-01'

    obj = {
        'nombreCultivo': cultivo['nombreCultivo'] if 'nombreCultivo' in cultivo else None,
        'areaCultivo':  cultivo['areaCultivo'] if 'areaCultivo' in cultivo else None,
        'unidadArea': cultivo['unidadArea'] if 'unidadArea' in cultivo else None,
        'areaTotCultHa': cultivo['areaTotCultHa'] if 'areaTotCultHa' in cultivo else None,
        'materiralSiembra': cultivo['materiralSiembra'] if 'materiralSiembra' in cultivo else None,
        'cantSemillas': cultivo['cantSemillas'] if 'cantSemillas' in cultivo else None,
        'medidaSemilla': cultivo['medidaSemilla'] if 'medidaSemilla' in cultivo else None,
        'equivCargaKg': cultivo['equivCargaKg'] if 'equivCargaKg' in cultivo else None,
        'equivaleKilos': cultivo['equivaleKilos'] if 'equivaleKilos' in cultivo else None,
        'fuenteSemilla': cultivo['fuenteSemilla'] if 'fuenteSemilla' in cultivo else None,
        'fechaAfectacion': cultivo['fechaAfectacion'] if 'fechaAfectacion' in cultivo else None,
        'diasCultivoExpuesto': cultivo['diasCultivoExpuesto'] if 'diasCultivoExpuesto' in cultivo else None,
        'fechaSiembra': cultivo['fechaSiembra'] if 'fechaSiembra' in cultivo else None,
        'fechaPrimeCosecha': fechaPrimeCosecha,
        'fechaEsperaCosecha': fechaEsperaCosecha,
        'cantCosechada': cultivo['cantCosechada'] if 'cantCosechada' in cultivo else None,
        'medidaCantCosechada': cultivo['medidaCantCosechada'] if 'medidaCantCosechada' in cultivo else None,
        'equivaleKilosCosecha': cultivo['equivaleKilosCosecha'] if 'equivaleKilosCosecha' in cultivo else None,
        'equivKgCargZon': cultivo['codEquivKg'] if 'codEquivKg' in cultivo else None,
        'totalReciCosechado': cultivo['totalReciCosechado'] if 'totalReciCosechado' in cultivo else None,
        'cantProduProducir': cultivo['cantProduProducir'] if 'cantProduProducir' in cultivo else None,
        'medidaReportar': cultivo['medidaReportar'] if 'medidaReportar' in cultivo else None,
        'totalReportado': cultivo['totalReportado'] if 'totalReportado' in cultivo else None,
        'equivaleKilosReportar': cultivo['equivaleKilosReportar'] if 'equivaleKilosReportar' in cultivo else None,
        'proyEqvKg': cultivo['proyEqvKg'] if 'proyEqvKg' in cultivo else None,
        'totalProyectaVenta': cultivo['totalProyectaVenta'] if 'totalProyectaVenta' in cultivo else None,
        'costoPromeJornal': cultivo['costoPromeJornal'] if 'costoPromeJornal' in cultivo else None,
        'porceResiembra': cultivo['porceResiembra'] if 'porceResiembra' in cultivo else None,
        'perdEstInv': cultivo['perdEstInv'] if 'perdEstInv' in cultivo else None,
        'renEspProd': cultivo['renEspProd'] if 'renEspProd' in cultivo else None,
        'rendRealProd': cultivo['rendRealProd'] if 'rendRealProd' in cultivo else None,
        'perdEstimRendCult': cultivo['perdEstimRendCult'] if 'perdEstimRendCult' in cultivo else None,
        'afectaMaquinaria': cultivo['afectaMaquinaria'] if 'afectaMaquinaria' in cultivo else None,
        'nuevaEquivalencia': cultivo['nuevaEquivalencia'] if 'nuevaEquivalencia' in cultivo else None,
        'nombrenuvaunidad':  cultivo['nombrenuvaunidad'] if 'nombrenuvaunidad' in cultivo else None, 
        'nuevaunidadmetros': cultivo['nuevaunidadmetros'] if 'nuevaunidadmetros' in cultivo else None,
        'costoPromeJornal': cultivo['costoPromeJornal'] if 'costoPromeJornal' in cultivo else None,
        
    }

    validacion = [

    ]

    return obj


# Validate the direct costs fields in agro system
def validate_direct_costs_agro(costo):
    _costo = None
    noJornales = None
    
    if not 'gastos' in costo:
        _costo = 0
    elif costo['gastos'] == '':
        _costo = 0
    else:
        _costo = costo['gastos']

    if costo['noJornales'] == '' or not 'noJornales' in costo:
        noJornales = 0
    else:
        noJornales = costo['noJornales']

    obj = {
        'actividad': costo['actividad'] if 'actividad' in costo else None,
        'gastos': _costo,
        'id': costo['idTipoCostoDirecto'] if 'idTipoCostoDirecto' in costo else None,
        'noJornales': noJornales
    }

    return obj


# Validate the indirect costs fields in agro system
def valdate_indirect_costs_agro(costo):
    obj = {
        'actividad': costo['actividad'] if 'actividad' in costo else None,
        'costo': costo['costo'] if 'costo' in costo else None,
        'id': costo['id'] if 'id' in costo else None,
        'tipoCostoInDirecto': costo['tipoCostoInDirecto'] if 'tipoCostoInDirecto' in costo else None
    }

    return obj


# Validate the fertilizer fields in agro system
def validate_fertilizer_type_agro(infraestructura):
    validatedInfraestructura = []
    for fertilizante in infraestructura:
        obj = {
            'canFertilizante': fertilizante['canFertilizante'] if 'canFertilizante' in fertilizante else None,
            'fechaAdquisicion': fertilizante['fechaAdquisicion'] if 'fechaAdquisicion' in fertilizante else None,
            'idTipoFertilizante': fertilizante['idTipoFertilizante'] if 'idTipoFertilizante' in fertilizante else None,
            'menuFechaAdquisicion': fertilizante['menuFechaAdquisicion'] if 'menuFechaAdquisicion' in fertilizante else None,
            'nombre': fertilizante['nombre'] if 'nombre' in fertilizante else None,
            'nombreTipoFerti': fertilizante['nombreTipoFerti'] if 'nombreTipoFerti' in fertilizante else None,
            'valPesos': fertilizante['valPesos'] if 'valPesos' in fertilizante else None,
        }

        validatedInfraestructura.append(obj)

    return validatedInfraestructura


# Validate the machinery type in agro system
def validate_machinery_type_agro(infraestructura):
    validatedInfraestructura = []
    for maquinaria in infraestructura:
        obj = {
            'anoAdquisicion': maquinaria['anoAdquisicion'] if 'anoAdquisicion' in maquinaria else None,
            'idTipoMaquinariaAgricola': maquinaria['idTipoMaquinariaAgricola'] if 'idTipoMaquinariaAgricola' in maquinaria else None,
            'nombreTipoMaquinaria': maquinaria['nombreTipoMaquinaria'] if 'nombreTipoMaquinaria' in maquinaria else None,
            'porceDisminucion': maquinaria['porceDisminucion'] if 'porceDisminucion' in maquinaria else None,
            'valorPesos': maquinaria['valorPesos'] if 'valorPesos' in maquinaria else None,
        }

        validatedInfraestructura.append(obj)

    return validatedInfraestructura


# Validate the plaguicide type in agro system
def validate_plaguicide_type_agro(infraestructura):
    validatedPlaguicidas = []
    for plaguicida in infraestructura:
        obj = {
            'cantPlaguicidaKg': plaguicida['cantPlaguicidaKg'] if 'cantPlaguicidaKg' in plaguicida else None,
            'cantPlaguicidaLt': plaguicida['cantPlaguicidaLt'] if 'cantPlaguicidaLt' in plaguicida else None,
            'idTipoPlaguicida': plaguicida['idTipoPlaguicida'] if 'idTipoPlaguicida' in plaguicida else None,
            'idTipoPresentacion': plaguicida['idTipoPresentacion'] if 'idTipoPresentacion' in plaguicida else None,
            'nombreTipoPlaguicida': plaguicida['nombreTipoPlaguicida'] if 'nombreTipoPlaguicida' in plaguicida else None,
            'valPesos': plaguicida['valPesos'] if 'valPesos' in plaguicida else None,
        }

        validatedPlaguicidas.append(obj)

    return validatedPlaguicidas


# Validate the seed type in agro system
def validate_seed_type_agro(infraestructura):
    validatedSemilla = []
    for semilla in infraestructura:
        obj = {
            'tipoCultivo': semilla['tipoCultivo'] if 'tipoCultivo' in semilla else None,
            'canSemillas': semilla['canSemillas'] if 'canSemillas' in semilla else None,
            'especie': semilla['especie'] if 'especie' in semilla else None,
            'valPesos': semilla['valPesos'] if 'valPesos' in semilla else None,
            'materiralSiembra': semilla['materiralSiembra'] if 'materiralSiembra' in semilla else None,
            'cantSemillas': semilla['cantSemillas'] if 'cantSemillas' in semilla else None,
            'medidaSemilla': semilla['medidaSemilla'] if 'medidaSemilla' in semilla else None,
            'fuenteSemilla': semilla['fuenteSemilla'] if 'fuenteSemilla' in semilla else None,
            'equivaleKilos': semilla['equivaleKilos'] if 'equivaleKilos' in semilla else None,
            'nuevaEquivalencia': semilla['nuevaEquivalencia'] if 'nuevaEquivalencia' in semilla else None
        }

        validatedSemilla.append(obj)
    return validatedSemilla


# Validate fields from apiarian system
def validate_fields_apiarian(dataEspecie):
    array_apicola = []
    if len(dataEspecie) > 0:
        for sistema in dataEspecie:
                
                array_apicola.append(
                    {
                        'numColmenas': sistema['numColmenas'] if 'numColmenas' in sistema else None,
                        'valorColmena': sistema['valorColmena'] if 'valorColmena' in sistema else None,
                        'propoleoMensual': sistema['propoleoMensual'] if 'propoleoMensual' in sistema else None,
                        'mielMensual': sistema['mielMensual'] if 'mielMensual' in sistema else None,
                        'jaleaMensual': sistema['jaleaMensual'] if 'jaleaMensual' in sistema else None,
                        'valorMensual': sistema['valorMensual'] if 'valorMensual' in sistema else None,
                        'ingresoMensual': sistema['ingresoMensual'] if 'ingresoMensual' in sistema else None,

                        'valorCriaAnual': sistema['valorCriaAnual'] if 'valorCriaAnual' in sistema else None,

                        #'sistema': sistema['sistema'] if 'sistema' in sistema else None,
                        'maquinarias': sistema['maquinarias'] if 'maquinarias' in sistema else None,
                        'dataInfraestructura': sistema['dataInfraestructura'] if 'dataInfraestructura' in sistema else None,
                        'afectacion': sistema['afectacion'] if 'afectacion' in sistema else False,
                        'insumos': sistema['insumos'] if 'insumos' in sistema else None,
                    }
                )


                validacion = [
                    {'campo': 'numColmenas', 'valor': array_apicola[-1]['numColmenas'], 'obligatorio': 1},
                    {'campo': 'valorColmena', 'valor': array_apicola[-1]['valorColmena'], 'obligatorio': 0},
                    {'campo': 'propoleoMensual', 'valor': array_apicola[-1]['propoleoMensual'], 'obligatorio': 1},
                    {'campo': 'mielMensual', 'valor': array_apicola[-1]['mielMensual'], 'obligatorio': 1},
                    {'campo': 'jaleaMensual', 'valor': array_apicola[-1]['jaleaMensual'], 'obligatorio': 1},
                    {'campo': 'valorMensual', 'valor': array_apicola[-1]['valorMensual'], 'obligatorio': 0},
                    {'campo': 'ingresoMensual', 'valor': array_apicola[-1]['ingresoMensual'], 'obligatorio': 0},

                    {'campo': 'valorCriaAnual', 'valor': array_apicola[-1]['valorCriaAnual'], 'obligatorio': 0},

                    #{'campo': 'sistema', 'valor': array_apicola[-1]['sistema'], 'obligatorio': 1},
                    {'campo': 'maquinarias', 'valor': array_apicola[-1]['maquinarias'], 'obligatorio': 0},
                    {'campo': 'dataInfraestructura', 'valor': array_apicola[-1]['dataInfraestructura'], 'obligatorio': 0},
                    {'campo': 'afectacion', 'valor': array_apicola[-1]['afectacion'], 'obligatorio': 1},
                    {'campo': 'insumos', 'valor': array_apicola[-1]['insumos'], 'obligatorio': 0}
                ]

                estadoValidate = validate_fields(validacion)

                if estadoValidate == 0:
                    return [], False

        return array_apicola, estadoValidate
        
    return [], True

# Validate the fields from peq system
def validate_fields_peq(dataEspecie):
    array_pecuario = []
    #if len(dataEspecie) > 0:
    #    for _sistema in dataEspecie:
            #print(dataEspecie)
            #dataPecuario = _sistema['dataPecuario']
            #for sistema in dataPecuario:
    costos_variables = None
    costos_fijos = None

    for sistema in dataEspecie:
        if 'costosVariables' in sistema:
            costos_variables, estadoValidate = validate_variable_costs_peq(sistema)
            if estadoValidate == 0:
                return array_pecuario, estadoValidate

        if 'costosFijos' in sistema:
            costos_fijos, estadoValidate = validate_nonvariable_costs_peq(sistema)
            if estadoValidate == 0:
                return array_pecuario, estadoValidate
        
        array_pecuario.append(
            {
                'nombreRaza': str(sistema['nombreRaza']) if 'nombreRaza' in sistema else None,
                'pesoAnimal': float(sistema['pesoAnimal']) if 'pesoAnimal' in sistema else None,
                'numAnimal': int(sistema['numAnimal']) if 'numAnimal' in sistema else None,
                'uniMedidaAnimal': sistema['uniMedidaAnimal'] if 'uniMedidaAnimal' in sistema else None,
                'peso': float(sistema['peso']) if 'peso' in sistema else None,
                'valorAnimal': float(str(sistema['valorAnimal']).replace(',','')) if 'valorAnimal' in sistema and sistema['valorAnimal'] else None,
                'areaAnimal': float(sistema['areaAnimal']) if 'areaAnimal' in sistema else None,
                'unidadArea': sistema['unidadArea'] if 'unidadArea' in sistema else None,
                'menuFechaProduccion': sistema['menuFechaProduccion'] if 'menuFechaProduccion' in sistema else None,
                'fechaProduccion': sistema['fechaProduccion'] if 'fechaProduccion' in sistema else None,
                'menuFechaIniEvento': sistema['menuFechaIniEvento'] if 'menuFechaIniEvento' in sistema else None,
                'fechaIniEvento': sistema['fechaIniEvento'] if 'fechaIniEvento' in sistema else None,
                'numAnimalEnfermos': int(sistema['numAnimalEnfermos']) if 'numAnimalEnfermos' in sistema else None,
                'numAnimalHembMuerto': int(sistema['numAnimalHembMuerto']) if 'numAnimalHembMuerto' in sistema else None,
                'numAnimalMachMuerto': int(sistema['numAnimalMachMuerto']) if 'numAnimalMachMuerto' in sistema else None,
                'edadAnimal': float(sistema['edadAnimal']) if 'edadAnimal' in sistema else None,
                'tipoProducto': sistema['tipoProducto'] if 'tipoProducto' in sistema else None,
                'produMensualAfectacion': float(sistema['produMensualAfectacion']) if 'produMensualAfectacion' in sistema else None,
                'produPotencial': float(sistema['produPotencial']) if 'produPotencial' in sistema else None,
                'unidadProdccion': sistema['unidadProdccion'] if 'unidadProdccion' in sistema else None,
                'pesoProduccion': float(sistema['pesoProduccion']) if 'pesoProduccion' in sistema else None,
                'valorVentaProducto': float(str(sistema['valorVentaProducto']).replace(',','')) if 'valorVentaProducto' in sistema and sistema['valorVentaProducto'] else None,

                'pesoPromedioUnidad': float(sistema['pesoPromedioUnidad']) if 'pesoPromedioUnidad' in sistema else None,

                'huevosAvicola': sistema['huevosAvicola'] if 'huevosAvicola' in sistema else None,
                'costosVariables': costos_variables,
                'costosFijos': costos_fijos,
                'sistema': sistema['sistema'] if 'sistema' in sistema else None,
                'dataMaquinaria': sistema['dataMaquinaria'] if 'dataMaquinaria' in sistema else None,
                'dataInfraestructura': sistema['dataInfraestructura'] if 'dataInfraestructura' in sistema else None,
                'mesesRecuperarPecuaria': sistema['mesesRecuperarPecuaria'] if 'mesesRecuperarPecuaria' in sistema else None,
                'kilosUnidad': sistema['kilosUnidad'] if 'kilosUnidad' in sistema else None,
                'sistemaNuevo': sistema['sistemaNuevo'] if 'sistemaNuevo' in sistema else None,
                'nombreUnidadMedidaNuevo': sistema['nombreUnidadMedidaNuevo'] if 'nombreUnidadMedidaNuevo' in sistema else None,
                'unidadMedidaNuevo': sistema['unidadMedidaNuevo'] if 'unidadMedidaNuevo' in sistema else None,
                'pesoNuevo': sistema['pesoNuevo'] if 'pesoNuevo' in sistema else None,
                'unidadAreaNuevo': sistema['unidadAreaNuevo'] if 'unidadAreaNuevo' in sistema else None,
                'tipoProductoNuevo': sistema['tipoProductoNuevo'] if 'tipoProductoNuevo' in sistema else None,
                'pesoProduccionNuevo': sistema['pesoProduccionNuevo'] if 'pesoProduccionNuevo' in sistema else None,
                'nombreUnidadProduccionNueva': sistema['nombreUnidadProduccionNueva'] if 'nombreUnidadProduccionNueva' in sistema else None,
                'unidadProduccionNueva': sistema['unidadProduccionNueva'] if 'unidadProduccionNueva' in sistema else None,
                'dataInsumos': sistema['dataInsumos'] if 'dataInsumos' in sistema else None
            }
        )


        
        
        validacion = [
            {'campo': 'nombreRaza', 'valor': array_pecuario[-1]['nombreRaza'], 'obligatorio': 1},
            {'campo': 'pesoAnimal', 'valor': array_pecuario[-1]['pesoAnimal'], 'obligatorio': 0},
            {'campo': 'numAnimal', 'valor': array_pecuario[-1]['numAnimal'], 'obligatorio': 1},
            {'campo': 'uniMedidaAnimal', 'valor': array_pecuario[-1]['uniMedidaAnimal'], 'obligatorio': 1},
            {'campo': 'peso', 'valor': array_pecuario[-1]['peso'], 'obligatorio': 0},
            {'campo': 'valorAnimal', 'valor': array_pecuario[-1]['valorAnimal'], 'obligatorio': 0},
            {'campo': 'areaAnimal', 'valor': array_pecuario[-1]['areaAnimal'], 'obligatorio': 0},
            {'campo': 'unidadArea', 'valor': array_pecuario[-1]['unidadArea'], 'obligatorio': 0},
            {'campo': 'fechaProduccion', 'valor': array_pecuario[-1]['fechaProduccion'], 'obligatorio': 0},
            {'campo': 'fechaIniEvento', 'valor': array_pecuario[-1]['fechaIniEvento'], 'obligatorio': 0},
            {'campo': 'numAnimalEnfermos', 'valor': array_pecuario[-1]['numAnimalEnfermos'], 'obligatorio': 1},
            {'campo': 'numAnimalHembMuerto', 'valor': array_pecuario[-1]['numAnimalHembMuerto'], 'obligatorio': 0},
            {'campo': 'numAnimalMachMuerto', 'valor': array_pecuario[-1]['numAnimalMachMuerto'], 'obligatorio': 0},
            {'campo': 'edadAnimal', 'valor': array_pecuario[-1]['edadAnimal'], 'obligatorio': 1},
            {'campo': 'tipoProducto', 'valor': array_pecuario[-1]['tipoProducto'], 'obligatorio': 1},
            {'campo': 'produMensualAfectacion', 'valor': array_pecuario[-1]['produMensualAfectacion'], 'obligatorio': 1},
            {'campo': 'produPotencial', 'valor': array_pecuario[-1]['produPotencial'], 'obligatorio': 1},
            {'campo': 'unidadProdccion', 'valor': array_pecuario[-1]['unidadProdccion'], 'obligatorio': 1},
            {'campo': 'pesoProduccion', 'valor': array_pecuario[-1]['pesoProduccion'], 'obligatorio': 0},
            {'campo': 'valorVentaProducto', 'valor': array_pecuario[-1]['valorVentaProducto'], 'obligatorio': 1},
            
            {'campo': 'pesoPromedioUnidad', 'valor': array_pecuario[-1]['pesoPromedioUnidad'], 'obligatorio': 0},

            {'campo': 'huevosAvicola', 'valor': array_pecuario[-1]['huevosAvicola'], 'obligatorio': 0},
            {'campo': 'mesesRecuperarPecuaria', 'valor': array_pecuario[-1]['mesesRecuperarPecuaria'], 'obligatorio': 1}
        ]
        

        estadoValidate =  validate_fields(validacion)
        if estadoValidate == 0:
            break
            
    return array_pecuario, estadoValidate
    #return [], True


# Validate the fields from the variable costs in the peq system
def validate_variable_costs_peq(_sistema):
    sistema = _sistema['costosVariables']
    array_costo = []
    for costo in sistema:
        array_costo.append(
            {
                'tipoCosto': costo['codCostoVariable'] if 'codCostoVariable' in costo else None,
                'valor': str(costo['costoVariable']).replace(',','') if 'costoVariable' in costo and costo['costoVariable'] else None
            }
        )
    
    return array_costo, 1


# Validate the fields from the non variable costs in peq system
def validate_nonvariable_costs_peq(_sistema):
    sistema = _sistema['costosFijos']
    array_costo = []
    for costo in sistema:
        array_costo.append(
            {
                'tipoCosto': costo['codCostoFijo'] if 'codCostoFijo' in costo else None,
                'valor': str(costo['costoFijo']).replace(',','') if 'costoFijo' in costo and costo['costoFijo'] else None
            }
        )
    
    return array_costo, 1



# Validate the affectation fields from the peq system
def validate_peq_affectation(afectacion):
    obj = {
        'tipoInsumo': afectacion['tipoInsumo'] if 'tipoInsumo' in afectacion else None,
        'nombreComercial': afectacion['nombreComercial'] if 'nombreComercial' in afectacion else None,
        'cantInsumo': afectacion['cantInsumo'] if 'cantInsumo' in afectacion else None,
        'unidadMedida': afectacion['unidadMedida'] if 'unidadMedida' in afectacion else None, 
        'valorBienes': str(afectacion['valorBienes']).replace(',','') if 'valorBienes' in afectacion and afectacion['valorBienes'] else None,
        'nuevoInsumo': afectacion['nuevoInsumo'] if 'nuevoInsumo' in afectacion else None
    }

    validacion = [
        {'campo': 'tipoInsumo', 'valor': obj['tipoInsumo'], 'obligatorio': 1},
        {'campo': 'nombreComercial', 'valor': obj['nombreComercial'], 'obligatorio': 1},
        {'campo': 'cantInsumo', 'valor': obj['cantInsumo'], 'obligatorio': 1},
        {'campo': 'unidadMedida', 'valor': obj['unidadMedida'], 'obligatorio': 1},
        {'campo': 'valorBienes', 'valor': obj['valorBienes'], 'obligatorio': 1},
        {'campo': 'nuevoInsumo', 'valor': obj['nuevoInsumo'], 'obligatorio': 0},
    ]

    estadoValidate = validate_fields(validacion)

    return obj, estadoValidate


# Validate the machinery BBA fields from the peq system
def validate_machineryBBA_peq(maquinaria):
    obj = {
        'tipoMaquinariaBba': maquinaria['tipoMaquinariaBba'] if 'tipoMaquinariaBba' in maquinaria else None,
        'nombreMaquinariaBba': maquinaria['nombreMaquinariaBba'] if 'nombreMaquinariaBba' in maquinaria else None,
        'valorReparacionBba': str(maquinaria['valorReparacionBba']).replace(',','') if 'valorReparacionBba' in maquinaria and maquinaria['valorReparacionBba'] else None,
    }


    return obj, True


# Validate the machinery PEM fields from the peq system
def validate_machineryPEM_peq(maquinaria):
    obj = {
        'tipoMaquinariaPem': maquinaria['tipoMaquinariaPem'] if 'tipoMaquinariaPem' in maquinaria else None,
        'nombreMarcaPem': maquinaria['nombreMarcaPem'] if 'nombreMarcaPem' in maquinaria else None,
        'valorReparacionPem': str(maquinaria['valorReparacionPem']).replace(',','') if 'valorReparacionPem' in maquinaria and maquinaria['valorReparacionPem'] else None,

        'fechaAdquisicion': maquinaria['fechaAdquisicion'] if 'fechaAdquisicion' in maquinaria else None,
    }

    
    return obj, True


# Validate the infrastructure fields from the peq system
def validate_infrastructure_peq(infraestructura):
    obj = {
        'tipActivo': infraestructura['tipActivo'] if 'tipActivo' in infraestructura else None,
        'nombreEquipo': infraestructura['nombreEquipo'] if 'nombreEquipo' in infraestructura else infraestructura['nombreEquipoConstruc']  if 'nombreEquipoConstruc' in infraestructura else None,
        'fechaAdquisicion': infraestructura['fechaAdquisicion'] if 'fechaAdquisicion' in infraestructura else infraestructura['fechaConstruc'] if 'fechaConstruc' in infraestructura else None,
        'valorPagado': str(infraestructura['valorPagado']).replace(',','') if 'valorPagado' in infraestructura and infraestructura['valorPagado'] else infraestructura['valorPagadoConstruc'].replace(',','') if 'valorPagadoConstruc' in infraestructura and infraestructura['valorPagadoConstruc'] else None,
        'valorReponer': str(infraestructura['valorReponer']).replace(',','') if 'valorReponer' in infraestructura and infraestructura['valorReponer'] else infraestructura['valorReponerConstruc'].replace(',','') if 'valorReponerConstruc' in infraestructura and infraestructura['valorReponerConstruc'] else None,
        'tipAfecta': infraestructura['tipAfecta'] if 'tipAfecta' in infraestructura else None,
        'areaAfectada': infraestructura['areaAfectada'] if 'areaAfectada' in infraestructura else None,
        'valorReparacion': str(infraestructura['valorReparacion']).replace(',','') if 'valorReparacion' in infraestructura and infraestructura['valorReparacion'] else None,
        'mesesReparacion': infraestructura['mesesReparacion'] if 'mesesReparacion' in infraestructura else None
    }
    
    validacion = []

    if obj['tipActivo'] == 2:
        validacion = [
            {'campo': 'tipActivo', 'valor': obj['tipActivo'], 'obligatorio': 1},
            {'campo': 'nombreEquipo', 'valor': obj['nombreEquipo'], 'obligatorio': 1},
            {'campo': 'fechaAdquisicion', 'valor': obj['fechaAdquisicion'], 'obligatorio': 0},
            {'campo': 'valorPagado', 'valor': obj['valorPagado'], 'obligatorio': 1},
            {'campo': 'valorReponer', 'valor': obj['valorReponer'], 'obligatorio': 1},
            {'campo': 'tipAfecta', 'valor': obj['tipAfecta'], 'obligatorio': 1},
            {'campo': 'areaAfectada', 'valor': obj['areaAfectada'], 'obligatorio': 1},
            {'campo': 'valorReparacion', 'valor': obj['valorReparacion'], 'obligatorio': 1},
            {'campo': 'mesesReparacion', 'valor': obj['mesesReparacion'], 'obligatorio': 1}
        ]
    else:
        validacion = [
            {'campo': 'tipActivo', 'valor': obj['tipActivo'], 'obligatorio': 1},
            {'campo': 'nombreEquipo', 'valor': obj['nombreEquipo'], 'obligatorio': 1},
            {'campo': 'fechaAdquisicion', 'valor': obj['fechaAdquisicion'], 'obligatorio': 0},
            {'campo': 'valorPagado', 'valor': obj['valorPagado'], 'obligatorio': 1},
            {'campo': 'valorReponer', 'valor': obj['valorReponer'], 'obligatorio': 1}
        ]


    estadoValidate = validate_fields(validacion)

    return obj, estadoValidate


# Validate the fields in fishing system
def validate_fields_fishing(dataEspecie):
    obj = {
        'especieExplotada': dataEspecie['especieExplotada'] if 'especieExplotada' in dataEspecie else None,
        'embarcacionAfectada': dataEspecie['embarcacionAfectada'] if 'embarcacionAfectada' in dataEspecie else None,
        'instalacionAfectada': dataEspecie['instalacionAfectada'] if 'instalacionAfectada' in dataEspecie else None,
        'redesAfectadas': dataEspecie['redesAfectadas'] if 'redesAfectadas' in dataEspecie else None,
        'numeroRedes': dataEspecie['numeroRedes'] if 'numeroRedes' in dataEspecie else None,
        'valorRedes': float(str(dataEspecie['valorRedes']).replace(',','')) if 'valorRedes' in dataEspecie and dataEspecie['valorRedes'] else None,
        'numeroFaenas': dataEspecie['numeroFaenas'] if 'numeroFaenas' in dataEspecie else None,
        'cantidadFaenasMes': dataEspecie['cantidadFaenasMes'] if 'cantidadFaenasMes' in dataEspecie else None,
        'valorVentaPeces': float(str(dataEspecie['valorVentaPeces']).replace(',','')) if 'valorVentaPeces' in dataEspecie and dataEspecie['valorVentaPeces'] else None,
        'maquinariaAfectada': dataEspecie['maquinariaAfectada'] if 'maquinariaAfectada' in dataEspecie else None,
        'puertoDesembarque': dataEspecie['puertoDesembarque'] if 'puertoDesembarque' in dataEspecie else None,
        'tipoPesqueria': dataEspecie['tipoPesqueria'] if 'tipoPesqueria' in dataEspecie else None,
        'embarcaciones': dataEspecie['embarcaciones'] if 'embarcaciones' in dataEspecie else None,
        'maquinarias': dataEspecie['maquinarias'] if 'maquinarias' in dataEspecie else None,
        'tipoRedes': dataEspecie['tipoRedes'] if 'tipoRedes' in dataEspecie else None,
        'marcaRed': dataEspecie['marcaRed'] if 'marcaRed' in dataEspecie else None,
        'fechaAdquisicion': dataEspecie['fechaAdquisicion'] if 'fechaAdquisicion' in dataEspecie else None,
        'tipoPerdida': dataEspecie['tipoPerdida'] if 'tipoPerdida' in dataEspecie else None
    }

    return obj


# Validate the fields in embarkations from fishing system
def validate_embarkations(embarkation):
    obj = {
        'tipoEmbarcacion': embarkation['tipoEmbarcacion'] if 'tipoEmbarcacion' in embarkation else None,
        'patenteEmbarcacion': embarkation['patenteEmbarcacion'] if 'patenteEmbarcacion' in embarkation else None,
        'esloraEmbarcacion': float(embarkation['esloraEmbarcacion']) if 'esloraEmbarcacion' in embarkation else None,
        'valorEmbarcacion': float(str(embarkation['valorEmbarcacion']).replace(',','')) if 'valorEmbarcacion' in embarkation and embarkation['valorEmbarcacion'] else None,
        'observacionEmbarcacion': embarkation['observacionEmbarcacion'] if 'observacionEmbarcacion' in embarkation else None,

        'material': embarkation['material'] if 'material' in embarkation else None,
        'propulsion': embarkation['propulsion'] if 'propulsion' in embarkation else None,
        'edad': embarkation['edad'] if 'edad' in embarkation else None,
    }

    return obj


# Validate the fields in infrstructure from fishing system
def validate_infrastructure_fishing(infrastructure):
    obj = {
        'activoProductivo': infrastructure['activoProductivo'] if 'activoProductivo' in infrastructure else None,
        'nombreEquipo': infrastructure['nombreEquipo'] if 'nombreEquipo' in infrastructure else None,
        'fechaAdquisicion': infrastructure['fechaAdquisicion'] if 'fechaAdquisicion' in infrastructure else None,
        'valorActivo': float(str(infrastructure['valorActivo']).replace(',','')) if 'valorActivo' in infrastructure and infrastructure['valorActivo'] else None,
        'valorReponer': float(str(infrastructure['valorReponer']).replace(',','')) if 'valorReponer' in infrastructure and infrastructure['valorReponer'] else None,
        'tipoConstruccion': infrastructure['tipoConstruccion'] if 'tipoConstruccion' in infrastructure else None,
        'areaAfectada': float(infrastructure['areaAfectada']) if 'areaAfectada' in infrastructure else None,
        'valorInvertidoAdecuacion': float(str(infrastructure['valorInvertidoAdecuacion']).replace(',','')) if 'valorInvertidoAdecuacion' in infrastructure and infrastructure['valorInvertidoAdecuacion'] else None,
        'mesesReconstruccion': float(infrastructure['mesesReconstruccion']) if 'mesesReconstruccion' in infrastructure else None,
        'tipoRedes': infrastructure['tipoRedes'] if 'tipoRedes' in infrastructure else None,
        'tipoPerdida': infrastructure['tipoPerdida'] if 'tipoPerdida' in infrastructure else None
    }

    return obj

# Validate fields from the tracing of the event
def validate_tracing_event(idEvento, observacion):
    obj = {
		'idEvento': idEvento if idEvento else None,
		'observacion': observacion if observacion else None,
    }

    validacion = [
		{'campo': 'idEvento', 'valor': obj['idEvento'], 'obligatorio': 1},
		{'campo': 'observacion',
			'valor': obj['observacion'], 'obligatorio': 1},
	]

    estadoValidate = validate_fields(validacion)

    return obj, estadoValidate


# Validate the field from the attached file in tracing
def validate_attached_tracing(idSeguimiento, ruta, filename):
	obj = {
		'idSeguimiento': idSeguimiento if idSeguimiento else None,
		'ruta': ruta if ruta else None,
		'filename': filename if filename else None,
    }

	validacion = [
		{'campo': 'idSeguimiento',
			'valor': obj['idSeguimiento'], 'obligatorio': 1},
		{'campo': 'ruta', 'valor': obj['ruta'], 'obligatorio': 1},
		{'campo': 'filename', 'valor': obj['filename'], 'obligatorio': 1},
	]

	estadoValidate = validate_fields(validacion)

	return obj, estadoValidate

# Validate that the needed info to save fishing grounds have been send
def validate_fishing_grounds(caladero, encabezado):
    obj = {
        'nombrePuerto': encabezado['nombrePuerto'] if 'nombrePuerto' in encabezado else None,
        'latitud': caladero['position']['lat'] if 'position' in caladero and 'lat' in caladero['position'] else None,
        'longitud': caladero['position']['lng'] if 'position' in caladero and 'lng' in caladero['position'] else None,
        'altitud': float(encabezado['altitud']) if 'altitud' in encabezado and encabezado['altitud'] else None,
        'precision': float(encabezado['precision']) if 'precision' in encabezado and encabezado['precision'] else None,
    }

    validacion = [
        {'campo': 'nombrePuerto', 'valor': obj['nombrePuerto'], 'obligatorio': 0},
        {'campo': 'latitud', 'valor': obj['latitud'], 'obligatorio': 1},
        {'campo': 'longitud', 'valor': obj['longitud'], 'obligatorio': 1},
        {'campo': 'altitud', 'valor': obj['altitud'], 'obligatorio': 0},
        {'campo': 'precision', 'valor': obj['precision'], 'obligatorio': 0}
    ]

    estadoValidate = validate_fields(validacion)

    return obj, estadoValidate