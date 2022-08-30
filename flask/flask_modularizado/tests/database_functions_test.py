from app.services.database_service import DatabaseService

# This function is used in testing in order to delete the test user  and should only be used in testing, however, 
# it could be used if needed in other app service or function to delete a user by its email
def delete_user(email):
    try:   
        db_service = DatabaseService()
        connection = db_service.get_connection()
        cursor = connection.cursor()
        sql = ('''
            DELETE FROM Usuarios WHERE email = '{}'
        '''.format(email))

        cursor.execute(sql)
        connection.commit()
 
    except Exception as e:
        print(e) 
    finally:
        if not cursor.closed:
            cursor.close()
        if not connection.closed:
            connection.close()

def get_user_token(email):
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()
        cursor = connection.cursor()

        sql = ('''
            SELECT token FROM Usuarios WHERE email = '{}'
        '''.format(email))
        cursor.execute(sql)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results
    except Exception as e:
        print(e)
    finally:
        if not cursor.closed:
            cursor.close()
        if not connection.closed:
            connection.close()