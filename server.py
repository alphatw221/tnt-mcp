"""
FastMCP quickstart example.

cd to the `examples/snippets/clients` directory and run:
    uv run server fastmcp_quickstart stdio
"""

from fastmcp import FastMCP
from fastmcp.server.auth import StaticTokenVerifier
import aiohttp
import json
from typing import Literal, Optional

from dotenv import load_dotenv
from fastmcp.server.dependencies import get_access_token
import os
import ssl

load_dotenv()

dev = os.environ.get('DEV') == 'true'


def _load_tokens() -> dict:
    """從 tokens.json 載入多用戶 API key 設定（dev 模式不需要）"""
    if dev:
        return {}
    tokens_file = os.environ.get("TOKENS_FILE", "tokens.json")
    with open(tokens_file) as f:
        return json.load(f)


auth = StaticTokenVerifier(tokens=_load_tokens())

# Create an MCP server
mcp = FastMCP("TNT-MCP", auth=auth)


def get_user_config() -> dict:
    """
    取得使用者設定。
    - dev 模式（stdio）：從 .env 讀取
    - 雲端模式（HTTP）：從 Bearer token 的 claims 讀取
    """
    if dev:
        domain = os.environ.get('DOMAIN')
        return {
            'user_access_token': os.environ.get('USER_ACCESS_TOKEN'),
            'domain': domain,
            'store_uuid': os.environ.get('STORE_UUID'),
            'internal_base_url': None,  # dev 模式直接用 domain
        }
    token = get_access_token()
    protocol = token.claims.get('protocol', 'https')
    host = token.claims.get('host')
    port = token.claims.get('port', '')
    base = f"{protocol}://{host}:{port}" if port else f"{protocol}://{host}"
    return {
        'user_access_token': token.claims.get('user_access_token'),
        'domain': token.claims.get('domain'),
        'store_uuid': token.claims.get('store_uuid'),
        'internal_base_url': base,
    }


def _build_url(config: dict, path: str) -> str:
    """用內部 service URL 避免 hairpin NAT，dev 模式直接用 domain"""
    if config['internal_base_url']:
        return f"{config['internal_base_url']}{path}"
    return f"http://{config['domain']}{path}"


def _base_headers(config: dict) -> dict:
    """基本 headers，cluster 內部請求加 Host header 讓後端能比對 domain"""
    headers = {
        "Authorization": f"Bearer {config['user_access_token']}",
        "Content-Type": "application/json",
    }
    if config['internal_base_url']:
        headers["Host"] = config['domain']
    return headers


# 创建一个不验证 SSL 证书的上下文
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


@mcp.tool()
async def my_application_create_webpage( webpage_name: str, ) -> str:
    """
    在我的應用中創建網頁
    """
    config = get_user_config()

    async with aiohttp.ClientSession() as session:
        async with session.post(
            _build_url(config, "/api/v1/website/webpage/create/"),
            ssl=ssl_context,
            json={'name': webpage_name},
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text



@mcp.tool()
async def my_application_create_element(
    target_webpage_uuid: Optional[str],
    target_webpage_position: Optional[Literal['head', 'body']],
    target_parent_relation_uuid: Optional[str],
    target_relative_position: Optional[Literal['before', 'after', 'in']] ,
    element_name: str,
    element_tag_name: str,
    element_inner_html: str,
    element_props: dict,
    element_type: Optional[Literal['custom_slider', 'ck_editor', 'customer_login_form', 'customer_register_form', 'product_detail', 'cart_detail', 'checkout_form', 'order_detail', 'order_payment', 'my_orders',
                      'my_account_button','cart_button', 'shop', 'website_search_bar', 'contact_us_form', 'blog_post_detail']]
    ) -> str:
    """
    在我的應用中創建元素
    如果需要將元素加入網頁的head/body 使用 target_webpage_uuid 以及 target_webpage_position 參數
    如果需要將元素創建相對於目標參考元素 使用 target_parent_relation_uuid 以及 target_relative_position 參數
    """
    config = get_user_config()

    async with aiohttp.ClientSession() as session:
        async with session.post(
            _build_url(config, f"/api/v1/website/element/r_create/?target_webpage_uuid={target_webpage_uuid}&target_webpage_position={target_webpage_position}&target_element_relation_uuid={target_parent_relation_uuid}&target_relative_position={target_relative_position}"),
            ssl=ssl_context,
            json={
                'name': element_name,
                'tag_name': element_tag_name,
                'inner_html': element_inner_html,
                'props': element_props,
                'type': element_type,
            },
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text

@mcp.tool()
async def my_application_delete_webpage( webpage_uuid: str, ) -> str:
    """
    在我的應用中刪除網頁
    """
    config = get_user_config()

    async with aiohttp.ClientSession() as session:
        async with session.delete(
            _build_url(config, f"/api/v1/website/webpage/{webpage_uuid}/delete/"),
            ssl=ssl_context,
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text


@mcp.tool()
async def my_application_delete_element( parent_relation_uuid: str, ) -> str:
    """
    在我的應用中移除元素關係
    """
    config = get_user_config()

    async with aiohttp.ClientSession() as session:
        async with session.delete(
            _build_url(config, f"/api/v1/website/element/{parent_relation_uuid}/delete/"),
            ssl=ssl_context,
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text


#更新網頁
@mcp.tool()
async def my_application_update_webpage(
    webpage_uuid: str,
    webpage_name: Optional[str],
    webpage_props:Optional[dict],
    webpage_data: Optional[dict]
    ) -> str:
    """
    在我的應用中更新網頁
    """
    config = get_user_config()

    body = {}
    if webpage_name:
        body['name'] = webpage_name
    if webpage_props:
        body['props'] = webpage_props
    if webpage_data:
        body['data'] = webpage_data
    async with aiohttp.ClientSession() as session:
        async with session.put(
            _build_url(config, f"/api/v1/website/webpage/{webpage_uuid}/update/"),
            ssl=ssl_context,
            json=body,
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text

#更新元素
@mcp.tool()
async def my_application_update_element(
    element_uuid: str,
    element_name: Optional[str],
    element_tag_name: Optional[str],
    element_inner_html: Optional[str],
    element_props:Optional[dict],
    element_type: Optional[Literal['custom_slider', 'ck_editor', 'customer_login_form', 'customer_register_form', 'product_detail', 'cart_detail', 'checkout_form', 'order_detail', 'order_payment', 'my_orders',
                      'my_account_button','cart_button', 'shop', 'website_search_bar', 'contact_us_form', 'blog_post_detail']]
    ) -> str:
    """
    在我的應用中更新元素
    """
    config = get_user_config()

    body = {}
    if element_name:
        body['name'] = element_name
    if element_tag_name:
        body['tag_name'] = element_tag_name
    if element_inner_html:
        body['inner_html'] = element_inner_html
    if element_props:
        body['props'] = element_props
    if element_type:
        body['type'] = element_type
    async with aiohttp.ClientSession() as session:
        async with session.put(
            _build_url(config, f"/api/v1/website/element/{element_uuid}/update/"),
            ssl=ssl_context,
            json=body,
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text

#檢視我的素材
@mcp.tool()
async def my_application_list_my_media_assets(
    media_type: Literal['image', 'video']
    ) -> str:
    """
    檢視網站可用的素材
    """
    config = get_user_config()

    async with aiohttp.ClientSession() as session:
        async with session.get(
            _build_url(config, f"/api/v1/store/{config['store_uuid']}/store_file/list/?is_public=true&media_type={media_type}"),
            ssl=ssl_context,
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text


#元素動作
@mcp.tool()
async def my_application_action_to_target_element(
    parent_relation_uuid: str,
    action: Literal['mirror', 'clone', 'move'],

    target_webpage_uuid: Optional[str],
    target_webpage_position: Optional[Literal['head', 'body']],
    target_parent_relation_uuid: Optional[str],
    target_relative_position: Optional[Literal['before', 'after', 'in']]

    ) -> str:
    """
    在我的應用中 移動/鏡像/克隆 目標元素
    如果需要將元素移至網頁的head/body 使用 target_webpage_uuid 以及 target_webpage_position 參數
    如果需要將元素移至相對於目標參考元素 使用 target_parent_relation_uuid 以及 target_relative_position 參數
    """
    config = get_user_config()

    async with aiohttp.ClientSession() as session:
        async with session.put(
            _build_url(config, f"/api/v1/website/element/{parent_relation_uuid}/r_action/{action}/"),
            ssl=ssl_context,
            json={
                'target_webpage_uuid': target_webpage_uuid,
                'target_webpage_position': target_webpage_position,
                'target_element_relation_uuid': target_parent_relation_uuid,
                'target_relative_position': target_relative_position,
            },
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text


@mcp.tool()
async def my_application_get_detail_element_structure(element_uuid: str, ) -> str:
    """
    在我的應用中取得目標元素詳細的JSON格式資料
    """
    config = get_user_config()

    async with aiohttp.ClientSession() as session:
        async with session.get(
            _build_url(config, f"/api/v1/website/element/{element_uuid}/agent/retrieve/?detail=true"),
            ssl=ssl_context,
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text


@mcp.tool()
async def my_application_get_brief_webpage_structure(webpage_name: str, object_uuid: Optional[str]) -> str:
    """
    在我的應用中取得目標網頁精簡的JSON格式文本架構
    """
    config = get_user_config()

    async with aiohttp.ClientSession() as session:
        async with session.get(
            _build_url(config, f"/api/v1/website/webpage/{webpage_name or ''}/{object_uuid or ''}/agent/retrieve/?detail=false"),
            ssl=ssl_context,
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text

@mcp.tool()
async def my_application_get_element_component_source(component: Optional[Literal['custom_slider', 'ck_editor', 'customer_login_form', 'customer_register_form', 'product_detail', 'cart_detail', 'checkout_form', 'order_detail', 'order_payment', 'my_orders', 
                      'my_account_button','cart_button', 'shop', 'website_search_bar', 'contact_us_form', 'blog_post_detail', 'ComposeProductModal', 'OrderItemsSummary', 'GuestCheckoutNotification']]) -> str:
    """
    取得我的應用中特定element type組件的原始碼以及預設樣式表
    """
    config = get_user_config()


    async with aiohttp.ClientSession() as session:
        async with session.get(
            _build_url(config, f"/website_backend/source-viewer/{component}.html"),
            ssl=ssl_context,
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text


if __name__ == "__main__":
    if dev:
        mcp.run(transport="stdio")
    else:
        mcp.run(transport="streamable-http", host="0.0.0.0", port=8080, stateless_http=True)
