from starlette.applications import Starlette
from starlette.responses import HTMLResponse, FileResponse
from starlette.routing import Route
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import List
from jinja2 import Template
import aiohttp
import time


class VisitingChef(BaseModel):
    restaurant: str
    chefs: List[str]


def beautify(text):
    return text.strip().replace("a.m.", "AM").replace("p.m.", "PM")


async def scrape_visiting_chefs(url: str) -> List[VisitingChef]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.text()
    soup = BeautifulSoup(content, 'html.parser')
    specials_div = soup.find('div', class_='col-12 col-sm-6 col-lg-4').find_all('div')
    data = []

    if len(specials_div) > 0:
        for restaurant_block in specials_div:
            if not restaurant_block.find('h5'):
                continue
            restaurant_name = restaurant_block.find('h5').text.strip()
            chefs = [beautify(chef.find_next('em').text) for chef in restaurant_block.find_all('a', href=True, chefid=True)]
            data.append(VisitingChef(restaurant=restaurant_name, chefs=chefs))

    return data


async def homepage(request):
    url = "https://www.rit.edu/dining/menus"
    chefs_data = await scrape_visiting_chefs(url)

    with open('template.html') as file:
        template_content = file.read()

    today = time.strftime("%A, %B %d, %Y")

    content = ""
    for item in chefs_data:
        content += f"<h2>{item.restaurant}</h2><ul>"
        for chef in item.chefs:
            content += f"<li>{chef}</li>"
        content += "</ul>"

    template = Template(template_content)
    html = template.render(
        today=today,
        content=content,
        updated="Aug 28, 2024"
    )

    return HTMLResponse(html)


app = Starlette(debug=True, routes=[
    Route('/', homepage),
    Route('/rit-logo.webp', endpoint=lambda request: FileResponse('rit-logo.webp')),
    Route('/tiger.png', endpoint=lambda request: FileResponse('tiger.png'))
])
