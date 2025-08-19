from django.shortcuts import redirect
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from django.contrib import messages


@main_auth(on_cookies=True)
def create_deal(request):
    if request.method == 'POST':
        stage_id = request.POST.get('stage_id')
        title = request.POST.get('title')
        opportunity = request.POST.get('opportunity')
        currency = request.POST.get('currency')
        begindate = request.POST.get('begindate')
        closedate = request.POST.get('closedate')
        priorities = request.POST.get('priorities')

        fields = {
            'TITLE': title,
            'STAGE_ID': stage_id,
            'OPPORTUNITY': opportunity,
            'BEGINDATE': begindate,
            'CURRENCY_ID': currency,
            'CLOSEDATE': closedate,
            'UF_CRM_1755509630': priorities,
            'ASSIGNED_BY_ID': request.bitrix_user.id,
        }

        if begindate and closedate and closedate < begindate:
            messages.error(request, "Дата завершения не может быть раньше даты начала.")
            return redirect("deals_table")

        bx24 = request.bitrix_user_token
        try:
            bx24.call_api_method("crm.deal.add", {'fields': fields})
        except Exception as e:
            print(f"Ошибка при создании сделки: {e}")

    return redirect('deals_table')