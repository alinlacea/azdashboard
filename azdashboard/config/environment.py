from azdashboard.config import settings

if settings.environment == 'production':
    import azdashboard.config.environments.production as env
elif settings.environment == 'development':
    import azdashboard.config.environments.development as env
elif settings.environment == 'test':
    import azdashboard.config.environments.test as env
else:
    raise RuntimeError("Environment not set or incorrect")

server = env.server
debug = env.debug
reloader = env.reloader
db_url = env.db_url
db_echo = env.db_echo
