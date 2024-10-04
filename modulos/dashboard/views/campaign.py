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

        # Faz a requisição para a API
        api_url = f"https://control.star.dev.br/api/campaigns?dataInicio={data_inicio}&dataFim={data_fim}"
        response = requests.get(api_url)

        # Verifica o status da resposta da API
        if response.status_code == 200:
            campaigns = response.json().get('campaigns', [])

        # Inicializando as variáveis globais para os cálculos
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

        # Itera sobre as campanhas e realiza os cálculos
        for campaign in campaigns:
            total_numbers_value = campaign.get('total_numbers')
            total_msg_success_value = campaign.get('send_success')
            total_msg_erro_value = campaign.get('send_error')
            total_responses_value = campaign.get('response_count', 0)

            # Acumula os dados globais
            total_numbers += int(total_numbers_value) if total_numbers_value else 0
            total_success += int(total_msg_success_value) if total_msg_success_value else 0
            total_erro += int(total_msg_erro_value) if total_msg_erro_value else 0
            total_responses += total_responses_value

            # Verifica se a campanha foi finalizada
            if campaign.get('status') == 'finalizado':
                campaign_finaly += 1

            # Calcula a taxa de resposta individual da campanha
            campaign_success = int(total_msg_success_value) if total_msg_success_value else 0
            campaign_response_rate = (total_responses_value / campaign_success) * 100 if campaign_success > 0 else 0
            campaign['response_rate'] = round(campaign_response_rate, 1)

            # Formatando datas
            start_date_str = campaign.get('start_date')
            if start_date_str:
                start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S.%f')
                campaign['start_date_formatted'] = start_date_obj.strftime('%Y-%m-%d %H:%M')
            else:
                campaign['start_date_formatted'] = 'N/A'

            end_date_str = campaign.get('end_date')
            if end_date_str:
                end_date_obj = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S.%f')
                campaign['end_date_formatted'] = end_date_obj.strftime('%Y-%m-%d %H:%M')
            else:
                campaign['end_date_formatted'] = 'N/A'

            # Verifica se a campanha foi iniciada hoje
            start_date = datetime.strptime(campaign.get('start_date'), '%Y-%m-%dT%H:%M:%S.%f').date()
            if start_date == datetime.now().date():
                total_numbers_now += int(total_numbers_value) if total_numbers_value else 0
                total_erro_now += int(total_msg_erro_value) if total_msg_erro_value else 0
                total_success_now += int(total_msg_success_value) if total_msg_success_value else 0
                total_responses_now += campaign.get('response_count', 0)
                campaign_total_now += 1
                if campaign.get('status') == 'finalizado':
                    campaign_finaly_now += 1

        # Calcula a taxa de resposta global para o período filtrado
        response_rate = (total_responses / total_success) * 100 if total_success > 0 else 0
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
            'response_rate': f"{response_rate:.2f}",
            'response_rate_now': f"{response_rate_now:.2f}",
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
        # Faz a requisição para a API
        api_url = f"https://control.star.dev.br/api/campaigns/{campaign_id}"
        response = requests.get(api_url)
        campaign_response = response.json()

        # Verifica o status da resposta da API
        if response.status_code != 200:
            messages.error(request, "[details_campaign] ERROR: campanha não existe")
            return redirect('dashboard_campaign')

        # Extraindo os dados da campanha
        campaign_data_str = campaign_response.get('campaign', '[]')
        campaign_list = json.loads(campaign_data_str)
        if not campaign_list:
            raise Exception("[details_campaign] ERROR: Dados da campanha não encontrados.")
        campaign_obj = campaign_list[0]  # Pega o primeiro elemento da lista
        campaign_fields = campaign_obj.get('fields', {})  # Acessa o 'fields' da campanha
        campaign_fields['id'] = campaign_obj['pk']

        # Extraindo e convertendo os logs
        logs_data_str = campaign_response.get('logs', '[]')
        logs = json.loads(logs_data_str)

        # Contagem de respostas separada
        responses = campaign_response.get('responses', 0)

        # Inicializando os arrays de contagem para cada hora do dia
        array_horas_sucesso = [0] * 24  # Mensagens de sucesso
        array_horas_erro = [0] * 24     # Mensagens de erro

        # Itera sobre os logs e separa os dados por hora e status
        for log in logs:
            fields = log.get('fields', {})
            criado = fields.get('created_at')
            status = fields.get('status')

            if criado:
                # Converte a string para um objeto datetime
                data_criacao = datetime.strptime(criado, '%Y-%m-%dT%H:%M:%S.%f')
                hora = data_criacao.hour  # Obtém a hora do log

                # Formata a data de criação
                start_date_str = fields.get('created_at')
                if start_date_str:
                    try:
                        start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S.%f')
                        log['fields']['start_date_formatted'] = start_date_obj.strftime('%Y-%m-%d %H:%M')
                    except ValueError:
                        log['fields']['start_date_formatted'] = 'Formato de data inválido'
                else:
                    log['fields']['start_date_formatted'] = 'Data não disponível'

                # Atualiza o array correspondente com base no status
                if status == 'sucesso':
                    array_horas_sucesso[hora] += 1
                elif status == 'erro':
                    array_horas_erro[hora] += 1

        # Métricas da campanha
        total_numbers = int(campaign_fields.get('total_numbers', 0) or 0)  # Garante que o valor não seja None
        total_success = int(campaign_fields.get('send_success', 0) or 0)  # Mesma coisa para send_success
        total_erro = int(campaign_fields.get('send_erro', 0) or 0)  # Mesma coisa para send_erro

        # Calcula a taxa de resposta com base no total de sucessos
        response_rate = (responses / total_success) * 100 if total_success > 0 else 0

        # Renderiza os dados para o template
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
        print(f'[details_campaign] ERROR: {e}')
        messages.error(request, f'[details_campaign] ERROR: {str(e)}')
        return redirect('dashboard_campaign')
    
@login_required
def encerrar_campaign(request, campaign_id):
    try:
        api_url = f"https://control.star.dev.br/api/campaigns/exit/{campaign_id}"
        response = requests.post(api_url)
        campaign_response = response.json()

        # Verifica o status da resposta da API
        if response.status_code != 200 or response.status_code != 201:
            print(f'[encerra_campanha] error {campaign_response}')
            messages.error(request, "[details_campaign] ERROR: campanha não existe")
            return redirect('dashboard_campaign')
        
        messages.success(request, "Campanha encerrada com sucesso.")
        return redirect('dashboard_campaign')
    except Exception as e:
        print(f'[encerra_campanha] error {e}')
        messages.error(request, f'[encerra_campanha] ERROR: {str(e)}')
        redirect('dashboard_campaign')

def delete_campaign(request, campaign_id):
    try:
        api_url = f"https://control.star.dev.br/api/campaigns/del/{campaign_id}"
        response = requests.post(api_url)
        campaign_response = response.json()

        # Verifica o status da resposta da API
        if response.status_code != 200 or response.status_code != 201:
            print(f'[encerra_campanha] error {campaign_response}')
            messages.error(request, "[details_campaign] ERROR: campanha não existe")
            return redirect('dashboard_campaign')
        
        messages.success(request, "Campanha excluida com sucesso!")
        return redirect('dashboard_campaign')
    except Exception as e:
        print(f'[encerra_campanha] error {e}')
        messages.error(request, f'[encerra_campanha] ERROR: {str(e)}')
        redirect('dashboard_campaign')
