import jwt

from app.exceptions import CustomException
from app.helpers import raise_exception



# Get the events types
def get_events_type(connection):
  try:
    cursor = connection.cursor()
    sql = ("""
      SELECT * FROM Tipo_evento;
    """)

    cursor.execute(sql)
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
      results.append(dict(zip(columns, row)))

  except CustomException as e:
    print('ERROR (visor/database_manager/get_events_type): ', e.to_dict['error'])
    return e, 500
  except Exception as e:
    print('ERROR (visor/database_manager/get_events_type): ', e)
    return CustomException('Ocurrio un error al obtener los tipos de eventos', str(e)), 500
  else:
    return results, 200


# Get the towns per event
def get_town_events(connection):
  try:
    cursor = connection.cursor()

    #Those towns that has the same name are concated with the department name
    sql = ("""
      SELECT m.cod_municipios, CASE WHEN nom_municipio IN 
      (SELECT nom_municipio FROM Municipios WHERE cod_municipios NOT IN(m.cod_municipios)) 
      THEN CONCAT(nom_municipio, ' / ', d.nombre_dpto) 
      ELSE nom_municipio END 
      FROM Evento e JOIN Municipios m ON e.cod_municipio_fk = m.cod_municipios 
        JOIN Departamentos d ON m.cod_dpto_FK = d.cod_dpto
        JOIN Evento_sist_prod_afectado ON cod_evento_fk = cod_evento
      WHERE e.validado = true
        GROUP BY cod_municipios, nombre_dpto;
    """)
    cursor.execute(sql)
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
      results.append(dict(zip(columns, row)))
  except CustomException as e:
    print('ERROR (visor/database_manager/get_town_events): ', e.to_dict['error'])
    return e, 500
  except Exception as e:
    print('ERROR (visor/database_manager/get_town_events): ', e)
    return CustomException('Ocurrio un error al obtener los municipios de los eventos', str(e)), 500
  else:
    return results, 200


# Get the departments per event
def get_dpto_events(connection):
  try:
    cursor = connection.cursor()

    sql = ("""
       SELECT cod_dpto, nombre_dpto FROM Evento e JOIN Municipios m ON e.cod_municipio_fk = m.cod_municipios 
       JOIN Departamentos d ON m.cod_dpto_fk = d.cod_dpto 
       WHERE e.validado = true
       GROUP BY cod_dpto;
    """)

    cursor.execute(sql)
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
      results.append(dict(zip(columns, row)))
  
  except CustomException as e:
    print('ERROR (visor/database_manager/get_dpto_events): ', e.to_dict['error'])
    return e, 500
  except Exception as e:
    print('ERROR (visor/database_manager/get_dpto_events): ', e)
    return CustomException('Ocurrio un error al obtner los departmentos', str(e)), 500
  else:
    return results, 200
  finally:
    if cursor:
      if not cursor.closed:
        cursor.close()


# Get the types of productive system
def get_exp_types(connection):
  try:
    cursor = connection.cursor()

    sql = ("""
      SELECT * FROM Sistema_productivo_afectado
    """)

    cursor.execute(sql)
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
      results.append(dict(zip(columns, row)))

  except CustomException as e:
    print('ERROR (visor/database_manager/get_exp_types): ', e.to_dict['error'])
    return e, 500
  except Exception as e:
    print('ERROR (visor/database_manager/get_exp_types): ', e)
    return CustomException('Ocurrio un error al obtener los tipos de explotaciones', str(e)), 500
  else:
    return results, 200
  finally: 
    if cursor:
      if not cursor.closed:
        cursor.close()


# Get the first date of all events
def first_date(connection):
  try:
    cursor = connection.cursor()
    
    sql = (""" SELECT fecha_registro_evento::TEXT FROM evento ORDER BY fecha_registro_evento ASC LIMIT 1;""")

    cursor.execute(sql)
    date = cursor.fetchone()[0]
  except CustomException as e:
    print('ERROR (visor/database_manager/first_date): ', e.to_dict['error'])
    return e, 500
  except Exception as e:
    print('ERROR (visor/database_manager/first_date): ', e)
    return CustomException('Ocurrio un error al obtener la fecha del primer evento', str(e)), 500
  else:
    return date, 200
  finally:
    if cursor:
      if not cursor.closed:
        cursor.close()


# Filter the events for the visor
def filtered_events(connection, obj):
  try:
    cursor = connection.cursor()

    params = []
    where = ''

    prod_sis = obj['prodSis'] if 'prodSis' in obj and obj['prodSis'] != '' else None
    if prod_sis:
      values = ''
      for i in range(len(prod_sis)):
        values += (prod_sis[i] + ', ') if i != len(prod_sis) - 1 else prod_sis[i]
      param = 'es.cod_sist_prod_afect_FK IN (' + values + ')'
      params.append(param)

    tip_ev = obj['tipoEvento'] if 'tipoEvento' in obj and obj['tipoEvento'] != '' else None
    if tip_ev:
      values = '' 
      for i in range(len(tip_ev)):
        values += (tip_ev[i] + ', ') if i != len(tip_ev) - 1 else tip_ev[i]
      param = 'a.cod_tipo_evento_fk IN (' + values + ')'
      params.append(param)

    ini = obj['fechaInicial'] if 'fechaInicial' in obj and obj['fechaInicial'] != '' else None
    fin = obj['fechaFinal'] if 'fechaFinal' in obj and obj['fechaFinal'] != '' else None
    

    if len(params) > 0:
      for param in params:
        where += ' AND ' + param 


    sql = ("""
      SELECT *
      FROM crosstab('	   
	   select subconsulta.*,
	   evento_indicador.siglas,
	   evento_indicador.valor
	   from(SELECT
       a.cod_evento,
	   a.coord_x::TEXT,
       a.coord_y::TEXT,
	   CASE WHEN rutas.ruta IS NOT NULL THEN true ELSE false END AS ruta,
       TO_CHAR(a.fecha_registro_evento, ''YYYY-MM-DD'') AS fecha_registro_evento,
	   d.nombre_dpto,
	   m.nom_municipio,
     tp.cod_tip_evento,
	   tp.tipo_evento,
	   sum(coalesce(Especie_forestal_sembrada.area_afectada_Ha,0))::int AS forestal_ha_afectada,
	   sum(coalesce(Cultivos_afectados.cantidad_semilla_utilizo_siembra_ha,0))::int AS agricola_cantidad_semilla_siembra,
	   sum(coalesce(n_pecuaria.num_animales_hembra_muertos,0) + coalesce(n_pecuaria.num_animales_macho_muertos,0))::Int AS pecuario_animales_muertos,
       sum(coalesce(n_apicola.num_colmenas_afectadas,0))::int AS colmenas_afectadas,
	   sum(coalesce(n_pesquera.redes_afectadas,0))::int as redes_afectadas
	   FROM evento a
	   JOIN Municipios m ON (a.cod_municipio_FK = m.cod_municipios)
       JOIN Departamentos d ON(m.cod_dpto_FK = d.cod_dpto)
	   JOIN Tipo_evento tp ON cod_tip_evento = a.cod_tipo_evento_FK
	   LEFT JOIN (
         SELECT Evento_seguimiento_adju.ruta, Evento_seguimiento.cod_evento_fk FROM Evento_seguimiento_adju JOIN Evento_seguimiento 
         ON Evento_seguimiento_adju.cod_evento_seguimiento_fk = Evento_seguimiento.cod_evento_seguimiento
		 group by Evento_seguimiento_adju.ruta, Evento_seguimiento.cod_evento_fk
       ) AS rutas ON rutas.cod_evento_fk = a.cod_evento
	   JOIN Evento_sist_prod_afectado es ON (es.cod_evento_FK = a.cod_evento)
	   LEFT JOIN especie_forestal_sembrada ON especie_forestal_sembrada.cod_especie_forestal_sembrada = es.cod_especie_forestal_fk
	   LEFT JOIN cultivos_afectados ON cultivos_afectados.cod_cultivo = es.cod_cultivo_afectado_fk
	   LEFT JOIN novedad_pecuaria AS n_pecuaria ON n_pecuaria.cod_novedad_peq = es.cod_novedad_pecuaria_fk
	   LEFT JOIN novedad_pecuaria AS n_apicola ON n_apicola.cod_novedad_peq = es.cod_novedad_pecuaria_apicola_fk
	   LEFT JOIN(
         SELECT subconsulta.* FROM (SELECT Novedad_pesquera.cod_novedad_pesq, 
         Novedad_pesquera.num_redes AS redes_afectadas
         FROM Novedad_pesquera
         JOIN infraestructura_pesquera ON infraestructura_pesquera.cod_novedad_pesquera_fk = novedad_pesquera.cod_novedad_pesq
         GROUP BY cod_novedad_pesq
         ORDER BY cod_novedad_pesq DESC) AS subconsulta
       ) AS n_pesquera ON n_pesquera.cod_novedad_pesq = es.cod_novedad_pesquera_FK
       WHERE (fecha_registro_evento BETWEEN DATE('%s') AND DATE('%s')) AND a.validado = true 
      """
      +
      where
      +
      """
	   group by a.cod_evento,
	   a.coord_x::TEXT,
       a.coord_y::TEXT,
	   rutas.ruta,
       a.fecha_registro_evento,
	   d.nombre_dpto,
	   m.nom_municipio,
     tp.cod_tip_evento,
	   tp.tipo_evento
	   order by a.cod_evento) as subconsulta
	   left join (select a.cod_indicador_valor, case when a.cod_indicador_fk = b.cod_indicador then a.valor::bigint else null end valor,
a.cod_evento_fk, b.siglas
from indicador_valor a
join indicador b on b.cod_indicador = a.cod_indicador_fk
JOIN evento ev ON a.cod_evento_FK = ev.cod_evento AND ev.validado = true) 
	   as evento_indicador on
	   evento_indicador.cod_evento_fk = subconsulta.cod_evento
	   order by 1,16','select siglas from indicador order by siglas')
as prueba(
	   cod_evento int,
	   coord_x text,
       coord_y text,
	   ruta boolean,
       fecha_registro_evento text,
	   nombre_dpto text,
	   nom_municipio text,
     cod_tip_evento int,
	   tipo_evento text,
	   forestal_ha_afectada BIGINT,
	   agricola_cantidad_semilla_siembra BIGINT,
	   pecuario_animales_muertos int,
       colmenas_afectadas int,
	   redes_afectadas BIGINT,
	   ind_AMmpeq BIGINT,
		ind_CFPmpeq BIGINT,
		ind_CPAmf BIGINT,
		ind_CPmf BIGINT,
		ind_CTDma BIGINT,
		ind_CTDmf BIGINT,
		ind_CTIma BIGINT,
		ind_CTImf BIGINT,
		ind_CTma BIGINT,
		ind_CTmpeq BIGINT,
		ind_CVPmpeq BIGINT,
		ind_DImpesq BIGINT,
		ind_IAPmpesq BIGINT,
		ind_IPFmpesq BIGINT,
		ind_PEKGAMmpeq BIGINT,
		ind_PEma BIGINT,
		ind_PEmf BIGINT,
		ind_PPImpeq BIGINT,
		ind_PPmpeq BIGINT,
		ind_PPRDCma BIGINT,
		ind_PPRmf BIGINT,
		ind_VAMmpeq BIGINT,
		ind_VEDma BIGINT,
		ind_VEDmf BIGINT,
		ind_VPECma BIGINT,
		ind_VPEPmf BIGINT
    )
	  
    """)


    val = (ini, fin)
    cursor.execute(sql, val)

    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
      results.append(dict(zip(columns, row)))
    

  except CustomException as e:
    print('ERROR (visor/database_manager/filtered_events): ', e.to_dict['error'])
    return e, 500
  except Exception as e:
    print('ERROR (visor/database_manager/filtered_events): ', e)
    return CustomException('Ocurrio un error al filtrar los eventos', str(e)), 500
  else:
    return results, 200
  finally:
    if cursor:
      if not cursor.closed:
        cursor.close()


# This function is to build the where clause of the queries that filter the information by UER
def build_where(obj, unit=False):
  try:
    where = ''
    params = []

    # unit Means that the mun or the dpto is only one parameter and not more 
    if unit:
      if 'cod_mun' in obj:
        param = 'lg.cod_municipios = ' + obj['cod_mun']
        params.append(param)
      else:
        param = 'd.cod_dpto = ' + obj['cod_dpto']
        params.append(param)
    else:
      if 'cod_mun' in obj:
        mun = obj['cod_mun'] if  obj['cod_mun'] != '' else None
        if mun:
          values = ''
          for i in range(len(mun)):
            values += (mun[i] + ', ') if i != len(mun) -1 else mun[i]
          param = 'lg.cod_municipios IN (' + values + ')'
          params.append(param)
      else:
        dpto = obj['cod_dpto'] if 'cod_dpto' in obj and obj['cod_dpto'] != '' else None
        if dpto:
          values = ''
          for i in range(len(dpto)):
            values += (dpto[i] + ', ') if i != len(dpto) -1 else dpto[i]
          param = 'd.cod_dpto IN (' + values + ')'
          params.append(param)
 
    prod_sis = obj['prodSis'] if 'prodSis' in obj and obj['prodSis'] != '' else None
    if prod_sis:
      values = ''
      for i in range(len(prod_sis)):
        values += (prod_sis[i] + ', ') if i != len(prod_sis) - 1 else prod_sis[i]
      param = 'es.cod_sist_prod_afect_FK IN (' + values + ')'
      params.append(param)
    
    tip_ev = obj['tipoEvento'] if 'tipoEvento' in obj and obj['tipoEvento'] != '' else None
    if tip_ev:
      values = ''
      for i in range(len(tip_ev)):
        values += (tip_ev[i] + ', ') if i != len(tip_ev) - 1 else tip_ev[i]
      param = 'e.cod_tipo_evento_fk IN (' + values + ')'
      params.append(param)
    
    ini = obj['fechaInicial'] if 'fechaInicial' in obj and obj['fechaInicial'] != '' else None
    fin = obj['fechaFinal'] if 'fechaFinal' in obj and obj['fechaFinal'] != '' else None

    if len(params) > 0:
      for param in params:
        where += ' AND ' + param

  except CustomException as e:
    print('ERROR (visor/database_manager/build_where): ', e.to_dict['error'])
    return e, 500
  except Exception as e:
    print('ERROR (visor/database_manager/build_where): ', e)
    return CustomException('Ocurrio un error con los parametros del filtro', str(e)), 500
  else:
    return where, ini, fin, 200


# Get geojson with attributes and geom consulted by town or department
def filter_by_town(connection, obj):
  try:
    cursor = connection.cursor()

    where_clause = build_where(obj)
    if where_clause[3] != 200:
      raise_exception(where_clause[0].to_dict()['message'],  where_clause[0].to_dict()['error'])

    where = where_clause[0]
    ini = where_clause[1]
    fin = where_clause[2]
    

    group = ''
    ind = ''
    join_ind = ''
    if 'cod_mun' in obj:
      group = ' GROUP BY lg.nom_municipio, lg.cod_municipios, lg.geom, d.nombre_dpto, d.cod_dpto'
      select = 'lg.nom_municipio, lg.cod_municipios, d.nombre_dpto, d.cod_dpto'
      ind = 'lg.'
      join_ind = """
        JOIN (
          SELECT 
            cod_municipios,
            nombre_dpto,
            sum(forestal_ha_afectada)::BIGINT as forestal_ha_afectada,
            sum(agricola_cantidad_semilla_siembra)::BIGINT as agricola_cantidad_semilla_siembra,
            sum(pecuario_animales_muertos)::BIGINT as pecuario_animales_muertos,
            sum(colmenas_afectadas)::BIGINT as colmenas_afectadas,
            sum(redes_afectadas)::BIGINT as redes_afectadas,
            sum(ind_AMmpeq)::BIGINT as ind_AMmpeq,
            sum(ind_CFPmpeq)::BIGINT as ind_CFPmpeq,
            sum(ind_CPAmf)::BIGINT as ind_CPAmf,
            sum(ind_CPmf)::BIGINT as ind_CPmf,
            sum(ind_CTDma)::BIGINT as ind_CTDma,
            sum(ind_CTDmf)::BIGINT as ind_CTDmf,
            sum(ind_CTIma)::BIGINT as ind_CTIma,
            sum(ind_CTImf)::BIGINT as ind_CTImf,
            sum(ind_CTma)::BIGINT as ind_CTma,
            sum(ind_CTmpeq)::BIGINT as ind_CTmpeq,
            sum(ind_CVPmpeq)::BIGINT as ind_CVPmpeq,
            sum(ind_DImpesq)::BIGINT as ind_DImpesq,
            sum(ind_IAPmpesq)::BIGINT as ind_IAPmpesq,
            sum(ind_IPFmpesq)::BIGINT as ind_IPFmpesq,
            sum(ind_PEKGAMmpeq)::BIGINT as ind_PEKGAMmpeq,
            AVG(ind_PEma)::BIGINT as ind_PEma,
            AVG(ind_PEmf)::BIGINT as ind_PEmf,
            AVG(ind_PPImpeq)::BIGINT as ind_PPImpeq,
            AVG(ind_PPmpeq)::BIGINT as ind_PPmpeq,
            AVG(ind_PPRDCma)::BIGINT as ind_PPRDCma,
            AVG(ind_PPRmf)::BIGINT as ind_PPRmf,
            sum(ind_VAMmpeq)::BIGINT as ind_VAMmpeq,
            sum(ind_VEDma)::BIGINT as ind_VEDma,
            sum(ind_VEDmf)::BIGINT as ind_VEDmf,
            sum(ind_VPECma)::BIGINT as ind_VPECma,
            sum(ind_VPEPmf)::BIGINT as ind_VPEPmf
              FROM crosstab('	   
            select subconsulta.*,
            evento_indicador.siglas,
            evento_indicador.valor
            from(SELECT
              a.cod_evento,
            a.coord_x::TEXT,
              a.coord_y::TEXT, 
              TO_CHAR(a.fecha_registro_evento, ''YYYY-MM-DD'') AS fecha_registro_evento,
            d.nombre_dpto,
            m.cod_municipios,			
            sum(coalesce(Especie_forestal_sembrada.area_afectada_Ha,0))::int AS forestal_ha_afectada,
            sum(coalesce(Cultivos_afectados.cantidad_semilla_utilizo_siembra_ha,0))::int AS agricola_cantidad_semilla_siembra,
            sum(coalesce(n_pecuaria.num_animales_hembra_muertos,0) + coalesce(n_pecuaria.num_animales_macho_muertos,0))::Int AS pecuario_animales_muertos,
              sum(coalesce(n_apicola.num_colmenas_afectadas,0))::int AS colmenas_afectadas,
            sum(coalesce(n_pesquera.redes_afectadas,0))::int as redes_afectadas
            FROM evento a
            JOIN Municipios m ON (a.cod_municipio_FK = m.cod_municipios)
              JOIN Departamentos d ON(m.cod_dpto_FK = d.cod_dpto)
            
            JOIN Evento_sist_prod_afectado es ON (es.cod_evento_FK = a.cod_evento)
            LEFT JOIN especie_forestal_sembrada ON especie_forestal_sembrada.cod_especie_forestal_sembrada = es.cod_especie_forestal_fk
            LEFT JOIN cultivos_afectados ON cultivos_afectados.cod_cultivo = es.cod_cultivo_afectado_fk
            LEFT JOIN novedad_pecuaria AS n_pecuaria ON n_pecuaria.cod_novedad_peq = es.cod_novedad_pecuaria_fk
            LEFT JOIN novedad_pecuaria AS n_apicola ON n_apicola.cod_novedad_peq = es.cod_novedad_pecuaria_apicola_fk
            LEFT JOIN(
                SELECT subconsulta.* FROM (SELECT Novedad_pesquera.cod_novedad_pesq, 
                SUM(Novedad_pesquera.num_redes) AS redes_afectadas
                FROM Novedad_pesquera
                JOIN infraestructura_pesquera ON infraestructura_pesquera.cod_novedad_pesquera_fk = novedad_pesquera.cod_novedad_pesq
                GROUP BY cod_novedad_pesq
                ORDER BY cod_novedad_pesq DESC) AS subconsulta
              ) AS n_pesquera ON n_pesquera.cod_novedad_pesq = es.cod_novedad_pesquera_FK
            WHERE a.validado = true
            group by a.cod_evento,
            a.coord_x::TEXT,
              a.coord_y::TEXT,
              a.fecha_registro_evento,
            d.nombre_dpto,
            m.cod_municipios
            order by a.cod_evento) as subconsulta
            left join (select a.cod_indicador_valor, case when a.cod_indicador_fk = b.cod_indicador then a.valor::bigint else null end valor,
        a.cod_evento_fk, b.siglas
        from indicador_valor a
        join indicador b on b.cod_indicador = a.cod_indicador_fk 
        JOIN evento ev ON ev.cod_evento = a.cod_evento_fk AND ev.validado=true) 
            as evento_indicador on
            evento_indicador.cod_evento_fk = subconsulta.cod_evento
            order by 1,13','select siglas from indicador order by siglas')
        as prueba(
            cod_evento int,
            coord_x text,
              coord_y text,
              fecha_registro_evento text,
            nombre_dpto text,
            cod_municipios int,
            forestal_ha_afectada float,
            agricola_cantidad_semilla_siembra float,
            pecuario_animales_muertos int,
              colmenas_afectadas int,
            redes_afectadas float,
            ind_AMmpeq float,
            ind_CFPmpeq float,
            ind_CPAmf float,
            ind_CPmf float,
            ind_CTDma float,
            ind_CTDmf float,
            ind_CTIma float,
            ind_CTImf float,
            ind_CTma float,
            ind_CTmpeq float,
            ind_CVPmpeq float,
            ind_DImpesq float,
            ind_IAPmpesq float,
            ind_IPFmpesq float,
            ind_PEKGAMmpeq float,
            ind_PEma float,
            ind_PEmf float,
            ind_PPImpeq float,
            ind_PPmpeq float,
            ind_PPRDCma float,
            ind_PPRmf float,
            ind_VAMmpeq float,
            ind_VEDma float,
            ind_VEDmf float,
            ind_VPECma float,
            ind_VPEPmf float
            ) 
          group by cod_municipios, nombre_dpto
        ) AS indicadores_municipio ON lg.cod_municipios = indicadores_municipio.cod_municipios
      """
    elif 'cod_dpto' in obj:
      group = ' GROUP BY d.nombre_dpto, d.cod_dpto, d.geom'
      select = 'd.nombre_dpto, d.cod_dpto'
      ind = 'd.'
      join_ind = """
        JOIN (SELECT 
          cod_dpto,
          sum(forestal_ha_afectada)::BIGINT as forestal_ha_afectada,
          sum(agricola_cantidad_semilla_siembra)::BIGINT as agricola_cantidad_semilla_siembra,
          sum(pecuario_animales_muertos)::BIGINT as pecuario_animales_muertos,
          sum(colmenas_afectadas) as colmenas_afectadas,
          sum(redes_afectadas)::BIGINT as redes_afectadas,
          sum(ind_AMmpeq)::BIGINT as ind_AMmpeq,
          sum(ind_CFPmpeq)::BIGINT as ind_CFPmpeq,
          sum(ind_CPAmf)::BIGINT as ind_CPAmf,
          sum(ind_CPmf)::BIGINT as ind_CPmf,
          sum(ind_CTDma)::BIGINT as ind_CTDma,
          sum(ind_CTDmf)::BIGINT as ind_CTDmf,
          sum(ind_CTIma)::BIGINT as ind_CTIma,
          sum(ind_CTImf)::BIGINT as ind_CTImf,
          sum(ind_CTma)::BIGINT as ind_CTma,
          sum(ind_CTmpeq)::BIGINT as ind_CTmpeq,
          sum(ind_CVPmpeq)::BIGINT as ind_CVPmpeq,
          sum(ind_DImpesq)::BIGINT as ind_DImpesq,
          sum(ind_IAPmpesq)::BIGINT as ind_IAPmpesq,
          sum(ind_IPFmpesq)::BIGINT as ind_IPFmpesq,
          sum(ind_PEKGAMmpeq)::BIGINT as ind_PEKGAMmpeq,
          AVG(ind_PEma)::BIGINT as ind_PEma,
          AVG(ind_PEmf)::BIGINT as ind_PEmf,
          AVG(ind_PPImpeq)::BIGINT as ind_PPImpeq,
          AVG(ind_PPmpeq)::BIGINT as ind_PPmpeq,
          AVG(ind_PPRDCma)::BIGINT as ind_PPRDCma,
          AVG(ind_PPRmf)::BIGINT as ind_PPRmf,
          sum(ind_VAMmpeq)::BIGINT as ind_VAMmpeq,
          sum(ind_VEDma)::BIGINT as ind_VEDma,
          sum(ind_VEDmf)::BIGINT as ind_VEDmf,
          sum(ind_VPECma)::BIGINT as ind_VPECma,
          sum(ind_VPEPmf)::BIGINT as ind_VPEPmf
            FROM crosstab('	   
          select subconsulta.*,
          evento_indicador.siglas,
          evento_indicador.valor
          from(SELECT
            a.cod_evento,
          a.coord_x::TEXT,
            a.coord_y::TEXT,
            TO_CHAR(a.fecha_registro_evento, ''YYYY-MM-DD'') AS fecha_registro_evento,
          d.cod_dpto,
          m.cod_municipios,			
          sum(coalesce(Especie_forestal_sembrada.area_afectada_Ha,0))::int AS forestal_ha_afectada,
          sum(coalesce(Cultivos_afectados.cantidad_semilla_utilizo_siembra_ha,0))::int AS agricola_cantidad_semilla_siembra,
          sum(coalesce(n_pecuaria.num_animales_hembra_muertos,0) + coalesce(n_pecuaria.num_animales_macho_muertos,0))::Int AS pecuario_animales_muertos,
            sum(coalesce(n_apicola.num_colmenas_afectadas,0))::int AS colmenas_afectadas,
          sum(coalesce(n_pesquera.redes_afectadas,0))::int as redes_afectadas
          FROM evento a
          JOIN Municipios m ON (a.cod_municipio_FK = m.cod_municipios)
            JOIN Departamentos d ON(m.cod_dpto_FK = d.cod_dpto)
          
          JOIN Evento_sist_prod_afectado es ON (es.cod_evento_FK = a.cod_evento)
          LEFT JOIN especie_forestal_sembrada ON especie_forestal_sembrada.cod_especie_forestal_sembrada = es.cod_especie_forestal_fk
          LEFT JOIN cultivos_afectados ON cultivos_afectados.cod_cultivo = es.cod_cultivo_afectado_fk
          LEFT JOIN novedad_pecuaria AS n_pecuaria ON n_pecuaria.cod_novedad_peq = es.cod_novedad_pecuaria_fk
          LEFT JOIN novedad_pecuaria AS n_apicola ON n_apicola.cod_novedad_peq = es.cod_novedad_pecuaria_apicola_fk
          LEFT JOIN(
              SELECT subconsulta.* FROM (SELECT Novedad_pesquera.cod_novedad_pesq, 
              SUM(Novedad_pesquera.num_redes) AS redes_afectadas
              FROM Novedad_pesquera
              JOIN infraestructura_pesquera ON infraestructura_pesquera.cod_novedad_pesquera_fk = novedad_pesquera.cod_novedad_pesq
              GROUP BY cod_novedad_pesq 
              ORDER BY cod_novedad_pesq DESC) AS subconsulta
            ) AS n_pesquera ON n_pesquera.cod_novedad_pesq = es.cod_novedad_pesquera_FK
          WHERE a.validado = true
          group by a.cod_evento,
          a.coord_x::TEXT,
            a.coord_y::TEXT,
            a.fecha_registro_evento,
          d.cod_dpto,
          m.cod_municipios
          order by a.cod_evento) as subconsulta
          left join (select a.cod_indicador_valor, case when a.cod_indicador_fk = b.cod_indicador then a.valor::bigint else null end valor,
      a.cod_evento_fk, b.siglas
      from indicador_valor a
      join indicador b on b.cod_indicador = a.cod_indicador_fk
      JOIN evento ev ON ev.cod_evento = a.cod_evento_fk AND ev.validado=true) 
          as evento_indicador on
          evento_indicador.cod_evento_fk = subconsulta.cod_evento
          order by 1,13','select siglas from indicador order by siglas')
      as prueba(
          cod_evento int,
          coord_x text,
            coord_y text,
            fecha_registro_evento text,
          cod_dpto int,
          cod_municipios int,
          forestal_ha_afectada float,
          agricola_cantidad_semilla_siembra float,
          pecuario_animales_muertos int,
            colmenas_afectadas int,
          redes_afectadas float,
          ind_AMmpeq float,
          ind_CFPmpeq float,
          ind_CPAmf float,
          ind_CPmf float,
          ind_CTDma float,
          ind_CTDmf float,
          ind_CTIma float,
          ind_CTImf float,
          ind_CTma float,
          ind_CTmpeq float,
          ind_CVPmpeq float,
          ind_DImpesq float,
          ind_IAPmpesq float,
          ind_IPFmpesq float,
          ind_PEKGAMmpeq float,
          ind_PEma float,
          ind_PEmf float,
          ind_PPImpeq float,
          ind_PPmpeq float,
          ind_PPRDCma float,
          ind_PPRmf float,
          ind_VAMmpeq float,
          ind_VEDma float,
          ind_VEDmf float,
          ind_VPECma float,
          ind_VPEPmf float
          ) 
        group by cod_dpto) AS indicadores_dpto ON  d.cod_dpto = indicadores_dpto.cod_dpto
      """

    
    sql = ("""
      SELECT row_to_json(fc) FROM ( 
      SELECT 'FeatureCollection' As type, array_to_json(array_agg(f)) As features FROM (
        SELECT 'Feature' As type , ST_AsGeoJSON("""+ind+"""geom)::json As geometry , row_to_json((
        SELECT l FROM (SELECT """+select+""",
        forestal_ha_afectada,
        agricola_cantidad_semilla_siembra,
        pecuario_animales_muertos,
        colmenas_afectadas,
        redes_afectadas,
        ind_AMmpeq,
        ind_CFPmpeq,
        ind_CPAmf,
        ind_CPmf,
        ind_CTDma,
        ind_CTDmf,
        ind_CTIma,
        ind_CTImf,
        ind_CTma,
        ind_CTmpeq,
        ind_CVPmpeq,
        ind_DImpesq,
        ind_IAPmpesq,
        ind_IPFmpesq,
        ind_PEKGAMmpeq,
        ind_PEma,
        ind_PEmf,
        ind_PPImpeq,
        ind_PPmpeq,
        ind_PPRDCma,
        ind_PPRmf,
        ind_VAMmpeq,
        ind_VEDma,
        ind_VEDmf,
        ind_VPECma,
        ind_VPEPmf) As l)) As properties 
        FROM municipios As lg 
        JOIN Evento e ON e.cod_municipio_fk = lg.cod_municipios
        JOIN tipo_evento b ON (b.cod_tip_evento = e.cod_tipo_evento_FK)
        JOIN Evento_sist_prod_afectado es ON (es.cod_evento_FK = e.cod_evento)
        JOIN Departamentos d ON(lg.cod_dpto_FK = d.cod_dpto)
        """
        + join_ind +
        """
        where ST_IsValid("""+ind+"""geom) AND (fecha_registro_evento BETWEEN DATE(%s) AND DATE(%s)) AND e.validado = true """ + where + group +
        """, forestal_ha_afectada,
        agricola_cantidad_semilla_siembra,
        pecuario_animales_muertos,
        colmenas_afectadas,
        redes_afectadas,
        ind_AMmpeq,
        ind_CFPmpeq,
        ind_CPAmf,
        ind_CPmf,
        ind_CTDma,
        ind_CTDmf,
        ind_CTIma,
        ind_CTImf,
        ind_CTma,
        ind_CTmpeq,
        ind_CVPmpeq,
        ind_DImpesq,
        ind_IAPmpesq,
        ind_IPFmpesq,
        ind_PEKGAMmpeq,
        ind_PEma,
        ind_PEmf,
        ind_PPImpeq,
        ind_PPmpeq,
        ind_PPRDCma,
        ind_PPRmf,
        ind_VAMmpeq,
        ind_VEDma,
        ind_VEDmf,
        ind_VPECma,
        ind_VPEPmf
      ) As f )  As fc;
      """
    )

    val = (ini, fin)
    cursor.execute(sql, val)  

    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
      results.append(dict(zip(columns, row)))
    
    
  except CustomException as e:
    print('ERROR (visor/database_manager/filter_by_town): ', e.to_dict['error'])
    return e, 500
  except Exception as e:
    print('ERROR (visor/database_manager/filter_by_town): ', e)
    return CustomException('Ocurrio un error al filtrar por UER', str(e)), 500
  else:
    return results, 200
  finally:
    if cursor:
      if not cursor.closed:
        cursor.close()


# This function is used to get the data for the graphs on the visor modal
# it gets the consolidated information per departament or town
def get_graphs_data(connection, obj):
  try:

    where_clause = build_where(obj, unit=True)
    if where_clause[3] != 200:
      raise_exception(where_clause[0].to_dict()['message'],  where_clause[0].to_dict()['error'])

    where = where_clause[0]
    ini = where_clause[1]
    fin = where_clause[2]

    res_general = general_graph(connection, ini, fin, where)
    if res_general[1] != 200:
      raise_exception(res_general[0].to_dict()['message'],  res_general[0].to_dict()['error'])

    res_forestal = forestal_graphs(connection, ini, fin, where)
    if res_forestal[1] != 200:
      raise_exception(res_forestal[0].to_dict()['message'],  res_forestal[0].to_dict()['error'])

    res_agro = agro_graphs(connection, ini, fin, where)
    if res_agro[1] != 200:
      raise_exception(res_agro[0].to_dict()['message'],  res_agro[0].to_dict()['error'])

    res_peq = peq_graphs(connection, ini, fin, where)
    if res_peq[1] != 200:
      raise_exception(res_peq[0].to_dict()['message'],  res_peq[0].to_dict()['error'])

    res_pesq = pesq_graphs(connection, ini, fin, where)
    if res_pesq[1] != 200:
      raise_exception(res_pesq[0].to_dict()['message'],  res_pesq[0].to_dict()['error'])

    res = {
      'general': res_general[0],
      'forestal': res_forestal[0],
      'agro': res_agro[0],
      'peq': res_peq[0],
      'pesq': res_pesq[0]
    }


  except CustomException as e:
    print('ERROR (visor/database_manager/get_graphs_data): ', e.to_dict['error'])
    return e, 500
  except Exception as e:
    print('ERROR (visor/database_manager/get_graphs_data): ', e)
    return CustomException('Ocurrio un error al obtener los datos de las graficas', str(e))
  else:
    return res, 200


# This function gets the information for the general graphs on the visor
# Number of events per event type
def general_graph(connection, ini, fin, where):
  try:
    cursor = connection.cursor()

    sql = ("""
      SELECT COUNT(cod_evento) AS cantidad_eventos, tipo_evento FROM Evento e
      JOIN Tipo_evento b ON cod_tipo_evento_FK = b.cod_tip_evento
      JOIN Municipios lg ON cod_municipio_FK = lg.cod_municipios
      JOIN Departamentos d ON lg.cod_dpto_FK = d.cod_dpto
      JOIN Evento_sist_prod_afectado es ON es.cod_evento_FK = e.cod_evento
      WHERE fecha_registro_evento BETWEEN DATE(%s) AND DATE(%s) """
      +where+
      """
      AND e.validado = true
      GROUP BY tipo_evento;
    """)

    val = (ini, fin)

    cursor.execute(sql, val)
    res = []
    columns = [column[0] for column in cursor.description]
    for row in cursor.fetchall():
      res.append(dict(zip(columns, row)))

  except CustomException as e:
    print('ERROR (visor/database_manager/general_graph): ', e.to_dict['error'])
    return e, 500
  except Exception as e:
    print('ERROR (visor/database_manager/general_graph): ', e)
    return CustomException('Ocurrio un error al obtener los datos generales de las graficas', str(e))
  else:
    return res, 200

  
# This function get specfically the data to the forestal graphs 
def forestal_graphs(connection, ini, fin, where):
  try:
    cursor = connection.cursor()

    res = {
      'esp_afectadas_tipo': [],
      'infra_valor': []
    }

    sql = ("""
      SELECT cod_esp_forestal_afectada, especie_forestal_afectada, COUNT(cod_esp_forestal_afectada) AS num_especie 
      FROM Especie_forestal_afectada JOIN Especie_forestal_sembrada ON cod_esp_forestal_afectada = cod_especie_forestal_afec_FK
      JOIN Evento_sist_prod_afectado es ON es.cod_especie_forestal_FK = cod_especie_forestal_sembrada
      JOIN Evento e ON cod_evento_FK = e.cod_evento
      JOIN Municipios lg ON cod_municipio_FK = lg.cod_municipios
      JOIN Departamentos d ON lg.cod_dpto_FK = d.cod_dpto
      JOIN Tipo_evento b ON cod_tipo_evento_FK = b.cod_tip_evento
      WHERE fecha_registro_evento BETWEEN DATE(%s) AND DATE(%s) """
      +where+
      """
      AND e.validado = true
      GROUP BY cod_esp_forestal_afectada;
    """)

    val = (ini, fin)

    cursor.execute(sql, val)

    columns = [column[0] for column in cursor.description]
    for row in cursor.fetchall():
      res['esp_afectadas_tipo'].append(dict(zip(columns, row)))

    sql = ("""
      SELECT cod_tipo_infraestructura, tipo_infraestructura, SUM(vlr_pesos_afectacion)::BIGINT AS valor_semilla, 
      SUM(valor_pesos_afectacion)::BIGINT AS valor_fert, SUM(vlr_pesos_afectacion_pla)::BIGINT AS valor_pla, 
      SUM(vlr_pesos_afectacion_maq)::BIGINT AS valor_maq
      FROM Infraestructura_forestal JOIN Especie_forestal_sembrada ON cod_especie_forestal_sembrada = cod_especie_forestal_sembrada_FK
      JOIN Tipo_infraestructura ON cod_tipo_infraestructura = cod_tipo_infraestrucrtura_fk
      JOIN Evento_sist_prod_afectado es ON es.cod_especie_forestal_FK = cod_especie_forestal_sembrada
      JOIN Evento e ON cod_evento_FK = e.cod_evento
      JOIN Municipios lg ON cod_municipio_FK = lg.cod_municipios
	    JOIN Departamentos d ON lg.cod_dpto_FK = d.cod_dpto 
      JOIN Tipo_evento b ON cod_tipo_evento_FK = b.cod_tip_evento
      WHERE fecha_registro_evento BETWEEN DATE(%s) AND DATE(%s)
      """
      +where+
      """
      AND e.validado = true
      GROUP BY cod_tipo_infraestructura ORDER BY cod_tipo_infraestructura;
    """)

    val = (ini, fin)

    cursor.execute(sql, val)
    print(sql, val)

    columns = [column[0] for column in cursor.description]
    for row in cursor.fetchall():
      res['infra_valor'].append(dict(zip(columns, row)))
      
  except CustomException as e:
    print("ERROR (visor/database_manager/forestal_graphs): ", e.to_dict()['error'])
    return e, 500
  except Exception as e:
    print("ERROR (visor/database_manager/forestal_graphs): ", e)
    return CustomException('Ocurrio un error al obtener los datos de las graficas del sistema forestal', str(e)), 500
  else:
    return res, 200
  finally:
    if cursor:
      if not cursor.closed:
        cursor.close()


# This function get specfically the data to the agro graphs 
def agro_graphs(connection, ini, fin, where):
  try:
    cursor = connection.cursor()

    res = {
      'semillas_por_cultivo': [],
      'inf_plaguicida': []
    }

    sql = ("""
      SELECT tipo_cultivo, COUNT(cod_tipo_cultivo) AS cantidad FROM Cultivos_afectados 
      JOIN Tipo_cultivo ON cod_tipo_cultivo = cod_nombre_FK 
      JOIN Evento_sist_prod_afectado es ON es.cod_cultivo_afectado_FK = cod_cultivo
      JOIN Evento e ON cod_evento_FK = e.cod_evento
      JOIN Municipios lg ON cod_municipio_FK = lg.cod_municipios
	    JOIN Departamentos d ON lg.cod_dpto_FK = d.cod_dpto 
      JOIN Tipo_evento b ON cod_tipo_evento_FK = b.cod_tip_evento
      WHERE fecha_registro_evento BETWEEN DATE(%s) AND DATE(%s) """ 
      +where+
      """
      AND e.validado = true
      GROUP BY cod_tipo_cultivo;
    """)

    val = (ini, fin)

    cursor.execute(sql, val)

    columns = [column[0] for column in cursor.description]
    for row in cursor.fetchall():
      res['semillas_por_cultivo'].append(dict(zip(columns, row)))

    
    sql = ("""
      SELECT tipo_plaguicida, presentacion, SUM(cantidad_plaguicidas_almac_afec_litros) AS litros,
      SUM(cantidad_plaguicidas_almac_afec_kg) AS kg, SUM(vlr_pesos_plaguicidas) AS valor FROM Infraestructura
      JOIN Tipo_plaguicida ON cod_tip_plaguicida = cod_tipo_plaguicida_FK
      JOIN Presentacion ON cod_presentacion = cod_presentacion_FK 
      JOIN Cultivo_Infraestructura ON cod_infraestructura_FK = cod_infraestructura
      JOIN Evento_sist_prod_afectado es ON cod_cultivo_FK = es.cod_cultivo_afectado_FK
      JOIN Evento e ON cod_evento_FK = e.cod_evento
      JOIN Municipios lg ON cod_municipio_FK = lg.cod_municipios
	    JOIN Departamentos d ON lg.cod_dpto_FK = d.cod_dpto 
      JOIN Tipo_evento b ON b.cod_tip_evento = cod_tipo_evento_FK
      WHERE fecha_registro_evento BETWEEN DATE(%s) AND DATE(%s) """
      +where+
      """
	    AND e.validado = true
      GROUP BY cod_tip_plaguicida, cod_presentacion;
    """)

    val = (ini, fin)

    cursor.execute(sql, val)

    columns = [column[0] for column in cursor.description]
    for row in cursor.fetchall():
      res['inf_plaguicida'].append(dict(zip(columns, row)))
  except CustomException as e:
    print("ERROR (visor/database_manager/agro_graphs): ", e.to_dict()['error'])
    return e, 500
  except Exception as e:
    print("ERROR (visor/database_manager/agro_graphs): ", e)
    return CustomException("Ocurrio un error al obtener los datos de las graficas del sistema agropecuario", str(e)), 500
  else:
    return res, 200
  finally:
    if cursor:
      if not cursor.closed:
        cursor.close()


# This function get specfically the data to the peq graphs 
def peq_graphs(connection, ini, fin, where):
  try:
    cursor = connection.cursor()

    res = {
      'animales_muertos_por_raza': [],
      'animales_muertos_por_fecha': []
    }

    sql = ("""
      SELECT nombre_raza, SUM(num_animales_hembra_muertos) AS hembras_muertas, 
      SUM(num_animales_macho_muertos) AS machos_muertos FROM Novedad_pecuaria
      JOIN Evento_sist_prod_afectado es ON es.cod_novedad_pecuaria_FK = cod_novedad_peq
      JOIN Evento e ON cod_evento_FK = e.cod_evento
      JOIN Municipios lg ON cod_municipio_FK = lg.cod_municipios
	    JOIN Departamentos d ON lg.cod_dpto_FK = d.cod_dpto
      JOIN Tipo_evento b ON b.cod_tip_evento = cod_tipo_evento_FK
      WHERE nombre_raza IS NOT NULL AND 
      fecha_registro_evento BETWEEN DATE(%s) AND DATE(%s)"""
      +where+
      """
	    AND e.validado = true
      GROUP BY nombre_raza;
    """)

    val = (ini, fin)

    cursor.execute(sql, val)

    columns = [column[0] for column in cursor.description]
    for row in cursor.fetchall():
      res['animales_muertos_por_raza'].append(dict(zip(columns, row)))

    sql = ("""
      SELECT mes, anio, animales_muertos FROM (
        SELECT 
          DATE(CONCAT(EXTRACT(YEAR FROM fecha_registro_evento), '-', 
			      CASE WHEN LENGTH(EXTRACT(MONTH FROM fecha_registro_evento)::TEXT) = 1
			      THEN
				      CONCAT('0', EXTRACT(MONTH FROM fecha_registro_evento)::TEXT,'-01')
			      ELSE
				      CONCAT(EXTRACT(MONTH FROM fecha_registro_evento)::TEXT,'-01')
			      END
		      )) AS fecha,
        to_char(fecha_registro_evento,'Mon') as mes, extract(year from fecha_registro_evento)::TEXT as anio, 
	      COALESCE(SUM(num_animales_hembra_muertos), 0) + COALESCE(SUM(num_animales_macho_muertos), 0) AS animales_muertos
      FROM Novedad_pecuaria
      JOIN Evento_sist_prod_afectado es ON es.cod_novedad_pecuaria_FK = cod_novedad_peq
      JOIN Evento e ON cod_evento_FK = e.cod_evento
      JOIN Municipios lg ON cod_municipio_FK = lg.cod_municipios
	    JOIN Departamentos d ON lg.cod_dpto_FK = d.cod_dpto
      JOIN Tipo_evento b ON b.cod_tip_evento = cod_tipo_evento_FK
      WHERE nombre_raza IS NOT NULL AND fecha_registro_evento BETWEEN DATE(%s) AND DATE(%s)"""
      +where+
      """
	    AND e.validado = true
	    GROUP BY fecha, mes,anio
	    ORDER BY fecha ASC
	  ) AS c;
    """)

    val = (ini, fin)

    cursor.execute(sql, val)

    columns = [column[0] for column in cursor.description]
    for row in cursor.fetchall():
      res['animales_muertos_por_fecha'].append(dict(zip(columns, row)))

  except CustomException as e:
    print("ERROR (visor/database_manager/peq_graphs): ", e.to_dict()['error'])
    return e, 500
  except Exception as e:
    print("ERROR (visor/database_manager/peq_graphs): ", e)
    return CustomException("Ocurrio un error al obtener los datos de las graficas del sistema pecuario", str(e)), 500
  else:
    return res, 200
  finally:
    if cursor:
      if not cursor.closed:
        cursor.close()


# This function get specfically the data to the pesq graphs 
def pesq_graphs(connection, ini, fin, where):
  try:
    cursor = connection.cursor()

    res = {
      'precio_por_tipo_pesq': [],
      'precio_por_tipo_act': []
    }

    sql = ("""
      SELECT tipo_pesqueria, SUM(precio_pagado) AS precio_pagado FROM Infraestructura_pesquera
      JOIN Novedad_pesquera ON cod_novedad_pesq = cod_novedad_pesquera_FK
      JOIN Novedad_pesquera_tipo_pes ON cod_novedad_pesq = Novedad_pesquera_tipo_pes.cod_novedad_pesquera_FK
      JOIN Tipo_pesqueria ON cod_tipo_pesquera_FK = cod_tipo_pesqueria
      JOIN Evento_sist_prod_afectado es ON es.cod_novedad_pesquera_FK = cod_novedad_pesq
      JOIN Evento e ON cod_evento_FK = e.cod_evento
      JOIN Municipios lg ON cod_municipio_FK = lg.cod_municipios
	    JOIN Departamentos d ON lg.cod_dpto_FK = d.cod_dpto
      JOIN Tipo_evento b ON b.cod_tip_evento = cod_tipo_evento_FK
      WHERE fecha_registro_evento BETWEEN DATE(%s) AND DATE(%s)"""
      +where+
      """
	    AND e.validado = true
      GROUP BY cod_tipo_pesqueria;
    """)

    val = (ini, fin)

    cursor.execute(sql, val)

    columns = [column[0] for column in cursor.description]
    for row in cursor.fetchall():
      res['precio_por_tipo_pesq'].append(dict(zip(columns, row)))

    sql = ("""
      SELECT tipo_activo, SUM(precio_pagado) AS precio_pagado FROM Infraestructura_pesquera
      JOIN Novedad_pesquera ON cod_novedad_pesq = cod_novedad_pesquera_FK
      JOIN Tipo_activo ON cod_tipo_activo_FK = cod_tipo_activo
      JOIN Evento_sist_prod_afectado es ON es.cod_novedad_pesquera_FK = cod_novedad_pesq
      JOIN Evento e ON cod_evento_FK = e.cod_evento
      JOIN Municipios lg ON cod_municipio_FK = lg.cod_municipios
	    JOIN Departamentos d ON lg.cod_dpto_FK = d.cod_dpto
      JOIN Tipo_evento b ON b.cod_tip_evento = cod_tipo_evento_FK
      WHERE fecha_registro_evento BETWEEN DATE(%s) AND DATE(%s)""" 
      +where+
      """
	    AND e.validado = true
      GROUP BY cod_tipo_activo;
    """)

    val = (ini, fin)

    cursor.execute(sql, val)

    columns = [column[0] for column in cursor.description]
    for row in cursor.fetchall():
      res['precio_por_tipo_act'].append(dict(zip(columns, row)))

  except CustomException as e:
    print("ERROR (visor/database_manager/pesq_graphs): ", e.to_dict()['error'])
    return e, 500
  except Exception as e:
    print("ERROR (visor/database_manager/pesq_graphs): ", e)
    return CustomException("Ocurrio un error al obtener los datos de las graficas del sistema pesquero", str(e)), 500
  else:
    return res, 200
  finally:
    if cursor:
      if not cursor.closed:
        cursor.close()


# Get the routes of the attached files from an event
def get_routes(id_evento, connection):
  try:
    cursor = connection.cursor()

    sql = ("""
      SELECT CONCAT(ruta,'/', nombre_archivo) AS ruta FROM Evento_seguimiento es JOIN Evento_seguimiento_adju esa 
        ON esa.cod_evento_seguimiento_fk = es.cod_evento_seguimiento where cod_evento_fk = %s;
    """)

    val = ([id_evento])

    cursor.execute(sql, val)

    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
      results.append(dict(zip(columns, row)))

    sql = ("""
      SELECT CONCAT(ruta, '/', nombre_archivo) AS ruta FROM Evento_adjunto WHERE cod_evento_fk = %s
    """)

    val = ([id_evento])

    cursor.execute(sql, val)

    columns = [column[0] for column in cursor.description]
    for row in cursor.fetchall():
      results.append(dict(zip(columns, row)))

  except CustomException as e:
    print('ERROR (visor/database_manager/get_routes): ', e.to_dict['error'])
    return e, 500
  except Exception as e:
    print('ERROR (visor/database_manager/get_routes): ', e)
    return CustomException('Ocurrio un error al obtener las rutas de los archivos', str(e)), 500
  else:
    return results, 200
  finally:
    if cursor:
      if not cursor.close:
        cursor.close()
    