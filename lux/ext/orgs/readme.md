# Organisations

This extensions add organisations to the [applications](../applications/readme.md)
extensions.

## Entity

**Organisations** and **Users** are specialised Entities, the Entity table
contains both organisations and users and distinguish between the two via
the ``type`` field.

An Entity can own objects via the **EntityOwnership** table which contains a one-to-one
relationship with a row on a foreign table.


## Organisations

An organisation

* can own one or more applications via the **OrganisationApp** model
* must have at least on organisation **owner**
* can own one or more objects via the **EntityOwnership** table
* cannot be deleted if
  * It is the master organisation
  * It owns objects via the Ownership table
  * It has more than one member

In addition **one organisation, the master organisation, must control the master application**.

## Users

A User

* can own one or more organisations via the **OrgMember** model
* can be part of one or more organisations via the **OrgMember** table
* can own one or more objects via the **EntityOwnership** table
* cannot own applications
