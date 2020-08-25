from splinter import Browser
from bs4 import BeautifulSoup
import time
import pandas as pd



def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    return Browser("chrome", **executable_path, headless=False)


def scrape_info():
    browser = init_browser()

    # URL of news page to be scraped
    nasa_news_url = 'https://mars.nasa.gov/news/'
    browser.visit(nasa_news_url)

    time.sleep(1)

    # Create news BeautifulSoup object; parse with 'html.parser'
    html = browser.html
    nasa_news_soup = BeautifulSoup(html, 'html.parser')

    # Collect the latest News Title and Paragraph Text
    news_title = nasa_news_soup.find_all('div', class_='content_title')[1].text
    news_p = nasa_news_soup.find_all('div', class_='article_teaser_body')[0].text

    # URL of images page to be scraped and create image bs object
    nasa_image_url='https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(nasa_image_url)
    html = browser.html
    nasa_image_soup = BeautifulSoup(html, 'html.parser')

    # Get featured image link
    nasa_jpl_url= 'https://www.jpl.nasa.gov'
    relative_image= nasa_image_soup.find('div', class_='carousel_container').find('div', class_='carousel_items')
    relative_image_path= relative_image.find('article', class_="carousel_item")['style']

    featured_image_url_1= nasa_jpl_url + ((relative_image_path).strip("^background-image: url\(\'"))
    featured_image_url=featured_image_url_1.strip("$\'\);")

    # Scrape the table containing facts about Mars
    mars_facts_url = 'https://space-facts.com/mars/'
    tables = pd.read_html(mars_facts_url)
    mars_facts_df_1 = tables[2]
    mars_facts_df_1.columns = ["Description", "Mars"]
    mars_facts_df=mars_facts_df_1.set_index('Description')
    #Use Pandas to convert the data to a HTML table string
    mars_html_table = mars_facts_df.to_html()
    mars_html_table.replace('\n', '')

    # Scrape Mars Hemispheres 
    mars_usgs_url = 'https://astrogeology.usgs.gov'
    mars_hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    browser.visit(mars_hemispheres_url)
    mars_hemispheres_html = browser.html
    mars_hemispheres_soup = BeautifulSoup(mars_hemispheres_html, 'html.parser')

    # Mars hemispheres products data
    mars_hemispheres_list = mars_hemispheres_soup.find('div', class_='collapsible results')
    mars_hemispheres_data = mars_hemispheres_list.find_all('div', class_='item')

    hemisphere_image_urls = []
    # Iterate through mars hemisphere data
    for hem in mars_hemispheres_data:
        # Get Title
        mars_hemisphere = hem.find('div', class_="description")
        title = mars_hemisphere.h3.text
        
        # Get image link 
        hemisphere_link = mars_hemisphere.a["href"]    
        browser.visit(mars_usgs_url + hemisphere_link)
        
        hem_image_html = browser.html
        hem_image_soup = BeautifulSoup(hem_image_html, 'html.parser')
        
        image_link = hem_image_soup.find('div', class_='downloads')
        image_url = image_link.find('li').a['href']

        # Create Dictionary and append to a list
        hem_image_dict = {}
        hem_image_dict['title'] = title
        hem_image_dict['img_url'] = image_url
        
        hemisphere_image_urls.append(hem_image_dict)

    # Store data in a dictionary
    mars_data = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_image_url": featured_image_url,
        "mars_html_table": str(mars_html_table),
        "hemisphere_image_urls": hemisphere_image_urls
    }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data
