# CCHDO API
This is the planning document for the (non panic) API developed by CCHDO
for running the various web services it has got going on.

It will be messy at first, even this readme is messy.

## URIs

* Metadata Manipulation:
  * `/{type}` Lists all objects of some type.
  * `/{type}/{id}` Display or manipulate object of some type with id `id`.
  * `/{type}/{id}/{relationship_type}` List all objects of type `relationship_type` attached to type with id.
  * `/{type}/{id}/{relationship_type}/{relatipnship_id}` Display or manipulate the relationship.
  * `/{type}/schema` Return the JSONSchema that the type object is validated against

* Transaction Management:
  * `/transaction` [GET] list any open transactions
  * `/transaction/begin` [POST] start a new transaction
  * `/transaction/{id}` [GET, POST, DELETE], list, remove, or finialize
      a transaction.

### Query params

* `?fields=field1,field2...`Limit fields of return objects to those matching the comma seperated list
* `?include=relation1,relation2` include the entire objects of relationships


## Type Objects

### Person:
```json
{
  "name":"",
  "email":""
}
```

### Role:
```json
{
  "roleName":""
}
```
