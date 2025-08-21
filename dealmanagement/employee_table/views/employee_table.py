import random
import datetime
import pytz
from django.shortcuts import render
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
import time


@main_auth(on_cookies=True)
def employee_table(request):
    bx24 = request.bitrix_user_token
    employees = []

    try:
        users_resp = bx24.call_api_method("user.get", {
            "FILTER": {"ACTIVE": "Y"},
            "SELECT": ["ID", "NAME", "LAST_NAME", "UF_DEPARTMENT"]
        })

        users = users_resp.get("result", [])
        user_map = {str(u["ID"]): u for u in users}

        dept_resp = bx24.call_api_method("department.get", {
            "SELECT": ["ID", "NAME", "UF_HEAD", "PARENT"]
        })
        departments = dept_resp.get("result", [])
        dep_map = {str(d["ID"]): d for d in departments}

        department_managers = {}
        for dep in departments:
            dep_id = str(dep["ID"])
            head_id = dep.get("UF_HEAD")
            if head_id and str(head_id) in user_map:
                head_user = user_map[str(head_id)]
                manager_name = f"{head_user.get('LAST_NAME', '')} {head_user.get('NAME', '')}".strip()
                if manager_name:
                    department_managers[dep_id] = {
                        'name': manager_name,
                        'id': head_id
                    }

        def get_all_managers(dep_ids, current_user_id):
            managers = []
            visited = set()
            added_manager_ids = set()

            for dep_id in dep_ids:
                current_dep_id = str(dep_id)
                hierarchy_level = 0

                while current_dep_id and current_dep_id in dep_map and current_dep_id not in visited:
                    visited.add(current_dep_id)

                    if current_dep_id in department_managers:
                        manager_info = department_managers[current_dep_id]
                        manager_id_str = str(manager_info['id'])

                        if (manager_id_str != str(current_user_id) and
                                manager_id_str not in added_manager_ids):
                            manager_info_copy = manager_info.copy()
                            manager_info_copy['hierarchy_level'] = hierarchy_level
                            managers.append(manager_info_copy)
                            added_manager_ids.add(manager_id_str)

                    parent_id = dep_map[current_dep_id].get("PARENT")
                    if parent_id:
                        current_dep_id = str(parent_id)
                        hierarchy_level += 1
                    else:
                        break

            managers.sort(key=lambda x: x['hierarchy_level'])
            return managers

        generate_calls = request.GET.get("generate_calls")
        if generate_calls:
            _generate_fake_calls_real(bx24, users)

        for user in users:
            user_id = user["ID"]
            user_name = f"{user.get('LAST_NAME', '')} {user.get('NAME', '')}".strip()
            position = user.get("WORK_POSITION", "")
            dep_ids = user.get("UF_DEPARTMENT", [])
            managers = get_all_managers(dep_ids, user_id) if dep_ids else []

            calls_count = _get_calls_last_24h(bx24, user_id)

            employees.append({
                "id": user_id,
                "name": user_name,
                "position": position,
                "managers": managers,
                "department_ids": dep_ids,
                "calls": calls_count
            })

        employees.sort(key=lambda x: x['name'])

    except Exception as e:
        import traceback
        traceback.print_exc()
        return render(request, "employee_table.html", {"error": str(e)})

    return render(request, "employee_table.html", {"employees": employees})


def _get_calls_last_24h(bx24, user_id):
    since = (datetime.datetime.utcnow() - datetime.timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S")
    calls_resp = bx24.call_api_method("voximplant.statistic.get", {
        "FILTER": {
            "PORTAL_USER_ID": user_id,
            "CALL_TYPE": 2,
            ">=CALL_DURATION": 61,
            ">=CALL_START_DATE": since,
        },
        "SELECT": ["CALL_ID"]
    })
    result = calls_resp.get("result", [])
    return len(result)


def _generate_fake_calls_real(bx24, users):
    timezone = pytz.timezone("Europe/Moscow")
    now = datetime.datetime.now(timezone)

    PHONE_NUMBERS = ["+79218455312", "+77756493455", "+74356756354", "+79083456732", "+79064326754"]

    for user in users:
        user_id = user["ID"]
        num_calls = random.randint(1, 3)

        for _ in range(num_calls):
            phone = random.choice(PHONE_NUMBERS)
            duration = random.randint(1, 600)

            call_start = now - datetime.timedelta(seconds=random.randint(0, 86400))
            call_start_iso = call_start.isoformat()

            try:

                register_data = bx24.call_api_method("telephony.externalcall.register", {
                    "USER_ID": user_id,
                    "PHONE_NUMBER": phone,
                    "CALL_START_DATE": call_start_iso,
                    "TYPE": 2,
                    "CRM_CREATE": 0,
                    "SHOW": 0,
                })


                call_id = register_data.get("result", {}).get("CALL_ID")

                if call_id:
                    bx24.call_api_method("telephony.externalcall.finish", {
                        "CALL_ID": call_id,
                        "USER_ID": user_id,
                        "DURATION": duration,
                        "STATUS_CODE": "200",
                        "ADD_TO_CHAT": 0,
                    })
                    time.sleep(0.5)

            except Exception as e:
                print(f"Ошибка при генерации звонка для пользователя {user_id}: {e}")
                continue