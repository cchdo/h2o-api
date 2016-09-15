# CCHDO API
This is the planning document for the (non panic) API developed by CCHDO
for running the various web services it has got going on.

It will be messy at first, even this readme is messy.

## URIs

* User Manipulation:
  * Non Authed Routes:
    * `/user/login` (post) Return JWT
    * `/user/register` (post) Register a new user (email confirm?)
    * `/user/reset` (post) Send reset email
  * Authed Routes (the only ones in the entire system):
    * `/user/{id}/logout` (post) Change session ID, invalidates existing JWT
    * `/user/{id}/deactivate` (post) don't allow a user to login anymore
    * `/user/{id}/permissions` (get, post) view or add permissions
    * `/user/{id}/type_permissions` (get, post) like above but for types
        not permission objects
    * `/user/{id}/keys` (get, post) View a user's api keys

* API Key Manipulations:
  * `/key/{id}` (get, delete) view or invalidate an apikey

* Type Manipulation:
  * `/type` (get, post) List or create type objects
  * `/type/{id}` (get, delete) list or delete specific type obejct
  * `/type/{id}/schema` (get, put) modify a types validation schema 
  * `/type/{id}/ld` (get, put) modify a types JSON-LD context
  * `/type/{id}/unique` (get, put) modify a types globally unique keys

* Metadata Manipulation:
  * `/{type}` (get, post) Lists all objects of some type.
  * `/{type}/{id}` (get, post, patch, delete) Display or manipulate object of some type with id `id`.
  * `/{type}/schema` (get) Return the JSONSchema that the type object is validated against
  * `/{type}/{id}/links/{id}` (post, delete) Manipulate item relationships

* Transaction Management:
  * `/transaction` [GET] list any open transactions
  * `/transaction/begin` [POST] start a new transaction
  * `/transaction/{id}` [GET, POST, DELETE], list, remove, or finialize
      a transaction.

* Search:
  * `/search`
  * `/search/{type}`

### Query params

* `?include=relation1,relation2` include the entire objects of
    relationships. Examples:
    * the following would return all the needed information to construct
        a cchdo cruise page
        `/cruise/664?include=person,ship,country,note,geometry,program,references,attachment,attachment.note`
* `?filter=` TODO figure out what filters will be supported, we probably
    want this to just exclude objects matching the filter, e.g. if we
    want a cruise object to be returned and search "swift" with the
    filter specifying the role should be Chief Scientist, the correct
    cruise should still return even if a "swift" matching object is also
    attached to the cruise WITH OUT the Chief Scientist role.
* `?bbox=` special case for geometry searching, will limit the results
    to items directly attached to geometry objects within the bounding
    box
* `?fields=cruise.expocode,person.name` which fields the search term
    should be applied to
* `?q=some+search+term` the search term, attempt to case insensitive
    match to the fields in ?fields

Example for the current CCHDO search:

* `/search/cruise?q=Swift&filter=person.role%3DChief%20Scientist?fields=cruise.expocode,cruise.date_start,cruise.date_end,person.name,ship.name,program.name,reference.value`


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
