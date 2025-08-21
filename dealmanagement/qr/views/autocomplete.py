import json
from django.http import JsonResponse
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth

@main_auth(on_cookies=True)
def autocomplete(request):
    query = request.GET.get("q", "").strip()
    results = []

    if query and hasattr(request, "bitrix_user_token"):
        bx24 = request.bitrix_user_token
        try:
            resp = bx24.call_api_method("crm.product.list", {
                "filter": {"%NAME": query},
                "select": ["ID", "NAME", "PRICE"]
            })

            if isinstance(resp, str):
                resp = json.loads(resp)

            products = resp.get("result", []) if isinstance(resp, dict) else []

            for p in products:
                results.append({
                    "id": p.get("ID"),
                    "name": p.get("NAME"),
                    "price": p.get("PRICE")
                })
        except Exception as e:
            print(f"Ошибка autocomplete: {e}")

    return JsonResponse(results, safe=False)
