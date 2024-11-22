TAG_METADATA = [
    {
        'name': 'User | v1',
        'description': 'Operation with user v1.',
    },
    {
        'name': 'Company | v1',
        'description': 'Operation with company v1.',
    },
    {
        'name': 'Authentication | v1',
        'description': 'Authentication with email invites v1.',
    },
    {
        'name': 'JWT | v1',
        'description': 'Authentication with jwt v1.',
    },
    {
        'name': 'Healthz',
        'description': 'Standard health check.',
    },
]

TITLE = 'API business control system'
DESCRIPTION = (
    'Implemented on FastAPI.\n\nBusiness control system API\n\nFor contact - https://t.me/log1s7'
)
VERSION = '0.0.1'

ERRORS_MAP = {
    'mongo': 'Mongo connection failed',
    'postgres': 'PostgreSQL connection failed',
    'redis': 'Redis connection failed',
    'rabbit': 'RabbitMQ connection failed',
}
