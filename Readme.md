# Installation steps
1. Clone the repository
2. Install docker and docker-compose or docker desktop on windows
3. Run Dependencies using docker compose command
```bash
docker compose up
```
4. Go to http://localhost:8000 to view the application
5. Use the postman collection to test the API by using the below button or exporting the collection from the repository

[![Run in Postman](https://run.pstmn.io/button.svg)](https://elements.getpostman.com/redirect?entityId=17951063-9a433acf-4fc4-46a3-a7ea-c6b4ad53da59&entityType=collection)

6. Default Password for the user signed up is "Test@123"

### API Details
1. Use signup api with body email, first_name, last_name json.
2. After signup use login Api with body email and password json.
3. After login, you can search users with search user api.
4. Having the user id from search user, use send request api to send friend request with to_user_id in json
5. Use list friend request api to list out the requests.(Login with other user before)
6. Use Accept request / Reject request api to accept/reject the friend request.(the request id must be passed in the url pattern which van be obtained in list requests)
7. use list friends api to list your friends.
