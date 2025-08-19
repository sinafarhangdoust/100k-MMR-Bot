
# 100K MMR Bot

The most accurate DOTA 2 AI Assistant. 

## How to run 100K MMR Bot locally 

1. Get an OpenAI API key. You will need to add it as an environment variable `OPENAI_API_KEY=<your-api-key>`.
2. Get a LangSmith API key. 
3. Clone [chainlit-datalayer](https://github.com/Chainlit/chainlit-datalayer).
4. Navigate to chainlit-datalayer directory. 
5. Create a python virtual environment.
6. Install asyncpg by running `pip install asyncpg`.
7. Copy the environment variables by running `cp .env.example .env`.
8. Run `docker compose up -d`.
9. Run `npx prisma migrate deploy`.
10. Run `npx prisma studio`. Now you should be able to access the database at `http://localhost:5555`.
11. Now head back to 100k-mmr-bot directory.
12. Create a python virtual environment and install the dependencies by running `pip install -r requirements.txt`.
13. Generate a chainlit JWT token by running `chainlit create-secret` and copy the value you will need to for the environment variable `CHAINLIT_AUTH_SECRET`.
14. Run app.py with the following environment variables:
    ```shell
    OPENAI_API_KEY=<your-api-key>
    CHAINLIT_AUTH_SECRET=<your-chainlit-auth-secret>
    DATABASE_URL=postgresql://root:root@localhost:5432/postgres
    LANGSMITH_API_KEY=<your-langsmith-api-key>
    LANGSMITH_ENDPOINT=https://api.smith.langchain.com
    LANGSMITH_PROJECT=100k-mmr-bot
    LANGSMITH_TRACING=true
    ```

## How to scrape data

1. Navigate to Scraper directory.
2. Run `hero_scraper.py` to scrape all the heroes. (You can modify the output path inside main)
3. Run `items_scraper.py` to scrape all the items. (You can modify the output path inside main)
4. Run `mechanics_scraper.py` to scrape all the mechanics. (ou can modify the output path inside main)
