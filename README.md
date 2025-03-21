Setup:
1. python -m venv <myenvpath>
2.
  a) UNIX: source <myenvpath>/bin/activate
  
  b) Windows: <myenvpath>\Scripts\Activate.bat (oder so ähnlich)
  
4. pip install -r requirements.txt
5. python manage.py runserver (und ggf. noch die Adresse, z.B. 127.0.0.1:1234)

"Production"-Server (sofern man das so nennen kann):
-> http://s40kcwoowcwo8ogk4w0kwk8k.85.215.173.212.sslip.io


Zum Authentication-Verfahren:
1. Tokens bekommen:

curl \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "user1234"}' \
  http://localhost:8000/api/token/

2. Tokens nutzen (im Header)

curl \
  -X GET \
  -H "Content-Type: application/json" \
  -H 'Authorization: Bearer [hier access token einfügen]' \
  http://localhost:8000/amiauth
