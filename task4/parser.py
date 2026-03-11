from playwright.sync_api import sync_playwright
import time


def extract_product_data(card, page=None):
    """
    Извлекает данные товара из карточки (универсально для каталога и страницы товара)
    
    :param card: элемент карточки товара (Locator)
    :param page: объект страницы 
    :return: dict с данными товара
    """
    product = {}
    
    try:
        # id
        product['product_id'] = card.get_attribute('data-product-uid')
        
        # название
        title_el = card.locator('.js-store-prod-name').first
        if title_el.count() > 0:
            product['title'] = title_el.text_content().strip()
        
        # описание
        description = None
        for selector in [
            '.js-store-prod-all-text',      # Полное описание (страница товара)
            '.js-store-prod-descr',         # Краткое описание (каталог)
        ]:
            
            desc_el = card.locator(selector).first
            if desc_el.count() > 0:
                description = desc_el.text_content().strip()
                if description:
                    break
        product['description'] = description
        
        # цена
        price_el = card.locator('[data-product-price-def]').first
        if price_el.count() > 0:
            price_attr = price_el.get_attribute('data-product-price-def')
            if price_attr and price_attr.isdigit():
                product['price'] = price_attr
        
        # ссылка на сам товар
        product_url = card.get_attribute('data-product-url')
        if product_url:
            product['url'] = product_url
        
        # ссылка на картинку товара
        product_img = card.get_attribute('data-product-img')
        if product_img:
            product['image'] = product_img.strip()
         
    except Exception as e:
        print(f"Ошибка: {e}")
        return None
    
    return product if product.get('title') else None


def parse(url="https://divoroom.store/catalog", headless=True):
    products = []
    
    with sync_playwright() as p:
        with p.chromium.launch(headless=headless) as browser:
            page = browser.new_page()
            
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            is_product_page = page.locator('.js-store-product.t-store__product-snippet').count() > 0
            
            if is_product_page:
                page.wait_for_selector('[data-product-uid]', timeout=15000)
                time.sleep(0.5)
                
                card = page.locator('.js-store-product.t-store__product-snippet').first
                
                if card.count() > 0:
                    product = extract_product_data(card, page)
                    if product:
                        products.append(product)
            
            else:
                page.wait_for_selector('.js-product.t-store__card', timeout=15000)
                time.sleep(0.5)
                
                # Нажимаем "загрузить ещё" пока не дойдём до конца
                while True:
                    load_more_btn = page.locator('.js-store-load-more-btn-text').first
                    
                    if load_more_btn.count() > 0 and load_more_btn.is_visible():
                        load_more_btn.scroll_into_view_if_needed()
                        load_more_btn.click()
                        
                        try:
                            page.wait_for_load_state('networkidle', timeout=10000)
                        except:
                            pass
                        time.sleep(1)
                    else:
                        break
                
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)
                
                cards = page.locator('.js-product.t-store__card').all()
                
                for _, card in enumerate(cards):
                    try:
                        product = extract_product_data(card)
                        if product:
                            products.append(product)
                    except Exception as e:
                        print(f"Ошибка: {e}")
    
    return products