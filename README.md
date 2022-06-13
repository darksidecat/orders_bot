# Orders bot
The bot was created for internal use in the company in order for managers to create orders for marketing materials, for their further processing by the marketing department.

Released to open source as an example of using aiogram v3, aiogram-dialog and several other technologies.

### Used technologies
* Python;
* aiogram v3 (Telegram Bot framework);
* aiogram-dialog (GUI framework for telegram bot);
* Docker and Docker Compose (containerization);
* PostgreSQL (database);
* Redis (persistent storage for some ongoing game data);
* SQLAlchemy (working with database from Python);
* Alembic (database migrations made easy);
* A small piece of DDD ideology (Domain Driven Design);

### Project deployment:
1. Clone the repository:
    `git clone https://github.com/darksidecat/orders_bot.git`

2. Copy `.env.example` to `.env` and fill in the values

4. Create volumes by running:
    `make prepare-volumes`

5. Up bot and environment by running:
    `make prod`

### ToDo's
* Coverage critical code with tests;
* Add docker container for database backuping;
* Add few exporting services: CSV, Google Sheets;
* Support for multiple languages (maybe?);
