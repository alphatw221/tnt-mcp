"""
FastMCP quickstart example.

cd to the `examples/snippets/clients` directory and run:
    uv run server fastmcp_quickstart stdio
"""

from mcp.server.fastmcp import FastMCP
import aiohttp
from typing import Literal, Optional

from dotenv import load_dotenv
import os

load_dotenv()  

# Create an MCP server
mcp = FastMCP("Demo")

dev = os.environ.get('DEV')=='true'
domain = '127.0.0.1:8000' if dev else os.environ.get('DOMAIN') 
user_access_token = os.environ.get('USER_ACCESS_TOKEN')


types = ['custom_slider', 'ck_editor', 'customer_login_form', 'customer_register_form', 'product_detail', 'cart_detail', 'checkout_form', 'order_detail', 'order_payment', 'my_orders', 
                      'my_account_button','cart_button', 'shop', 'website_search_bar', 'contact_us_form', 'blog_post_detail']

@mcp.tool()
async def my_application_create_webpage( webpage_name: str, ) -> str:
    """
    在我的應用中創建網頁
    """

    protocol = "http" if dev else "https"

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{protocol}://{domain}/api/v1/website/webpage/create/",
            json={
                'name':webpage_name
            },
            headers={
                "Authorization": f"Bearer {user_access_token}",
                "Content-Type": "application/json"
            }
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

    protocol = "http" if dev else "https"

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{protocol}://{domain}/api/v1/website/element/r_create/?target_webpage_uuid={target_webpage_uuid}&target_webpage_position={target_webpage_position}&target_element_relation_uuid={target_parent_relation_uuid}&target_relative_position={target_relative_position}",
            json={
                'name':element_name,
                'tag_name':element_tag_name,
                'inner_html':element_inner_html,
                'props':element_props,
                'type':element_type
            },
            headers={
                "Authorization": f"Bearer {user_access_token}",
                "Content-Type": "application/json"
            }
        ) as resp:
            text = await resp.text()
            return text

@mcp.tool()
async def my_application_delete_webpage( webpage_uuid: str, ) -> str:
    """
    在我的應用中刪除網頁
    """

    protocol = "http" if dev else "https"

    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"{protocol}://{domain}/api/v1/website/webpage/{webpage_uuid}/delete/",
            headers={
                "Authorization": f"Bearer {user_access_token}",
                "Content-Type": "application/json"
            }
        ) as resp:
            text = await resp.text()
            return text


@mcp.tool()
async def my_application_delete_element( parent_relation_uuid: str, ) -> str:
    """
    在我的應用中移除元素關係
    """

    protocol = "http" if dev else "https"

    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"{protocol}://{domain}/api/v1/website/element/{parent_relation_uuid}/delete/",
            headers={
                "Authorization": f"Bearer {user_access_token}",
                "Content-Type": "application/json"
            }
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

    protocol = "http" if dev else "https"

    json = {}
    if webpage_name:
        json['name'] = webpage_name
    if webpage_props:
        json['props'] = webpage_props
    if webpage_data:
        json['data'] = webpage_data
    async with aiohttp.ClientSession() as session:
        async with session.put(
            f"{protocol}://{domain}/api/v1/website/webpage/{webpage_uuid}/update/",
            json=json,
            headers={
                "Authorization": f"Bearer {user_access_token}",
                "Content-Type": "application/json"
            }
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

    protocol = "http" if dev else "https"

    json = {}
    if element_name:
        json['name'] = element_name
    if element_tag_name:
        json['tag_name'] = element_tag_name
    if element_inner_html:
        json['inner_html'] = element_inner_html
    if element_props:
        json['props'] = element_props
    if element_type:
        json['type'] = element_type
    async with aiohttp.ClientSession() as session:
        async with session.put(
            f"{protocol}://{domain}/api/v1/website/element/{element_uuid}/update/",
            json=json,
            headers={
                "Authorization": f"Bearer {user_access_token}",
                "Content-Type": "application/json"
            }
        ) as resp:
            text = await resp.text()
            return text

#檢視我的素材
@mcp.tool()
async def my_application_list_my_media_assets(
    store_uuid: str,
    media_type: Literal['image', 'video']
    ) -> str:
    """
    檢視網站可用的素材
    """

    protocol = "http" if dev else "https"

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{protocol}://{domain}/api/v1/store/{store_uuid}/store_file/list/?is_public=true&media_type={media_type}",
            headers={
                "Authorization": f"Bearer {user_access_token}",
                "Content-Type": "application/json"
            }
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


    protocol = "http" if dev else "https"

    async with aiohttp.ClientSession() as session:
        async with session.put(
            f"{protocol}://{domain}/api/v1/website/element/{parent_relation_uuid}/r_action/{action}/",
            json={
                'target_webpage_uuid':target_webpage_uuid,
                'target_webpage_position':target_webpage_position,
                'target_element_relation_uuid':target_parent_relation_uuid,
                'target_relative_position':target_relative_position
            },
            headers={
                "Authorization": f"Bearer {user_access_token}",
                "Content-Type": "application/json"
            }
        ) as resp:
            text = await resp.text()
            return text




@mcp.tool()
async def my_application_get_detail_element_structure(element_uuid: str, ) -> str:
    """
    在我的應用中取得目標元素詳細的JSON格式資料
    """

    protocol = "http" if dev else "https"

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{protocol}://{domain}/api/v1/website/element/{element_uuid}/agent/retrieve/?detail=true"
        ) as resp:
            text = await resp.text()
            return text
        


@mcp.tool()
async def my_application_get_brief_webpage_structure(webpage_name: str, object_uuid: Optional[str]) -> str:
    """
    在我的應用中取得目標網頁精簡的JSON格式文本架構
    """

    protocol = "http" if dev else "https"

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{protocol}://{domain}/api/v1/website/webpage/{webpage_name or ''}/{object_uuid or ''}/agent/retrieve/?detail=false"
        ) as resp:
            text = await resp.text()
            return text

@mcp.tool()
async def my_application_get_element_component_source(component: Optional[Literal['custom_slider', 'ck_editor', 'customer_login_form', 'customer_register_form', 'product_detail', 'cart_detail', 'checkout_form', 'order_detail', 'order_payment', 'my_orders', 
                      'my_account_button','cart_button', 'shop', 'website_search_bar', 'contact_us_form', 'blog_post_detail', 'ComposeProductModal']]) -> str:
    """
    取得我的應用中特定element type組件的原始碼以及預設樣式表
    """


    protocol = 'https'
    domain = os.environ.get('DOMAIN') 
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{protocol}://{domain}/website_backend/source-viewer/{component}.html"
        ) as resp:
            text = await resp.text()
            return text


