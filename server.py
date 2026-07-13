"""
FastMCP quickstart example.

cd to the `examples/snippets/clients` directory and run:
    uv run server fastmcp_quickstart stdio
"""

from fastmcp import FastMCP
from fastmcp.server.auth import StaticTokenVerifier
import aiohttp
import json
from typing import Annotated, Literal, Optional
from datetime import datetime
from pydantic import Field

# 集中管理 element type 選項，create / update / get_source 共用同一份
ElementType = Optional[Literal[
    'custom_slider',
    'ck_editor',
    'customer_login_form',
    'customer_register_form',
    'customer_reset_password_form',
    'product_detail',
    'cart_detail',
    'checkout_form',
    'order_detail',
    'order_payment',
    'my_orders',
    'my_account_button',
    'cart_button',
    'shop',
    'SingleProduct',
    'website_search_bar',
    'contact_us_form',
    'blog_post_detail',
    'blog_grid',
    'BlogPostSingle',
    'ComposeProductModal',
    'OrderItemsSummary',
    'GuestCheckoutNotification',
    'ECPay',
    'CashOnDelivery',
    'dynamic_route_element',
]]

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
        protocol = os.environ.get('PROTOCOL', 'https')
        return {
            'user_access_token': os.environ.get('USER_ACCESS_TOKEN'),
            'domain': domain,
            'store_uuid': os.environ.get('STORE_UUID'),
            'internal_base_url': None,  # dev 模式直接用 domain
            'protocol': protocol,
        }
    token = get_access_token()
    protocol = token.claims.get('protocol', 'https')
    host = token.claims.get('host')
    port = token.claims.get('port', '')
    if host:
        base = f"{protocol}://{host}:{port}" if port else f"{protocol}://{host}"
    else:
        base = None
    return {
        'user_access_token': token.claims.get('user_access_token'),
        'domain': token.claims.get('domain'),
        'store_uuid': token.claims.get('store_uuid'),
        'internal_base_url': base,
    }


def _build_api_url(config: dict, path: str) -> str:
    """用內部 service URL 避免 hairpin NAT，dev 模式直接用 domain"""
    if config['internal_base_url']:
        return f"{config['internal_base_url']}{path}"
    protocol = config.get('protocol', 'https')
    return f"{protocol}://{config['domain']}{path}"

def _build_source_viewer_url(config: dict, path: str) -> str:
    
    if config['internal_base_url']:
        return f"http://tnt-ssr-engine-vite-service.default.svc.cluster.local{path}"
    protocol = config.get('protocol', 'https')
    return f"{protocol}://{config['domain']}{path}"

def _base_headers(config: dict, content_type: Optional[str] = "application/json") -> dict:
    """基本 headers，cluster 內部請求加 Host header 讓後端能比對 domain

    content_type=None 時不帶 Content-Type，讓 aiohttp 依 data 內容自動設定
    （例如 multipart/form-data 需要自動產生 boundary）
    """
    headers = {
        "Authorization": f"Bearer {config['user_access_token']}",
    }
    if content_type:
        headers["Content-Type"] = content_type
    if config['internal_base_url']:
        headers["Host"] = config['domain']
    return headers


def _to_form_data(body: dict) -> aiohttp.FormData:
    """把 body dict 轉成 multipart/form-data，給只吃 multipart 的後端 endpoint 用"""
    form = aiohttp.FormData(default_to_multipart=True)
    for key, value in body.items():
        if isinstance(value, bool):
            form.add_field(key, str(value).lower())
        elif isinstance(value, (list, dict)):
            form.add_field(key, json.dumps(value))
        else:
            form.add_field(key, str(value))
    return form


# 创建一个不验证 SSL 证书的上下文
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


@mcp.tool(output_schema=None)
async def my_application_create_webpage( webpage_name: str, ) -> str:
    """
    在我的應用中創建網頁
    """
    config = get_user_config()

    async with aiohttp.ClientSession() as session:
        async with session.post(
            _build_api_url(config, "/api/v1/website/webpage/create/"),
            ssl=ssl_context,
            json={'name': webpage_name},
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text



@mcp.tool(output_schema=None)
async def my_application_create_element(
    element_name: str,
    element_tag_name: str,
    element_inner_html: str,
    element_props: dict,
    target_webpage_uuid: Optional[str] = None,
    target_webpage_position: Optional[Literal['head', 'body']] = None,
    target_parent_relation_uuid: Optional[str] = None,
    target_relative_position: Optional[Literal['before', 'after', 'in']] = None,
    element_type: ElementType = None,
    ) -> str:
    """
    在我的應用中創建元素
    如果需要將元素加入網頁的head/body 使用 target_webpage_uuid 以及 target_webpage_position 參數
    如果需要將元素創建相對於目標參考元素 使用 target_parent_relation_uuid 以及 target_relative_position 參數
    """
    config = get_user_config()

    async with aiohttp.ClientSession() as session:
        async with session.post(
            _build_api_url(config, f"/api/v1/website/element/r_create/?target_webpage_uuid={target_webpage_uuid}&target_webpage_position={target_webpage_position}&target_element_relation_uuid={target_parent_relation_uuid}&target_relative_position={target_relative_position}"),
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

@mcp.tool(output_schema=None)
async def my_application_delete_webpage( webpage_uuid: str, ) -> str:
    """
    在我的應用中刪除網頁
    """
    config = get_user_config()

    async with aiohttp.ClientSession() as session:
        async with session.delete(
            _build_api_url(config, f"/api/v1/website/webpage/{webpage_uuid}/delete/"),
            ssl=ssl_context,
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text


@mcp.tool(output_schema=None)
async def my_application_delete_element( parent_relation_uuid: str, ) -> str:
    """
    在我的應用中移除元素關係
    """
    config = get_user_config()

    async with aiohttp.ClientSession() as session:
        async with session.delete(
            _build_api_url(config, f"/api/v1/website/element/{parent_relation_uuid}/delete/"),
            ssl=ssl_context,
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text


#更新網頁
@mcp.tool(output_schema=None)
async def my_application_update_webpage(
    webpage_uuid: str,
    webpage_name: Optional[str] = None,
    webpage_props: Optional[dict] = None,
    webpage_data: Optional[dict] = None,
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
            _build_api_url(config, f"/api/v1/website/webpage/{webpage_uuid}/update/"),
            ssl=ssl_context,
            json=body,
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text

#更新元素
@mcp.tool(output_schema=None)
async def my_application_update_element(
    element_uuid: str,
    element_name: Optional[str] = None,
    element_tag_name: Optional[str] = None,
    element_inner_html: Optional[str] = None,
    element_props: Optional[dict] = None,
    element_type: ElementType = None,
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
            _build_api_url(config, f"/api/v1/website/element/{element_uuid}/update/"),
            ssl=ssl_context,
            json=body,
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text

#檢視我的素材
@mcp.tool(output_schema=None)
async def my_application_list_my_media_assets(
    media_type: Literal['image', 'video']
    ) -> str:
    """
    檢視網站可用的素材
    """
    config = get_user_config()

    async with aiohttp.ClientSession() as session:
        async with session.get(
            _build_api_url(config, f"/api/v1/store/{config['store_uuid']}/store_file/list/?is_public=true&media_type={media_type}"),
            ssl=ssl_context,
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text


#元素動作
@mcp.tool(output_schema=None)
async def my_application_action_to_target_element(
    parent_relation_uuid: str,
    action: Literal['mirror', 'clone', 'move'],
    target_webpage_uuid: Optional[str] = None,
    target_webpage_position: Optional[Literal['head', 'body']] = None,
    target_parent_relation_uuid: Optional[str] = None,
    target_relative_position: Optional[Literal['before', 'after', 'in']] = None,
    ) -> str:
    """
    在我的應用中 移動/鏡像/克隆 目標元素
    如果需要將元素移至網頁的head/body 使用 target_webpage_uuid 以及 target_webpage_position 參數
    如果需要將元素移至相對於目標參考元素 使用 target_parent_relation_uuid 以及 target_relative_position 參數
    """
    config = get_user_config()

    async with aiohttp.ClientSession() as session:
        async with session.put(
            _build_api_url(config, f"/api/v1/website/element/{parent_relation_uuid}/r_action/{action}/"),
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


@mcp.tool(output_schema=None)
async def my_application_get_detail_element_structure(element_uuid: str, ) -> str:
    """
    在我的應用中取得目標元素詳細的JSON格式資料
    """
    config = get_user_config()

    async with aiohttp.ClientSession() as session:
        async with session.get(
            _build_api_url(config, f"/api/v1/website/element/{element_uuid}/agent/retrieve/?detail=true"),
            ssl=ssl_context,
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text

# @mcp.tool()
# async def my_application_get_detail_website_structure() -> str:
#     """
#     在我的應用中取得整個網站的所有頁面細節的JSON格式文本架構
#     """
#     config = get_user_config()

#     async with aiohttp.ClientSession() as session:
#         async with session.get(
#             _build_api_url(config, f"/api/v1/website/website/retrieve/"),
#             ssl=ssl_context,
#             headers=_base_headers(config),
#         ) as resp:
#             text = await resp.text()
#             return text
@mcp.tool(output_schema=None)
async def my_application_list_all_webpages() -> str:
    """
    在我的應用中取得所有網頁
    """
    config = get_user_config()

    async with aiohttp.ClientSession() as session:
        async with session.get(
            _build_api_url(config, f"/api/v1/website/webpage/list/"),
            ssl=ssl_context,
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text
        
@mcp.tool(output_schema=None)
async def my_application_get_brief_webpage_structure(webpage_name: str, object_uuid: Optional[str] = None) -> str:
    """
    在我的應用中取得目標網頁精簡的JSON格式文本架構
    """
    config = get_user_config()

    async with aiohttp.ClientSession() as session:
        async with session.get(
            _build_api_url(config, f"/api/v1/website/webpage/{webpage_name or ''}/{object_uuid or ''}/agent/retrieve/?detail=false"),
            ssl=ssl_context,
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text

@mcp.tool()
async def my_application_get_element_component_source(component: ElementType) -> str:
    """
    取得我的應用中特定element type組件的原始碼以及預設樣式表
    """
    config = get_user_config()


    async with aiohttp.ClientSession() as session:
        async with session.get(
            _build_source_viewer_url(config, f"/website_backend/source-viewer/{component}.html"),
            ssl=ssl_context,
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text


#檢視部落格文章
@mcp.tool(output_schema=None)
async def my_application_retrieve_blog_post(blog_post_uuid: str) -> str:
    """
    在我的應用中取得目標部落格文章的詳細資料
    """
    config = get_user_config()

    async with aiohttp.ClientSession() as session:
        async with session.get(
            _build_api_url(config, f"/api/v1/store/{config['store_uuid']}/blog_post/{blog_post_uuid}/retrieve/"),
            ssl=ssl_context,
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text


#更新部落格文章
@mcp.tool(output_schema=None)
async def my_application_update_blog_post(
    blog_post_uuid: str,
    # image: Optional[str] = None,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    namespace: Optional[str] = None,
    priority: Optional[int] = None,
    tags: Optional[list] = None,
    visibility: Optional[Literal['visable', 'invisable', 'schedule']] = None,
    visible_start_time: Optional[datetime] = None,
    visible_end_time: Optional[datetime] = None,
    description: Optional[str] = None,
    keywords: Optional[str] = None,
    content: Annotated[
        Optional[str],
        Field(description="部落格文章內文，使用 CKEditor 編輯與檢視，需為 CKEditor 相容的 HTML 格式字串（例如 <p>, <h2>, <ul> 等標籤）"),
    ] = None,
    # blog_post_category_relations: Optional[list] = None,
    # blog_post_author_relations: Optional[list] = None,
    ) -> str:
    """
    在我的應用中更新目標部落格文章
    """
    config = get_user_config()

    body = {}
    if title is not None:
        body['title'] = title
    if subtitle is not None:
        body['subtitle'] = subtitle
    if namespace is not None:
        body['namespace'] = namespace
    if priority is not None:
        body['priority'] = priority
    if tags is not None:
        body['tags'] = tags
    if visibility is not None:
        body['visibility'] = visibility
    if visible_start_time is not None:
        body['visible_start_time'] = visible_start_time.isoformat()
    if visible_end_time is not None:
        body['visible_end_time'] = visible_end_time.isoformat()
    if description is not None:
        body['description'] = description
    if keywords is not None:
        body['keywords'] = keywords
    if content is not None:
        body['content'] = content

    async with aiohttp.ClientSession() as session:
        async with session.put(
            _build_api_url(config, f"/api/v1/store/{config['store_uuid']}/blog_post/{blog_post_uuid}/update/"),
            ssl=ssl_context,
            data=_to_form_data(body),
            headers=_base_headers(config, content_type=None),
        ) as resp:
            text = await resp.text()
            return text


#檢視商品
@mcp.tool(output_schema=None)
async def my_application_retrieve_product(product_uuid: str) -> str:
    """
    在我的應用中取得目標商品的詳細資料
    """
    config = get_user_config()

    async with aiohttp.ClientSession() as session:
        async with session.get(
            _build_api_url(config, f"/api/v1/store/{config['store_uuid']}/product/{product_uuid}/retrieve/"),
            ssl=ssl_context,
            headers=_base_headers(config),
        ) as resp:
            text = await resp.text()
            return text


#更新商品
@mcp.tool(output_schema=None)
async def my_application_update_product(
    product_uuid: str,
    name: Optional[str] = None,
    sku: Optional[str] = None,
    stock: Optional[int] = None,
    category: Optional[str] = None,
    tags: Optional[list] = None,
    # product_type: Optional[str] = None,
    currency: Optional[str] = None,
    currency_sign: Optional[str] = None,
    price: Optional[float] = None,
    discount_price: Optional[float] = None,
    discount_start_time: Optional[datetime] = None,
    discount_end_time: Optional[datetime] = None,
    visibility: Optional[Literal['visable', 'invisable', 'schedule']] = None,
    visible_start_time: Optional[datetime] = None,
    visible_end_time: Optional[datetime] = None,
    taxable: Optional[bool] = None,
    tax_rate: Optional[float] = None,
    inventory_control: Optional[bool] = None,
    single_page_product: Optional[bool] = None,
    enable_review: Optional[bool] = None,
    require_customer_login: Optional[bool] = None,
    bundle: Optional[int] = None,
    unit: Optional[str] = None,
    length: Optional[float] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    weight: Optional[float] = None,
    weight_unit: Optional[str] = None,
    priority: Optional[int] = None,
    description: Optional[str] = None,
    keywords: Optional[str] = None,
    content: Annotated[
        Optional[str],
        Field(description="商品內文，使用 CKEditor 編輯與檢視，需為 CKEditor 相容的 HTML 格式字串（例如 <p>, <h2>, <ul> 等標籤）"),
    ] = None,
    spec: Annotated[
        Optional[str],
        Field(description="商品規格，使用 CKEditor 編輯與檢視，需為 CKEditor 相容的 HTML 格式字串（例如 <p>, <h2>, <ul> 等標籤）"),
    ] = None,
    ) -> str:
    """
    在我的應用中更新目標商品
    """
    config = get_user_config()

    body = {}
    if name is not None:
        body['name'] = name
    if sku is not None:
        body['sku'] = sku
    if stock is not None:
        body['stock'] = stock
    if category is not None:
        body['category'] = category
    if tags is not None:
        body['tags'] = tags
    # if product_type is not None:
    #     body['type'] = product_type
    if currency is not None:
        body['currency'] = currency
    if currency_sign is not None:
        body['currency_sign'] = currency_sign
    if price is not None:
        body['price'] = price
    if discount_price is not None:
        body['discount_price'] = discount_price
    if discount_start_time is not None:
        body['discount_start_time'] = discount_start_time.isoformat()
    if discount_end_time is not None:
        body['discount_end_time'] = discount_end_time.isoformat()
    if visibility is not None:
        body['visibility'] = visibility
    if visible_start_time is not None:
        body['visible_start_time'] = visible_start_time.isoformat()
    if visible_end_time is not None:
        body['visible_end_time'] = visible_end_time.isoformat()
    if taxable is not None:
        body['taxable'] = taxable
    if tax_rate is not None:
        body['tax_rate'] = tax_rate
    if inventory_control is not None:
        body['inventory_control'] = inventory_control
    if single_page_product is not None:
        body['single_page_product'] = single_page_product
    if enable_review is not None:
        body['enable_review'] = enable_review
    if require_customer_login is not None:
        body['require_customer_login'] = require_customer_login
    if bundle is not None:
        body['bundle'] = bundle
    if unit is not None:
        body['unit'] = unit
    if length is not None:
        body['length'] = length
    if width is not None:
        body['width'] = width
    if height is not None:
        body['height'] = height
    if weight is not None:
        body['weight'] = weight
    if weight_unit is not None:
        body['weight_unit'] = weight_unit
    if priority is not None:
        body['priority'] = priority
    if description is not None:
        body['description'] = description
    if keywords is not None:
        body['keywords'] = keywords
    if content is not None:
        body['content'] = content
    if spec is not None:
        body['spec'] = spec

    async with aiohttp.ClientSession() as session:
        async with session.put(
            _build_api_url(config, f"/api/v1/store/{config['store_uuid']}/product/{product_uuid}/update/"),
            ssl=ssl_context,
            data=_to_form_data(body),
            headers=_base_headers(config, content_type=None),
        ) as resp:
            text = await resp.text()
            return text


if __name__ == "__main__":
    if dev:
        mcp.run(transport="stdio")
    else:
        mcp.run(transport="streamable-http", host="0.0.0.0", port=8080, stateless_http=True)
