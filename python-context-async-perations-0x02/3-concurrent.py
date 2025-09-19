import asyncio
import aiosqlite


# Async function: fetch all users
async def async_fetch_users():
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT * FROM users") as cursor:
            results = await cursor.fetchall()
            return results


# Async function: fetch users older than given age
async def async_fetch_older_users(age):
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT * FROM users WHERE age > ?", (age,)) as cursor:
            results = await cursor.fetchall()
            return results


# Run both queries concurrently
async def fetch_concurrently():
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users(40)  # required parameter
    )

    print("All Users:")
    for user in all_users:
        print(user)

    print("\nUsers older than 40:")
    for user in older_users:
        print(user)


# Entry point
if __name__ == "__main__":
    asyncio.run(fetch_concurrently())
