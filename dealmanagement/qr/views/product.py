import json
import secrets
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from qr.models import PublicProductLink
import qrcode
from io import BytesIO
from django.http import HttpResponse

@main_auth(on_cookies=True)
def product(request):
    product = None
    error = None
    if hasattr(request, "bitrix_user_token"):
        bx24 = request.bitrix_user_token
        uid = request.GET.get("uid")
        if uid:
            try:
                prod_resp = bx24.call_api_method("crm.product.get", {"id": uid})
                if isinstance(prod_resp, str):
                    prod_resp = json.loads(prod_resp)
                product_data = prod_resp.get("result") if isinstance(prod_resp, dict) else None
                if product_data:
                    images_resp = bx24.call_api_method("catalog.productImage.list", {"productId": uid})
                    if isinstance(images_resp, str):
                        images_resp = json.loads(images_resp)
                    images_list = images_resp.get("result", {}).get("productImages", []) if isinstance(images_resp, dict) else []
                    image_urls = [img.get("detailUrl") for img in images_list if img.get("detailUrl")]
                    product = {
                        "id": product_data.get("ID"),
                        "name": product_data.get("NAME"),
                        "price": product_data.get("PRICE"),
                        "description": product_data.get("DESCRIPTION"),
                        "images": image_urls,
                    }

                    links = PublicProductLink.objects.filter(product_id=uid)
                    product["links"] = links
            except Exception as e:
                error = f"Ошибка при получении товара: {e}"
    return render(request, "product.html", {"product": product, "error": error})

@main_auth(on_cookies=True)
def generate_qr(request, uid):
    bx24 = request.bitrix_user_token
    try:
        prod_resp = bx24.call_api_method("crm.product.get", {"id": uid})
        if isinstance(prod_resp, str):
            prod_resp = json.loads(prod_resp)
        product_data = prod_resp.get("result") if isinstance(prod_resp, dict) else {}
        images_resp = bx24.call_api_method("catalog.productImage.list", {"productId": uid})
        if isinstance(images_resp, str):
            images_resp = json.loads(images_resp)
        images_list = images_resp.get("result", {}).get("productImages", []) if isinstance(images_resp, dict) else []
        image_urls = [img.get("detailUrl") for img in images_list if img.get("detailUrl")]

        link = PublicProductLink.objects.create(
            product_id=uid,
            token=uuid.uuid4(),
            product_data={
                "id": product_data.get("ID"),
                "name": product_data.get("NAME"),
                "price": product_data.get("PRICE"),
                "description": product_data.get("DESCRIPTION"),
                "images": image_urls
            }
        )
    except Exception as e:
        print(f"Ошибка при создании QR: {e}")
    return redirect(f'/search/?uid={uid}')


@main_auth(on_cookies=True)
def qr_code(request, token):

    link = get_object_or_404(PublicProductLink, token=uuid.UUID(str(token)))

    public_url = request.build_absolute_uri(reverse("public_product", args=[str(link.token)]))
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(public_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return HttpResponse(buffer, content_type="image/png")


def public_product(request, token):
    link = get_object_or_404(PublicProductLink, token=token)
    product = link.product_data if link.product_data else {"id": link.product_id, "name": "Секретный товар", "price": "N/A", "description": "Описание доступно только через Bitrix API", "images": []}
    return render(request, "public_product.html", {"product": product})
