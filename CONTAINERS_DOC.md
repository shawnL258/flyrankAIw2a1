Stage 0:
docker ps showing a running container
<img width="938" height="128" alt="image" src="https://github.com/user-attachments/assets/45734f22-1c70-4b5c-bc90-8d76eee5cb99" />

docker exec -it <db_name> psql -U <user> -d <tasks>
<img width="713" height="258" alt="image" src="https://github.com/user-attachments/assets/c80faec9-ad97-440d-85c2-8977a495cd33" />

Stage 1:
docker exec postgres then check database tables and selected all rows from tasks after 3 attempts
<img width="607" height="822" alt="image" src="https://github.com/user-attachments/assets/b13c7659-0538-4671-8ee2-1fe0229a59b2" />

Stage 2:
Testing GET and GET ?={id} endpoints
<img width="802" height="170" alt="image" src="https://github.com/user-attachments/assets/80b8a497-dd69-4235-bd92-61d687877fda" />

Stage 3:
POST, PUT, and DELETE in /tasks endpoint returning all the right corresponding endpoints
<img width="921" height="372" alt="image" src="https://github.com/user-attachments/assets/a8edc112-057f-4e65-8387-988c690e882b" />

