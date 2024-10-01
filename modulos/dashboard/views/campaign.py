from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import requests
from datetime import datetime
from calendar import monthrange

import json

@login_required
def dashboard_campaign(request):
    try:
        data_inicio = request.GET.get('dataInicio')
        data_fim = request.GET.get('dataFim')
        campaigns = []

        # Se os parâmetros não forem passados, definir o início e o fim do mês atual
        if not data_inicio:
            data_inicio = datetime.now().replace(day=1).strftime('%Y-%m-%d')

        if not data_fim:
            today = datetime.now()
            last_day = monthrange(today.year, today.month)[1]
            data_fim = today.replace(day=last_day).strftime('%Y-%m-%d')

        api_url = f"http://186.216.60.62:8888/api/campaigns?dataInicio={data_inicio}&dataFim={data_fim}"
        response = requests.get(api_url)

        if response.status_code == 200:
            campaigns_data = response.json()
            campaigns = json.loads(campaigns_data['campaigns'])

        total_numbers = 0 
        total_numbers_now = 0
        campaign_total_now = 0
        total_success = 0
        total_success_now = 0
        total_erro = 0
        total_erro_now = 0
        total_responses = 0
        total_responses_now = 0
        campaign_finaly = 0
        campaign_finaly_now = 0

        for campaign in campaigns:
            total_numbers_value = campaign['fields'].get('total_numbers')
            total_msg_success_value = campaign['fields'].get('send_success')
            total_msg_erro_value = campaign['fields'].get('send_erro') 
            total_responses += int(campaign['fields'].get('responses'))
            
            total_numbers += int(total_numbers_value) if total_numbers_value else 0
            total_success += int(total_msg_success_value) if total_msg_success_value else 0
            total_erro += int(total_msg_erro_value) if total_msg_erro_value else 0

            if campaign['fields'].get('status') == 'finalizado':
                campaign_finaly += 1

            campaign['fields']['response_rate'] = (int(campaign['fields']['responses']) / total_success) * 100 if total_success > 0 else 0

            start_date_str = campaign['fields'].get('start_date')
            if start_date_str:
                start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                campaign['fields']['start_date_formatted'] = start_date_obj.strftime('%Y-%m-%d %H:%M')
            else:
                campaign['fields']['start_date_formatted'] = 'N/A'

            end_date_str = campaign['fields'].get('end_date')
            if end_date_str:
                end_date_obj = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                campaign['fields']['end_date_formatted'] = end_date_obj.strftime('%Y-%m-%d %H:%M')
            else:
                campaign['fields']['end_date_formatted'] = 'N/A'

            start_date = datetime.strptime(campaign['fields']['start_date'], '%Y-%m-%dT%H:%M:%S.%fZ').date()
            if start_date == datetime.now().date():
                total_numbers_now += int(total_numbers_value) if total_numbers_value else 0
                total_erro_now += int(total_msg_erro_value) if total_msg_erro_value else 0
                total_success_now += int(total_msg_success_value) if total_msg_success_value else 0
                total_responses_now += int(campaign['fields'].get('responses'))
                campaign_total_now += 1
                if campaign['fields'].get('status') == 'finalizado':
                    campaign_finaly_now += 1

        response_rate = 0
        response_rate_now = 0
        if total_success > 0:
            response_rate = (total_responses / total_success) * 100
        if total_success_now > 0:
            response_rate_now = (total_responses_now / total_success_now) * 100
        
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
            'response_rate': response_rate,
            'response_rate_now': response_rate_now,
            'campaign_finaly': campaign_finaly,
            'campaign_finaly_now': campaign_finaly_now
        })
        
    except Exception as e:
        print(e)
        messages.error(request, f'[dashboard_campaign] ERROR: {str(e)}')
        return redirect('index')

@login_required
def details_campaign(request, campaign_id):
    try:
        api_url = f"http://186.216.60.62:8888/api/campaigns/{campaign_id}"
        response = requests.get(api_url)
        campaign_response = response.json()
        print(campaign_response)
        if response.status_code != 200 and response.status_code != 201:
            print("[details_campaign] ERROR: campanha não existe")
            messages.error(request, response.text)
            return redirect('dashboard_campaign')

        # Extraindo e convertendo a string JSON da campanha
        campaign_data_str = campaign_response.get('campaign', '[]')
        campaign_list = json.loads(campaign_data_str)
        if not campaign_list:
            raise Exception("[details_campaign] ERROR: Dados da campanha não encontrados.")
        campaign_obj = campaign_list[0]  # Pega o primeiro elemento da lista
        campaign_fields = campaign_obj.get('fields', {})  # Acessa o 'fields' da campanha

        # Extraindo e convertendo a string JSON dos logs
        logs_data_str = campaign_response.get('logs', '[]')
        logs = json.loads(logs_data_str)

        # Inicializando os arrays de contagem para cada hora do dia
        array_horas_sucesso = [0] * 24  # Mensagens de sucesso
        array_horas_erro = [0] * 24     # Mensagens de erro

        # Itera sobre os logs e separa os dados por hora e status
        for log in logs:
            fields = log.get('fields', {})
            criado = fields.get('created_at')
            status = fields.get('status')  # Verifica o status da mensagem

            if criado:
                # Converte a string para um objeto datetime
                data_criacao = datetime.strptime(criado, '%Y-%m-%dT%H:%M:%S.%fZ')
                hora = data_criacao.hour  # Obtém a hora do log

                start_date_str = fields.get('created_at')
                if start_date_str:  # Verifica se existe uma data antes de converter
                    try:
                        start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                        log['fields']['start_date_formatted'] = start_date_obj.strftime('%Y-%m-%d %H:%M')
                    except ValueError:
                        # Caso o formato da data não corresponda, tratamos o erro aqui
                        log['fields']['start_date_formatted'] = 'Formato de data inválido'
                else:
                    log['fields']['start_date_formatted'] = 'Data não disponível'

                # Atualiza o array correspondente com base no status
                if status == 'sucesso':
                    array_horas_sucesso[hora] += 1  # Incrementa o índice para sucesso
                elif status == 'erro':
                    array_horas_erro[hora] += 1  # Incrementa o índice para erro

        # Métricas da campanha
        total_numbers = int(campaign_fields.get('total_numbers') if campaign_fields.get('total_numbers') else 0)
        total_success = int(campaign_fields.get('send_success') if campaign_fields.get('send_success') else 0)
        total_erro = int(campaign_fields.get('send_erro') if campaign_fields.get('send_erro') else 0)
        responses = int(campaign_fields.get('responses') if campaign_fields.get('responses') else 0)

        # Calcula a taxa de resposta
        response_rate = (responses / total_success) * 100 if total_success > 0 else 0

        return render(request, 'details/details-campaign.html', {
            'campaign': campaign_fields,
            'total_numbers': total_numbers,
            'total_success': total_success,
            "total_erro": total_erro,
            'response_rate': response_rate,
            'msg_sucess': array_horas_sucesso,
            'msg_erro': array_horas_erro,
            'logs': logs,
        })

    except Exception as e:
        print(f'[details_campaign] ERROR exception: {e}')
        messages.error(request, f'[details_campaign] ERROR: {str(e)}')
        return redirect('dashboard_campaign')