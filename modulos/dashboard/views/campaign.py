from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from calendar import monthrange
from .utils import call_api
import json

@login_required
def dashboard_campaign(request):
    try:
        data_inicio = request.GET.get('dataInicio')
        data_fim = request.GET.get('dataFim')

        # Se os parâmetros não forem passados, definir o início e o fim do mês atual
        if not data_inicio:
            data_inicio = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        if not data_fim:
            today = datetime.now()
            last_day = monthrange(today.year, today.month)[1]
            data_fim = today.replace(day=last_day).strftime('%Y-%m-%d')

        # Faz a requisição para a API
        api_url = f"https://control.star.dev.br/api/campaigns?dataInicio={data_inicio}&dataFim={data_fim}"
        campaigns_data = call_api(request, "GET", api_url)

        if not campaigns_data:
            return redirect('dashboard_campaign')

        # Inicializando as variáveis globais para os cálculos
        total_numbers, total_success, total_erro, total_responses = 0, 0, 0, 0
        total_numbers_now, total_success_now, total_erro_now, total_responses_now = 0, 0, 0, 0
        campaign_total_now, campaign_finaly, campaign_finaly_now = 0, 0, 0

        # Itera sobre as campanhas e realiza os cálculos
        campaigns = campaigns_data.get('campaigns', [])
        for campaign in campaigns:
            total_numbers_value = int(campaign.get('total_numbers', 0))
            total_success_value = int(campaign.get('send_success', 0))
            total_error_value = int(campaign.get('send_error', 0))
            total_responses_value = int(campaign.get('response_count', 0))

            # Acumula os dados globais
            total_numbers += total_numbers_value
            total_success += total_success_value
            total_erro += total_error_value
            total_responses += total_responses_value

            # Verifica se a campanha foi finalizada
            if campaign.get('status') == 'finalizado':
                campaign_finaly += 1

            # Calcula a taxa de resposta individual da campanha
            response_rate = (total_responses_value / total_success_value) * 100 if total_success_value > 0 else 0
            campaign['response_rate'] = round(response_rate, 1)

            # Verifica se a campanha foi iniciada hoje
            start_date = datetime.strptime(campaign.get('start_date', ''), '%Y-%m-%dT%H:%M:%S.%f').date()
            if start_date == datetime.now().date():
                total_numbers_now += total_numbers_value
                total_success_now += total_success_value
                total_erro_now += total_error_value
                total_responses_now += total_responses_value
                campaign_total_now += 1
                if campaign.get('status') == 'finalizado':
                    campaign_finaly_now += 1

        # Calcula as taxas de resposta globais
        global_response_rate = (total_responses / total_success) * 100 if total_success > 0 else 0
        response_rate_now = (total_responses_now / total_success_now) * 100 if total_success_now > 0 else 0

        # Renderiza os dados para o template
        return render(request, 'dashboard/dashboard-campaign.html', {
            'campaigns': campaigns,
            'total_numbers': total_numbers,
            'total_numbers_now': total_numbers_now,
            'campaign_total': len(campaigns),
            'campaign_total_now': campaign_total_now,
            'total_success': total_success,
            'total_success_now': total_success_now,
            "total_erro": total_erro,
            'total_erro_now': total_erro_now,
            'response_rate': f"{global_response_rate:.2f}",
            'response_rate_now': f"{response_rate_now:.2f}",
            'campaign_finaly': campaign_finaly,
            'campaign_finaly_now': campaign_finaly_now
        })

    except Exception as e:
        print(f"[dashboard_campaign] Error: {e}")
        messages.error(request, f"Erro ao carregar campanhas: {str(e)}")
        return redirect('dashboard_campaign')

@login_required
def details_campaign(request, campaign_id):
    try:
        api_url = f"https://control.star.dev.br/api/campaigns/{campaign_id}"
        campaign_response = call_api(request, "GET", api_url)

        if not campaign_response:
            print(f"[api_url] error não request sem resposta {campaign_response}")
            return redirect('dashboard_campaign')

        campaign_list = json.loads(campaign_response.get('campaign', '[]'))
        if not campaign_list:
            messages.error(request, "Dados da campanha não encontrados.")
            return redirect('dashboard_campaign')

        campaign_obj = campaign_list[0]  # Pega o primeiro elemento da lista
        campaign_fields = campaign_obj.get('fields', {})
        campaign_fields['id'] = campaign_obj['pk']

        logs_data_str = campaign_response.get('logs', '[]')
        logs = json.loads(logs_data_str)

        responses = campaign_response.get('responses', 0)

        # Inicializando os arrays de contagem para cada hora do dia
        array_horas_sucesso = [0] * 24
        array_horas_erro = [0] * 24

        # Itera sobre os logs e separa os dados por hora e status
        for log in logs:
            fields = log.get('fields', {})
            criado = fields.get('created_at')
            status = fields.get('status')

            if criado:
                data_criacao = datetime.strptime(criado, '%Y-%m-%dT%H:%M:%S.%f')
                hora = data_criacao.hour
                if status == 'sucesso':
                    array_horas_sucesso[hora] += 1
                elif status == 'erro':
                    array_horas_erro[hora] += 1

        total_numbers = int(campaign_fields.get('total_numbers', 0))
        total_success = int(campaign_fields.get('send_success', 0))
        total_erro = int(campaign_fields.get('send_error', 0))
        response_rate = (responses / total_success) * 100 if total_success > 0 else 0

        return render(request, 'details/details-campaign.html', {
            'campaign': campaign_fields,
            'total_numbers': total_numbers,
            'total_success': total_success,
            "total_erro": total_erro,
            'response_rate': f"{response_rate:.2f}",
            'msg_sucess': array_horas_sucesso,
            'msg_erro': array_horas_erro,
            'logs': logs,
        })

    except Exception as e:
        print(f"[details_campaign] Error: {e}")
        messages.error(request, f"Erro ao carregar detalhes da campanha: {str(e)}")
        return redirect('dashboard_campaign')

@login_required
def encerrar_campaign(request, campaign_id):
    try:
        api_url = f"https://control.star.dev.br/api/campaigns/exit/{campaign_id}"
        campaign_response = call_api(request, "POST", api_url)

        if campaign_response:
            messages.success(request, "Campanha encerrada com sucesso.")
        return redirect('dashboard_campaign')

    except Exception as e:
        print(f"[encerrar_campaign] Error: {e}")
        messages.error(request, f"Erro ao encerrar campanha: {str(e)}")
        return redirect('dashboard_campaign')

@login_required
def delete_campaign(request, campaign_id):
    try:
        api_url = f"https://control.star.dev.br/api/campaigns/del/{campaign_id}"
        campaign_response = call_api(request, "POST", api_url)

        if campaign_response:
            messages.success(request, "Campanha excluída com sucesso!")
        return redirect('dashboard_campaign')

    except Exception as e:
        print(f"[delete_campaign] Error: {e}")
        messages.error(request, f"Erro ao excluir campanha: {str(e)}")
        return redirect('dashboard_campaign')
