import asyncio

async def deleteAfter(ctx, seconds):
    await asyncio.sleep(seconds)
    await ctx.message.delete()
