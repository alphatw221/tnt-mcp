import os
import aiohttp
import ssl

async def test():

    component = 'product_detail'
    protocol = 'https'
    domain = os.environ.get('DOMAIN')

    # 创建一个不验证 SSL 证书的上下文
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{protocol}://{domain}/website_backend/source-viewer/{component}.html",
            ssl=ssl_context
        ) as resp:
            text = await resp.text()
            return text

if __name__ == '__main__':
    import asyncio
    from dotenv import load_dotenv

    load_dotenv()  

    result = asyncio.run(test())
    print(result)