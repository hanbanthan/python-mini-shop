"""Pydantic request/reponse schema for API

RULE: schema seperate from domain model in src/models
- not import/direct return Product, Customer, Order (dataclass)
outside API. Reason :
- Domain model have business method, private field, 
should not serialize to JSON
- Changing DB/model can not break API contract given to client
- need a "translator" layer
"""

