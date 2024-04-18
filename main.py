from starlette.applications import Starlette
from starlette.responses import HTMLResponse, FileResponse
from starlette.routing import Route
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import List
import aiohttp
import time

class VisitingChef(BaseModel):
    restaurant: str
    chefs: List[str]

async def scrape_visiting_chefs(url: str) -> List[VisitingChef]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.text()
    soup = BeautifulSoup(content, 'html.parser')
    specials_div = soup.find('div', class_='todays-specials-div')
    data = []
    
    if specials_div:
        restaurant_blocks = specials_div.find_all('p', class_='h5')
        for block in restaurant_blocks:
            restaurant_name = block.text.strip()
            chefs = [chef.text.strip() for chef in block.find_next_sibling('ul').find_all('a')]
            data.append(VisitingChef(restaurant=restaurant_name, chefs=chefs))
    
    return data

async def homepage(request):
    url = "https://www.rit.edu/dining/menus"
    chefs_data = await scrape_visiting_chefs(url)
    html_content = """
        <html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
            <link rel="icon" type="image/png" href="tiger.png">

            <script defer data-domain="rit-dining.mufasa.cc" src="https://analytics.paracosmos.studio/js/script.js"></script>

            <meta name="description" content="Today's visiting chefs at RIT Dining">
            <meta name="author" content="@mufasa159">
            <meta name="keywords" content="RIT, Dining, Visiting Chefs, Daily Specials">
            <meta name="robots" content="index, follow">

            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>RIT Dining - Today's Visiting Chefs</title>
            <style>
                body { 
                    font-family: Inter, sans-serif;
                    margin: 40px auto;
                    background-color: #F6F6F6;
                    color: #000;
                    max-width: 600px;
                }

                h2 {
                    font-size: 1em;
                    margin-bottom: 10px;
                    margin-top: 30px;
                    font-weight: 600;
                    color: #F76902;
                }

                ul { 
                    list-style-type: none;
                    padding: 0;
                }

                li { 
                    background-color: #FFF;
                    padding: 10px;
                    margin-bottom: 5px;
                    border-radius: 5px;
                    border: 1px solid #E5E5E5;
                    color: #686868;
                }
                
                .footer {
                    text-decoration: none;
                    margin: 50px auto 0px auto;
                    font-size: 0.8em;
                    color: #A5A5A5;
                    text-align: center;
                    font-weight: 400;
                }

                a {
                    color: #A5A5A5;
                    text-decoration: none;
                    transition: color 0.2s;
                }

                a:hover {
                    color: #07F;
                }

                img {
                    display: block;
                    max-width: 200px;
                    height: auto;
                    margin: 0px auto 20px auto;
                }

                .date {
                    font-size: 0.9em;
                    color: #262626;
                    margin-bottom: 50px;
                    text-align: center;
                    font-weight: 600;
                }

                @media screen and (max-width: 768px) {
                    body {
                        margin: 40px 20px;
                        max-width: none;
                    }
                }
            </style>
        </head>
        <body>
            <img src='./rit-logo.webp' alt='RIT Logo'>
    """
    todays_date = time.strftime("%A, %B %d, %Y")
    html_content += f"<p class='date'>{todays_date}</p>"
    for item in chefs_data:
        html_content += f"<h2>{item.restaurant}</h2><ul>"
        for chef in item.chefs:
            html_content += f"<li>{chef[:-1]}</li>"
        html_content += "</ul>"
    html_content += """
        <p class='footer'>
            Data from  
            <a href='https://www.rit.edu/dining/menus' target='_blank'>
                https://www.rit.edu/dining/menus
            </a>
            <br/>

            Developed by 
            <a href='https://github.com/mufasa159' target='_blank'>
                @mufasa159
            </a>
        </p>
    </body>
    </html>
    """
    return HTMLResponse(html_content)

app = Starlette(debug=True, routes=[
    Route('/', homepage),
    Route('/rit-logo.webp', endpoint=lambda request: FileResponse('rit-logo.webp')),
    Route('/tiger.png', endpoint=lambda request: FileResponse('tiger.png'))
])
