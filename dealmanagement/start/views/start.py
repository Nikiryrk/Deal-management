from django.shortcuts import render
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from datetime import datetime
from django.conf import settings


@main_auth(on_start=True, set_cookie=True)
def start(request):
    app_settings = settings.APP_SETTINGS
    deals = []

    STAGE_NAMES = {
        'NEW': 'Новая',
        'PREPARATION': 'Подготовка документов',
        'PREPAYMENT_INVOICE': 'Счёт на предоплату',
        'EXECUTING': 'В работе',
        'FINAL_INVOICE': 'Финальный счёт',
    }

    PRIORITY_NAMES = {
        '50': 'Высокий',
        '52': 'Средний',
        '54': 'Низкий',
    }

    if hasattr(request, 'bitrix_user_token'):
        bx24 = request.bitrix_user_token
        try:
            deals_response = bx24.call_api_method(
                'crm.deal.list',
                {
                    'filter': {
                        'ASSIGNED_BY_ID': request.bitrix_user.id,
                        'CLOSED': 'N'
                    },
                    'order': {'DATE_CREATE': 'DESC'},
                    'select': [
                        'ID', 'TITLE', 'STAGE_ID'10-ти
                        'OPPORTUNITY', 'CURRENCY_ID',
                        'BEGINDATE', 'CLOSEDATE', 'DATE_CREATE','UF_CRM_1755509630'
                    ],
                    'start': 0
                }
            )
            deals = deals_response.get('result', [])[:10]
            for deal in deals:
                deal['formatted_begin'] = format_date(deal.get('BEGINDATE'))
                deal['formatted_close'] = format_date(deal.get('CLOSEDATE'))
                deal['stage_name'] = STAGE_NAMES.get(deal.get('STAGE_ID'), deal.get('STAGE_ID', 'Неизвестно'))
                priority_value = str(deal.get('UF_CRM_1755509630', ''))
                deal['priority_name'] = PRIORITY_NAMES.get(priority_value, 'Не указан')
                deal['priority_class'] = f"priority-{priority_value}"
        except Exception as e:
            print(f"Ошибка при получении сделок: {e}")

    return render(request, 'start_page.html', {
        'request': request,
        'app_settings': app_settings,
        'deals': deals,
        'deals_count': len(deals)
    })


def format_date(date_str):
    if not date_str:
        return "-"
    try:
        return (
            datetime
            .fromisoformat(date_str.replace('Z', '+00:00'))
            .strftime('%d.%m.%Y')
        )
    except:
        return date_str[:10] if date_str else "-"
