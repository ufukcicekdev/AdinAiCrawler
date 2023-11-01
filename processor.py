import uuid
from datetime import datetime
import datetime as dt
from utility.db import DBHelper
from fileupload import *
import json
import os
import re
from logger import log_to_db
from dotenv import load_dotenv



# Load the .env file
load_dotenv()


db_helper = DBHelper("crawlerDb")

AWS_STORAGE_DICT_PATH = os.getenv('AWS_STORAGE_DICT_PATH')
AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN')


def get_campaings_links(page, selector_dict, domain_link, domain_id, base_url, for_loop, domain_name, run_js):
    products = page.query_selector_all(for_loop)
    product_count = len(products)
    selector, attribute = selectors_parse("menu_name", selector_dict)
    menu_name = page.evaluate(f"document.querySelector('{selector}').innerText;")
    try:
        for product in range(product_count):
            if run_js:
                try:
                    page.evaluate(run_js)
                    page.wait_for_timeout(3000)
                except Exception as e:
                    log_to_db('ERROR', str(e))

            campaing_name_selector, campaing_name_attribute = selectors_parse("campaing_name", selector_dict)
            geturl_selector, geturl_attribute = selectors_parse("geturl", selector_dict)
            telephone_selector, telephone_attribute = selectors_parse("telephone", selector_dict)
            socialmedia_selector, socialmedia_attribute = selectors_parse("socialmedia", selector_dict)
            celular_selector, celular_attribute = selectors_parse("celular", selector_dict)
            campaingsdetail_selector, campaingsdetail_attribute = selectors_parse("campaingsdetail", selector_dict)
            campaings_price_selector, campaings_price_attribute = selectors_parse("campaings_price", selector_dict)
            screenshots_selector, screenshots_attribute = selectors_parse("screenshots", selector_dict)

    

            img_url = take_screenshot(page, screenshots_selector, product, domain_name)
            campaing_name = get_inner_text(page, campaing_name_selector, campaing_name_attribute, product)
            campaing_url = get_href_links(page, geturl_selector, geturl_attribute, product, base_url)
            telephone_options = get_inner_text(page, telephone_selector, telephone_attribute, product)
            socialmedia_options = get_inner_text(page, socialmedia_selector, socialmedia_attribute, product)
            celular_options = get_inner_text(page, celular_selector, celular_attribute, product)
            campaingsdetail_options = get_inner_text(page, campaingsdetail_selector, campaingsdetail_attribute, product)
            campaings_price_options = get_inner_text(page, campaings_price_selector, campaings_price_attribute, product)

            create_campaign_json(domain_id,
                menu_name, campaing_name, campaing_url, telephone_options,
                socialmedia_options, celular_options, campaingsdetail_options,
                campaings_price_options, img_url
            )

        next_page_selector, next_page_attribute = selectors_parse("next_page", selector_dict)

        if next_page_selector:
            while True:
                result = click_button(page, next_page_selector)
                if result:
                    get_campaings_links(page, selector_dict, domain_link, domain_id, base_url, for_loop, domain_name)
                else:
                    break

    except Exception as e:
        log_to_db('ERROR', str(e))

def create_campaign_json(domain_id, menu_name, campaing_name, campaing_url, telephone_options, socialmedia_options, celular_options, campaingsdetail_options, campaings_price_options, img_url):
    
    # campaign_data = {
    #     "domain_id":domain_id,
    #     "menu_name": menu_name,
    #     "campaign_name": campaing_name,
    #     "campaign_url": campaing_url,
    #     "telephone_options": telephone_options,
    #     "socialmedia_options": socialmedia_options,
    #     "celular_options": celular_options,
    #     "campaingsdetail_options": campaingsdetail_options,
    #     "campaings_price_options": campaings_price_options,
    #     "img_url":img_url
    # }
    query_insert_links(domain_id, menu_name, campaing_name, campaing_url, telephone_options, socialmedia_options, celular_options, campaingsdetail_options, campaings_price_options, img_url)


def query_insert_links(domain_id, menu_name, campaing_name, campaing_url, telephone_options, socialmedia_options, celular_options, campaingsdetail_options, campaings_price_options, img_url):
    try:
        now_time = dt.datetime.now()
        created_at = now_time.strftime("%Y-%m-%d")
        time_stamp = now_time.strftime("%Y-%m-%d %H:%M:%S")
        sql_script = ("""INSERT INTO public.temp_adin_telecommunication_product_detail
                (domain_id, menu_title, campaign_title, campaign_url, 
                    minute_usage, social_media_gb, celular_gb, campaign_detail, 
                    campaign_price_detail, img_url, create_date, "time_stamp") 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""")
        values = (domain_id, menu_name, campaing_name, campaing_url, telephone_options, socialmedia_options, celular_options, campaingsdetail_options, campaings_price_options, img_url, created_at, time_stamp)
        db_helper.execute(sql_script,values)
    except Exception as e:
        log_to_db('ERROR', str(e))


def save_campaigns_to_json(campaigns, filename):
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(campaigns, json_file, ensure_ascii=False, indent=4)


def take_screenshot(page, selector, index, domain_name):
    element = page.query_selector_all(selector)[index]
    if element:
        current_date = datetime.now().date()  # Sadece tarih alınır
        date_string = current_date.strftime("%Y-%m-%d")  # Tarih formatı
        screenshot_filename = f'ScreenShots/{domain_name}_{date_string}_{str(uuid.uuid4())}.png'
        element.screenshot(path=screenshot_filename)
        file_name_to_upload = screenshot_filename  # Yüklemek istediğiniz dosyanın adını belirtin
        local_file_path = os.path.join( file_name_to_upload)
        remote_file_name = f'{AWS_STORAGE_DICT_PATH}{domain_name}/{date_string}/{file_name_to_upload}'  # Uzak depo yolunu belirtin
        upload_file_to_s3(local_file_path, remote_file_name)
        os.remove(local_file_path)
        page.wait_for_load_state()
        page.wait_for_timeout(5000)

        img_url = AWS_S3_CUSTOM_DOMAIN + "/" + remote_file_name
    else:
        print(f"Element not found: {selector}")
        img_url = ""

    return img_url


def click_button(page, selector):
    result = False
    try:
        page.evaluate(f"document.querySelector('{selector}').click();")
        page.wait_for_timeout(1500)
        result = True
        return result
    except Exception as e:
        log_to_db('ERROR', str(e))
        return result

def get_href_links(page, selector, attribute, index, base_url):
    try:
        link = page.evaluate(f"document.querySelectorAll('{selector}')[{index}].getAttribute('{attribute}');")
        if link is not None:
            url = base_url_check(link, base_url)
        else:
            url = ""
    except Exception as e:
        log_to_db('ERROR', str(e))
        url = ""
    return url

def get_inner_text(page, selector, attribute, index):
    try:
        result = page.evaluate(f"document.querySelectorAll('{selector}')[{index}].innerText;")
        result = re.sub(r'[\n\t]', '', result)
    except Exception as e:
        log_to_db('ERROR', str(e))
        result = ""
    return result

def selectors_parse(selector_name, selector_dict):
    for selector in selector_dict:
        for key, value in selector.items():
            if key == selector_name:
                selector = value.get("selector")
                attribute = value.get("attribute")
                return selector, attribute

def custom_selectors_parse(selector_name, selector_dict):
    for selector in selector_dict:
        for key, value in selector.items():
            if key == selector_name:
                selector = value.get("selector")
                attribute = value.get("attribute")
                return selector, attribute

def base_url_check(link, base_url):
    if link:
        if base_url in link:
            link = link
        else:
            link = base_url + link
        return link

def scroll_page(page):
    time = 1000
    while page.evaluate("document.body.scrollHeight") - page.evaluate("window.scrollY") > 720:
        next = page.evaluate("window.innerHeight")
        next = next - 300
        page.evaluate(f"window.scrollBy(0,{next});")
        page.wait_for_timeout(time)
    
    # Sayfa sonuna ulaşıldığında döngüyü sonlandır
    print("Sayfa sonuna ulaşıldı.")
