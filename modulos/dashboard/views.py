from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import requests
from datetime import datetime, timedelta
import json

@login_required
def dashboard_campaign(request):
    try:
        # Obter os parâmetros da URL
        data_inicio = request.GET.get('dataInicio')
        data_fim = request.GET.get('dataFim')
        campaigns = []
        
        # Se os parâmetros não forem passados, definir o início e o fim do mês atual
        if not data_inicio:
            # Definir o primeiro dia do mês atual
            data_inicio = datetime.now().replace(day=1).strftime('%Y-%m-%d')

        if not data_fim:
            # Definir o último dia do mês atual
            next_month = datetime.now().replace(day=28) + timedelta(days=4)  # Garante que cheguemos ao próximo mês
            data_fim = next_month.replace(day=1) - timedelta(days=1)  # Volta ao último dia do mês atual
            data_fim = data_fim.strftime('%Y-%m-%d')

        # URL da API com os parâmetros de data
        api_url = f"http://10.0.0.73:8888/api/campaigns?dataInicio={data_inicio}&dataFim={data_fim}"

        # Fazer a requisição GET para a API
        response = requests.get(api_url)
        
        if response.status_code == 200:
            # A resposta da API é uma string JSON, então convertemos para um objeto Python
            campaigns_data = response.json()
            
            # Converter o campo 'campaigns' de string para lista de dicionários
            campaigns = json.loads(campaigns_data['campaigns'])

        total_numbers = 0 
        total_numbers_now = 0
        campaign_total_now = 0
        total_success = 0
        total_success_now = 0
        total_erro = 0
        total_erro_now = 0
        total_responses_now = 0
        campaign_finaly = 0
        campaign_finaly_now = 0

        # Iterar sobre a lista de campanhas
        for campaign in campaigns:
            # Acessa o total_numbers dentro do campo 'fields'
            total_numbers_value = campaign['fields'].get('total_numbers')
            total_msg_success_value = campaign['fields'].get('send_success')
            total_msg_erro_value = campaign['fields'].get('send_erro') 
            total_responses = 30
            # Soma o valor de total, se não for None
            total_numbers += int(total_numbers_value) if total_numbers_value is not None else 0
            total_success += int(total_msg_success_value) if total_msg_success_value is not None else 0
            total_erro += int(total_msg_erro_value) if total_msg_erro_value is not None else 0

            if campaign['fields'].get('status') == 'finalizado':
                campaign_finaly += 1

            campaign['fields']['response_rate'] = (total_responses / total_success) * 100 if total_success > 0 else 0

            start_date_str = campaign['fields'].get('start_date')
            if start_date_str:
                start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                campaign['fields']['start_date_formatted'] = start_date_obj.strftime('%Y-%m-%d %H:%M')
            else:
                campaign['fields']['start_date_formatted'] = 'N/A'  # Ou outro valor padrão

            # Verificar se o 'end_date' não é None antes de tentar convertê-lo
            end_date_str = campaign['fields'].get('end_date')
            if end_date_str:
                end_date_obj = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                campaign['fields']['end_date_formatted'] = end_date_obj.strftime('%Y-%m-%d %H:%M')
            else:
                campaign['fields']['end_date_formatted'] = 'N/A'  # Ou outro valor padrão

            # Verificar se a campanha é de hoje e somar os valores de hoje
            start_date = datetime.strptime(campaign['fields']['start_date'], '%Y-%m-%dT%H:%M:%S.%fZ').date()
            if start_date == (datetime.now().date() + timedelta(days=1)):
                total_numbers_now += int(total_numbers_value) if total_numbers_value is not None else 0
                total_erro_now += int(total_msg_erro_value) if total_msg_erro_value is not None else 0
                total_success_now += int(total_msg_success_value) if total_msg_success_value is not None else 0
                total_responses_now += 34
                campaign_total_now += 1
                if campaign['fields'].get('status') == 'finalizado':
                    campaign_finaly_now += 1
            

        response_rate = (total_responses / total_success) * 100 if total_success > 0 else 0
        response_rate_now = (total_responses_now / total_success_now) * 100 if total_success_now > 0 else 0
        
        # Passar os valores totais para o template
        return render(request, 'dashboard/dashboard-campaign.html', {
            'campaigns': campaigns,
            'total_numbers': total_numbers,
            'total_numbers_now': total_numbers_now,
            'campaign_total': len(campaigns),
            'campaign_total_now': campaign_total_now,
            'total_success':total_success,
            'total_success_now': total_success_now,
            "total_erro": total_erro,
            'total_erro_now': total_erro_now,
            'response_rate': response_rate,
            'response_rate_now':response_rate_now,
            'campaign_finaly':campaign_finaly,
            'campaign_finaly_now':campaign_finaly_now
        })
        
    except Exception as e:
        # Em caso de erro, exibir a mensagem de erro e redirecionar
        print(e)
        messages.error(request, f'ERROR: {str(e)}')
        return redirect('index')