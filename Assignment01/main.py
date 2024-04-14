from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
load_dotenv()

from google.cloud.sql.connector import Connector, IPTypes
import pymysql
import uvicorn
import sqlalchemy

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    instance_connection_name = os.environ['INSTANCE_CONNECTION_NAME']
    db_user = os.environ['DB_USER']
    db_pass = os.environ['DB_PASS']
    db_name = os.environ['DB_NAME']

    ip_type = IPTypes.PUBLIC

    connector = Connector(ip_type)

    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        return conn
    
    connection_string = getconn()

    return connection_string

def check_database_connection():
    try:
        conn = connect_with_connector()
        return True
        # print('connection successful')

        # with conn.cursor() as cursor:
        #     cursor.execute("SELECT 1")
        #     result = cursor.fetchone()
        #     print('Test query result: ', result)
        #     return True
    except Exception as e:
        print('Connection failed: ', str(e))
    
# Health check endpoint
@app.get("/healthz", status_code=200)
async def health_check():
    if check_database_connection():
        response = Response()
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response
    else:
        raise HTTPException(status_code=503)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
