from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from calendar import monthrange
from .utils import *
import json

@login_required
def dashboard_campaign(request):
    try:
        # Obter os parâmetros de data da URL
        data_inicio = request.GET.get('dataInicio')
        data_fim = request.GET.get('dataFim')

        # Se os parâmetros não forem passados, definir o início e o fim do mês atual
        if not data_inicio:
            data_inicio = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        if not data_fim:
            today = datetime.now()
            last_day = monthrange(today.year, today.month)[1]
            data_fim = today.replace(day=last_day).strftime('%Y-%m-%d')

        # Converter data_inicio e data_fim para objetos datetime
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d')

        # Faz a requisição para a API
        api_url = f"https://control.star.dev.br/api/campaigns?dataInicio={data_inicio.strftime('%Y-%m-%d')}&dataFim={data_fim.strftime('%Y-%m-%d')}"
        campaigns_data = call_api(request, "GET", api_url)

        # Inicializando as variáveis globais para os cálculos
        total_numbers, total_success, total_erro, total_responses = 0, 0, 0, 0
        total_numbers_now, total_success_now, total_erro_now, total_responses_now = 0, 0, 0, 0
        campaign_total_now, campaign_finaly, campaign_finaly_now = 0, 0, 0

        ARRAY_MONTH_SUCCESS = get_days_range_array(data_inicio, data_fim)
        ARRAY_MONTH_ERROR = get_days_range_array(data_inicio, data_fim)
        ARRAY_MONTH_RESPONSE = get_days_range_array(data_inicio, data_fim)

        # Itera sobre as campanhas e realiza os cálculos
        campaigns = campaigns_data.get('campaigns', [])
        for campaign in campaigns:
            total_numbers_value = int(campaign.get('total_numbers', 0)) if campaign.get('total_numbers') is not None else 0
            total_success_value = int(campaign.get('send_success', 0)) if campaign.get('send_success') is not None else 0
            total_error_value = int(campaign.get('send_error', 0)) if campaign.get('send_error') is not None else 0
            total_responses_value = int(campaign.get('response_count', 0)) if campaign.get('response_count') is not None else 0

            # Acumula os dados globais
            total_numbers += total_numbers_value
            total_success += total_success_value
            total_erro += total_error_value
            total_responses += total_responses_value

            # Formatando datas
            start_date_str = campaign.get('start_date')
            if start_date_str:
                try:
                    start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S.%f')

                    # Verifica se a data está dentro do intervalo de data_inicio e data_fim
                    if data_inicio <= start_date_obj <= data_fim:
                        # Calcula o índice correto no array com base no número de dias desde data_inicio
                        day_index = (start_date_obj - data_inicio).days

                        # Atualiza os arrays com os valores acumulados
                        ARRAY_MONTH_SUCCESS[day_index] += total_success_value
                        ARRAY_MONTH_ERROR[day_index] += total_error_value
                        ARRAY_MONTH_RESPONSE[day_index] += total_responses_value

                    # Formata a data para exibição
                    campaign['start_date_formatted'] = start_date_obj.strftime('%Y-%m-%d %H:%M')
                except ValueError:
                    campaign['start_date_formatted'] = 'Data inválida'
            else:
                campaign['start_date_formatted'] = 'N/A'

            end_date_str = campaign.get('end_date')
            if end_date_str:
                try:
                    end_date_obj = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S.%f')
                    campaign['end_date_formatted'] = end_date_obj.strftime('%Y-%m-%d %H:%M')
                except ValueError:
                    campaign['end_date_formatted'] = 'Data inválida'
            else:
                campaign['end_date_formatted'] = 'N/A'

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
            'campaign_finaly_now': campaign_finaly_now,
            'msg_month': {
                'success': ARRAY_MONTH_SUCCESS,
                'error': ARRAY_MONTH_ERROR,
                'response': ARRAY_MONTH_RESPONSE
            }
        })

    except Exception as e:
        print(f"[dashboard_campaign] Error: {e}")
        messages.error(request, f"Erro ao carregar campanhas: {str(e)}")
        return redirect('index')

@login_required
def details_campaign(request, campaign_id):
    try:
        # Faz a requisição para a API
        api_url = f"https://control.star.dev.br/api/campaigns/{campaign_id}"
        campaign_response = call_api(request, "GET", api_url)

        if not campaign_response:
            print("response não obteve dados")
            messages.error(request, "Dados da campanha não encontrados.")
            return redirect('dashboard_campaign')

        # Extraindo os dados da campanha
        campaign_obj = campaign_response.get('campaign', {})
        if not campaign_obj:
            messages.error(request, "Dados da campanha não encontrados.")
            return redirect('dashboard_campaign')

        # A campanha já é um dicionário, então não é necessário o loop
        campaign_fields = campaign_obj
        campaign_fields['id'] = campaign_obj.get('id')

        
        

        # Extraindo e convertendo os logs que estão em formato string
        logs_str = campaign_response.get('logs', '[]')
        try:
            logs = json.loads(logs_str)  # Convertendo a string de logs em uma lista de dicionários
        except json.JSONDecodeError:
            logs = []
            print(f"Erro ao decodificar os logs: {logs_str}")

        # Inicializando os arrays de contagem para cada hora do dia
        array_horas_sucesso = [0] * 24  # Mensagens de sucesso
        array_horas_erro = [0] * 24     # Mensagens de erro
        array_horas_response = [0] * 24  # Respostas recebidas

        # Itera sobre os logs e separa os dados por hora e status
        for log in logs:
            fields = log.get('fields', {})
            criado = fields.get('created_at')
            status = fields.get('status')

            # Formatando datas
            fields_str = fields.get('created_at')
            if fields_str :
                fields_obj = datetime.strptime(fields_str, '%Y-%m-%dT%H:%M:%S.%f')
                fields['created_at_formatted'] =  fields_obj.strftime('%Y-%m-%d %H:%M')

            if criado:
                try:
                    # Converte a string para um objeto datetime
                    data_criacao = datetime.strptime(criado, '%Y-%m-%dT%H:%M:%S.%f')
                    hora = data_criacao.hour  # Obtém a hora do log

                    # Atualiza o array correspondente com base no status
                    if status == 'sucesso':
                        array_horas_sucesso[hora] += 1
                    elif status == 'erro':
                        array_horas_erro[hora] += 1
                    elif status == 'response':
                        array_horas_response[hora] += 1  # Contagem de respostas por hora
                except ValueError as ve:
                    print(f"Erro ao converter data: {ve}")

        # Métricas da campanha
        print(campaign_fields)
        total_numbers = int(campaign_fields.get('total_numbers', 0) or 0)
        total_success = int(campaign_fields.get('send_success', 0) or 0)
        total_erro = int(campaign_fields.get('send_error', 0) or 0)

        # Calcula a taxa de resposta com base no total de sucessos
        response_count = int(campaign_fields.get('response_count', 0))
        response_rate = (response_count / total_success) * 100 if total_success > 0 else 0

        # Renderiza os dados para o template
        return render(request, 'details/details-campaign.html', {
            'campaign': campaign_fields,
            'total_numbers': total_numbers,
            'total_success': total_success,
            "total_erro": total_erro,
            'response_rate': f"{response_rate:.2f}",
            'response_count': response_count,
            'msg_sucess': array_horas_sucesso,
            'msg_erro': array_horas_erro,
            'msg_response': array_horas_response,
            'logs': logs 
        })

    except Exception as e:
        print(f'[details_campaign] ERROR: {type(e).__name__} - {e}')
        messages.error(request, f'[details_campaign] ERROR: {str(e)}')
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
