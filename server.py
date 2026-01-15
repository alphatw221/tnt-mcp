"""
FastMCP quickstart example.

cd to the `examples/snippets/clients` directory and run:
    uv run server fastmcp_quickstart stdio
"""

from mcp.server.fastmcp import FastMCP
import aiohttp
from typing import Literal, Optional
# Create an MCP server
mcp = FastMCP("Demo")



@mcp.tool()
async def my_application_create_webpage(user_access_token: str, webpage_name: str, ) -> str:
    """
    在自建的網站編輯器應用中創建網頁
    """
    dev_mode = True
    protocal = "http" if dev_mode else "https"
    domain = "localhost:8000" if dev_mode else domain
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{protocal}://{domain}/api/v1/website/webpage/create/",
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
    user_access_token: str, 
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
    在自建的網站編輯器應用中創建元素
    將元素加入網頁的head/body 使用 target_webpage_uuid 以及 target_webpage_position 參數
    將元素創建相對於目標參考元素 使用 target_parent_relation_uuid 以及 target_relative_position 參數
    """
    dev_mode = True
    protocal = "http" if dev_mode else "https"
    domain = "localhost:8000" if dev_mode else domain
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{protocal}://{domain}/api/v1/website/element/r_create/?target_webpage_uuid={target_webpage_uuid}&target_webpage_position={target_webpage_position}&target_element_relation_uuid={target_parent_relation_uuid}&target_relative_position={target_relative_position}",
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
async def my_application_delete_webpage(user_access_token: str, webpage_uuid: str, ) -> str:
    """
    在自建的網站編輯器應用中刪除網頁
    """
    dev_mode = True
    protocal = "http" if dev_mode else "https"
    domain = "localhost:8000" if dev_mode else domain
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"{protocal}://{domain}/api/v1/website/webpage/{webpage_uuid}/delete/",
            headers={
                "Authorization": f"Bearer {user_access_token}",
                "Content-Type": "application/json"
            }
        ) as resp:
            text = await resp.text()
            return text


@mcp.tool()
async def my_application_delete_element(user_access_token: str, parent_relation_uuid: str, ) -> str:
    """
    在自建的網站編輯器應用中移除元素關係
    """
    dev_mode = True
    protocal = "http" if dev_mode else "https"
    domain = "localhost:8000" if dev_mode else domain
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"{protocal}://{domain}/api/v1/website/element/{parent_relation_uuid}/delete/",
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
    user_access_token: str, 
    webpage_uuid: str, 
    webpage_name: Optional[str],
    webpage_props:Optional[dict],
    webpage_data: Optional[dict]
    ) -> str:
    """
    在自建的網站編輯器應用中更新網頁
    """
    dev_mode = True
    protocal = "http" if dev_mode else "https"
    domain = "localhost:8000" if dev_mode else domain
    json = {}
    if webpage_name:
        json['name'] = webpage_name
    if webpage_props:
        json['props'] = webpage_props
    if webpage_data:
        json['data'] = webpage_data
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"{protocal}://{domain}/api/v1/website/webpage/{webpage_uuid}/update/",
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
    user_access_token: str, 
    element_uuid: str, 
    element_name: Optional[str],
    element_tag_name: Optional[str],
    element_inner_html: Optional[str],
    element_props:Optional[dict],
    element_type: Optional[Literal['custom_slider', 'ck_editor', 'customer_login_form', 'customer_register_form', 'product_detail', 'cart_detail', 'checkout_form', 'order_detail', 'order_payment', 'my_orders', 
                      'my_account_button','cart_button', 'shop', 'website_search_bar', 'contact_us_form', 'blog_post_detail']]
    ) -> str:
    """
    在自建的網站編輯器應用中更新元素
    """
    dev_mode = True
    protocal = "http" if dev_mode else "https"
    domain = "localhost:8000" if dev_mode else domain
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
        async with session.delete(
            f"{protocal}://{domain}/api/v1/website/element/{element_uuid}/update/",
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
async def list_my_media_assets(
    user_access_token: str, 
    store_uuid: str,
    media_type: Literal['image', 'video']
    ) -> str:
    """
    檢視商店的可用的素材
    """
    dev_mode = True
    protocal = "http" if dev_mode else "https"
    domain = "localhost:8000" if dev_mode else domain
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{protocal}://{domain}/api/v1/store/{store_uuid}/store_file/list/",
            headers={
                "Authorization": f"Bearer {user_access_token}",
                "Content-Type": "application/json"
            }
        ) as resp:
            text = await resp.text()
            return text


#元素動作
@mcp.tool()
async def taking_action_to_target_element(
    user_access_token: str, 
    parent_relation_uuid: str,
    action: Literal['mirror', 'clone', 'move'],

    target_webpage_uuid: Optional[str], 
    target_webpage_position: Optional[Literal['head', 'body']],
    target_parent_relation_uuid: Optional[str], 
    target_relative_position: Optional[Literal['before', 'after', 'in']]

    ) -> str:
    """
    在自建的網站編輯器應用中 移動/鏡像/克隆 目標元素
    將元素移至網頁的head/body 使用 target_webpage_uuid 以及 target_webpage_position 參數
    將元素移至相對於目標參考元素 使用 target_parent_relation_uuid 以及 target_relative_position 參數
    """

    dev_mode = True
    protocal = "http" if dev_mode else "https"
    domain = "localhost:8000" if dev_mode else domain
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"{protocal}://{domain}/api/v1/website/element/{parent_relation_uuid}/r_action/{action}/",
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
async def get_my_application_detail_element_structure(element_uuid: str, ) -> str:
    """
    在自建的網站編輯器應用中取得目標元素詳細的JSON格式資料
    """
    dev_mode = True
    protocal = "http" if dev_mode else "https"
    domain = "localhost:8000" if dev_mode else domain
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{protocal}://{domain}/api/v1/website/element/{element_uuid}/agent/retrieve/?detail=true"
        ) as resp:
            text = await resp.text()
            return text
        


@mcp.tool()
async def get_my_application_brief_webpage_structure(domain: str, webpage_name: str, object_uuid: Optional[str]) -> str:
    """
    在自建的網站編輯器應用中取得目標網頁精簡的JSON格式文本架構
    """
    dev_mode = True
    protocal = "http" if dev_mode else "https"
    domain = "localhost:8000" if dev_mode else domain
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{protocal}://{domain}/api/v1/website/webpage/{webpage_name or ''}/{object_uuid or ''}/agent/retrieve/?detail=false"
        ) as resp:
            text = await resp.text()
            return text



