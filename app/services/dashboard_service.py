from datetime import date, timedelta

from app.services.db import get_db_connection
from app.services.sessao_service import encerrar_sessoes_expiradas


def _buscar_valor(cursor, query, parametros):
    cursor.execute(query, parametros)
    return cursor.fetchone()['total']


def buscar_dados_dashboard(terapeuta_id):
    """Reúne indicadores e séries curtas para o painel do terapeuta."""

    encerrar_sessoes_expiradas(terapeuta_id)

    conn = get_db_connection()

    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)

    try:

        # ==========================================
        # INDICADORES
        # ==========================================

        indicadores = {

            'pacientes': _buscar_valor(
                cursor,
                '''
                SELECT COUNT(*) AS total
                FROM pacientes
                WHERE terapeuta_id = %s
                ''',
                (terapeuta_id,)
            ),

            'agendados': _buscar_valor(
                cursor,
                '''
                SELECT COUNT(*) AS total
                FROM agendamentos
                WHERE terapeuta_id = %s
                  AND status = 'AGENDADO'
                  AND data_hora_fim >= NOW()
                ''',
                (terapeuta_id,)
            ),

            'concluidos': _buscar_valor(
                cursor,
                '''
                SELECT COUNT(*) AS total
                FROM agendamentos
                WHERE terapeuta_id = %s
                  AND status = 'CONCLUIDO'
                ''',
                (terapeuta_id,)
            ),

            'cancelados': _buscar_valor(
                cursor,
                '''
                SELECT COUNT(*) AS total
                FROM agendamentos
                WHERE terapeuta_id = %s
                  AND status = 'CANCELADO'
                ''',
                (terapeuta_id,)
            ),

            'em_andamento': _buscar_valor(
                cursor,
                '''
                SELECT COUNT(*) AS total
                FROM sessoes s
                INNER JOIN agendamentos a
                    ON a.id = s.agendamento_id
                WHERE a.terapeuta_id = %s
                  AND s.ativa = TRUE
                ''',
                (terapeuta_id,)
            ),

        }


        # ==========================================
        # PERÍODO DO GRÁFICO
        # ==========================================

        inicio_periodo = date.today() - timedelta(days=6)
        fim_periodo = date.today()


        # ==========================================
        # AGENDADOS POR DIA
        # ==========================================

        cursor.execute(
            '''
            SELECT
                DATE(data_hora_inicio) AS dia,
                COUNT(DISTINCT paciente_id) AS total
            FROM agendamentos
            WHERE terapeuta_id = %s
              AND status = 'AGENDADO'
              AND DATE(data_hora_inicio)
                  BETWEEN %s AND %s
            GROUP BY DATE(data_hora_inicio)
            ''',
            (
                terapeuta_id,
                inicio_periodo,
                fim_periodo
            )
        )

        agendados_por_dia = {
            linha['dia']: linha['total']
            for linha in cursor.fetchall()
        }


        # ==========================================
        # CONCLUÍDOS POR DIA
        # ==========================================

        cursor.execute(
            '''
            SELECT
                DATE(data_hora_inicio) AS dia,
                COUNT(*) AS total
            FROM agendamentos
            WHERE terapeuta_id = %s
              AND status = 'CONCLUIDO'
              AND DATE(data_hora_inicio)
                  BETWEEN %s AND %s
            GROUP BY DATE(data_hora_inicio)
            ''',
            (
                terapeuta_id,
                inicio_periodo,
                fim_periodo
            )
        )

        concluidos_por_dia = {
            linha['dia']: linha['total']
            for linha in cursor.fetchall()
        }


        # ==========================================
        # CANCELADOS POR DIA
        # ==========================================

        cursor.execute(
            '''
            SELECT
                DATE(data_hora_inicio) AS dia,
                COUNT(*) AS total
            FROM agendamentos
            WHERE terapeuta_id = %s
              AND status = 'CANCELADO'
              AND DATE(data_hora_inicio)
                  BETWEEN %s AND %s
            GROUP BY DATE(data_hora_inicio)
            ''',
            (
                terapeuta_id,
                inicio_periodo,
                fim_periodo
            )
        )

        cancelados_por_dia = {
            linha['dia']: linha['total']
            for linha in cursor.fetchall()
        }


        # ==========================================
        # SÉRIE DO GRÁFICO
        # ==========================================

        serie = []
        maior_valor = 1

        for deslocamento in range(7):

            dia = (
                inicio_periodo
                + timedelta(days=deslocamento)
            )

            agendados = agendados_por_dia.get(dia, 0)
            concluidos = concluidos_por_dia.get(dia, 0)
            cancelados = cancelados_por_dia.get(dia, 0)

            maior_valor = max(
                maior_valor,
                agendados,
                concluidos,
                cancelados
            )

            serie.append({
                'rotulo': dia.strftime('%d/%m'),
                'agendados': agendados,
                'concluidos': concluidos,
                'cancelados': cancelados
            })


        # ==========================================
        # PERCENTUAIS DO GRÁFICO
        # ==========================================

        for item in serie:

            item['agendados_percentual'] = round(
                item['agendados']
                / maior_valor
                * 100,
                1
            )

            item['concluidos_percentual'] = round(
                item['concluidos']
                / maior_valor
                * 100,
                1
            )

            item['cancelados_percentual'] = round(
                item['cancelados']
                / maior_valor
                * 100,
                1
            )


        # ==========================================
        # PACIENTES RECENTES
        # ==========================================

        cursor.execute(
            '''
            SELECT
                nome,
                email,
                telefone,
                criado_em
            FROM pacientes
            WHERE terapeuta_id = %s
            ORDER BY criado_em DESC
            LIMIT 12
            ''',
            (terapeuta_id,)
        )

        pacientes_recentes = cursor.fetchall()


        # ==========================================
        # PRÓXIMOS AGENDAMENTOS
        # ==========================================

        cursor.execute(
            '''
            SELECT
                p.nome AS paciente_nome,
                a.data_hora_inicio,
                s.ativa
            FROM agendamentos a

            INNER JOIN pacientes p
                ON p.id = a.paciente_id

            LEFT JOIN sessoes s
                ON s.agendamento_id = a.id

            WHERE a.terapeuta_id = %s
              AND a.status = 'AGENDADO'
              AND a.data_hora_fim >= NOW()

            ORDER BY a.data_hora_inicio ASC

            LIMIT 5
            ''',
            (terapeuta_id,)
        )

        proximos_agendamentos = cursor.fetchall()


        # ==========================================
        # AGENDAMENTOS CANCELADOS
        # ==========================================

        cursor.execute(
            '''
            SELECT
                p.nome AS paciente_nome,
                a.data_hora_inicio,
                a.data_hora_fim,
                a.status
            FROM agendamentos a

            INNER JOIN pacientes p
                ON p.id = a.paciente_id

            WHERE a.terapeuta_id = %s
              AND a.status = 'CANCELADO'

            ORDER BY a.data_hora_inicio DESC

            LIMIT 5
            ''',
            (terapeuta_id,)
        )

        agendamentos_cancelados = cursor.fetchall()


        # ==========================================
        # RETORNO
        # ==========================================

        return {
            'indicadores': indicadores,
            'serie': serie,
            'pacientes_recentes': pacientes_recentes,
            'proximos_agendamentos': proximos_agendamentos,
            'agendamentos_cancelados': agendamentos_cancelados
        }

    finally:

        cursor.close()
        conn.close()