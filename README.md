# Python-CRUD-REST-API with flask and SQLite
This is a beginner level CRUD REST API in python that handles data of employees and uses SQLite as a database and implemented JWT for authentication. 
Steps to start this Project:
1. Clone this repository
2. Open the folder in VS code or PyCharm
3. in app.py SECRET KEY is empty, here you can put your secret key (any string for running in local)
4. save it and run terminal ( make sure current dicrectory is the project name that you saved the folder)
5. run this command to create python virtual environment with **python -m venv venv**
6. now run this command to create virtual environment **.\venv\Scripts\activate**
7. now run **pip install -r requirements.txt**
8. now run the project with **python app.py**
9. You can use postman to call the api

Here is the API calls:
1.To create an employee send a POST http request to the url that you got after running the project
http://127.0.0.1/5000/employee

Go to body tab then click on raw then from drop down select json and then paste below paylod in the box and hit the send button.

{
  "name":"John Chaurasiya"
  "designation":"Sales Head"
  "phone":"9876543210"
}

2. To get all employee:
   Send a GET call insted of post and remove the payload from the body
   http://127.0.0.1/5000/employee

3. To get employee by id:
   Send a GET call with the user id
   http://127.0.0.1/5000/employee/2

4. To update an employee, send a PUT request with body containing all the information
   http://127.0.0.1/5000/employee/1
{
  "name":"John Chaurasiya"
  "designation":"Sales Head"
  "phone":"1234567890"
}
here we have changed only phone number but other fields should be there in the payload as it is

5. To delete an employee, send a DELETE request with employee id
   http://127.0.0.1/5000/employee/1


Now, you have performed all the CRUD operation on the employee REST API
