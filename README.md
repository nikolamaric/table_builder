# Table Builder application

The goal is to build a simple backend for a table builder app, where the user can build tables dynamically. The app has
the following endpoints:

| Request type | Endpoint	           | Action                                                                                                                            |
|--------------|---------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| POST	        | /api/table          | Generate dynamic Django model based on user provided fields types and titles. The field type can be a string, number, or Boolean. |
| PUT          | /api/table/:id	     | This end point allows the user to update the structure of dynamically generated model.                                            |
| POST         | 	/api/table/:id/row | Allows the user to add rows to the dynamically generated model while respecting the model schema.                                 |
| GET          | /api/table/:id/rows | Get all the rows in the dynamically generated model.                                                                              |

## How to run it?

**Fork the repo, position to the root and do the following steps:**

- Build the docker images: `docker-compose build`

- Run docker images: `docker-compose up -d`

And you are ready to go! Everything is running on: `localhost:8000`. So it means that if you want to create a new
dynamic table, you should send POST on: `http://localhost:8000/api/table`.

Do the same for other endpoints too.

## API Endpoints:

### POST /api/table 

**_(Create new table)_**

Request body:

```json
{
  "name": "Table 1",
  "fields": {
    "name": "str",
    "age": "int",
    "is_active": "bool"
  }
}
```

### PUT /api/table/:id 

**_(Update table - only new fields will be added, existing fields will not be updated.)_**

Request body:

```json
{
  "fields": {
    "name": "str",
    "age": "int",
    "email": "str" // new field
  }
}
```

### POST /api/table/:id/row 

**_(Create new row)_**

Request body:

```json
{
  "name": "John",
  "age": 25,
  "is_active": true,
  "email": "foo@bar.com"
}
```

### GET /api/table/:id/rows 

**_(Get all rows)_**

Response body:

```json
[
  {
    "id": 1,
    "name": "John",
    "age": 25,
    "is_active": true,
    "email": "foo@bar.com"
  }
]
```