CCHDO API
=========
This is the planning document for the (non panic) API developed by CCHDO
for running the various web services it has got going on.

URIs
----

`/{type}`
  Lists all objects of some type.
`/{type}/{id}`
  Display or manipulate object of some type with id `id`.
`/{type}/{id}/{relationship_type}`
  List all objects of type `relationship_type` attached to type with id.
`/{type}/{id}/{relationship_type}/{relatipnship_id}`
  Display or manipulate the relationship.

Query params:

`?fields=field1,field2...`
  Limit fields of return objects to those matching the comma seperated
  list
`?include=relation1,relation2`
  include the entire objects of relationships
  
  Dot syntax allowed? e.g. `role.person`



Type Objects
------------

Person:
  ```json
  {
    "name":"",
    "email":""
  }
  ```
Role:
  ```json
  {
    "roleName":""
  }
  ```

