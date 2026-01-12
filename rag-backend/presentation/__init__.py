"""
Presentation Layer - API Controllers

This layer contains:
- FastAPI routes (thin controllers)
- Request/response models (Pydantic)
- Dependency injection setup
- API documentation

Dependencies:
- CAN depend on Application layer (use cases, DTOs)
- CAN depend on Infrastructure layer (for DI setup)
- CANNOT depend on Domain layer directly
"""

