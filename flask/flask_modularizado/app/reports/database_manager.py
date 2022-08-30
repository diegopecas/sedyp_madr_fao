from app.exceptions import CustomException
from app.helpers import raise_exception

# Gets the data of the reports per system
def get_reports_system(id, connection):
  try:
    obj = {}

    if id == 1:
      agro = get_agro_reports(connection)
      if agro[1] !=200:
        raise_exception(agro[0].to_dict()['message'],  agro[0].to_dict()['error'])
      
      obj = agro[0]
    elif id == 2:
      peq = get_peq_reports(connection)
      if peq[1] != 200:
        raise_exception(peq[0].to_dict()['message'],  peq[0].to_dict()['error'])

      obj = peq[0]
    elif id == 3:
      forestal = get_forestal_reports(connection)
      if forestal[1] != 200:
        raise_exception(forestal[0].to_dict()['message'],  forestal[0].to_dict()['error'])

      obj = forestal[0]
    elif id == 4:
      pesq = get_pesq_reports(connection)
      if pesq[1] != 200:
        raise_exception(pesq[0].to_dict()['message'],  pesq[0].to_dict()['error'])
      
      obj = pesq[0]
    elif id == 5:
      api = get_apiarian_reports(connection)
      if api[1] != 200:
        raise_exception(api[0].to_dict()['message'],  api[0].to_dict()['error'])

      obj = api[0]
  except CustomException as e:
    print("ERROR (user/database_manager/get_reports_system):", e.to_dict()['error'])
    return e, 500
  except Exception as e:
    print("ERROR (user/database_manager/get_reports_system):", e)
    return CustomException('Ocurrio un error al obtener los datos de los reportes', str(e)), 500
  else:
    return obj, 200

# Gets the data of the reports for agro system
def get_agro_reports(connection):
  try:
    cursor = connection.cursor()
    obj = {}

    sql = ("""
        select row_to_json(row) FROM (
        select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from evento
        join evento_productos_agropecuario on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
        join productor_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
        join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
        join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
        join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
        join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
        join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
        join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
        join cultivos_afectados on cultivos_afectados.cod_cultivo = evento_sist_prod_afectado.cod_cultivo_afectado_fk
        where evento.validado = true) as subconsulta
        join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
        join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
      """)

    cursor.execute(sql)
    general = []
    for g in cursor.fetchall():
      general.append(g[0])
    

    sql = ("""
        select row_to_json(row) FROM (
        select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from productor_agropecuario
        join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
        join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
        join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
        join evento_productos_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
        join evento on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
        join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
        join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
        join cultivos_afectados on cultivos_afectados.cod_cultivo = evento_sist_prod_afectado.cod_cultivo_afectado_fk
        join indicador_valor on evento.cod_evento = indicador_valor.cod_evento_fk
        join indicador on indicador_valor.cod_indicador_fk = indicador.cod_indicador
        join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
        where evento.validado = true) as subconsulta
        join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
        join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
      """)

    cursor.execute(sql)
    indicadores = []
    for i in cursor.fetchall():
      indicadores.append(i[0])


    sql = ("""
        select row_to_json(row) FROM (
        select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from productor_agropecuario
        join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
        join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
        join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
        join evento_productos_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
        join evento on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
        join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
        join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
        join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
        join cultivos_afectados on cultivos_afectados.cod_cultivo = evento_sist_prod_afectado.cod_cultivo_afectado_fk
        where evento.validado = true) as subconsulta
        join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
        join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
      """)

    cursor.execute(sql)
    condicion_juridica = []
    for c in cursor.fetchall():
      condicion_juridica.append(c[0])

    sql = ("""
        select row_to_json(row) FROM (
        select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from productor_agropecuario
        join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
        join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
        join sexo on productor_agropecuario.cod_sexo_fk = sexo.cod_sexo
        join evento_productos_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
        join evento on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
        join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
        join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
        join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
        join cultivos_afectados on cultivos_afectados.cod_cultivo = evento_sist_prod_afectado.cod_cultivo_afectado_fk
        where evento.validado = true) as subconsulta
        join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
        join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
      """)

    cursor.execute(sql)
    sexo = []
    for s in cursor.fetchall():
      sexo.append(s[0])

    sql = ("""
        select row_to_json(row) FROM (
        select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from evento_sist_prod_afectado
        join evento on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
        join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
        join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
        join cultivos_afectados on cultivos_afectados.cod_cultivo = evento_sist_prod_afectado.cod_cultivo_afectado_fk
        join evento_productos_agropecuario on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
        join productor_agropecuario on productor_agropecuario.cod_productor_agropecuario = evento_productos_agropecuario.cod_producto_agro
        join tipo_productor on tipo_productor.cod_tipo_productor = productor_agropecuario.cod_tipo_productor_fk
        join grupo_etnico on grupo_etnico.cod_grupo_etnico = productor_agropecuario.cod_grupo_etnico_fk
        where evento.validado = true) as subconsulta
        join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
        join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
      """)

    cursor.execute(sql)
    pertenencia_etnica = []
    for p in cursor.fetchall():
      pertenencia_etnica.append(p[0])

    sql = ("""
        select row_to_json(row) FROM (
        select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from evento_sist_prod_afectado
        join evento on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
        join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
        join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
        join cultivos_afectados on cultivos_afectados.cod_cultivo = evento_sist_prod_afectado.cod_cultivo_afectado_fk
        join evento_productos_agropecuario on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
        join productor_agropecuario on productor_agropecuario.cod_productor_agropecuario = evento_productos_agropecuario.cod_producto_agro
        join tipo_productor on tipo_productor.cod_tipo_productor = productor_agropecuario.cod_tipo_productor_fk
        join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
        join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
        where evento.validado = true) as subconsulta
        join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
        join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
      """)

    cursor.execute(sql)
    numero_agricultores = []
    for n in cursor.fetchall():
      numero_agricultores.append(n[0])

    sql = ("""
        select row_to_json(row) FROM (
        select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from evento_sist_prod_afectado
        join evento on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
        join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
        join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
        join cultivos_afectados on cultivos_afectados.cod_cultivo = evento_sist_prod_afectado.cod_cultivo_afectado_fk
        join tipo_cultivo on tipo_cultivo.cod_tipo_cultivo = cultivos_afectados.cod_nombre_fk
        where evento.validado = true) as subconsulta
        join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
        join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
      """)

    cursor.execute(sql)
    semillas_utilizadas = []
    for s in cursor.fetchall():
      semillas_utilizadas.append(s[0])

    sql = ("""
        select row_to_json(row) FROM (
        select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from evento_sist_prod_afectado
        join evento on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
        join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
        join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
        join cultivos_afectados on cultivos_afectados.cod_cultivo = evento_sist_prod_afectado.cod_cultivo_afectado_fk
        join tipo_cultivo on tipo_cultivo.cod_tipo_cultivo = cultivos_afectados.cod_nombre_fk
        join costos_de_produccion on costos_de_produccion.cod_cultivo_afectado_fk = cultivos_afectados.cod_cultivo
        join tipo_actividad on tipo_actividad.cod_tipo_actividad = costos_de_produccion.cod_actividad_fk
        where evento.validado = true) as subconsulta
        join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
        join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
      """)

    cursor.execute(sql)
    costos_directos = []
    for c in cursor.fetchall():
      costos_directos.append(c[0])

    sql = ("""
        select row_to_json(row) FROM (
        select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from evento_sist_prod_afectado
        join evento on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
        join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
        join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
        join cultivos_afectados on cultivos_afectados.cod_cultivo = evento_sist_prod_afectado.cod_cultivo_afectado_fk
        join tipo_cultivo on tipo_cultivo.cod_tipo_cultivo = cultivos_afectados.cod_nombre_fk
        join cultivo_infraestructura on  cultivo_infraestructura.cod_cultivo_fk = cultivos_afectados.cod_cultivo								   
        join infraestructura on infraestructura.cod_infraestructura = cultivo_infraestructura.cod_infraestructura_fk
        where evento.validado = true) as subconsulta
        join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
        join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
      """)

    cursor.execute(sql)
    infraestructura = []
    for i in cursor.fetchall():
      infraestructura.append(i[0])

    sql = ("""
        select row_to_json(row) FROM (
        select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from evento_sist_prod_afectado
        join evento on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
        join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
        join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
        join cultivos_afectados on cultivos_afectados.cod_cultivo = evento_sist_prod_afectado.cod_cultivo_afectado_fk
        join tipo_cultivo on tipo_cultivo.cod_tipo_cultivo = cultivos_afectados.cod_nombre_fk
        join costos_indirectos_produccion on costos_indirectos_produccion.cod_cultivo_afectado_fk = cultivos_afectados.cod_cultivo
        join rubros on 	rubros.cod_rubros = costos_indirectos_produccion.cod_rubro_fk
        where evento.validado = true) as subconsulta
        join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
        join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
      """)

    cursor.execute(sql)
    costos_indirectos = []
    for i in cursor.fetchall():
      costos_indirectos.append(i[0])

    obj = {
      'agricola': {
        'general': general,
        'indicadores': indicadores,
        'condicion_juridica': condicion_juridica,
        'sexo': sexo,
        'pertenencia_etnica': pertenencia_etnica,
        'numero_agricultores': numero_agricultores,
        'semillas_utilizadas': semillas_utilizadas,
        'costos_directos': costos_directos,
        'infraestructura': infraestructura,
        'costos_indirectos': costos_indirectos
      }
    }

  except CustomException as e:
    print("ERROR (user/database_manager/get_agro_reports):", e.to_dict()['error'])
    return e, 500
  except Exception as e:
    print("ERROR (user/database_manager/get_agro_reports):", e)
    return CustomException('Ocurrio un error al obtener los datos de los reportes del sistema agrícola', str(e)), 500
  else:
    return obj, 200
  finally:
    if cursor:
      if not cursor.closed:
        cursor.close()


# Gets the data of the reports for peq system
def get_peq_reports(connection):
  try:
    cursor = connection.cursor()
    obj = {}

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from evento
      join evento_productos_agropecuario on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join productor_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
      join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
      join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join novedad_pecuaria on novedad_pecuaria.cod_novedad_peq = evento_sist_prod_afectado.cod_novedad_pecuaria_fk
      where evento.validado = true and sistema_productivo_afectado.sistema_productivo_afectado='Explotación Pecuario / Acuicola') as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    general = []
    for g in cursor.fetchall():
      general.append(g[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from productor_agropecuario
      join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
      join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join evento_productos_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
      join evento on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join novedad_pecuaria on novedad_pecuaria.cod_novedad_peq = evento_sist_prod_afectado.cod_novedad_pecuaria_fk
      join indicador_valor on evento.cod_evento = indicador_valor.cod_evento_fk
      join indicador on indicador_valor.cod_indicador_fk = indicador.cod_indicador
      where evento.validado = true and sistema_productivo_afectado.sistema_productivo_afectado='Explotación Pecuario / Acuicola') as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    indicadores = []
    for i in cursor.fetchall():
      indicadores.append(i[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from productor_agropecuario
      join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
      join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join evento_productos_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
      join evento on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join novedad_pecuaria on novedad_pecuaria.cod_novedad_peq = evento_sist_prod_afectado.cod_novedad_pecuaria_fk
      where evento.validado = true and sistema_productivo_afectado.sistema_productivo_afectado='Explotación Pecuario / Acuicola') as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    condicion_juridica = []
    for c in cursor.fetchall():
      condicion_juridica.append(c[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from productor_agropecuario
      join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join sexo on productor_agropecuario.cod_sexo_fk = sexo.cod_sexo
      join evento_productos_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
      join evento on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join novedad_pecuaria on novedad_pecuaria.cod_novedad_peq = evento_sist_prod_afectado.cod_novedad_pecuaria_fk
      where evento.validado = true and sistema_productivo_afectado.sistema_productivo_afectado='Explotación Pecuario / Acuicola') as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    sexo = []
    for s in cursor.fetchall():
      sexo.append(s[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (
      select * from evento_sist_prod_afectado
      join evento on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join novedad_pecuaria on novedad_pecuaria.cod_novedad_peq = evento_sist_prod_afectado.cod_novedad_pecuaria_fk
      join evento_productos_agropecuario on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join productor_agropecuario on productor_agropecuario.cod_productor_agropecuario = evento_productos_agropecuario.cod_producto_agro
      join tipo_productor on tipo_productor.cod_tipo_productor = productor_agropecuario.cod_tipo_productor_fk
      join grupo_etnico on grupo_etnico.cod_grupo_etnico = productor_agropecuario.cod_grupo_etnico_fk
      where evento.validado = true and sistema_productivo_afectado.sistema_productivo_afectado='Explotación Pecuario / Acuicola') as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    pertenencia_etnica = []
    for p in cursor.fetchall():
      pertenencia_etnica.append(p[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from evento_sist_prod_afectado
      join evento on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join novedad_pecuaria on novedad_pecuaria.cod_novedad_peq = evento_sist_prod_afectado.cod_novedad_pecuaria_fk
      join evento_productos_agropecuario on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join productor_agropecuario on productor_agropecuario.cod_productor_agropecuario = evento_productos_agropecuario.cod_producto_agro
      join tipo_productor on tipo_productor.cod_tipo_productor = productor_agropecuario.cod_tipo_productor_fk
      join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      where evento.validado = true and sistema_productivo_afectado.sistema_productivo_afectado='Explotación Pecuario / Acuicola') as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    numero_agricultores = []
    for n in cursor.fetchall():
      numero_agricultores.append(n[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from evento
      join evento_productos_agropecuario on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join productor_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
      join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
      join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join novedad_pecuaria on novedad_pecuaria.cod_novedad_peq = evento_sist_prod_afectado.cod_novedad_pecuaria_fk
      join afectacion_peq on afectacion_peq.cod_novedad_pecuaria_fk = novedad_pecuaria.cod_novedad_peq
      where evento.validado = true and sistema_productivo_afectado.sistema_productivo_afectado='Explotación Pecuario / Acuicola') as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    novedad_pecuaria = []
    for n in cursor.fetchall():
      novedad_pecuaria.append(n[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from evento
      join evento_productos_agropecuario on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join productor_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
      join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
      join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join novedad_pecuaria on novedad_pecuaria.cod_novedad_peq = evento_sist_prod_afectado.cod_novedad_pecuaria_fk
      join maquinaria_bba on maquinaria_bba.cod_novedad_pecuaria_fk = novedad_pecuaria.cod_novedad_peq
      where evento.validado = true and sistema_productivo_afectado.sistema_productivo_afectado='Explotación Pecuario / Acuicola') as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    maquinaria = []
    for m in cursor.fetchall():
      maquinaria.append(m[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from evento
      join evento_productos_agropecuario on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join productor_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
      join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
      join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join novedad_pecuaria on novedad_pecuaria.cod_novedad_peq = evento_sist_prod_afectado.cod_novedad_pecuaria_fk
      join infraestructura_pecuario on infraestructura_pecuario.cod_novedad_pecuario_fk = novedad_pecuaria.cod_novedad_peq
      where evento.validado = true and sistema_productivo_afectado.sistema_productivo_afectado='Explotación Pecuario / Acuicola') as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    infraestructura = []
    for i in cursor.fetchall():
      infraestructura.append(i[0])

    
    obj= {
      'pecuario': {
        'general': general,
        'indicadores': indicadores,
        'condicion_juridica': condicion_juridica,
        'sexo': sexo,
        'pertenencia_etnica': pertenencia_etnica,
        'numero_agricultores': numero_agricultores,
        'novedad_pecuaria': novedad_pecuaria,
        'maquinaria': maquinaria,
        'infraestructura': infraestructura
      }
    }

  except CustomException as e:
    print("ERROR (user/database_manager/get_peq_reports):", e.to_dict()['error'])
    return e, 500
  except Exception as e:
    print("ERROR (user/database_manager/get_peq_reports):", e)
    return CustomException('Ocurrio un error al obtener los datos de los reportes del sistema pecuario', str(e)), 500
  else:
    return obj, 200
  finally:
    if cursor:
      if not cursor.closed:
        cursor.close()


# Gets the data of the reports for forestal system
def get_forestal_reports(connection):
  try:
    cursor = connection.cursor()
    obj = {}

    sql = ("""
        select row_to_json(row) FROM (
        select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (
        select * from evento
        join evento_productos_agropecuario on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
        join productor_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
        join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
        join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
        join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
        join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
        join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
        join especie_forestal_sembrada on especie_forestal_sembrada.cod_especie_forestal_sembrada = evento_sist_prod_afectado.cod_especie_forestal_fk
        join fase_productiva on especie_forestal_sembrada.cod_fase_productiva_fk = fase_productiva.cod_fase_productiva
        join especie_forestal_afectada on especie_forestal_sembrada.cod_especie_forestal_afec_fk = especie_forestal_afectada.cod_esp_forestal_afectada
        where evento.validado = true
        ) as subconsulta
        join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
        join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
      """)

    cursor.execute(sql)
    general = []
    for g in cursor.fetchall():
      general.append(g[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*, municipios.nom_municipio, departamentos.nombre_dpto from (select * from productor_agropecuario
      join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
      join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join evento_productos_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
      join evento on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join especie_forestal_sembrada on especie_forestal_sembrada.cod_especie_forestal_sembrada = evento_sist_prod_afectado.cod_especie_forestal_fk
      join indicador_valor on evento.cod_evento = indicador_valor.cod_evento_fk
      join indicador on indicador_valor.cod_indicador_fk = indicador.cod_indicador
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      where evento.validado = true) as subconsulta 
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    indicadores = []
    for i in cursor.fetchall():
      indicadores.append(i[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*, municipios.nom_municipio, departamentos.nombre_dpto from (select * from productor_agropecuario
      join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
      join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join sexo on productor_agropecuario.cod_sexo_fk = sexo.cod_sexo
      join evento_productos_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
      join evento on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join especie_forestal_sembrada on especie_forestal_sembrada.cod_especie_forestal_sembrada = evento_sist_prod_afectado.cod_especie_forestal_fk
      join fase_productiva on especie_forestal_sembrada.cod_fase_productiva_fk = fase_productiva.cod_fase_productiva
      join especie_forestal_afectada on especie_forestal_sembrada.cod_especie_forestal_afec_fk = especie_forestal_afectada.cod_esp_forestal_afectada
      where evento.validado = true) as subconsulta 
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    condicion_juridica = []
    for c in cursor.fetchall():
      condicion_juridica.append(c[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*, municipios.nom_municipio, departamentos.nombre_dpto from (select * from productor_agropecuario
      join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join sexo on productor_agropecuario.cod_sexo_fk = sexo.cod_sexo
      join evento_productos_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
      join evento on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join especie_forestal_sembrada on especie_forestal_sembrada.cod_especie_forestal_sembrada = evento_sist_prod_afectado.cod_especie_forestal_fk
      join fase_productiva on especie_forestal_sembrada.cod_fase_productiva_fk = fase_productiva.cod_fase_productiva
      join especie_forestal_afectada on especie_forestal_sembrada.cod_especie_forestal_afec_fk = especie_forestal_afectada.cod_esp_forestal_afectada
      where evento.validado = true) as subconsulta 
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    sexo = []
    for s in cursor.fetchall():
      sexo.append(s[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*, municipios.nom_municipio, departamentos.nombre_dpto from (select * from evento_sist_prod_afectado
      join evento on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join especie_forestal_sembrada on especie_forestal_sembrada.cod_especie_forestal_sembrada = evento_sist_prod_afectado.cod_especie_forestal_fk
      join especie_forestal_afectada on especie_forestal_afectada.cod_esp_forestal_afectada = especie_forestal_sembrada.cod_especie_forestal_afec_fk
      join evento_productos_agropecuario on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join productor_agropecuario on productor_agropecuario.cod_productor_agropecuario = evento_productos_agropecuario.cod_producto_agro
      join tipo_productor on tipo_productor.cod_tipo_productor = productor_agropecuario.cod_tipo_productor_fk
      join grupo_etnico on grupo_etnico.cod_grupo_etnico = productor_agropecuario.cod_grupo_etnico_fk
      where evento.validado = true) as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    pertenencia_etnica = []
    for p in cursor.fetchall():
      pertenencia_etnica.append(p[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*, municipios.nom_municipio, departamentos.nombre_dpto from (select * from evento_sist_prod_afectado
      join evento on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join especie_forestal_sembrada on especie_forestal_sembrada.cod_especie_forestal_sembrada = evento_sist_prod_afectado.cod_especie_forestal_fk
      join especie_forestal_afectada on especie_forestal_afectada.cod_esp_forestal_afectada = especie_forestal_sembrada.cod_especie_forestal_afec_fk
      join evento_productos_agropecuario on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join productor_agropecuario on productor_agropecuario.cod_productor_agropecuario = evento_productos_agropecuario.cod_producto_agro
      join tipo_productor on tipo_productor.cod_tipo_productor = productor_agropecuario.cod_tipo_productor_fk
      join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join sexo on productor_agropecuario.cod_sexo_fk = sexo.cod_sexo
      where evento.validado = true
      ) as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    numero_agricultores = []
    for n in cursor.fetchall():
      numero_agricultores.append(n[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from(select * from evento_sist_prod_afectado
      join evento on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join especie_forestal_sembrada on especie_forestal_sembrada.cod_especie_forestal_sembrada = evento_sist_prod_afectado.cod_especie_forestal_fk
      join especie_forestal_afectada on especie_forestal_afectada.cod_esp_forestal_afectada = especie_forestal_sembrada.cod_especie_forestal_afec_fk
      where sistema_productivo_afectado.sistema_productivo_afectado = 'Explotación Forestal' and evento.validado = true) as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    ha_afectadas_especie = []
    for h in cursor.fetchall():
      ha_afectadas_especie.append(h[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select *
      from evento
      join evento_productos_agropecuario on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join productor_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
      join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
      join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join especie_forestal_sembrada on especie_forestal_sembrada.cod_especie_forestal_sembrada = evento_sist_prod_afectado.cod_especie_forestal_fk
      join costos_directos on especie_forestal_sembrada.cod_especie_forestal_sembrada = costos_directos.cod_especie_forestal_fk
      join actividad on costos_directos.cod_actividad_fk = actividad.cod_actividad
      where evento.validado = true) as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    costos_directos = []
    for c in cursor.fetchall():
      costos_directos.append(c[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,subconsulta2.*,municipios.nom_municipio, departamentos.nombre_dpto from (select *
      from productor_agropecuario
      join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
      join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join evento_productos_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
      join evento on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join especie_forestal_sembrada on especie_forestal_sembrada.cod_especie_forestal_sembrada = evento_sist_prod_afectado.cod_especie_forestal_fk
      join fase_productiva on especie_forestal_sembrada.cod_fase_productiva_fk = fase_productiva.cod_fase_productiva
      join especie_forestal_afectada on especie_forestal_sembrada.cod_especie_forestal_afec_fk = especie_forestal_afectada.cod_esp_forestal_afectada
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      where evento.validado=true) as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk
      join (select infraestructura_forestal.cod_especie_forestal_sembrada_fk, (case 
      when infraestructura_forestal.cod_tipo_infraestrucrtura_fk=1 then infraestructura_forestal.vlr_pesos_afectacion
      when infraestructura_forestal.cod_tipo_infraestrucrtura_fk=2 then infraestructura_forestal.valor_pesos_afectacion 
      when infraestructura_forestal.cod_tipo_infraestrucrtura_fk=3 then infraestructura_forestal.vlr_pesos_afectacion_pla
      when infraestructura_forestal.cod_tipo_infraestrucrtura_fk=4 then infraestructura_forestal.vlr_pesos_afectacion_maq
      end) valor_infraestructura_afectada, tipo_infraestructura.* from infraestructura_forestal
      join tipo_infraestructura on tipo_infraestructura.cod_tipo_infraestructura = infraestructura_forestal.cod_tipo_infraestrucrtura_fk
      ) as subconsulta2 on subconsulta.cod_especie_forestal_sembrada = subconsulta2.cod_especie_forestal_sembrada_fk) AS row
    """)

    cursor.execute(sql)
    infraestructura = []
    for i in cursor.fetchall():
      infraestructura.append(i[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from evento
      join evento_productos_agropecuario on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join productor_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
      join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
      join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join especie_forestal_sembrada on especie_forestal_sembrada.cod_especie_forestal_sembrada = evento_sist_prod_afectado.cod_especie_forestal_fk
      join costos_fijos_indirectos on especie_forestal_sembrada.cod_especie_forestal_sembrada = costos_fijos_indirectos.cod_especie_forestal_fk
      join rubros on rubros.cod_rubros = costos_fijos_indirectos.cod_rubro_fk
      where evento.validado=true) as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    costos_indirectos = []
    for c in cursor.fetchall():
      costos_indirectos.append(c[0])
    
    obj= {
      'forestal': {
        'general': general,
        'indicadores': indicadores,
        'condicion_juridica': condicion_juridica,
        'sexo': sexo,
        'pertenencia_etnica': pertenencia_etnica,
        'numero_agricultores': numero_agricultores,
        'ha_afectadas_especie': ha_afectadas_especie,
        'costos_directos': costos_directos,
        'infraestructura': infraestructura,
        'costos_indirectos': costos_indirectos
      }
    }

  except CustomException as e:
    print("ERROR (user/database_manager/get_forestal_reports):", e.to_dict()['error'])
    return e, 500
  except Exception as e:
    print("ERROR (user/database_manager/get_forestal_reports):", e)
    return CustomException('Ocurrio un error al obtener los datos de los reportes del sistema forestal', str(e)), 500
  else:
    return obj, 200
  finally:
    if cursor:
      if not cursor.closed:
        cursor.close()


# Gets the data of the reports for pesq system
def get_pesq_reports(connection):
  try:
    cursor = connection.cursor()
    obj = {}

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from evento
      join evento_productos_agropecuario on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join productor_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
      join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
      join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join novedad_pesquera on novedad_pesquera.cod_novedad_pesq = evento_sist_prod_afectado.cod_novedad_pesquera_fk
      left join embarcacion on embarcacion.cod_novedad_pesquera_fk = novedad_pesquera.cod_novedad_pesq
      where evento.validado = true) as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    general = []
    for g in cursor.fetchall():
      general.append(g[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from productor_agropecuario
      join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
      join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join evento_productos_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
      join evento on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join novedad_pesquera on novedad_pesquera.cod_novedad_pesq = evento_sist_prod_afectado.cod_novedad_pesquera_fk
      where evento.validado = true) as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    condicion_juridica = []
    for c in cursor.fetchall():
      condicion_juridica.append(c[0]) 

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from productor_agropecuario
      join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join sexo on productor_agropecuario.cod_sexo_fk = sexo.cod_sexo
      join evento_productos_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
      join evento on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join novedad_pesquera on novedad_pesquera.cod_novedad_pesq = evento_sist_prod_afectado.cod_novedad_pesquera_fk
      where evento.validado = true) as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    sexo = []
    for s in cursor.fetchall():
      sexo.append(s[0]) 

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (
      select * from evento_sist_prod_afectado
      join evento on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join novedad_pesquera on novedad_pesquera.cod_novedad_pesq = evento_sist_prod_afectado.cod_novedad_pesquera_fk
      join evento_productos_agropecuario on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join productor_agropecuario on productor_agropecuario.cod_productor_agropecuario = evento_productos_agropecuario.cod_producto_agro
      join tipo_productor on tipo_productor.cod_tipo_productor = productor_agropecuario.cod_tipo_productor_fk
      join grupo_etnico on grupo_etnico.cod_grupo_etnico = productor_agropecuario.cod_grupo_etnico_fk
      where evento.validado = true) as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    pertenencia_etnica = []
    for p in cursor.fetchall():
      pertenencia_etnica.append(p[0]) 

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from evento_sist_prod_afectado
      join evento on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join evento_productos_agropecuario on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join productor_agropecuario on productor_agropecuario.cod_productor_agropecuario = evento_productos_agropecuario.cod_producto_agro
      join tipo_productor on tipo_productor.cod_tipo_productor = productor_agropecuario.cod_tipo_productor_fk
      join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join novedad_pesquera on novedad_pesquera.cod_novedad_pesq = evento_sist_prod_afectado.cod_novedad_pesquera_fk
      where evento.validado = true) as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    numero_agricultores = []
    for n in cursor.fetchall():
      numero_agricultores.append(n[0]) 

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (
      select * from productor_agropecuario
      join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
      join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join evento_productos_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
      join evento on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join novedad_pesquera on novedad_pesquera.cod_novedad_pesq = evento_sist_prod_afectado.cod_novedad_pesquera_fk
      join indicador_valor on evento.cod_evento = indicador_valor.cod_evento_fk
      join indicador on indicador_valor.cod_indicador_fk = indicador.cod_indicador
      where evento.validado = true) as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    indicadores = []
    for i in cursor.fetchall():
      indicadores.append(i[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from evento
      join evento_productos_agropecuario on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join productor_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
      join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
      join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join novedad_pesquera on novedad_pesquera.cod_novedad_pesq = evento_sist_prod_afectado.cod_novedad_pesquera_fk
      join infraestructura_pesquera on infraestructura_pesquera.cod_novedad_pesquera_fk = novedad_pesquera.cod_novedad_pesq
      join tipo_activo on tipo_activo.cod_tipo_activo  = infraestructura_pesquera.cod_tipo_activo_fk
      join embarcacion on embarcacion.cod_novedad_pesquera_fk = novedad_pesquera.cod_novedad_pesq
      join tipo_embarcacion on tipo_embarcacion.cod_tipo_embarcacion = embarcacion.cod_tipo_embarcacion_fk
      where evento.validado = true) as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    novedad_pesquera = []
    for n in cursor.fetchall():
      novedad_pesquera.append(n[0])

    obj= {
      'pesquero': {
        'general': general,
        'indicadores': indicadores,
        'condicion_juridica': condicion_juridica,
        'sexo': sexo,
        'pertenencia_etnica': pertenencia_etnica,
        'numero_agricultores': numero_agricultores,
        'indicadores': indicadores,
        'novedad_pesquera': novedad_pesquera
      }
    }
  except CustomException as e:
    print("ERROR (user/database_manager/get_pesq_reports):", e.to_dict()['error'])
    return e, 500
  except Exception as e:
    print("ERROR (user/database_manager/get_pesq_reports):", e)
    return CustomException('Ocurrio un error al obtener los datos de los reportes del sistema pesquero', str(e)), 500
  else:
    return obj, 200
  finally:
    if cursor:
      if not cursor.closed:
        cursor.close()


# Gets the data of the reports for apiarian system
def get_apiarian_reports(connection):
  try:
    cursor = connection.cursor()
    obj = {}

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from evento
      join evento_productos_agropecuario on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join productor_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
      join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
      join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join novedad_pecuaria on novedad_pecuaria.cod_novedad_peq = evento_sist_prod_afectado.cod_novedad_pecuaria_apicola_fk
      where evento.validado = true and sistema_productivo_afectado.sistema_productivo_afectado='Explotación Apícola') as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    general = []
    for g in cursor.fetchall():
      general.append(g[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from productor_agropecuario
      join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
      join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join evento_productos_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
      join evento on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join novedad_pecuaria on novedad_pecuaria.cod_novedad_peq = evento_sist_prod_afectado.cod_novedad_pecuaria_apicola_fk
      where evento.validado = true and sistema_productivo_afectado.sistema_productivo_afectado='Explotación Apícola') as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    condicion_juridica = []
    for c in cursor.fetchall():
      condicion_juridica.append(c[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from productor_agropecuario
      join tipo_productor on productor_agropecuario.cod_tipo_productor_fk = tipo_productor.cod_tipo_productor
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join sexo on productor_agropecuario.cod_sexo_fk = sexo.cod_sexo
      join evento_productos_agropecuario on productor_agropecuario.cod_productor_agropecuario  = evento_productos_agropecuario.cod_producto_agro
      join evento on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join evento_sist_prod_afectado on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join novedad_pecuaria on novedad_pecuaria.cod_novedad_peq = evento_sist_prod_afectado.cod_novedad_pecuaria_apicola_fk
      where evento.validado = true and sistema_productivo_afectado.sistema_productivo_afectado='Explotación Apícola') as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    sexo = []
    for s in cursor.fetchall():
      sexo.append(s[0])

    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (
      select * from evento_sist_prod_afectado
      join evento on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join evento_productos_agropecuario on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join productor_agropecuario on productor_agropecuario.cod_productor_agropecuario = evento_productos_agropecuario.cod_producto_agro
      join tipo_productor on tipo_productor.cod_tipo_productor = productor_agropecuario.cod_tipo_productor_fk
      join grupo_etnico on grupo_etnico.cod_grupo_etnico = productor_agropecuario.cod_grupo_etnico_fk
      join novedad_pecuaria on novedad_pecuaria.cod_novedad_peq = evento_sist_prod_afectado.cod_novedad_pecuaria_apicola_fk
      where evento.validado = true and sistema_productivo_afectado.sistema_productivo_afectado='Explotación Apícola') as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    pertenencia_etnica = []
    for p in cursor.fetchall():
      pertenencia_etnica.append(p[0])

    
    sql = ("""
      select row_to_json(row) FROM (
      select subconsulta.*,municipios.nom_municipio, departamentos.nombre_dpto from (select * from evento_sist_prod_afectado
      join evento on evento.cod_evento = evento_sist_prod_afectado.cod_evento_fk
      join tipo_evento on tipo_evento.cod_tip_evento = evento.cod_tipo_evento_fk
      join sistema_productivo_afectado on evento_sist_prod_afectado.cod_sist_prod_afect_fk =  sistema_productivo_afectado.cod_sis_prod_afec
      join evento_productos_agropecuario on evento_productos_agropecuario.cod_evento_fk = evento.cod_evento
      join productor_agropecuario on productor_agropecuario.cod_productor_agropecuario = evento_productos_agropecuario.cod_producto_agro
      join tipo_productor on tipo_productor.cod_tipo_productor = productor_agropecuario.cod_tipo_productor_fk
      join condicion_juridica on productor_agropecuario.cod_condicion_juridica_fk = condicion_juridica.cod_condicion_juridica
      join tipo_documento2 on productor_agropecuario.cod_tipo_documento_fk = tipo_documento2.cod_tipo_documento
      join novedad_pecuaria on novedad_pecuaria.cod_novedad_peq = evento_sist_prod_afectado.cod_novedad_pecuaria_apicola_fk
      where evento.validado = true and sistema_productivo_afectado.sistema_productivo_afectado='Explotación Apícola') as subconsulta
      join municipios on municipios.cod_municipios = subconsulta.cod_municipio_fk
      join departamentos on departamentos.cod_dpto = municipios.cod_dpto_fk) AS row
    """)

    cursor.execute(sql)
    numero_agricultores = []
    for n in cursor.fetchall():
      numero_agricultores.append(n[0])

    obj = {
      'apicola': {
        'general': general,
        'condicion_juridica': condicion_juridica,
        'sexo': sexo,
        'pertenencia_etnica': pertenencia_etnica,
        'numero_agricultores': numero_agricultores
      }
    }
      
  except CustomException as e:
    print("ERROR (user/database_manager/get_apiarian_reports):", e.to_dict()['error'])
    return e, 500
  except Exception as e:
    print("ERROR (user/database_manager/get_apiarian_reports):", e)
    return CustomException('Ocurrio un error al obtener los datos de los reportes del sistema apícola', str(e)), 500
  else:
    return obj, 200
  finally:
    if cursor:
      if not cursor.closed:
        cursor.close()